"""Kino formatı — səs: prosedural kinematik musiqi + SFX + diktor emalı + miks (numpy/scipy, xarici fayl YOX).

Hamısı bizim kodumuzdur → müəllif hüququ / ContentID riski yoxdur.
Quruluş (araşdırma, kino-arastirma.md §3):
  ağrı hissəsi  — minor (Am–F), piano ostinatosu, ürək döyüntüsü, qaranlıq pad
  dönüş-dən əvvəl — riser (1,4 s) → 0,35 s TAM SÜKUT (gözlənti pozulması) → BOOM
  ümid hissəsi  — major-a keçid (C–G–Am–F), taiko/kick, strings crescendo
  qrafik zirvəsi — ikinci zərbə + parıltı, sonda C major (həll)
Musiqi diktorun altında avtomatik endirilir (ducking).
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
rng = np.random.default_rng(7)

NOTE = {n: i for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}


def hz(name):  # 'A3' -> Hz
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + 12 * (o + 1) - 69) / 12)


CHORDS = {  # akkord: (bas, [səslər])
    'Am': ('A1', ['A2', 'E3', 'A3', 'C4', 'E4']),
    'F': ('F1', ['F2', 'C3', 'A3', 'C4', 'F4']),
    'C': ('C2', ['C3', 'G3', 'C4', 'E4', 'G4']),
    'G': ('G1', ['G2', 'D3', 'B3', 'D4', 'G4']),
    'Dm': ('D2', ['D3', 'A3', 'D4', 'F4', 'A4']),
    'Em': ('E2', ['E3', 'B3', 'E4', 'G4', 'B4']),
}


def lp(x, f, o=2):
    return sosfilt(butter(o, min(f, SR / 2 - 100) / (SR / 2), 'low', output='sos'), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f / (SR / 2), 'high', output='sos'), x, axis=0)


def bp(x, f0, f1):
    return sosfilt(butter(2, [f0 / (SR / 2), min(f1, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x, axis=0)


def tarr(d):
    return np.arange(int(d * SR)) / SR


class Bus:
    """Stereo bufer; add(t, mono|stereo, pan)."""

    def __init__(self, dur):
        self.x = np.zeros((int(dur * SR) + SR * 4, 2), np.float32)

    def add(self, t, s, pan=0.0, g=1.0):
        a = int(max(0, t) * SR)
        if s.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            s = np.stack([s * l * 1.414, s * r * 1.414], 1)
        n = min(len(s), len(self.x) - a)
        if n > 0:
            self.x[a:a + n] += s[:n] * g


def reverb_ir(d=2.6, damp=5200, seed=3):
    r = np.random.default_rng(seed)
    t = tarr(d)
    ir = r.standard_normal((len(t), 2)) * np.exp(-t / (d / 6.5))[:, None]
    ir = lp(ir, damp)
    ir[:int(.012 * SR)] *= np.linspace(0, 1, int(.012 * SR))[:, None]
    return (ir / np.sqrt((ir ** 2).sum(0))).astype(np.float32)


def apply_reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x + y * wet


# ---------- alətlər ----------
def piano(f, d=2.2, v=1.0):
    t = tarr(d)
    s = np.zeros_like(t)
    for n in range(1, 9):
        fn = n * f * np.sqrt(1 + 0.0004 * n * n)
        if fn > 12000:
            break
        s += np.sin(2 * np.pi * fn * t + rng.random() * 6) * (1 / n ** 1.25) * np.exp(-t * (1.4 + n * 0.9))
    s += lp(rng.standard_normal(len(t)) * np.exp(-t * 90), 2500) * .15  # çəkic
    a = int(.004 * SR)
    s[:a] *= np.linspace(0, 1, a)
    return (s * v * .32).astype(np.float32)


def saw_voices(f, t, n=5, cents=9, vib=0.0):
    s = np.zeros_like(t)
    for k in range(n):
        dt = (k - (n - 1) / 2) / max(1, (n - 1) / 2) * cents
        ff = f * 2 ** (dt / 1200) * (1 + vib * np.sin(2 * np.pi * 5.1 * t + k))
        ph = np.cumsum(ff) / SR + rng.random()
        s += 2 * (ph % 1) - 1
    return s / n


def pad(chord, d, cut=900, v=1.0, att=.5, rel=.8):
    t = tarr(d)
    s = sum(saw_voices(hz(nm), t, 3, 7) for nm in CHORDS[chord][1][:4])
    s = lp(s, cut, 2)
    env = np.minimum(1, t / att) * np.minimum(1, (d - t) / rel).clip(0, 1)
    return (s * env * v * .09).astype(np.float32)


def strings(chord, d, v=1.0, att=1.2, bright=2600):
    t = tarr(d)
    s = sum(saw_voices(hz(nm) * 2, t, 7, 11, vib=.0025) for nm in CHORDS[chord][1][1:])
    s = lp(hp(s, 180), bright, 2)
    env = (np.minimum(1, t / att) ** 2) * np.minimum(1, (d - t) / .6).clip(0, 1)
    return (s * env * v * .05).astype(np.float32)


def sub(chord, d, v=1.0):
    t = tarr(d)
    f = hz(CHORDS[chord][0])
    s = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / .08) * np.minimum(1, (d - t) / .3).clip(0, 1)
    return (np.tanh(s * 1.4) * env * v * .16).astype(np.float32)


def kick(v=1.0):
    t = tarr(.6)
    f = 48 + 110 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    s += lp(rng.standard_normal(len(t)) * np.exp(-t * 200), 3000) * .3
    return (np.tanh(s * 1.6) * v * .55).astype(np.float32)


def taiko(v=1.0, f0=95):
    t = tarr(1.1)
    f = f0 * (.72 + .28 * np.exp(-t * 18))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
    s += bp(rng.standard_normal(len(t)), 120, 900) * np.exp(-t * 22) * .6
    return (np.tanh(s * 1.3) * v * .5).astype(np.float32)


def heartbeat(v=1.0):
    def thump(d):
        t = tarr(d)
        return np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 25)) / SR) * np.exp(-t * 14)
    a, b = thump(.35), thump(.35) * .7
    s = np.zeros(int(.7 * SR))
    s[:len(a)] += a
    o = int(.24 * SR)
    s[o:o + len(b)] += b
    return (lp(s, 300) * v * .7).astype(np.float32)


def boom(v=1.0):
    t = tarr(4.0)
    f = 30 + 55 * np.exp(-t * 4)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1)
    s += lp(rng.standard_normal(len(t)), 700) * np.exp(-t * 7) * .8
    s += hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 40) * .35  # çatlama
    return (np.tanh(s * 1.8) * v * .62).astype(np.float32)


def riser(d=1.4, v=1.0):
    t = tarr(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    seg = 8
    for k in range(seg):  # pilləli bandpass yuxarı sürüşmə (hamar keçid)
        f = 300 * (20 ** ((k + .5) / seg))
        w = np.clip(1 - np.abs(t / d * seg - k - .5), 0, 1)
        out += bp(n, f * .7, f * 1.4) * w
    gl = np.sin(2 * np.pi * np.cumsum(180 * (5 ** (t / d))) / SR) * .25
    env = (t / d) ** 2.2
    return ((out * .6 + gl) * env * v * .32).astype(np.float32)


def rev_swell(d=1.2, v=1.0):
    t = tarr(d)
    s = hp(rng.standard_normal(len(t)), 4000) * (t / d) ** 3
    return (s * v * .22).astype(np.float32)


def whoosh(d=.38, v=1.0):
    t = tarr(d)
    n = rng.standard_normal(len(t))
    s = bp(n, 400, 2200) * np.sin(np.pi * t / d) ** 2 + bp(n, 2200, 7000) * np.sin(np.pi * t / d) ** 6 * .5
    return (s * v * .22).astype(np.float32)


def tick(v=1.0):
    t = tarr(.08)
    return (np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * v * .12).astype(np.float32)


def shimmer(chord, d=2.5, v=1.0):
    t = tarr(d)
    s = sum(np.sin(2 * np.pi * hz(nm) * 4 * t + i) * np.exp(-t * (1.2 + i * .3)) for i, nm in enumerate(CHORDS[chord][1][2:]))
    a = int(.01 * SR)
    s[:a] *= np.linspace(0, 1, a)
    return (s * v * .05).astype(np.float32)


# ---------- partitura ----------
def score(lines, C, D, dur, turn, peak=None, bpm=92, accents=(), ticks=(), slip=None):
    """lines: [{scene}], C/D: diktor başlanğıc/müddət, turn: dönüş xəttinin indeksi, peak: zirvə anı (s).
    Qaytarır: (music stereo, sfx stereo, events) — events vizual tərəf üçün (zərbə anları)."""
    mus, sfx, wet = Bus(dur), Bus(dur), Bus(dur)
    ev = []
    nL = len(lines)
    tT = C[turn] if turn is not None else None
    pre = ['Am', 'F', 'Am', 'Dm', 'Am', 'F']
    post = ['C', 'G', 'Am', 'F', 'C', 'G']
    # akkord bölmələri: hər diktor xətti öz akkordu
    bounds = [0.0] + [C[i] for i in range(1, nL)] + [dur + 1.5]
    pi_, qi = 0, 0
    for i in range(nL):
        a, b = bounds[i], bounds[i + 1]
        after = tT is not None and a >= tT - .01
        if after:
            ch = post[qi % len(post)] if i < nL - 1 else 'C'
            qi += 1
        else:
            ch = pre[pi_ % len(pre)]
            pi_ += 1
        d = b - a + .6
        sc = lines[i].get('scene', '')
        if tT is not None and not after and i == turn - 1:
            d = max(.2, tT - .35 - a)  # dönüşdən 0,35 s əvvəl HƏR ŞEY susur
            mus.add(a, pad(ch, d, 700, 1.0, .05, .05))
            mus.add(a, sub(ch, d, .9))
        elif not after:
            mus.add(a, pad(ch, d, 650 + 120 * i, 1.0, .05 if i == 0 else .25, .6))
            mus.add(a, sub(ch, d, 1.0))
        else:
            prog = (a - tT) / max(.1, dur - tT)
            mus.add(a, pad(ch, d, 1400 + 1600 * prog, 1.1, .2, .6))
            mus.add(a, sub(ch, d, 1.15))
            wet.add(a, strings(ch, d, .7 + .8 * prog, 1.0 if qi > 1 else .25))
        # piano: ağrı hissəsində 8-lik ostinato, sonra yarım notlar
        notes = CHORDS[ch][1][2:]
        step = 60 / bpm / 2 if not after else 60 / bpm
        k, t = 0, a
        end = (tT - .35) if (tT is not None and not after and i == turn - 1) else b
        while t < end - .05:
            nm = notes[[0, 1, 2, 1][k % 4]]
            f = hz(nm) * (2 if after else 1)
            wet.add(t, piano(f, 1.8, .55 if not after else .45), pan=(-.3 if k % 2 else .3))
            k += 1
            t += step
        if sc in ('night', 'count', 'pain') and not after:
            for hb in np.arange(a + .15, min(b, end) - .3, 60 / 64):
                sfx.add(hb, heartbeat(.75))
    # açılış zərbəsi (0-cı kadr — fade-in YOX)
    sfx.add(0, kick(1.0))
    wet.add(0, taiko(.8, 80))
    wet.add(0.02, shimmer('Am', 2.0, .8))
    ev.append(('hit', 0.0))
    # dönüş: riser → sükut → boom
    if tT is not None:
        r = 1.4
        sfx.add(tT - .35 - r, riser(r, 1.0))
        sfx.add(tT - .005, boom(1.0))
        wet.add(tT, taiko(1.0, 70))
        wet.add(tT, shimmer('C', 3.0, 1.0))
        ev.append(('boom', tT))
        # zərb alətləri: dönüşdən sonra, crescendo
        beat = 60 / bpm
        stop = (peak + 2.4 * beat) if peak else dur - 1.2
        for k8 in range(int((stop - tT - beat * 2) / (beat / 2))):  # 8-lik tor
            t = tT + beat * 2 + k8 * beat / 2
            prog = (t - tT) / max(.1, stop - tT)
            if k8 % 8 == 0:
                sfx.add(t, kick(.7 + .3 * prog))
            if k8 % 8 == 4:
                wet.add(t, taiko(.45 + .45 * prog, 105), pan=-.2)
            if prog > .4 and k8 % 4 == 2:
                wet.add(t, taiko(.22 + .3 * prog, 140), pan=.35)
            if prog > .72 and k8 % 2 == 1:
                wet.add(t, taiko(.15 + .25 * prog, 175), pan=-.35)
    if peak:
        sfx.add(peak - 1.2, rev_swell(1.2, 1.0))
        sfx.add(peak, boom(.75))
        wet.add(peak, taiko(.9, 85))
        wet.add(peak, shimmer('C', 3.0, 1.2))
        ev.append(('peak', peak))
    # aksent sözləri: alt zərbə + içəri sovrulma
    for ta in accents:
        if tT is not None and abs(ta - tT) < .3:
            continue
        sfx.add(ta - .3, whoosh(.32, .7))
        sfx.add(ta, kick(.55))
        ev.append(('acc', ta))
    for tk in ticks:
        sfx.add(tk, tick(1.0))
    if slip is not None:  # −5: aşağı enən «çöküş»
        t_ = tarr(.7)
        dr = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(320 * np.exp(-t_ * 4.5) + 40) / SR)) * np.exp(-t_ * 4)
        sfx.add(slip, (lp(dr, 1800) * .28).astype(np.float32))
        sfx.add(slip, boom(.45))
        ev.append(('slip', slip))
    # səhnə keçidlərində whoosh
    for i in range(1, nL):
        if tT is not None and i == turn:
            continue
        sfx.add(C[i] - .22, whoosh(.38, .9), pan=(.4 if i % 2 else -.4))
        ev.append(('cut', C[i]))
    ir = reverb_ir()
    m = mus.x + apply_reverb(wet.x, ir, .55)
    m = apply_reverb(m, ir, .12)
    s = apply_reverb(sfx.x, ir, .18)
    # dinamika: ağrı hissəsi intim (sakit), dönüşdən sonra zirvəyə qədər crescendo, sonra yumşaq enmə
    tt = np.arange(len(m)) / SR
    g = np.full(len(m), .78)
    if tT is not None:
        pk = peak or dur - 1
        g = np.where(tt >= tT, .95 + .6 * np.clip((tt - tT) / max(.1, pk - tT), 0, 1) ** 1.5, g)
        g = np.where(tt > pk, 1.55 - .35 * np.clip((tt - pk) / 2.5, 0, 1), g)
        # TAM SÜKUT (gözlənti pozulması): dönüşdən 0,35 s əvvəl, 40 ms kəsik
        a0, a1 = tT - .35, tT - .015
        q = np.clip(np.minimum((tt - a0) / .04, (a1 - tt) / .01), 0, 1)
        g = g * (1 - q)
        s = s * (1 - q)[:, None] + 0
        # boom/riser-in özü sükutdan sonra gəlsin: riser sükutdan ƏVVƏL bitir, boom tT-.02-də başlayır
    m = m * g[:, None]
    return m, s, ev


# ---------- diktor + miks ----------
def biquad_peak(x, f, gdb, q=1.0):
    A = 10 ** (gdb / 40)
    w = 2 * np.pi * f / SR
    al = np.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
    from scipy.signal import lfilter
    return lfilter(b / a[0], a / a[0], x)


def env_follow(x, att=.01, rel=.25):
    e = np.abs(x)
    out = np.zeros_like(e)
    ka, kr = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    v = 0.0
    # sürətli: blok RMS + interpolyasiya
    blk = 256
    n = len(e) // blk + 1
    r = np.sqrt(np.array([np.mean(e[i * blk:(i + 1) * blk] ** 2) if i * blk < len(e) else 0 for i in range(n)]))
    sm = np.zeros(n)
    ka, kr = np.exp(-blk / (att * SR)), np.exp(-blk / (rel * SR))
    for i in range(n):
        k = ka if r[i] > v else kr
        v = k * v + (1 - k) * r[i]
        sm[i] = v
    return np.interp(np.arange(len(e)), np.arange(n) * blk, sm)


def voice_chain(v):
    """Diktor: HP 75 Hz, isti bas (+2,5 dB 140 Hz), aydınlıq (+2 dB 3,2 kHz), kompressor, kiçik otaq."""
    v = hp(v, 75)
    v = biquad_peak(v, 140, 2.5, .8)
    v = biquad_peak(v, 3200, 2.0, .9)
    e = env_follow(v, .005, .12)
    thr = np.percentile(e[e > 1e-4], 70) if np.any(e > 1e-4) else 1
    g = np.where(e > thr, (thr / np.maximum(e, 1e-9)) ** (1 - 1 / 3), 1.0)
    v = v * g
    v = v / (np.max(np.abs(v)) + 1e-9) * .9
    st = np.stack([v, v], 1).astype(np.float32)
    return apply_reverb(st, reverb_ir(1.1, 4000, 11), .07)


def mix(vo, music, fx, duck_db=9.0):
    n = max(len(vo), len(music), len(fx))
    P = lambda x: np.pad(x, ((0, n - len(x)), (0, 0)))
    vo, music, fx = P(vo), P(music), P(fx)
    e = env_follow(vo[:, 0], .02, .35)
    e = e / (np.max(e) + 1e-9)
    duck = 10 ** (-duck_db * np.clip(e * 3, 0, 1) / 20)
    m = music * duck[:, None] * .55 + fx * (.5 + .5 * duck[:, None]) * .8 + vo * 1.0
    m = np.tanh(m * 1.1) / np.tanh(1.1)
    return (m / (np.max(np.abs(m)) + 1e-9) * .93).astype(np.float32)
