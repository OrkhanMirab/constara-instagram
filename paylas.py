"""Constara Instagram + Facebook avtomatik paylasma.

queue/<ad>/post.json olan postlardan VAXTI CATMIS birini paylasir,
sonra qovlugu posted/<ad>/ (ugurlu) ve ya failed/<ad>/ (xeta) qovluguna kocurur.
GitHub Actions bunu saatda bir defe ve queue/ deyisende isledir.

Env: IG_ACCESS_TOKEN, IG_USER_ID, FB_PAGE_TOKEN, FB_PAGE_ID (GitHub Secrets), GITHUB_REPOSITORY, GITHUB_SHA.
Yalniz Python standart kitabxanasi.

post.json:
{
  "type": "image" | "carousel" | "reels" | "story",
  "caption": "Post metni #hashtag",
  "media": ["1.jpg", "2.jpg"],          // reels ucun: ["video.mp4"]
  "publish_after": "2026-11-09T18:00:00+03:00",   // istege bagli; yoxdursa derhal
  "share_to_feed": true,                // istege bagli, yalniz reels
  "platforms": ["instagram", "facebook"] // istege bagli; susmaya gore ikisi de
}
Gundelik plan (plan/YYYY-MM-DD.json + schedule.json, bax plan.py) de burda paylasilir:
media runner-de gen/ ile hazirlanir, sekiller 'media' budagina (tek commit, force) qoyulur,
main-e yalniz posted/<id>/post.json + result.json yazilir (repo boyumesin).
Her platform ayrica paylasilir: biri ugursuz olsa, o biri yene paylasilir.
En azi biri ugurludursa post posted/-a, hamisi ugursuzdursa failed/-e gedir.
"""
import json
import os
import shutil
import subprocess
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
FB_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")
FB_PAGE = os.environ.get("FB_PAGE_ID", "")
PLATFORMS = ("instagram", "facebook")
REPO = os.environ.get("GITHUB_REPOSITORY", "OrkhanMirab/constara-instagram")
def _head_sha():
    # Dovre run-u yeni commit-leri pull edir, GITHUB_SHA ise kohne qalir -> raw URL-de cari HEAD lazimdir
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parent,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA", "main")


SHA = _head_sha()
MAX_PER_24H = int(os.environ.get("MAX_PER_24H", "45"))  # spam kimi gorunmesin
UA = {"User-Agent": "constara-instagram/1.0"}


class PostError(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def api(method, path, _token=None, **params):
    params["access_token"] = _token or TOKEN
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


URL_OVERRIDE = {}  # runner-de hazirlanan sekiller: Path -> media budagindaki raw URL


def raw_url(path: Path):
    if path in URL_OVERRIDE:
        return URL_OVERRIDE[path]
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


def upload_video(cid_resp, path: Path, token=None):
    """Resumable upload: fayl birbasa runner-den Meta-ya gedir (public URL lazim deyil)."""
    uri = cid_resp.get("uri") or cid_resp.get("upload_url")
    if not uri:
        raise PostError("resumable upload uri qaytarilmadi")
    data = path.read_bytes()
    req = urllib.request.Request(uri, data=data, method="POST", headers={
        **UA,
        "Authorization": f"OAuth {token or TOKEN}",
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


def validate(d: Path, post: dict):
    """Platformadan asili olmayan yoxlama. (type, caption, media) qaytarir."""
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
    elif typ == "carousel":
        if not 2 <= len(media) <= 10:
            raise PostError("carousel: 2-10 fayl lazimdir")
        for m in media:
            if m.suffix.lower() not in (".jpg", ".jpeg"):
                raise PostError(f"carousel: yalniz JPEG ({m.name})")
    elif typ == "reels":
        if len(media) != 1 or media[0].suffix.lower() not in (".mp4", ".mov"):
            raise PostError("reels: tam 1 MP4/MOV lazimdir")
    elif typ == "story":
        if len(media) != 1 or media[0].suffix.lower() not in (".jpg", ".jpeg"):
            raise PostError("story: tam 1 JPEG lazimdir")
    else:
        raise PostError(f"namelum type: {typ!r}")
    return typ, caption, media


def build_container(d: Path, post: dict) -> str:
    typ, caption, media = validate(d, post)

    if typ == "image":
        cid = api("POST", f"{IG}/media", image_url=raw_url(media[0]), caption=caption)["id"]
        wait_ready(cid, 120)
        return cid

    if typ == "story":
        cid = api("POST", f"{IG}/media", media_type="STORIES", image_url=raw_url(media[0]))["id"]
        wait_ready(cid, 120)
        return cid

    if typ == "carousel":
        children = []
        for m in media:
            c = api("POST", f"{IG}/media", image_url=raw_url(m), is_carousel_item="true")["id"]
            children.append(c)
        for c in children:
            wait_ready(c, 120)
        cid = api("POST", f"{IG}/media", media_type="CAROUSEL",
                  children=",".join(children), caption=caption)["id"]
        wait_ready(cid, 120)
        return cid

    if typ == "reels":
        params = dict(media_type="REELS", upload_type="resumable", caption=caption,
                      share_to_feed="true" if post.get("share_to_feed", True) else "false")
        resp = api("POST", f"{IG}/media", **params)
        upload_video(resp, media[0])
        wait_ready(resp["id"], 900)
        return resp["id"]


def publish_instagram(d: Path, post: dict) -> dict:
    if not TOKEN or not IG:
        raise PostError("IG_ACCESS_TOKEN / IG_USER_ID yoxdur (GitHub Secrets)")
    cid = build_container(d, post)
    mid = api("POST", f"{IG}/media_publish", creation_id=cid)["id"]
    link = api("GET", mid, fields="permalink").get("permalink") or (
        "https://www.instagram.com/stories/constara.app/" if post.get("type") == "story" else None)
    return {"media_id": mid, "permalink": link}


def fb(method, path, **params):
    return api(method, path, _token=FB_TOKEN, **params)


def fb_link(obj_id):
    link = fb("GET", obj_id, fields="permalink_url").get("permalink_url") or ""
    if link.startswith("/"):
        link = "https://www.facebook.com" + link
    return link


def publish_facebook(d: Path, post: dict) -> dict:
    if not FB_TOKEN or not FB_PAGE:
        raise PostError("FB_PAGE_TOKEN / FB_PAGE_ID yoxdur (GitHub Secrets)")
    typ, caption, media = validate(d, post)

    if typ == "image":
        r = fb("POST", f"{FB_PAGE}/photos", url=raw_url(media[0]), message=caption)
        pid = r.get("post_id") or r["id"]
        return {"post_id": pid, "permalink": fb_link(pid)}

    if typ == "story":
        ph = fb("POST", f"{FB_PAGE}/photos", url=raw_url(media[0]), published="false")["id"]
        r = fb("POST", f"{FB_PAGE}/photo_stories", photo_id=ph)
        return {"post_id": r.get("post_id") or ph, "permalink": f"https://www.facebook.com/{FB_PAGE}"}

    if typ == "carousel":
        params = {"message": caption}
        for i, m in enumerate(media):
            ph = fb("POST", f"{FB_PAGE}/photos", url=raw_url(m), published="false")["id"]
            params[f"attached_media[{i}]"] = json.dumps({"media_fbid": ph})
        pid = fb("POST", f"{FB_PAGE}/feed", **params)["id"]
        return {"post_id": pid, "permalink": fb_link(pid)}

    # reels
    start = fb("POST", f"{FB_PAGE}/video_reels", upload_phase="start")
    vid = start["video_id"]
    upload_video(start, media[0], token=FB_TOKEN)
    fin = fb("POST", f"{FB_PAGE}/video_reels", upload_phase="finish", video_id=vid,
             video_state="PUBLISHED", description=caption)
    if not fin.get("success", True):
        raise PostError(f"facebook reels finish ugursuz: {fin}")
    t0 = time.time()
    while time.time() - t0 < 900:
        st = fb("GET", vid, fields="status").get("status", {})
        vs = st.get("video_status")
        print(f"   fb {vid}: {vs}")
        if vs == "error" or (st.get("processing_phase") or {}).get("status") == "error":
            raise PostError(f"facebook reels emal xetasi: {st}")
        if vs in ("ready", "published") or (st.get("publishing_phase") or {}).get("status") == "complete":
            break
        time.sleep(10)
    else:
        raise PostError("facebook reels 900s erzinde hazir olmadi")
    return {"video_id": vid, "permalink": fb_link(vid)}


PUBLISHERS = {"instagram": publish_instagram, "facebook": publish_facebook}


def due(post: dict) -> bool:
    pa = post.get("publish_after")
    if not pa:
        return True
    return datetime.fromisoformat(pa) <= now()


def posted_last_24h() -> int:
    n = 0
    for r in POSTED.glob("*/result.json"):
        try:
            res = json.loads(r.read_text())
            if "facebook" in res and "instagram" not in res:
                continue  # yalniz FB-ye geden post Instagram limitine sayilmir
            t = datetime.fromisoformat(res["posted_at"])
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


def publish_post(d: Path, post: dict):
    """Butun platformalara paylasir. (result, ok_sayi, platformalar) qaytarir."""
    platforms = post.get("platforms") or list(PLATFORMS)
    print(f"▶ {d.name} ({post.get('type')}) -> {', '.join(platforms)}")
    result, ok = {}, 0
    for p in platforms:
        try:
            if p not in PUBLISHERS:
                raise PostError(f"namelum platform: {p!r}")
            result[p] = PUBLISHERS[p](d, post)
            ok += 1
            print(f"✅ {p}: {result[p].get('permalink')}")
        except PostError as e:
            result[p] = {"error": str(e)}
            print(f"❌ {p}: {e}")
        except Exception as e:  # bir platformanin gozlenilmez xetasi o birini dayandirmasin
            result[p] = {"error": f"{type(e).__name__}: {e}"}
            print(f"❌ {p}: {type(e).__name__}: {e}")
    return result, ok, platforms


def git(*args, inp=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=inp, capture_output=True, text=True, check=True).stdout.strip()


def push_media(item_id: str, files):
    """Sekilleri 'media' budagina tek (valideynsiz) commit kimi force-push edir, raw URL-leri yazir.
    Tarixce yigilmir: her defe yalniz cari postun sekilleri qalir."""
    entries = []
    for f in files:
        blob = git("hash-object", "-w", str(f))
        entries.append(f"100644 blob {blob}\t{f.name}")
    sub = git("mktree", inp="\n".join(entries) + "\n")
    tree = git("mktree", inp=f"040000 tree {sub}\t{item_id}\n")
    sha = git("-c", "user.name=constara-bot", "-c", "user.email=bot@users.noreply.github.com",
              "commit-tree", tree, "-m", f"media {item_id}")
    git("push", "-f", "origin", f"{sha}:refs/heads/media")
    for f in files:
        URL_OVERRIDE[f] = f"https://raw.githubusercontent.com/{REPO}/{sha}/{item_id}/{urllib.parse.quote(f.name)}"


def render_item(typ, content, out: Path):
    sys.path.insert(0, str(ROOT / "gen"))
    import carousel, reel, story  # noqa: E402  (Pillow yalniz plan isleyende lazimdir)
    return {"carousel": carousel, "reels": reel, "story": story}[typ].render(content, out)


def run_plan(budget: int) -> int:
    """Vaxti catmis plan elementlerini paylasir. Paylasilan sayini qaytarir."""
    import plan as planmod
    sch = planmod.load_schedule()
    pf = ROOT / "plan" / f"{planmod.today(sch).isoformat()}.json"
    if not pf.exists():
        print(f"Plan yoxdur: {pf.relative_to(ROOT)}")
        return 0
    late = timedelta(minutes=sch.get("max_late_min", 120))
    done = 0
    for item_id, typ, slot, content in planmod.items_for(pf, sch):
        if (POSTED / item_id).exists() or (FAILED / item_id).exists():
            continue
        if slot > now():
            continue
        if now() - slot > late:
            d = FAILED / item_id
            d.mkdir(parents=True, exist_ok=True)
            (d / "result.json").write_text(json.dumps({"skipped": f"vaxt kecdi (slot {slot.isoformat()})",
                                                      "failed_at": now().isoformat()}) + "\n")
            print(f"⏭ {item_id}: slot {slot:%H:%M} cox kecib, atlandi")
            continue
        if done >= budget:
            print(f"⏸ {item_id}: bu run-da limit ({budget}), novbeti run-da")
            break
        if posted_last_24h() >= MAX_PER_24H:
            print(f"⏸ Son 24 saatda {MAX_PER_24H} post, {item_id} gozleyir")
            break
        build = ROOT / "_build" / item_id
        post = {"type": typ, "caption": content.get("caption", ""), "slot": slot.isoformat(),
                "platforms": content.get("platforms") or list(PLATFORMS), "content": content}
        try:
            names = render_item(typ, content, build)
            post["media"] = names
            if typ != "reels":
                push_media(item_id, [build / n for n in names])
            result, ok, platforms = publish_post(build, post)
        except Exception as e:
            result, ok, platforms = {"error": f"hazirlama: {type(e).__name__}: {e}"}, 0, []
            print(f"❌ {item_id}: {result['error']}")
        dest = POSTED / item_id if ok else FAILED / item_id
        dest.mkdir(parents=True, exist_ok=True)
        post.pop("media", None)
        (dest / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n")
        result["posted_at" if ok else "failed_at"] = now().isoformat()
        (dest / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        shutil.rmtree(build, ignore_errors=True)
        done += 1
        print(f"-> {dest.relative_to(ROOT)}")
    return done


def main():
    if (ROOT / "PAUSE").exists():  # token/Meta problemi zamani: hec ne paylasma, hec ne atlama
        print("⏸ PAUSE fayli var, paylasma dayandirilib:", (ROOT / "PAUSE").read_text().strip())
        return 0
    sch_budget = 3
    try:
        sch_budget = json.loads((ROOT / "schedule.json").read_text()).get("max_per_run", 3)
    except Exception:
        pass
    plan_done = run_plan(sch_budget)
    if plan_done:
        return 0
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
    if posted_last_24h() >= MAX_PER_24H:
        print(f"⏸ Son 24 saatda {MAX_PER_24H} post paylasilib, novbeti defe.")
        return 0

    d, post = ready[0]  # her isde yalniz 1 post (teb'i interval)
    result, ok, platforms = publish_post(d, post)
    if ok:
        result["posted_at"] = now().isoformat()
        t = move(d, POSTED, result)
    else:
        result["failed_at"] = now().isoformat()
        t = move(d, FAILED, result)
    print(f"-> {t.relative_to(ROOT)}")
    return 0 if ok == len(platforms) else 1


if __name__ == "__main__":
    sys.exit(main())
