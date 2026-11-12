"""M10 «Kibrit və odun» — motivasiya = kibrit, intizam = odun (Metafor formatı, 2026-11-12).

Gecə, soyuq ocaq. Fiqur kibrit çəkir (MOTIVATION): parlayır, sönür — 37 dəfə. Son kibritlə odunu yandırır.
Hər gün bir odun (DISCIPLINE): alov böyüyür, qaranlıq çəkilir, ulduzlar fırlanır. Partlayış → «Feed the fire.»
İşlətmə: python3 m10_fire.py <scratch> ; NODE_PATH=$(npm root -g) node render.mjs <scratch> ; ffmpeg (README: m01 kimi).
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 23.5
strikes = [1.45, 3.35, 5.05]                       # yavaş kibritlər (hər biri ~1,3 s yanır)
rapid = [5.95 + i * 0.2 for i in range(6)]          # sürətli montaj (sayğac 4 → 37)
IGNITE = 8.95                                        # son kibrit odunu yandırır
u = np.linspace(0, 1, 30)
logs = [round(float(x), 3) for x in 9.7 + (15.0 - 9.7) * u ** (1 / 1.5)]
BOOM = 15.25
END = 19.75

TEXTS = [
    (0.20, 1.35, "WAITING FOR MOTIVATION?", "MOTIVATION?", "gold"),
    (1.45, 4.20, "MOTIVATION IS A MATCH.", "MATCH.", "gold"),
    (4.30, 5.85, "BRIGHT. THEN GONE.", "GONE.", "red"),
    (7.35, 8.65, "MOST PEOPLE KEEP\nSTRIKING MATCHES.", "STRIKING", "red"),
    (8.75, 10.45, "USE IT TO LIGHT\nSOMETHING THAT LASTS.", "LASTS.", "gold"),
    (10.55, 13.00, "DISCIPLINE:\nONE LOG A DAY.", "ONE LOG", "gold"),
    (13.10, 15.10, "SMALL. BORING.\nEVERY DAY.", "EVERY DAY.", "gold"),
    (15.35, 17.40, "NOW IT BURNS\nWITHOUT MOTIVATION.", "WITHOUT", "gold"),
    (17.50, 19.60, "STOP WAITING TO FEEL IT.\nFEED THE FIRE.", "FEED THE FIRE.", "gold"),
]
TL = dict(fps=FPS, dur=DUR, strikes=strikes, rapid=rapid, ignite=IGNITE, logs=logs, boom=BOOM, end=END, texts=TEXTS)


def fire_level(t):
    if t < IGNITE + .1:
        return 0.0
    n = sum(1 for x in logs if t >= x + .3)
    return min(1.0, .06 + .94 * (n / 30) ** .9)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def audio(path):
    N = int(DUR * S.SR)
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    tt = np.arange(N) / S.SR
    lvl = np.array([fire_level(x) for x in tt[::441]])
    lvl = np.interp(tt, tt[::441], lvl).astype(np.float32)
    # külək: soyuqda güclü, od böyüdükcə azalır
    w = S.bp(noise(N, 1), 180, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * .23 * tt)) * (1 - .85 * lvl) * .10
    fx.add(0, w.astype(np.float32))
    # od gurultusu + çırtıltı
    rumble = S.lp(noise(N, 2), 160) * lvl * .55
    fx.add(0, rumble.astype(np.float32))
    r = np.random.default_rng(5)
    t = IGNITE
    while t < DUR - .3:
        L = fire_level(t)
        t += r.exponential(1 / (3 + 30 * L))
        d = int(.012 * S.SR)
        pop = S.hp(r.standard_normal(d), 1800) * np.exp(-np.arange(d) / (d / 4))
        fx.add(t, (pop * (.08 + .22 * L) * r.uniform(.4, 1)).astype(np.float32), pan=r.uniform(-.5, .5))

    def strike(t0, v=1.0):
        d = int(.09 * S.SR)
        scr = S.hp(noise(d, int(t0 * 100)), 2500) * np.exp(-np.arange(d) / (d / 3)) * .5
        fx.add(t0, (scr * v).astype(np.float32))
        fx.add(t0 + .05, S.whoosh(.45, .9 * v))
        ft = S.tarr(1.2)
        flare = S.lp(noise(len(ft), int(t0 * 77)), 600) * np.exp(-ft * 2.5) * .25
        fx.add(t0 + .05, (flare * v).astype(np.float32))
    for s in strikes:
        strike(s)
    for s in rapid:
        strike(s, .6)
    strike(IGNITE, 1.0)
    for x in logs:
        tt2 = S.tarr(.25)
        th = np.sin(2 * np.pi * (70 + 40 * np.exp(-tt2 * 30)) * tt2) * np.exp(-tt2 * 18) * .35
        fx.add(x + .3, th.astype(np.float32), pan=.15)
    # musiqi: soyuq piano → isti progressiya → zərbə → həll
    for i, nm in enumerate(['A4', 'E4', 'C5', 'B4', 'A4', 'E4']):
        mus.add(.3 + i * 1.3, S.piano(S.hz(nm), 2.6, .55))
    mus.add(0, S.pad('Am', 8.9, cut=500, v=.8, att=1.0))
    mus.add(4.4, S.sub('Am', 4.3, v=.4))
    mus.add(7.4, S.heartbeat(.7))
    mus.add(IGNITE, S.shimmer('C', 2.0, .8))
    prog = ['C', 'G', 'Am', 'F'] * 2
    for k, ch in enumerate(prog):
        t0 = 9.7 + k * .69
        if t0 > BOOM - .3:
            break
        mus.add(t0, S.pad(ch, .8, cut=1100 + 120 * k, v=.8, att=.1))
        mus.add(t0, S.strings(ch, .8, v=.6 + .12 * k, att=.25))
        mus.add(t0, S.sub(ch, .6, v=.5))
        for j in range(3):
            mus.add(t0 + j * .23, S.piano(S.hz(S.CHORDS[ch][1][2 + j]) * 2, 1.0, .4))
        if k >= 3:
            mus.add(t0, S.kick(.4 + .06 * k))
    fx.add(BOOM - 1.45, S.riser(1.4, 1.0))
    fx.add(BOOM, S.boom(1.0))
    fx.add(BOOM, S.taiko(.9))
    mus.add(BOOM, S.shimmer('C', 3.0, 1.3))
    for k, ch in enumerate(['C', 'F', 'Am', 'G', 'C']):
        t0 = BOOM + k * 1.65
        mus.add(t0, S.strings(ch, 1.9, v=1.2, att=.3))
        mus.add(t0, S.pad(ch, 1.9, cut=1500, v=.8, att=.1, rel=.6))
        mus.add(t0, S.sub(ch, 1.5, v=.55))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6', 'G5', 'E5']):
        mus.add(END + .3 + i * .42, S.piano(S.hz(nm), 2.2, .45))
    m = S.apply_reverb(mus.x, S.reverb_ir(2.8), .28)
    f = S.apply_reverb(fx.x, S.reverb_ir(1.2, 6000, 5), .12)
    out = (m * .55 + f * .9)[:N]
    fade = int(1.2 * S.SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out = out / (np.max(np.abs(out)) + 1e-9) * .9
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm10_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
