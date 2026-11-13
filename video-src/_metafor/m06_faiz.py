"""M06 «1%» — iki yol: 1% yaxşı (qızılı pilləkən yuxarı) və 1% pis (qırmızı pilləkən aşağı) (Metafor, 2026-11-14).

Eyni başlanğıc → gün sayğacı 1 → 30 → 100 → 365; 1.01^365 = 37.8, 0.99^365 = 0.03. Kamera fərq böyüdükcə geri çəkilir (yenilik).
İşlətmə: python3 m06_faiz.py <scratch> [--no-audio] [--tts <kokoro qovluğu>] ; render.mjs ; ffmpeg.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 23.5
DAYS = [(0, 1), (3.3, 1), (6.4, 30), (9.6, 100), (13.4, 365)]   # (vaxt, gün) — aralar arasında yumşaq keçid
REVEAL = 13.5
END = 17.4
TEXTS = [
    (0.10, 3.25, "IT'S JUST ONE DAY.\nWHAT CAN IT CHANGE?", "ONE DAY.", "gold"),
    (3.35, 6.40, "1% BETTER.\n1% WORSE.", "1% WORSE.", "red"),
    (6.50, 9.50, "AFTER A MONTH,\nYOU BARELY NOTICE.", "BARELY", "gold"),
    (9.60, 13.30, "AFTER A YEAR,\nIT'S A DIFFERENT LIFE.", "DIFFERENT LIFE.", "gold"),
    (13.45, 17.25, "37.8× BETTER.\nOR ALMOST NOTHING LEFT.", "37.8×", "gold"),
    (17.45, 23.30, "SAME START.\nDIFFERENT CHOICES.\nSEND THIS TO YOUR 1% FRIEND.", "1% FRIEND.", "gold"),
]
VO = [(0.15, "It's just one day. What could it change?"), (3.4, "One percent better. One percent worse."),
      (6.55, "After a month, you barely notice."), (9.65, "After a year, it's a different life."),
      (13.5, "Thirty-seven times better. Or almost nothing left."),
      (17.5, "Same start. Different choices. Send this to your one percent friend.")]
TL = dict(fps=FPS, dur=DUR, days=DAYS, reveal=REVEAL, end=END, texts=TEXTS)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def day_at(t):
    d = DAYS[0][1]
    for (a, d0), (b, d1) in zip(DAYS, DAYS[1:]):
        if t >= a:
            u = min(1, (t - a) / (b - a)); u = u * u * (3 - 2 * u); d = d0 + (d1 - d0) * u
    return d


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
    # gün tıqqıltısı: gün sayğacı artdıqca sürətlənir
    last, t = 1, 3.3
    while t < REVEAL:
        d = int(day_at(t))
        if d != last:
            fx.add(t, S.tick(.35 + .25 * min(1, (t - 3.3) / 10))); last = d
        t += 1 / 30
    fx.add(REVEAL - 1.4, S.riser(1.35, .9)); fx.add(REVEAL, S.boom(.9)); fx.add(REVEAL, S.taiko(.7))
    # musiqi: iki səs — qalxan arpecio (major) + enən bas (minor) → ayrılır
    for k, (ch, t0) in enumerate([('Am', 0), ('F', 3.3), ('C', 6.4), ('G', 9.6)]):
        d2 = [3.3, 3.1, 3.2, 3.8][k]
        mus.add(t0, S.pad(ch, d2, cut=600 + 150 * k, v=.65, att=.3)); mus.add(t0, S.sub(ch, d2 * .9, v=.4))
        step = [.8, .55, .35, .22][k]
        n = int(d2 / step)
        for j in range(n):
            nt = S.CHORDS[ch][1][2 + j % 3]
            mus.add(t0 + j * step, S.piano(S.hz(nt) * (2 if j % 6 < 3 else 4), 1.4, .34))
        if k >= 2:
            for j in range(int(d2 / .5)):
                mus.add(t0 + j * .5, S.kick(.3 + .08 * k))
    mus.add(REVEAL, S.shimmer('C', 3.0, 1.2))
    for k, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G', 'C']):
        t0 = REVEAL + k * 1.2
        mus.add(t0, S.strings(ch, 1.35, v=.8, att=.25)); mus.add(t0, S.pad(ch, 1.35, cut=1300, v=.65, att=.15)); mus.add(t0, S.sub(ch, 1.1, v=.45))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6']):
        mus.add(END + 1.2 + i * .45, S.piano(S.hz(nm), 2.4, .36))
    m = S.apply_reverb(mus.x, S.reverb_ir(2.8), .28)[:N]
    f = S.apply_reverb(fx.x, S.reverb_ir(1.0, 6000, 5), .1)[:N]
    vo = voice_track(N)
    out = S.mix(vo, m, f, duck_db=10.0)[:N] if vo is not None else np.tanh((m * .6 + f * .9)[:N])
    fade = int(.7 * S.SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm06_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
