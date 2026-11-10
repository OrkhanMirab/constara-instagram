"""Brend: rengler, srift, metn sarima. Pillow-dan basqa asililiq yoxdur."""
from pathlib import Path
from PIL import ImageFont

FONTS = Path(__file__).resolve().parent / "fonts"
BG = (10, 14, 20); TX = (214, 222, 232); MU = (147, 161, 178); CARD = (19, 25, 34)
LINE = (40, 48, 60); BAR = (44, 52, 64)
AC = (255, 107, 53); GR = (38, 214, 127); RD = (255, 77, 90); GO = (247, 192, 74); BL = (90, 170, 255)
ACCENTS = {"green": GR, "orange": AC, "gold": GO, "blue": BL, "red": RD}

_cache = {}


def font(weight, size):
    key = (weight, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(str(FONTS / f"InterDisplay-{weight}.otf"), int(size))
    return _cache[key]


def accent(name):
    return ACCENTS.get(name or "green", GR)


def wrap(d, text, fnt, maxw):
    out = []
    for para in str(text).split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=fnt) <= maxw:
                line = t
            else:
                if line:
                    out.append(line)
                line = w
        out.append(line)
    return out


def clean(text):
    """Inter-de emoji yoxdur (kvadrat cixir): 0x2600-den yuxari simvollari at (→ − saxlanilir)."""
    return "".join(ch for ch in str(text) if ord(ch) < 0x2600 or ch in "→←↑↓").replace("  ", " ").strip()


def fit(d, text, weight, size, maxw, max_lines, min_size=28):
    """Metni maxw-ye ve max_lines-a sigana qeder kicildir. (font, setirler) qaytarir."""
    text = clean(text)
    while True:
        f = font(weight, size)
        lines = wrap(d, text, f, maxw)
        widest = max((d.textlength(l, font=f) for l in lines), default=0)
        if (len(lines) <= max_lines and widest <= maxw) or size <= min_size:
            return f, lines
        size -= 4


def score_series(n, dips=()):
    """Birja qrafiki: her gun +1, dip gunlerinde -5 (Constara xal qaydasi)."""
    sc = [0]
    for k in range(1, n + 1):
        sc.append(sc[-1] + (-5 if k in dips else 1))
    return sc
