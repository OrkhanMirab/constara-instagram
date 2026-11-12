"""Kino formatı (K01, 2026-11-12) — kinematik motivasiya Reels: cfg.json → <out>/index.html (+ mix.wav, tl.json).

İşlət:  python3 video-src/_kino/kino.py <cfg.json> <out-qovluq> [--tts <kokoro qovluğu>]
Render: Constara `marketing/render.mjs`-i <scratch>/vid/ altına köçür, <scratch>/vid/<ad>/index.html → NODE_PATH=$(npm root -g) node render.mjs <ad>
Yoxla:  node video-src/_kino/snap.mjs <out>/index.html <png-qovluq>  (açar kadrlar)

cfg (bax nümunələr video-src/_kino/ornek-*.json):
{
  "tag": "DISCIPLINE",                 // 0-cı kadrda niş adı (yuxarı, pill)
  "lines": [                            // 7–9 diktor xətti, hər biri bir səhnə
    {"scene": "hook",  "vo": "Nobody is coming to save you.", "txt": "Nobody is coming to *save* you."},
    {"scene": "night", "vo": "...", "clock": "02:13"},
    {"scene": "count", "vo": "...", "num": [0, 365], "unit": "DAYS"},
    {"scene": "turn",  "vo": "But here's the truth.", "txt": "*Truth.*"},
    {"scene": "rise",  "vo": "..."},
    {"scene": "chart", "vo": "..."},
    {"scene": "cta",   "vo": "Comment link, and I'll send you the app.", "txt": "Comment *LINK* — I'll send you the app."}
  ],
  "voice": "am_michael", "speed": 0.95, "caption": "..."
}
Mətn işarələri (txt): *söz* = aksent (narıncı, iri, zərbə), _söz_ = serif kursiv (emosiya), ~söz~ = yaşıl (yaxşı nəticə), !söz! = qırmızı.
Səhnələr: hook (AÇIQ, isti işıq) · night (gecə, telefon işığı, yağış) · count (sayğac) · pain (qırmızı tutqun, siluet) ·
turn (sükut → zərbə, qara) · rise (şəfəq, siluet təpədə) · chart (Constara qrafiki: qalxış, −5 çöküş, NEW HIGH) · cta (LINK).
"""
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import sound  # noqa: E402

HERE = Path(__file__).resolve().parent
RIG_DIRS = [Path('/home/user/Constara/marketing/sablon'), Path('/home/user/life-analytics/marketing/sablon')]


def syl(w):
    w = w.lower()
    if re.search(r'\d', w):
        return max(1, len(re.sub(r'\D', '', w))) + 1
    w = re.sub(r'[^a-z]', '', w)
    if not w:
        return .5
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and n > 1 and not w.endswith('le'):
        n -= 1
    return max(1, n)


def gaps_in(clip, sr):
    """Klip içində ≥ 90 ms sükut aralıqları: [(başlanğıc, son)] saniyə."""
    fr = int(.01 * sr)
    n = len(clip) // fr
    r = np.sqrt(np.array([np.mean(clip[i * fr:(i + 1) * fr] ** 2) for i in range(n)]))
    thr = .06 * r.max()
    q = r < thr
    out, i = [], 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]:
                j += 1
            if i > 5 and j < n - 5 and (j - i) >= 9:
                out.append((i * .01, j * .01))
            i = j
        else:
            i += 1
    return out


def word_times(vo, clip, sr):
    """Diktor sözlərinin təxmini vaxtı (klip daxilində): heca nisbəti + daxili fasilələr."""
    words = vo.split()
    d = len(clip) / sr
    brk = [i for i, w in enumerate(words[:-1]) if re.search(r'[,.;:?!—]$', w)]
    G = gaps_in(clip, sr)
    segs = []  # (söz indeksləri, t0, t1)
    if brk and len(G) >= len(brk):
        G = sorted(sorted(G, key=lambda g: g[0] - g[1])[:len(brk)])
        a, t0 = 0, 0.0
        for bi, g in zip(brk, G):
            segs.append((list(range(a, bi + 1)), t0, g[0]))
            a, t0 = bi + 1, g[1]
        segs.append((list(range(a, len(words))), t0, d))
    else:
        segs.append((list(range(len(words))), 0.0, d))
    T = [None] * len(words)
    for idx, a, b in segs:
        wt = [syl(words[i]) + .35 for i in idx]
        tot = sum(wt)
        t = a
        for i, w in zip(idx, wt):
            T[i] = (round(t, 3), round(t + (b - a) * w / tot, 3))
            t += (b - a) * w / tot
    return words, T


def parse_txt(txt):
    """*..* aksent · _.._ serif · ~..~ yaşıl · !..! qırmızı (bir neçə sözü əhatə edə bilər)."""
    M = (('*', 'acc'), ('_', 'ser'), ('~', 'grn'), ('!', 'red'))
    out, cur = [], None
    for raw in txt.split():
        w, st = raw, cur
        for mk, name in M:
            if cur is None and w.lstrip('"\'(').startswith(mk):
                cur = st = name
                i = w.index(mk)
                w = w[:i] + w[i + 1:]
            if cur == name and mk in w:
                w = w.replace(mk, '')
                cur = None
        out.append({'w': w, 'st': st})
    return out


def map_words(scr, vo_words, vo_T):
    """Ekran sözlərini diktor vaxtına bağla (heca payı ilə)."""
    cs = np.cumsum([0] + [syl(w) + .35 for w in vo_words])
    cs = cs / cs[-1]
    tp = [vo_T[0][0]] + [t[1] for t in vo_T]
    ss = np.cumsum([0] + [syl(w['w']) + .35 for w in scr])
    ss = ss / ss[-1]
    for i, w in enumerate(scr):
        w['t0'] = round(float(np.interp(ss[i], cs, tp)), 3)
        w['t1'] = round(float(np.interp(ss[i + 1], cs, tp)), 3)
    return scr


def chunks(scr, mx=3):
    """1–3 sözlük qruplar; aksent sözləri öz qrupunda (zərbə anı), stil aralığı (≤ mx söz) bölünmür, durğu işarəsində qırılır."""
    ch, cur = [], []
    for i, w in enumerate(scr):
        acc = w['st'] == 'acc'
        prev = scr[cur[-1]]['st'] if cur else None
        span = 1
        if w['st'] and w['st'] != prev:  # stil aralığının başlanğıcı: uzunluğu
            while i + span < len(scr) and scr[i + span]['st'] == w['st']:
                span += 1
        span_end = prev and not w['st'] and not re.search(r'[,.;:?!\u2014]$', w['w'])
        if cur and (len(cur) >= mx or acc != (prev == 'acc') or (span > 1 and len(cur) + span > mx) or span_end):
            ch.append(cur)
            cur = []
        cur.append(i)
        if re.search(r'[,.;:?!\u2014]$', w['w']):
            ch.append(cur)
            cur = []
    if cur:
        ch.append(cur)
    return ch


def tts(lines, tdir, voice, speed):
    from kokoro_onnx import Kokoro
    k = Kokoro(str(tdir / 'kokoro-v1.0.onnx'), str(tdir / 'voices-v1.0.bin'))
    clips = []
    for ln in lines:
        s, sr = k.create(ln['vo'], voice=ln.get('voice', voice), speed=ln.get('speed', speed), lang='en-us')
        i = np.where(np.abs(s) > .01)[0]
        clips.append(s[max(0, i[0] - 200):i[-1] + 600].astype(np.float32))
    return clips, sr


def main():
    cfg_p, out = Path(sys.argv[1]), Path(sys.argv[2])
    tdir = Path(sys.argv[sys.argv.index('--tts') + 1]) if '--tts' in sys.argv else Path.cwd()
    cfg = json.loads(cfg_p.read_text(encoding='utf-8'))
    out.mkdir(parents=True, exist_ok=True)
    L = cfg['lines']
    clips, sr = tts(L, tdir, cfg.get('voice', 'am_michael'), cfg.get('speed', .95))
    turn = next((i for i, l in enumerate(L) if l['scene'] == 'turn'), None)
    # vaxt çizgisi: diktor 0,08 s-də başlayır (ilk 3 s-də nitq — Emplifi), dönüşdən əvvəl sükut
    t, C, D = .08, [], []
    for i, c in enumerate(clips):
        if turn is not None and i == turn:
            t += .45
        C.append(round(t, 3))
        D.append(round(len(c) / sr, 3))
        gap = L[i].get('gap', .32 if L[i]['scene'] != 'hook' else .22)
        t += len(c) / sr + gap
    dur = round(t + cfg.get('tail', 1.4), 2)
    chart = next((i for i in range(len(L) - 1, -1, -1) if L[i]['scene'] == 'chart'), None)
    peak = round(C[chart] + D[chart] * .82, 3) if chart is not None else None
    # diktor buferi (44,1 kHz)
    vo = np.zeros(int((dur + 1) * sound.SR), np.float32)
    TL = []
    for i, (ln, c) in enumerate(zip(L, clips)):
        words, T = word_times(ln['vo'], c, sr)
        scr = map_words(parse_txt(ln.get('txt', ln['vo'])), words, T)
        for w in scr:
            w['t0'] = round(C[i] + w['t0'], 3)
            w['t1'] = round(C[i] + w['t1'], 3)
        rs = np.interp(np.arange(0, len(c) / sr, 1 / sound.SR), np.arange(len(c)) / sr, c).astype(np.float32)
        a = int(C[i] * sound.SR)
        vo[a:a + len(rs)] += rs
        item = {k: v for k, v in ln.items() if k not in ('vo', 'txt')}
        item.update({'C': C[i], 'D': D[i], 'words': scr, 'chunks': chunks(scr, ln.get('mx', 4 if ln['scene'] == 'hook' else 3))})
        TL.append(item)
    voS = sound.voice_chain(vo)
    acc = [w['t0'] for it in TL for w in it['words'] if w['st'] == 'acc']
    slip = next((w['t0'] for it in TL if it['scene'] == 'chart' for w in it['words'] if re.search(r'−5|-5|minus|slip', w['w'], re.I)), None)
    ticks = []
    for it in TL:
        if it['scene'] == 'count':
            a, b = it.get('num', [0, 7])
            n = abs(b - a)
            step = max(1, n // 24)
            for kk in range(step, n + 1, step):  # vizual: oc(P(t, C+.1, .75 D))
                ticks.append(it['C'] + .1 + it['D'] * .75 * (1 - (1 - kk / n) ** (1 / 3)))
    music, fx, ev = sound.score(L, C, D, dur, turn, peak, cfg.get('bpm', 92), acc, ticks, slip)
    m = sound.mix(voS, music, fx, cfg.get('duck', 9))
    m = m[:int(dur * sound.SR)]
    sf.write(out / 'mix_raw.wav', m, sound.SR)
    # səs-küy normallaşdırma: -14 LUFS, TP -1 dB (IG/TikTok normu)
    # xətti normallaşdırma (dinamikanı sıxmır): ölç → həcm → limiter
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(out / 'mix_raw.wav'), '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(out / 'mix_raw.wav'), '-af',
                    'volume=%.2fdB,alimiter=limit=0.86:attack=3:release=60:level=disabled' % (-14 - I),
                    '-ar', '44100', '-ac', '2', str(out / 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(out / 'mix.wav'), '-b:a', '160k', str(out / 'mix.mp3')], check=True)
    tl = {'dur': dur, 'tag': cfg.get('tag', ''), 'lines': TL, 'turn': turn, 'peak': peak, 'ev': ev,
          'brand': cfg.get('brand', 'CONSTARA'), 'cta': cfg.get('cta', 'LINK')}
    (out / 'tl.json').write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding='utf-8')
    rig = next(p for p in RIG_DIRS if (p / 'rig.js').exists())
    html = (HERE / 'body.html').read_text(encoding='utf-8')
    html = (html.replace('__TL__', json.dumps(tl, ensure_ascii=False))
            .replace('__AUDIO__', base64.b64encode((out / 'mix.mp3').read_bytes()).decode())
            .replace('__RIG__', (rig / 'rig.js').read_text(encoding='utf-8'))
            .replace('__POSE__', (rig / 'poses.json').read_text(encoding='utf-8'))
            .replace('__TITLE__', cfg.get('title', cfg.get('tag', 'kino'))))
    (out / 'index.html').write_text(html, encoding='utf-8')
    print(json.dumps({'dur': dur, 'C': C, 'D': D, 'turn': turn, 'peak': peak}))


if __name__ == '__main__':
    main()
