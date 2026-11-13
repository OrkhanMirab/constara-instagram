"""M02 «Buz kubu» — gizli irəliləyiş (Metafor, 2026-11-14, gecə planı).

Hər gün buzun yanına bir şam qoyulur, termometr 25° → 31° — buz tərpənmir («Nothing is changing»). İçində qızılı toxum
getdikcə parlayır (iş yığılır). 32°-də buz bir anda əriyir, toxum cücərir. CTA: «Send this to someone stuck at 31°.»
İşlətmə: python3 m02_buz.py <scratch> [--no-audio] [--tts <kokoro qovluğu>] ; render.mjs ; ffmpeg.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 22.0
STEPS = [(3.4, 25), (4.4, 26), (5.4, 27), (7.2, 28), (8.5, 29), (10.6, 30), (13.1, 31), (14.15, 32)]   # (vaxt, °F) — hər addım bir şam
MELT = [14.3, 15.6]
SPROUT = [15.3, 18.0]
END = 18.7
TEXTS = [
    (0.10, 3.25, "WEEKS OF WORK.\nNOTHING IS CHANGING.", "NOTHING", "red"),
    (3.35, 6.50, "YOU SHOW UP.\nEVERY DAY.", "EVERY DAY.", "gold"),
    (6.60, 9.80, "STILL ICE.\nMOST PEOPLE QUIT HERE.", "QUIT", "red"),
    (9.90, 12.90, "THE WORK ISN'T LOST.\nIT'S STORED.", "STORED.", "gold"),
    (15.45, 18.55, "THEN, ALL AT ONCE,\nEVERYTHING CHANGES.", "EVERYTHING", "gold"),
    (18.75, 21.80, "SEND THIS TO SOMEONE\nSTUCK AT 31°.", "31°.", "gold"),
]
VO = [(0.15, "Weeks of work. And nothing is changing."), (3.35, "Twenty-five degrees. Twenty-six. Twenty-seven."),
      (6.65, "Still ice. Most people quit right here."), (9.95, "But the work isn't lost. It's being stored."),
      (12.95, "Thirty-one. Thirty-two."), (15.5, "And then, all at once, everything changes."),
      (18.8, "Send this to someone stuck at thirty-one.")]
TL = dict(fps=FPS, dur=DUR, steps=STEPS, melt=MELT, sprout=SPROUT, end=END, texts=TEXTS)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def voice_track(N):
    if '--tts' not in sys.argv:
        return None
    from kokoro_onnx import Kokoro
    from scipy.signal import resample_poly
    d = sys.argv[sys.argv.index('--tts') + 1]
    k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    v = np.zeros(N, np.float32)
    for t0, txt in VO:
        a, sr = k.create(txt, voice='am_michael', speed=0.92, lang='en-us')
        i = np.where(np.abs(a) > .01)[0]; a = a[max(0, i[0] - 200):i[-1] + 800]
        a = resample_poly(a, S.SR, sr).astype(np.float32)
        j = int(t0 * S.SR); v[j:j + len(a)] += a[:N - j]
        print(f'  vo {t0:5.2f} +{len(a) / S.SR:.2f}s  {txt}')
    return S.voice_chain(v)


def audio(path):
    N = int(DUR * S.SR)
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    tt = np.arange(N) / S.SR
    fx.add(0, (S.lp(noise(N, 2), 500) * .03).astype(np.float32))           # soyuq külək
    for t0, deg in STEPS[:-1]:                                               # şam yanır: kibrit + tik
        d = int(.07 * S.SR); fx.add(t0 - .05, (S.hp(noise(d, int(t0 * 9)), 2500) * np.exp(-np.arange(d) / (d / 3)) * .35).astype(np.float32))
        fx.add(t0, S.tick(.5))
    for k in range(5):                                                       # çatlama
        d = int(.04 * S.SR); fx.add(13.4 + k * .2, (S.hp(noise(d, 70 + k), 1500) * np.exp(-np.arange(d) / (d / 5)) * .5).astype(np.float32), pan=.3 - .15 * k)
    fx.add(MELT[0] - 1.3, S.riser(1.25, .8)); fx.add(MELT[0], S.boom(.8)); fx.add(MELT[0], S.taiko(.6))
    for k in range(10):                                                      # damcılar
        t0 = MELT[0] + .2 + k * .14; ct = S.tarr(.15)
        fx.add(t0, (np.sin(2 * np.pi * (900 + 300 * k % 600) * ct * (1 + 2 * ct)) * np.exp(-ct * 30) * .08).astype(np.float32), pan=(k % 3 - 1) * .3)
    # musiqi: soyuq minor (gözləmə) → 32°-də major açılış
    for k, (ch, t0) in enumerate([('Am', 0), ('F', 3.35), ('Dm', 6.6), ('Am', 9.9), ('F', 12.0)]):
        d2 = (3.35 if k < 3 else 3.25 if k == 3 else 2.3)
        mus.add(t0, S.pad(ch, d2, cut=500 + 80 * k, v=.7, att=.4)); mus.add(t0, S.sub(ch, d2 * .9, v=.35))
        for j in range(3):
            mus.add(t0 + .2 + j * 1.0, S.piano(S.hz(S.CHORDS[ch][1][2 + j]) * 2, 2.4, .38))
    mus.add(9.9, S.heartbeat(.4))
    mus.add(MELT[0], S.shimmer('C', 3.0, 1.2))
    for k, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G']):
        t0 = MELT[0] + k * 1.25
        mus.add(t0, S.strings(ch, 1.4, v=.7 + .08 * k, att=.25)); mus.add(t0, S.pad(ch, 1.4, cut=1200, v=.7, att=.15)); mus.add(t0, S.sub(ch, 1.1, v=.45))
        if k >= 1: mus.add(t0, S.kick(.35 + .05 * k))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6']):
        mus.add(END + .3 + i * .45, S.piano(S.hz(nm), 2.4, .36))
    m = S.apply_reverb(mus.x, S.reverb_ir(3.0), .3)[:N]
    f = S.apply_reverb(fx.x, S.reverb_ir(1.2, 6000, 5), .12)[:N]
    vo = voice_track(N)
    out = S.mix(vo, m, f, duck_db=10.0)[:N] if vo is not None else np.tanh((m * .6 + f * .9)[:N])
    fade = int(.6 * S.SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm02_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
