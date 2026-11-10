"""Gundelik diktorlu Reels (v16 «3 signs» sablonu) -> render -> 'reels/<tarix>' budagi -> plan/<tarix>.json.

Islet (constara-instagram kokunden):
  python3 video-src/_alet/reels.py <tarix> <reels.json> <is-qovlugu> [--from HH:MM]
reels.json: [cfg, ...] (4 eded), cfg:
  {"title": "QUITTING SMOKING", "fs": 46, "row": "No cigarette", "bg": "#2F6FDE",
   "n1": "[['You', c(1, .12)], ['sleep', c(1, .2), 'or'], ['\\n'], ['through', c(1, .3)], ['it.', c(1, .45), 'grn']]",
   "L": [7 diktor cumlesi; 2-ci (№1) GECE ile bagli olsun: sablonun №1 kadri gece/saat/ay-dir;
         3-cu = istek gelir ve kecir; 4-cu = bir defe surusursen, sifirdan baslamirsan; 5,6 = +1/−5 qrafiki],
   "caption": "..."}
Son cumle ve son kadr avtomatik: «Comment LINK, and I'll send you the app.»
Lazimdir: Constara reposu (/home/user/Constara ve ya /home/user/life-analytics), kokoro-onnx + soundfile,
is-qovlugunda kokoro-v1.0.onnx + voices-v1.0.bin, qlobal playwright, ffmpeg.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "video-src" / "v16-quitting-vaping"
ENGINE = next(p for p in (Path("/home/user/Constara"), Path("/home/user/life-analytics")) if (p / "marketing/render.mjs").exists())
CTA_VO = "Comment link, and I'll send you the app."
CTA_CAP = """[c(6), DUR + 1, '', 92, [['Comment', c(6)], ['"LINK"', c(6, .22), 'or'], ['\\n'], ["I'll", c(6, .5)], ['send', c(6, .58)], ['you', c(6, .66)], ['\\n'], ['the', c(6, .74)], ['app.', c(6, .82), 'grn']]]"""
OLD_CAP = """[c(6), DUR + 1, '', 92, [['Which', c(6)], ['sign', c(6, .2)], ['\\n'], ['are', c(6, .4)], ['you', c(6, .5)], ['on?', c(6, .62), 'or']]]"""


def make_src(cfg, d: Path):
    s = (TPL / "body.html").read_text(encoding="utf-8")
    R = [('<span style="font-size:46px">QUITTING VAPING</span>', '<span style="font-size:%dpx">%s</span>' % (cfg.get("fs", 46), cfg["title"])),
         ('<b>No vape</b>', '<b>%s</b>' % cfg["row"]),
         ("""[['You', c(1, .12)], ['sleep', c(1, .2), 'or'], ['\\n'], ['through', c(1, .3)], ['it.', c(1, .45), 'grn']]""", cfg["n1"]),
         ('.title span { display: inline-block; font: 400 52px/1 "Permanent Marker", cursive; color: #FFFDF6; background: #1E9E5B;',
          '.title span { display: inline-block; font: 400 52px/1 "Permanent Marker", cursive; color: #FFFDF6; background: %s;' % cfg.get("bg", "#1E9E5B")),
         (OLD_CAP, CTA_CAP)]
    for a, b in R:
        assert s.count(a) == 1, a[:60]
        s = s.replace(a, b)
    d.mkdir(parents=True, exist_ok=True)
    (d / "body.html").write_text(s, encoding="utf-8")
    L = list(cfg["L"][:6]) + [CTA_VO]
    assert len(L) == 7
    v = (TPL / "vo.py").read_text(encoding="utf-8")
    v = re.sub(r"^L=.*$", lambda m: "L=" + json.dumps(L), v, flags=re.M)
    (d / "vo.py").write_text(v, encoding="utf-8")


def run(cmd, cwd, env=None):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{cmd[:3]} -> {r.stderr[-800:]}")
    return r.stdout


def one(i, cfg, work: Path):
    name = f"r{i + 1:02d}"
    d = work / name
    make_src(cfg, d)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not (d / f).exists():
            os.symlink(work / f, d / f)
    run([sys.executable, "vo.py"], d)
    vid = work / "vid" / name
    vid.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "marketing/sablon/build.py", str(d / "body.html"), str(d / "cues.json"), str(d / "vo.b64"),
         str(vid / "index.html"), cfg["title"]], ENGINE)
    env = dict(os.environ, NODE_PATH=run(["npm", "root", "-g"], work).strip())
    run(["node", "render.mjs", name], work / "vid", env)
    out = work / "out" / f"{name}.mp4"
    out.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid / f"{name}.mp4"), "-c:v", "libx264", "-crf", "24",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], work)
    print(f"✅ {name}: {cfg['title']} ({out.stat().st_size // 1024} KB)", flush=True)
    return out


def git(*a, inp=None):
    return subprocess.run(["git", *a], cwd=ROOT, input=inp, capture_output=True, text=True, check=True).stdout.strip()


def push_branch(branch, files):
    entries = [f"100644 blob {git('hash-object', '-w', str(f))}\t{f.name}" for f in files]
    tree = git("mktree", inp="\n".join(entries) + "\n")
    sha = git("-c", "user.name=constara-bot", "-c", "user.email=bot@users.noreply.github.com", "commit-tree", tree, "-m", branch)
    git("push", "-f", "origin", f"{sha}:refs/heads/{branch}")


def main():
    date, cfgs, work = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), Path(sys.argv[3]).resolve()
    start = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else None
    (work / "vid").mkdir(parents=True, exist_ok=True)
    shutil.copy(ENGINE / "marketing/render.mjs", work / "vid/render.mjs")
    with ThreadPoolExecutor(2) as ex:  # 4 nuve: eyni anda 2 render
        outs = list(ex.map(lambda a: one(a[0], a[1], work), enumerate(cfgs)))
    branch = f"reels/{date}"
    push_branch(branch, outs)
    pf = ROOT / "plan" / f"{date}.json"
    plan = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else {"date": date, "carousels": [], "stories": []}
    plan["reels"] = [{"video_branch": branch, "video": o.name, "title": c["title"], "caption": c["caption"]} for o, c in zip(outs, cfgs)]
    if start:
        plan["reels_from"] = start
    pf.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"-> {branch} ({len(outs)} video), {pf.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
