# constara-instagram

@constara.app Instagram hesabına avtomatik paylaşma. Kod yalnız Python standart kitabxanasını işlədir.

## Necə işləyir
1. Post `queue/<ad>/` qovluğuna qoyulur: `post.json` + media faylları.
2. GitHub Actions (`.github/workflows/paylas.yml`) saatda bir dəfə, həm də `queue/` dəyişəndə `paylas.py`-ı işlədir.
3. Vaxtı çatmış **bir** post paylaşılır, sonra qovluq `posted/<ad>/` (link `result.json`-da) və ya `failed/<ad>/` (xəta `result.json`-da) qovluğuna köçür.
4. Son 24 saatda ən çox 4 post (`MAX_PER_24H`) paylaşılır.

## post.json
```json
{
  "type": "carousel",
  "caption": "Mətn #hashtag",
  "media": ["1.jpg", "2.jpg", "3.jpg"],
  "publish_after": "2026-11-09T18:00:00+03:00"
}
```
| type | media |
|---|---|
| `image` | 1 JPEG (PNG olmaz!) |
| `carousel` | 2–10 JPEG, eyni nisbətdə (1080×1350 tövsiyə olunur) |
| `reels` | 1 MP4 (H.264/AAC, 9:16, 3 san–15 dəq). Birbaşa yüklənir (resumable upload). `share_to_feed` istəyə bağlıdır |

`publish_after` yoxdursa, post dərhal paylaşılır. Qovluq adı: `YYYY-MM-DD-qisa-ad`.

## Secrets (Settings → Secrets and variables → Actions)
- `IG_ACCESS_TOKEN`: system-user tokeni (vaxtı bitmir)
- `IG_USER_ID`: `17841438908470809`

API ünvanı `graph.facebook.com`-dur (`graph.instagram.com` bu tokeni qəbul etmir).
