"""Story (1080x1920 JPEG). API ile sticker/link qoymaq olmur, ona gore sade sual/fikir kartidir.

Mezmun: {"kicker": "QUICK CHECK", "title": "...", "body": "...", "cta": "Reply with 1-5 👇", "accent": "orange"}
Ust/alt 250px tetbiqin interfeysi ucun bos saxlanilir.
"""
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw
from common import BG, TX, MU, CARD, RD, GR, GO, font, fit, accent, score_series

W, H, S = 1080, 1920, 2


def render(c, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    A = accent(c.get("accent", "orange"))
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    d.text((90 * S, 300 * S), c.get("kicker", "").upper(), font=font("Bold", 38 * S), fill=A)
    f, lines = fit(d, c["title"], "Bold", 104 * S, 900 * S, 5, 56 * S)
    y = 380
    for ln in lines:
        d.text((90 * S, y * S), ln, font=f, fill=TX)
        y += f.size * 1.12 / S
    y += 40
    fb, bl = fit(d, c.get("body", ""), "Medium", 50 * S, 900 * S, 5, 34 * S)
    for ln in bl:
        d.text((90 * S, y * S), ln, font=fb, fill=MU)
        y += fb.size * 1.38 / S
    # birja qrafiki
    dips = (9,) if c.get("dip", True) else ()
    sc = score_series(24, dips)
    lo, hi = min(sc), max(sc)
    x0, x1, yb, yt = 90, 990, 1540, max(y + 80, 1180)
    P = [((x0 + (x1 - x0) * k / 24) * S, (yb - (yb - yt) * (sc[k] - lo) / (hi - lo)) * S) for k in range(25)]
    for k in range(24):
        d.line([P[k], P[k + 1]], fill=RD if (k + 1) in dips else GR, width=8 * S)
    nx, ny = P[-1]
    d.ellipse([nx - 16 * S, ny - 16 * S, nx + 16 * S, ny + 16 * S], fill=GO)
    d.rounded_rectangle([90 * S, 1590 * S, 990 * S, 1680 * S], radius=45 * S, fill=CARD)
    fc, cl = fit(d, c.get("cta", "Link in bio"), "Bold", 40 * S, 820 * S, 1, 26 * S)
    d.text((540 * S, 1635 * S), cl[0], font=fc, fill=TX, anchor="mm")
    p = out / "story.jpg"
    im.resize((W, H), Image.LANCZOS).save(p, quality=90)
    return [p.name]


if __name__ == "__main__":
    render(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
