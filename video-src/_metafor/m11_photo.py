"""M11 «Son şəkil» — dostlar illər keçdikcə azalır, sonda biri qalır (Metafor formatı, 2026-11-13).

İstifadəçinin istəyi (moonshotmotion-un «dostlar» reelsinin hekayəsi), amma öz səhnəmiz: masa/şam/qədəh YOX —
hər yaşda dostlar birlikdə ŞƏKİL çəkdirir (taymer → flaş), polaroid ipə asılır, kadrda adam azalır.
60 yaşda taymeri tək qurursan — son saniyədə bir köhnə dost gəlir. Qızılı son polaroid. CTA: göndərmə (izləyici çəkmək).
İşlətmə: python3 m11_photo.py <scratch> ; NODE_PATH=$(npm root -g) node render.mjs <scratch> ; ffmpeg (aşağıda).
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 24.0
ERAS = [  # yaş, kadrda adam (sən daxil), başlanğıc, flaş
    dict(age=18, n=12, t0=0.0, flash=2.75),
    dict(age=25, n=7, t0=3.05, flash=5.35),
    dict(age=32, n=4, t0=5.65, flash=7.95),
    dict(age=45, n=3, t0=8.25, flash=10.55),
    dict(age=60, n=1, t0=10.85, flash=15.35),
]
WALK = [12.9, 14.5]          # köhnə dost gəlir
HUG = 14.55                  # qolunu çiyninə atır
BIG = [15.5, 20.0]           # qızılı son polaroid böyük
END = 20.1                   # CTA
TEXTS = [
    (0.10, 2.70, "AT 18, THE PHOTO\nIS ALWAYS FULL.", "FULL.", "gold"),
    (3.10, 5.30, "AT 25, SOMEONE\nMOVES AWAY.", "AWAY.", "red"),
    (5.70, 7.90, "AT 32, EVERYONE\nIS BUSY.", "BUSY.", "red"),
    (8.30, 10.50, "AT 45, YOU STOP\nASKING WHY.", "WHY.", "red"),
    (10.90, 12.85, "AT 60, YOU SET\nTHE TIMER ALONE.", "ALONE.", "red"),
    (13.05, 15.25, "BUT ONE OF THEM\nSTILL SHOWS UP.", "SHOWS UP.", "gold"),
    (15.60, 17.70, "TIME DOESN'T TAKE\nYOUR FRIENDS.", "TAKE", "gold"),
    (17.80, 19.95, "IT SHOWS YOU\nWHO WAS REAL.", "REAL.", "gold"),
    (20.20, 23.80, "SEND THIS TO THE ONE\nWHO'LL BE IN YOUR\nLAST PHOTO.", "LAST PHOTO.", "gold"),
]
TL = dict(fps=FPS, dur=DUR, eras=ERAS, walk=WALK, hug=HUG, big=BIG, end=END, texts=TEXTS)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def audio(path):
    N = int(DUR * S.SR)
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    # otaq səsi (çox zəif)
    fx.add(0, (S.lp(noise(N, 1), 300) * .025).astype(np.float32))

    def beep(t0, f=1900, v=.22):
        tt = S.tarr(.09)
        fx.add(t0, (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 30) * v).astype(np.float32))

    def shutter(t0, v=1.0):
        d = int(.05 * S.SR)
        c1 = S.hp(noise(d, int(t0 * 50)), 3000) * np.exp(-np.arange(d) / (d / 5)) * .6
        fx.add(t0, (c1 * v).astype(np.float32))
        fx.add(t0 + .07, (c1 * .7 * v).astype(np.float32))
        tt = S.tarr(.6)
        whine = np.sin(2 * np.pi * (3200 + 800 * tt) * tt) * np.exp(-tt * 6) * .05
        fx.add(t0 + .05, (whine * v).astype(np.float32))
        fx.add(t0 - .1, S.whoosh(.4, .5 * v))

    for i, e in enumerate(ERAS):
        for k in range(3):
            beep(e['flash'] - 1.2 + k * .4, 1700 + 120 * k)
        shutter(e['flash'], 1.2 if i == len(ERAS) - 1 else 1.0)
    # addımlar
    for k in range(7):
        t0 = WALK[0] + .1 + k * (WALK[1] - WALK[0] - .1) / 7
        tt = S.tarr(.18)
        th = np.sin(2 * np.pi * (90 + 50 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 22) * .28
        fx.add(t0, th.astype(np.float32), pan=.4 - k * .06)
    # musiqi: yavaş, nostalji piano (Am F C G) → tək qalanda yalnız tək notlar → dost gələndə major + strings
    prog = [('Am', 0.0), ('F', 2.65), ('C', 5.25), ('G', 7.85)]
    mel = [['E5', 'C5', 'A4'], ['F5', 'C5', 'A4'], ['E5', 'C5', 'G4'], ['D5', 'B4', 'G4']]
    for (ch, t0), m in zip(prog, mel):
        mus.add(t0, S.pad(ch, 2.9, cut=650, v=.7, att=.6))
        mus.add(t0, S.sub(ch, 2.5, v=.35))
        for j, nm in enumerate(m):
            mus.add(t0 + .2 + j * .78, S.piano(S.hz(nm), 2.4, .5))
    mus.add(10.4, S.pad('Am', 2.6, cut=420, v=.55, att=.4))
    for j, nm in enumerate(['A4', 'E4', 'C4']):           # tənha
        mus.add(10.9 + j * .9, S.piano(S.hz(nm), 2.6, .42))
    mus.add(12.8, S.heartbeat(.45))
    # dost gəlir: isti keçid
    for k, ch in enumerate(['F', 'C', 'G']):
        t0 = 13.0 + k * .78
        mus.add(t0, S.strings(ch, .95, v=.55 + .15 * k, att=.3))
        mus.add(t0, S.pad(ch, .95, cut=900 + 150 * k, v=.6, att=.15))
    fx.add(ERAS[-1]['flash'] - 1.4, S.riser(1.3, .7))
    mus.add(ERAS[-1]['flash'], S.shimmer('C', 3.0, 1.1))
    fx.add(ERAS[-1]['flash'] + .02, S.boom(.55))
    for k, ch in enumerate(['C', 'Am', 'F', 'G', 'C']):
        t0 = 15.4 + k * 1.75
        mus.add(t0, S.strings(ch, 2.0, v=.95, att=.4))
        mus.add(t0, S.pad(ch, 2.0, cut=1300, v=.7, att=.2, rel=.6))
        mus.add(t0, S.sub(ch, 1.6, v=.45))
    for i, nm in enumerate(['G4', 'C5', 'E5', 'G5', 'E5', 'C5']):
        mus.add(15.6 + i * .7, S.piano(S.hz(nm), 2.4, .42))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6']):
        mus.add(END + .3 + i * .5, S.piano(S.hz(nm), 2.6, .38))
    m = S.apply_reverb(mus.x, S.reverb_ir(3.0), .32)
    f = S.apply_reverb(fx.x, S.reverb_ir(1.0, 6000, 5), .1)
    out = (m * .6 + f * .9)[:N]
    fade = int(1.4 * S.SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out = out / (np.max(np.abs(out)) + 1e-9) * .9
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm11_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
