"""M01 «Bank» — Metafor formatının ilk nümunəsi (2026-11-12).

Üslub: tam qara fon, ağ fiqur + döşəmədə əks, bir qızılı aksent, adı yazılmış əşyalar, sayğac, sonda partlayış.
Hekayə: hər yaxşı gün = +1 sikkə bankaya; bir pis gecə = −5 (banka çatlayır); çoxu burada dayanır;
amma balans 15-dir, sıfır yox → davam → sikkə qalaqları həyat qrafikinə çevrilir → Constara + LINK.

İşlətmə:  python3 m01_bank.py <scratch_dir>
  → <scratch>/index.html (səhnə), <scratch>/audio.wav, sonra render.mjs + ffmpeg (aşağıda run()).
Diktor yoxdur: ekranda qısa monospace yazı + öz musiqimiz (../_kino/sound.py funksiyaları).
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS = 30
DUR = 19.5

# ---------------- zaman xətti ----------------
def accel(n, t0, t1, k=1.6):
    """n sikkə t0..t1 arası, sürətlənən (intervallar kiçilir)."""
    u = np.linspace(0, 1, n)
    return list(t0 + (t1 - t0) * u ** (1 / k))

drops1 = [round(x, 3) for x in accel(20, 1.5, 6.9)]       # gün 1–20 (+1)
RELAPSE = 7.45                                               # gün 21 (−5)
leaks = [RELAPSE + 0.18 + i * 0.13 for i in range(5)]
SLUMP = (8.3, 10.25)
drops2 = [round(x, 3) for x in accel(26, 10.55, 13.75)]    # gün 22–47 (+1) → 41
CHART = (14.05, 15.45)                                       # qrafik çəkilir, sonda BOOM
END = 16.35

TEXTS = [  # (başla, bit, mətn, vurğu sözü, vurğu rəngi)
    (0.15, 1.45, "YOUR LIFE HAS A BALANCE.", "BALANCE", "gold"),
    (1.55, 7.25, "EVERY GOOD DAY:  +1", "+1", "gold"),
    (7.35, 8.30, "ONE BAD NIGHT:  −5", "−5", "red"),
    (8.40, 9.30, "MOST PEOPLE QUIT HERE.", "QUIT", "red"),
    (9.35, 10.45, "BUT YOU'RE AT 15. NOT ZERO.", "15.", "gold"),
    (10.55, 13.85, "SO KEEP DEPOSITING.", "DEPOSITING.", "gold"),
    (14.05, 16.20, "THIS IS YOUR LIFE CHART.", "LIFE CHART.", "gold"),
]

# qrafik datası (kumulyativ xal)
series = [0]
for _ in drops1:
    series.append(series[-1] + 1)
series.append(series[-1] - 5)
for _ in drops2:
    series.append(series[-1] + 1)

TL = dict(fps=FPS, dur=DUR, drops1=drops1, relapse=RELAPSE, leaks=leaks, slump=SLUMP,
          drops2=drops2, chart=CHART, end=END, texts=TEXTS, series=series)


# ---------------- səs ----------------
def coin_ting(f, v=1.0):
    t = S.tarr(0.9)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + .5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 14)
         + .25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 22))
    a = int(.002 * S.SR)
    s[:a] *= np.linspace(0, 1, a)
    return (s * v * .10).astype(np.float32)


def audio(path):
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    # 1) qaranlıq-isti giriş: Am–F–Am, piano arpecio
    prog1 = [('Am', 0.0), ('F', 2.6), ('C', 5.2)]
    for ch, t0 in prog1:
        d = 2.6 if ch != 'C' else RELAPSE - 5.2
        mus.add(t0, S.pad(ch, d + .4, cut=800, v=.8, att=.6))
        mus.add(t0, S.sub(ch, d, v=.55))
        notes = S.CHORDS[ch][1]
        for i in range(int(d / .325)):
            nm = notes[[2, 3, 4, 3][i % 4]]
            mus.add(t0 + i * .325, S.piano(S.hz(nm) * (2 if i % 8 == 6 else 1), 1.6, v=.55 if i % 4 else .75), pan=.25 * ((i % 3) - 1))
    # sikkələr: pentatonik pilləkən yuxarı
    penta = ['C5', 'D5', 'E5', 'G5', 'A5', 'C6']
    for i, t in enumerate(drops1):
        fx.add(t + .26, coin_ting(S.hz(penta[i % 6]) * (1.0 if i < 12 else 1.0), .8 + .02 * i), pan=-.1)
    # 2) relapse: zərbə + aşağı düşən sikkələr + qaranlıq pad + ürək döyüntüsü
    fx.add(RELAPSE, S.boom(.55))
    fx.add(RELAPSE, S.whoosh(.3, 1.0))
    for i, t in enumerate(leaks):
        fx.add(t + .15, coin_ting(S.hz(['A4', 'G4', 'E4', 'D4', 'C4'][i]), .7), pan=.4)
    mus.add(RELAPSE, S.pad('Dm', 3.0, cut=420, v=.9, att=.3, rel=.6))
    mus.add(RELAPSE, S.sub('Dm', 2.9, v=.5))
    for t in (8.45, 9.3):
        fx.add(t, S.heartbeat(.9))
    fx.add(9.45, S.rev_swell(1.0, 1.0))
    # 3) dönüş: major, piano + strings + yüngül kick
    prog2 = [('C', 10.4), ('G', 11.3), ('Am', 12.2), ('F', 13.1)]
    for ch, t0 in prog2:
        mus.add(t0, S.pad(ch, 1.3, cut=1400, v=.8, att=.15))
        mus.add(t0, S.sub(ch, .9, v=.6))
        mus.add(t0, S.strings(ch, 1.25, v=.9 + .2 * prog2.index((ch, t0)), att=.4))
        notes = S.CHORDS[ch][1]
        for i in range(4):
            mus.add(t0 + i * .225, S.piano(S.hz(notes[2 + i % 3]) * 2, 1.2, v=.5))
        mus.add(t0, S.kick(.6))
        mus.add(t0 + .45, S.kick(.4))
    for i, t in enumerate(drops2):
        fx.add(t + .2, coin_ting(S.hz(penta[(i + 2) % 6]) * 1.0, .55), pan=-.1)
    # 4) qrafik: riser → 0,25 s sükut → BOOM + parıltı, C major həll
    fx.add(CHART[1] - 1.45, S.riser(1.4, 1.0))
    fx.add(CHART[1], S.boom(1.0))
    fx.add(CHART[1], S.taiko(.9))
    mus.add(CHART[1], S.shimmer('C', 3.0, 1.4))
    mus.add(CHART[1], S.strings('C', DUR - CHART[1], v=1.3, att=.3))
    mus.add(CHART[1], S.pad('C', DUR - CHART[1], cut=1600, v=.9, att=.05, rel=2.0))
    mus.add(CHART[1], S.sub('C', 2.5, v=.7))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6', 'G5', 'E5']):
        mus.add(END + .3 + i * .42, S.piano(S.hz(nm), 2.2, .5))
    m = S.apply_reverb(mus.x, S.reverb_ir(2.8), .28)
    f = S.apply_reverb(fx.x, S.reverb_ir(1.6, 6000, 5), .18)
    out = m * .6 + f * .85
    n = int(DUR * S.SR)
    out = out[:n]
    fade = int(1.2 * S.SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out = out / (np.max(np.abs(out)) + 1e-9) * .9
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm01_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    audio(os.path.join(scr, 'audio.wav'))
    print('html + audio hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
