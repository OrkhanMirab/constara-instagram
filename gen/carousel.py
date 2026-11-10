"""Karusel (1080x1350 JPEG) mezmun JSON-undan.

Mezmun:
{
  "kind": "list" | "myth" | "steps",      // slayd etiketi: "#1" / MYTH-FACT / "Step 1"
  "accent": "green" | "orange" | "gold" | "blue",
  "cover": ["5 signs", "you're more disciplined", "than you think."],  // 1-ci setir reng, iri
  "hook": "Count how many fit you →",
  "items": [{"h": "Basliq", "b": "Izah"}, ...],   // 3-6 eded
  "chart": {"title": "...", "body": "...", "dip": true, "label": "NEW HIGH"},  // istege bagli
  "cta": {"title": ["How many", "fit you?"], "list": ["qisa", ...], "note": "..."},
  "caption": "..."
}
"""
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw
from common import BG, TX, MU, CARD, LINE, BAR, RD, GR, GO, font, fit, accent, score_series

W, H, S = 1080, 1350, 2
X0, MAXW = 90, 900
accent_now = GR


def _slide(n, total):
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    d.S = S
    for i in range(total):
        x = (W / 2 - (total - 1) * 14 + i * 28) * S
        d.ellipse([x - 6 * S, 1264 * S, x + 6 * S, 1276 * S], fill=accent_now if i == n - 1 else LINE)
    d.text((X0 * S, 1252 * S), "constara", font=font("Bold", 28 * S), fill=TX)
    d.text((990 * S, 1252 * S), f"{n}/{total}", font=font("Medium", 26 * S), fill=MU, anchor="ra")
    return im, d


def _text(d, x, y, text, weight, size, color, max_lines, gap=1.18, maxw=MAXW, min_size=28):
    f, lines = fit(d, text, weight, size * S, maxw * S, max_lines, min_size * S)
    step = f.size * gap
    for ln in lines:
        d.text((x * S, y * S), ln, font=f, fill=color)
        y += step / S
    return y


def _save(im, path):
    im.resize((W, H), Image.LANCZOS).save(path, quality=90)


def render(c, out: Path):
    global accent_now
    out.mkdir(parents=True, exist_ok=True)
    A = accent_now = accent(c.get("accent"))
    items = c["items"]
    total = 1 + len(items) + (1 if c.get("chart") else 0) + 1
    if not 2 <= total <= 10:
        raise ValueError(f"karusel slayd sayi {total}")
    files = []

    def save(im, n):
        p = out / f"{n}.jpg"
        _save(im, p)
        files.append(p.name)

    # 1. qapaq
    im, d = _slide(1, total)
    cov = c["cover"]
    y = _text(d, X0, 140, cov[0], "Bold", 130, A, 1)
    y += 10
    y = _text(d, X0, y, " ".join(cov[1:]), "Bold", 100, TX, 4, gap=1.12)
    y = max(y + 60, 640)
    rows = min(len(items), int((1120 - y) // 84))
    for k in range(rows):
        d.rounded_rectangle([X0 * S, y * S, 990 * S, (y + 66) * S], radius=16 * S, fill=CARD)
        d.ellipse([112 * S, (y + 15) * S, 148 * S, (y + 51) * S], outline=A, width=4 * S)
        d.line([(121 * S, (y + 33) * S), (128 * S, (y + 41) * S), (141 * S, (y + 25) * S)], fill=A, width=5 * S)
        bw = [520, 430, 600, 380, 480, 550][k % 6]
        d.rounded_rectangle([175 * S, (y + 26) * S, (175 + bw) * S, (y + 40) * S], radius=7 * S, fill=BAR)
        y += 84
    _text(d, X0, 1150, c.get("hook", "Swipe →"), "Medium", 36, MU, 1)
    save(im, 1)

    # 2. maddeler
    kind = c.get("kind", "list")
    for i, it in enumerate(items):
        n = i + 2
        im, d = _slide(n, total)
        if kind == "myth":
            d.rounded_rectangle([X0 * S, 140 * S, 290 * S, 210 * S], radius=35 * S, fill=(60, 22, 28))
            d.text((190 * S, 175 * S), "MYTH", font=font("Bold", 34 * S), fill=RD, anchor="mm")
            y = _text(d, X0, 250, it["h"], "Bold", 72, TX, 4)
            y += 40
            d.rounded_rectangle([X0 * S, y * S, 290 * S, (y + 70) * S], radius=35 * S, fill=(14, 52, 36))
            d.text((190 * S, (y + 35) * S), "FACT", font=font("Bold", 34 * S), fill=GR, anchor="mm")
            _text(d, X0, y + 110, it["b"], "Medium", 46, MU, 6, gap=1.38)
        else:
            label = f"Step {i + 1}" if kind == "steps" else f"#{i + 1}"
            d.text((X0 * S, 140 * S), label, font=font("Bold", 120 * S), fill=A)
            y = _text(d, X0, 330, it["h"], "Bold", 84, TX, 4)
            y += 50
            _text(d, X0, y, it["b"], "Medium", 46, MU, 5, gap=1.38)
        frac = (i + 1) / len(items)
        d.rounded_rectangle([X0 * S, 1080 * S, 990 * S, 1150 * S], radius=35 * S, fill=CARD)
        d.rounded_rectangle([X0 * S, 1080 * S, (X0 + max(70, 900 * frac)) * S, 1150 * S], radius=35 * S, fill=A)
        d.text((540 * S, 1115 * S), f"{i + 1} of {len(items)}", font=font("Bold", 34 * S),
               fill=BG if 90 + 900 * frac > 620 else TX, anchor="mm")
        save(im, n)

    n = len(items) + 2
    # 3. qrafik (istege bagli)
    ch = c.get("chart")
    if ch:
        im, d = _slide(n, total)
        y = _text(d, X0, 150, ch["title"], "Bold", 84, TX, 2)
        _text(d, X0, y + 30, ch.get("body", ""), "Medium", 46, MU, 3, gap=1.38)
        dips = (13,) if ch.get("dip", True) else ()
        sc = score_series(30, dips)
        lo, hi = min(sc), max(sc)
        x0, x1, y0, y1 = 90, 990, 1150, 700
        P = [((x0 + (x1 - x0) * k / 30) * S, (y0 - (y0 - y1) * (sc[k] - lo) / (hi - lo)) * S) for k in range(31)]
        for k in range(30):
            d.line([P[k], P[k + 1]], fill=RD if (k + 1) in dips else GR, width=7 * S)
        nx, ny = P[-1]
        d.ellipse([nx - 15 * S, ny - 15 * S, nx + 15 * S, ny + 15 * S], fill=GO)
        d.text((nx - 10 * S, ny - 60 * S), ch.get("label", "NEW HIGH"), font=font("Bold", 34 * S), fill=GO, anchor="ra")
        save(im, n)
        n += 1

    # 4. CTA (saxlanilasi checklist)
    cta = c["cta"]
    im, d = _slide(n, total)
    t = cta["title"]
    _text(d, X0, 170, t[0], "Bold", 110, TX, 1)
    _text(d, X0, 295, t[1] if len(t) > 1 else "", "Bold", 110, A, 1)
    lst = cta.get("list") or [it["h"] for it in items]
    rh = 104 if len(lst) <= 5 else 88
    for j, txt in enumerate(lst[:6]):
        y = 480 + j * rh
        d.rounded_rectangle([X0 * S, y * S, 990 * S, (y + rh - 20) * S], radius=18 * S, fill=CARD)
        d.text((130 * S, (y + (rh - 20) / 2) * S), str(j + 1), font=font("Bold", 44 * S), fill=A, anchor="lm")
        f, lines = fit(d, txt, "Bold", 40 * S, 760 * S, 1, 26 * S)
        d.text((195 * S, (y + (rh - 20) / 2) * S), lines[0], font=f, fill=TX, anchor="lm")
    _text(d, X0, 1040, cta.get("note", ""), "Medium", 36, MU, 3, gap=1.3)
    save(im, n)
    return files


if __name__ == "__main__":
    render(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
