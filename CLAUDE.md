# constara-instagram

@constara.app hesabına avtomatik paylaşma növbəsi. İstifadəçi Azərbaycanca yazır, cavablar da Azərbaycanca olsun. Format və axın `README.md`-dədir.

## Post növbəyə qoymaq
- `queue/YYYY-MM-DD-ad/post.json` + media yaz, sonra `main`-ə push et. Actions özü paylaşır.
- Şəkil yalnız **JPEG**, karusel 1080×1350. Reels MP4 H.264 + AAC, yuv420p, 1080×1920.
- `publish_after` təbii saatlara qoyulsun (gündə 1–2 post, eyni dəqiqədə yox).
- Push-dan sonra nəticəni yoxla: `posted/<ad>/result.json` (permalink) və ya `failed/<ad>/result.json` (xəta).
- Xətalı postu düzəltmək üçün qovluğu `failed/`-dən `queue/`-ya köçür, `result.json`-ı sil və yenidən push et.
- Sınaq üçün `paylas.py`-ı urlopen mock ilə lokalda işlət. Real token heç vaxt repoya yazılmasın.

## Post silmək: API ilə MÜMKÜN DEYİL (2026-11-08 sınandı)
- `DELETE /{media_id}` karuseldə «Unsupported delete request» (code 100/33), Reels-də «Insufficient permissions» (#10) qaytarır.
- Postu yalnız istifadəçi telefondan silə bilər. Paylaşmazdan əvvəl məzmunu istifadəçiyə göstər.
- `sil.py` + `sil/*.txt` mexanizmi qalır, gələcəkdə şərhləri silmək üçün işlədilə bilər (`instagram_manage_comments` icazəsi var).
