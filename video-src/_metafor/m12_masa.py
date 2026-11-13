"""M12 «Masa» — ad günü masası illər keçdikcə boşalır, 60-da işıq yananda bir dost hələ oradadır (Metafor, 2026-11-13).

İstifadəçi: «stolda olsunlar, o video kimi, amma ondan yaxşı, premium və rəngli». Öz detallarımız: dəyirmi masa, asma lampa,
yaş yazılmış tort, şarlar/papaqlar/rəngli işıqlar azalır, BOŞ STULLAR qalır; 60-da ikinci lampa dostu göstərir.
İşlətmə: python3 m12_masa.py <scratch> [--no-audio] [--tts <kokoro-v1.0.onnx + voices-v1.0.bin qovluğu>]  (diktor: am_michael 0.92) ; cp render.mjs <scratch>/ ; node render.mjs <scratch> [snap t1,t2]
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 24.5
ERAS = [dict(age=18, t0=0.0), dict(age=25, t0=3.3), dict(age=32, t0=5.9), dict(age=45, t0=8.5), dict(age=60, t0=11.1)]
REVEAL = 13.7   # ikinci lampa yanır
TOAST = 15.6    # fincanlar qalxır
END = 20.6
TEXTS = [
    (0.05, 3.15, "AT 18, EVERY CHAIR\nIS TAKEN.", "EVERY CHAIR", "gold"),
    (3.40, 5.80, "AT 25, PEOPLE\nMOVE AWAY.", "AWAY.", "red"),
    (6.00, 8.40, "AT 32, EVERYONE\nIS BUSY.", "BUSY.", "red"),
    (8.60, 11.00, "AT 45, THE CHAIRS\nSTAY EMPTY.", "EMPTY.", "red"),
    (11.20, 13.55, "AT 60, YOU THINK\nYOU'RE ALONE.", "ALONE.", "red"),
    (13.85, 15.95, "LOOK WHO'S\nSTILL HERE.", "STILL HERE.", "gold"),
    (16.20, 18.30, "TIME DOESN'T TAKE\nYOUR FRIENDS.", "TAKE", "gold"),
    (18.40, 20.45, "IT SHOWS YOU\nWHO STAYED.", "STAYED.", "gold"),
    (20.70, 24.30, "SEND THIS TO THE ONE\nWHO'LL STILL BE\nAT YOUR TABLE.", "AT YOUR TABLE.", "gold"),
]
VO = [  # (başlanğıc, cümlə) — diktor (istifadəçi 11-13: «diktor»)
    (0.15, "At eighteen, every chair is taken."), (3.45, "At twenty-five, people move away."),
    (6.05, "At thirty-two, everyone is busy."), (8.62, "At forty-five, the chairs stay empty."),
    (11.30, "At sixty, you think you're alone."), (13.95, "Look who's still here."),
    (16.30, "Time doesn't take your friends."), (18.50, "It shows you who stayed."),
    (20.90, "Send this to the one who'll still be at your table."),
]
TL = dict(fps=FPS, dur=DUR, eras=ERAS, reveal=REVEAL, toast=TOAST, end=END, texts=TEXTS)


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
    return S.voice_chain(v)


def audio(path):
    N = int(DUR * S.SR)
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    # 18: şən otaq uğultusu (söhbət), getdikcə azalır
    tt = np.arange(N) / S.SR
    crowd = S.bp(noise(N, 4), 300, 2400) * np.interp(tt, [0, 3.2, 5.8, 8.4, 11.0, 24.5], [.16, .09, .045, .02, 0, 0])
    fx.add(0, crowd.astype(np.float32))
    for e in ERAS[1:]:                       # dövr keçidi: lampa titrəyir + saat
        fx.add(e['t0'] - .25, S.whoosh(.45, .55))
        fx.add(e['t0'], S.tick(.6))
    fx.add(REVEAL, S.boom(.35))              # lampa yanır (klik + isti)
    d = int(.03 * S.SR); fx.add(REVEAL - .02, (S.hp(noise(d, 9), 2000) * np.exp(-np.arange(d) / (d / 4)) * .5).astype(np.float32))
    ct = S.tarr(1.6)                         # fincan cingiltisi
    clink = (np.sin(2 * np.pi * 2350 * ct) + .6 * np.sin(2 * np.pi * 3520 * ct)) * np.exp(-ct * 4) * .12
    fx.add(TOAST + .45, clink.astype(np.float32))
    # musiqi: şən (C–G–Am–F, açıq) → getdikcə yavaş, tək piano → işıq yananda isti strings → həll
    for k, (ch, t0) in enumerate([('C', 0.0), ('G', 1.65), ('Am', 3.3), ('F', 5.9), ('Am', 8.5)]):
        d2 = 1.7 if k < 2 else 2.65
        mus.add(t0, S.pad(ch, d2, cut=1200 - 150 * k, v=.7, att=.2))
        mus.add(t0, S.sub(ch, d2 * .9, v=.35))
        notes = S.CHORDS[ch][1]
        for j in range(4 if k < 2 else 3):
            mus.add(t0 + .1 + j * (.4 if k < 2 else .85), S.piano(S.hz(notes[2 + j % 3]) * 2, 2.0, .45 - .05 * k))
    for j, nm in enumerate(['A4', 'E4', 'C4']):
        mus.add(11.2 + j * .85, S.piano(S.hz(nm), 2.6, .38))
    mus.add(11.1, S.pad('Am', 2.6, cut=400, v=.5, att=.4))
    mus.add(REVEAL, S.shimmer('C', 2.5, .9))
    for k, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G', 'C']):
        t0 = REVEAL + k * 1.45
        mus.add(t0, S.strings(ch, 1.6, v=.6 + .08 * k, att=.35))
        mus.add(t0, S.pad(ch, 1.6, cut=1000 + 100 * k, v=.65, att=.2))
        mus.add(t0, S.sub(ch, 1.3, v=.4))
    for i, nm in enumerate(['E5', 'G5', 'C6', 'G5', 'E5', 'C5']):
        mus.add(TOAST + i * .62, S.piano(S.hz(nm), 2.4, .4))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6']):
        mus.add(END + .4 + i * .5, S.piano(S.hz(nm), 2.6, .36))
    m = S.apply_reverb(mus.x, S.reverb_ir(3.0), .3)[:N]
    f = S.apply_reverb(fx.x, S.reverb_ir(1.2, 6000, 5), .12)[:N]
    vo = voice_track(N)
    if vo is not None:
        out = S.mix(vo, m, f, duck_db=10.0)[:N]
    else:
        out = (m * .6 + f * .9)[:N]
        out = np.tanh(out * 1.1) / np.tanh(1.1); out = out / (np.max(np.abs(out)) + 1e-9) * .9
    fade = int(1.4 * S.SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm12_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
