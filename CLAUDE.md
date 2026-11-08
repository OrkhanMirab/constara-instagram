# constara-instagram

@constara.app hesabına avtomatik paylaşma növbəsi. İstifadəçi Azərbaycanca yazır, cavablar da Azərbaycanca olsun. Format və axın `README.md`-dədir.

## Post növbəyə qoymaq
- `queue/YYYY-MM-DD-ad/post.json` + media yaz, sonra `main`-ə push et. Actions özü paylaşır.
- Şəkil yalnız **JPEG**, karusel 1080×1350. Reels MP4 H.264 + AAC, yuv420p, 1080×1920.
- `publish_after` təbii saatlara qoyulsun (gündə 1–2 post, eyni dəqiqədə yox).
- Push-dan sonra nəticəni yoxla: `posted/<ad>/result.json` (permalink) və ya `failed/<ad>/result.json` (xəta).
- Xətalı postu düzəltmək üçün qovluğu `failed/`-dən `queue/`-ya köçür, `result.json`-ı sil və yenidən push et.
- Sınaq üçün `paylas.py`-ı urlopen mock ilə lokalda işlət. Real token heç vaxt repoya yazılmasın.

## Post silmək
- `sil/<ad>.txt` faylına hər sətirdə bir `media_id` yaz (`posted/<ad>/result.json`-dan götürülür), sonra push et.
- Nəticə `sil-netice/<vaxt>.json` faylına yazılır. Uğurlu silinmədə `posted/<ad>/result.json`-a `deleted_at` əlavə olunur.
