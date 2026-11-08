"""sil/*.txt fayllarindaki media ID-lerini Instagram-dan silir.

Her setirde bir media_id (posted/<ad>/result.json-dan). Bos setir ve # serh kecilir.
Netice sil-netice/<vaxt>.json-a yazilir, emr fayli silinir. Ugurlu silinmede
posted/<ad>/result.json-a "deleted_at" elave olunur.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = os.environ.get("IG_API_HOST", "graph.facebook.com")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
UA = {"User-Agent": "constara-instagram/1.0"}


def delete(mid):
    url = f"https://{HOST}/{mid}?{urllib.parse.urlencode({'access_token': TOKEN})}"
    req = urllib.request.Request(url, method="DELETE", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return True, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode()).get("error", {})
            return False, f"{e.code}: {err.get('message')} (code {err.get('code')}, sub {err.get('error_subcode')})"
        except Exception:
            return False, f"HTTP {e.code}"


def mark_posted(mid, ts):
    for r in (ROOT / "posted").glob("*/result.json"):
        d = json.loads(r.read_text())
        if str(d.get("media_id")) == mid:
            d["deleted_at"] = ts
            r.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
            return r.parent.name
    return None


def main():
    files = sorted((ROOT / "sil").glob("*.txt"))
    if not files:
        print("Silinecek emr yoxdur.")
        return 0
    if not TOKEN:
        print("❌ IG_ACCESS_TOKEN yoxdur.")
        return 1
    ts = datetime.now(timezone.utc).isoformat()
    results, bad = [], 0
    for f in files:
        for line in f.read_text().splitlines():
            mid = line.split("#")[0].strip()
            if not mid:
                continue
            ok, res = delete(mid)
            folder = mark_posted(mid, ts) if ok else None
            print(("✅ silindi " if ok else "❌ silinmedi ") + f"{mid} {folder or ''} {res if not ok else ''}")
            results.append({"media_id": mid, "ok": ok, "response": res, "posted_folder": folder})
            bad += not ok
        f.unlink()
    out = ROOT / "sil-netice"
    out.mkdir(exist_ok=True)
    (out / f"{ts[:19].replace(':', '-')}.json").write_text(
        json.dumps({"at": ts, "results": results}, ensure_ascii=False, indent=2) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
