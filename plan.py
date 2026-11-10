"""Gundelik plan -> saatli paylasma slotlari.

plan/YYYY-MM-DD.json:
{
  "date": "2026-11-10",
  "from": "14:00",              // istege bagli: bu saatdan evvelki slotlar bos qalir
  "reels":     [ {reel mezmunu, "caption": ...}, ... ],      // gen/reel.py
  "carousels": [ {karusel mezmunu, "caption": ...}, ... ],   // gen/carousel.py
  "stories":   [ {story mezmunu}, ... ]                       // gen/story.py
}
Her siyahinin i-ci elementi o novun i-ci slotuna dusur (schedule.json). ID: <tarix>-<nov>-NN.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KINDS = {"reels": "reels", "carousels": "carousel", "stories": "story"}


def load_schedule():
    return json.loads((ROOT / "schedule.json").read_text(encoding="utf-8"))


def _tz(sch):
    sign = -1 if sch["tz"].startswith("-") else 1
    h, m = sch["tz"][1:].split(":")
    return timezone(sign * timedelta(hours=int(h), minutes=int(m)))


def _at(date, hhmm, tz):
    h, m = map(int, hhmm.split(":"))
    return datetime(date.year, date.month, date.day, h, m, tzinfo=tz)


def slots(date, kind, sch):
    tz = _tz(sch)
    cfg = sch[kind]
    if "times" in cfg:
        return [_at(date, t, tz) for t in cfg["times"]]
    t, end, out = _at(date, cfg["start"], tz), _at(date, sch["end"], tz), []
    while t <= end:
        out.append(t)
        t += timedelta(minutes=cfg["every_min"])
    return out


def items_for(plan_file: Path, sch):
    """[(id, typ, slot_datetime, content)] qaytarir."""
    p = json.loads(plan_file.read_text(encoding="utf-8"))
    date = datetime.strptime(p["date"], "%Y-%m-%d").date()
    tz = _tz(sch)
    out = []
    for key, typ in KINDS.items():
        frm = p.get(f"{key}_from") or p.get("from")  # meselen "reels_from": "17:00"
        start = _at(date, frm, tz) if frm else None
        if p.get(f"{key}_times"):  # plana xas saatlar (meselen "reels_times": ["15:25", "17:00"])
            all_slots = [_at(date, t, tz) for t in p[f"{key}_times"]]
        else:
            all_slots = slots(date, key, sch)
        free = [s for s in all_slots if not start or s >= start]
        for i, (content, slot) in enumerate(zip(p.get(key, []), free)):
            # diktorlu Reels (video_branch) ayrica ID: kohne kinetik reels-NN ile toqqusmasin
            pre = "vreel" if content.get("video_branch") else typ
            out.append((f"{p['date']}-{pre}-{i + 1:02d}", typ, slot, content))
    return sorted(out, key=lambda x: x[2])


def today(sch, now=None):
    return (now or datetime.now(timezone.utc)).astimezone(_tz(sch)).date()


if __name__ == "__main__":  # python3 plan.py plan/2026-11-10.json -> cedvel
    import sys
    sch = load_schedule()
    for i, typ, slot, c in items_for(Path(sys.argv[1]), sch):
        print(slot.strftime("%H:%M"), typ.ljust(8), i, "|", (c.get("cover") or c.get("hook") or [c.get("title", "")])[0])
