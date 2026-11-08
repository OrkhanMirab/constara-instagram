"""Constara Instagram avtomatik paylasma.

queue/<ad>/post.json olan postlardan VAXTI CATMIS birini paylasir,
sonra qovlugu posted/<ad>/ (ugurlu) ve ya failed/<ad>/ (xeta) qovluguna kocurur.
GitHub Actions bunu saatda bir defe ve queue/ deyisende isledir.

Env: IG_ACCESS_TOKEN, IG_USER_ID (GitHub Secrets), GITHUB_REPOSITORY, GITHUB_SHA.
Yalniz Python standart kitabxanasi.

post.json:
{
  "type": "image" | "carousel" | "reels",
  "caption": "Post metni #hashtag",
  "media": ["1.jpg", "2.jpg"],          // reels ucun: ["video.mp4"]
  "publish_after": "2026-11-09T18:00:00+03:00",   // istege bagli; yoxdursa derhal
  "share_to_feed": true                 // istege bagli, yalniz reels
}
"""
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUEUE, POSTED, FAILED = ROOT / "queue", ROOT / "posted", ROOT / "failed"
HOST = os.environ.get("IG_API_HOST", "graph.facebook.com")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG = os.environ.get("IG_USER_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "OrkhanMirab/constara-instagram")
SHA = os.environ.get("GITHUB_SHA", "main")
MAX_PER_24H = int(os.environ.get("MAX_PER_24H", "4"))  # spam kimi gorunmesin
UA = {"User-Agent": "constara-instagram/1.0"}


class PostError(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def api(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params)
    url = f"https://{HOST}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data}", headers=UA)
    else:
        req = urllib.request.Request(url, data=data.encode(), method="POST", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode()).get("error", {})
            msg = f"{e.code}: {err.get('message')} (code {err.get('code')}, sub {err.get('error_subcode')})"
            if err.get("error_user_msg"):
                msg += f" | {err['error_user_msg']}"
        except Exception:
            msg = f"HTTP {e.code}"
        raise PostError(f"{method} {path} -> {msg}") from None


def raw_url(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{REPO}/{SHA}/{urllib.parse.quote(rel)}"


def wait_ready(cid, timeout_s):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        st = api("GET", cid, fields="status_code,status")
        code = st.get("status_code")
        print(f"   {cid}: {code}")
        if code in ("FINISHED", "PUBLISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            raise PostError(f"konteyner {code}: {st.get('status')}")
        time.sleep(5)
    raise PostError(f"konteyner {timeout_s}s erzinde hazir olmadi")


def upload_video(cid_resp, path: Path):
    """Resumable upload: fayl birbasa runner-den Meta-ya gedir (public URL lazim deyil)."""
    uri = cid_resp.get("uri")
    if not uri:
        raise PostError("resumable upload uri qaytarilmadi")
    data = path.read_bytes()
    req = urllib.request.Request(uri, data=data, method="POST", headers={
        **UA,
        "Authorization": f"OAuth {TOKEN}",
        "offset": "0",
        "file_size": str(len(data)),
    })
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            res = json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise PostError(f"video upload -> HTTP {e.code}: {e.read().decode()[:300]}") from None
    if not res.get("success", True):
        raise PostError(f"video upload ugursuz: {res}")
    print(f"   video yuklendi ({len(data) // 1024} KB)")


def build_container(d: Path, post: dict) -> str:
    typ = post.get("type")
    caption = post.get("caption", "")
    media = [d / m for m in post.get("media", [])]
    for m in media:
        if not m.is_file():
            raise PostError(f"fayl yoxdur: {m.name}")
    if len(caption) > 2200:
        raise PostError("caption 2200 simvoldan uzundur")

    if typ == "image":
        if len(media) != 1 or media[0].suffix.lower() not in (".jpg", ".jpeg"):
            raise PostError("image: tam 1 JPEG lazimdir")
        cid = api("POST", f"{IG}/media", image_url=raw_url(media[0]), caption=caption)["id"]
        wait_ready(cid, 120)
        return cid

    if typ == "carousel":
        if not 2 <= len(media) <= 10:
            raise PostError("carousel: 2-10 fayl lazimdir")
        children = []
        for m in media:
            if m.suffix.lower() not in (".jpg", ".jpeg"):
                raise PostError(f"carousel: yalniz JPEG ({m.name})")
            c = api("POST", f"{IG}/media", image_url=raw_url(m), is_carousel_item="true")["id"]
            children.append(c)
        for c in children:
            wait_ready(c, 120)
        cid = api("POST", f"{IG}/media", media_type="CAROUSEL",
                  children=",".join(children), caption=caption)["id"]
        wait_ready(cid, 120)
        return cid

    if typ == "reels":
        if len(media) != 1 or media[0].suffix.lower() not in (".mp4", ".mov"):
            raise PostError("reels: tam 1 MP4/MOV lazimdir")
        params = dict(media_type="REELS", upload_type="resumable", caption=caption,
                      share_to_feed="true" if post.get("share_to_feed", True) else "false")
        resp = api("POST", f"{IG}/media", **params)
        upload_video(resp, media[0])
        wait_ready(resp["id"], 900)
        return resp["id"]

    raise PostError(f"namelum type: {typ!r}")


def due(post: dict) -> bool:
    pa = post.get("publish_after")
    if not pa:
        return True
    return datetime.fromisoformat(pa) <= now()


def posted_last_24h() -> int:
    n = 0
    for r in POSTED.glob("*/result.json"):
        try:
            t = datetime.fromisoformat(json.loads(r.read_text())["posted_at"])
            n += t > now() - timedelta(hours=24)
        except Exception:
            pass
    return n


def move(d: Path, dest_root: Path, info: dict):
    dest_root.mkdir(exist_ok=True)
    target = dest_root / d.name
    if target.exists():
        target = dest_root / f"{d.name}-{int(time.time())}"
    shutil.move(str(d), str(target))
    (target / "result.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return target


def main():
    items = sorted(p.parent for p in QUEUE.glob("*/post.json")) if QUEUE.exists() else []
    ready = []
    for d in items:
        try:
            post = json.loads((d / "post.json").read_text(encoding="utf-8"))
        except Exception as e:
            move(d, FAILED, {"error": f"post.json oxunmadi: {e}", "failed_at": now().isoformat()})
            continue
        if due(post):
            ready.append((d, post))
        else:
            print(f"⏳ {d.name}: {post['publish_after']} gozleyir")
    if not ready:
        print("Paylasilacaq post yoxdur.")
        return 0
    if not TOKEN or not IG:
        print("❌ IG_ACCESS_TOKEN / IG_USER_ID yoxdur (GitHub Secrets).")
        return 1
    if posted_last_24h() >= MAX_PER_24H:
        print(f"⏸ Son 24 saatda {MAX_PER_24H} post paylasilib, novbeti defe.")
        return 0

    d, post = ready[0]  # her isde yalniz 1 post (teb'i interval)
    print(f"▶ {d.name} ({post.get('type')})")
    try:
        cid = build_container(d, post)
        mid = api("POST", f"{IG}/media_publish", creation_id=cid)["id"]
        link = api("GET", mid, fields="permalink").get("permalink")
        t = move(d, POSTED, {"media_id": mid, "permalink": link, "posted_at": now().isoformat()})
        print(f"✅ Paylasildi: {link}  -> {t.relative_to(ROOT)}")
        return 0
    except PostError as e:
        t = move(d, FAILED, {"error": str(e), "failed_at": now().isoformat()})
        print(f"❌ {e}  -> {t.relative_to(ROOT)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
