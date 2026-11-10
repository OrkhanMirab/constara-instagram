"""Kinetik qrafik Reels (1080x1920, 30 fps, ~14 s, sessiz AAC treki). Personaj ve diktor yoxdur.

Mezmun:
{
  "hook": ["You're not lazy.", "You're untracked."],   // 1-3 qisa setir
  "beats": ["Day 1: +1", "Day 9: slip, -5", "Day 30: new high"],  // 3 eded
  "end": "Your life as a stock chart.",
  "accent": "orange",
  "dip": true,                 // qrafikde bir dusus (-5) olsun
  "caption": "..."
}
Sonda hemise: Comment "LINK" and I'll send you the app.
ffmpeg: PATH-dan ve ya imageio-ffmpeg paketinden.
"""
import sys
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
from common import BG, TX, MU, CARD, LINE, RD, GR, GO, font, fit, accent, score_series

W, H, FPS = 1080, 1920, 30
T_HOOK, T_BEAT, T_END = 2.6, 2.4, 4.0
CTA = 'Comment "LINK" and I\'ll send you the app.'


def ffmpeg_bin():
    p = shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def mix(c1, c2, a):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))


def render(c, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    A = accent(c.get("accent", "orange"))
    beats = c["beats"][:3]
    dips = (13,) if c.get("dip", True) else ()
    sc = score_series(30, dips)
    lo, hi = min(sc), max(sc)
    x0, x1, yb, yt = 90, 930, 1500, 1060
    P = [(x0 + (x1 - x0) * k / 30, yb - (yb - yt) * (sc[k] - lo) / (hi - lo)) for k in range(31)]
    t_beats = T_HOOK
    t_end = T_HOOK + T_BEAT * len(beats)
    dur = t_end + T_END
    n = int(dur * FPS)

    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hook_f, hook_l = fit(probe, "\n".join(c["hook"]), "Bold", 112, 880, 6, 60)
    beat_txt = [fit(probe, b, "Bold", 80, 880, 3, 48) for b in beats]
    end_f, end_l = fit(probe, c.get("end", "Your life as a stock chart."), "Bold", 92, 880, 3, 56)
    cta_f, cta_l = fit(probe, CTA, "Bold", 44, 860, 2, 30)

    def chart(d, upto, alpha):
        """upto: 0..30 gun. alpha: gorunme."""
        for gy in (yb, (yb + yt) / 2, yt):
            d.line([(x0, gy), (x1, gy)], fill=mix(BG, LINE, alpha), width=2)
        k_full = int(upto)
        for k in range(min(k_full, 30)):
            col = RD if (k + 1) in dips else GR
            d.line([P[k], P[k + 1]], fill=mix(BG, col, alpha), width=9)
            d.ellipse([P[k + 1][0] - 4, P[k + 1][1] - 4, P[k + 1][0] + 4, P[k + 1][1] + 4], fill=mix(BG, col, alpha))
        if k_full < 30:
            fr = upto - k_full
            a, b = P[k_full], P[k_full + 1]
            e = (a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr)
            col = RD if (k_full + 1) in dips else GR
            d.line([a, e], fill=mix(BG, col, alpha), width=9)
            hx, hy = e
        else:
            hx, hy = P[30]
        d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=mix(BG, GO if upto >= 30 else TX, alpha))
        val = sc[min(30, int(round(upto)))]
        d.text((x1, yt - 90), f"{val:+d}", font=font("Bold", 64), fill=mix(BG, GO if upto >= 30 else TX, alpha), anchor="ra")

    ff = subprocess.Popen([ffmpeg_bin(), "-y", "-loglevel", "error",
                           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                           "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                           "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
                           "-color_primaries", "bt709", "-color_trc", "bt709",
                           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out / "video.mp4")],
                          stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.text((90, 250), "constara", font=font("Bold", 36), fill=MU)
        if t < t_beats:  # 1. hook
            y = 560
            for j, ln in enumerate(hook_l):
                a = ease((t - 0.12 * j) / 0.45)
                col = A if j == len(hook_l) - 1 else TX
                d.text((90, y + 40 * (1 - a)), ln, font=hook_f, fill=mix(BG, col, a))
                y += hook_f.size * 1.12
            chart(d, 0, 0.5 * ease(t / 1.0))
        elif t < t_end:  # 2. beats + qrafik cizilir
            bi = int((t - t_beats) // T_BEAT)
            lt = (t - t_beats) - bi * T_BEAT
            a = ease(lt / 0.35)
            d.text((90, 420 + 30 * (1 - a)), f"{bi + 1}", font=font("Bold", 150), fill=mix(BG, A, a))
            bf, bl = beat_txt[bi]
            y = 620
            for ln in bl:
                d.text((90, y + 30 * (1 - a)), ln, font=bf, fill=mix(BG, TX, a))
                y += bf.size * 1.15
            for k in range(len(beats)):  # ilerleme noqteleri
                d.ellipse([90 + k * 36, 380, 106 + k * 36, 396], fill=A if k <= bi else LINE)
            prog = (t - t_beats) / (t_end - t_beats)
            chart(d, 30 * ease(prog * 1.02), 1.0)
        else:  # 3. son kadr
            lt = t - t_end
            a = ease(lt / 0.4)
            y = 470
            for ln in end_l:
                d.text((90, y + 30 * (1 - a)), ln, font=end_f, fill=mix(BG, TX, a))
                y += end_f.size * 1.12
            chart(d, 30, 1.0)
            b = ease((lt - 0.5) / 0.4)
            d.rounded_rectangle([90, 1580, 990, 1580 + 60 + cta_f.size * 1.2 * len(cta_l)], radius=36,
                                fill=mix(BG, CARD, b), outline=mix(BG, A, b), width=3)
            yy = 1610
            for ln in cta_l:
                d.text((540, yy), ln, font=cta_f, fill=mix(BG, TX, b), anchor="ma")
                yy += cta_f.size * 1.2
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg ugursuz")
    return ["video.mp4"]


if __name__ == "__main__":
    render(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
