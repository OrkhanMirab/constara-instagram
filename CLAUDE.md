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

## Meta quraşdırması (2026-11-08, hazırdır)
- Meta app «Orkhan Mirabov» (ID `1724058969208012`), **Constara Portfolio**-ya bağlıdır. Use case: «Manage messaging & content on Instagram», API setup with **Unified login**.
- Login configuration `29046229518364839` («Instagram Login Compatible»), token növü SUAT, **vaxtı heç vaxt bitmir**.
- Token icazələri: `instagram_basic`, `instagram_manage_messages`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights`.
- Hesab **@constara.app** Instagram Tester kimi əlavə olunub. App Review lazım deyil (development rejimi, öz hesabı).
- IG User ID `17841438908470809`. API ünvanı **graph.facebook.com**: `graph.instagram.com` bu tokeni qəbul etmir. `/me` boş siyahı, `me/accounts` boş data, `debug_token` isə app tokeni tələb edir. Ona görə ID Secrets-dən götürülür.
- Paylaşma limiti: 24 saatda 100 post (`content_publishing_limit`).
- Sınanıb və işləyir: karusel ✅, Reels (resumable upload) ✅. Post silmək ❌ (yuxarıya bax).
- Token yalnız GitHub Secrets-də və istifadəçinin kompüterindəki `D:\Ai\instagram-avto\.env` faylındadır. Heç vaxt çata yazdırma.

## Yol xəritəsi (istifadəçinin qərarı, 2026-11-08)
1. **İNDİ: Facebook Page avtomatik paylaşma.** Eyni Meta app işlədilir.
   - Constara FB səhifəsi lazımdır. Səhifə varmı, istifadəçidən soruş.
   - Səhifə Constara Portfolio-ya əlavə olunmalıdır.
   - App-ə «Manage everything on your Page» use case-i əlavə olunur (`pages_manage_posts`, `pages_read_engagement`, `pages_show_list`).
   - System user-ə səhifə aktivi verilir, sonra token yaradılır. `GET /{page-id}?fields=access_token` vaxtı bitməyən Page tokeni qaytarır. Secrets: `FB_PAGE_ID`, `FB_PAGE_TOKEN`.
   - Kod (`paylas.py`, platform modulu kimi):
     - şəkil: `POST /{page}/photos`;
     - karusel: hər şəkil `published=false` ilə yüklənir, sonra `POST /{page}/feed` + `attached_media`;
     - Reels: `POST /{page}/video_reels` (`upload_phase=start`) → rupload → `finish` + `video_state=PUBLISHED`.
   - `post.json`-a `"platforms": ["instagram","facebook"]` sahəsi əlavə olunur (susmaya görə hər ikisi). Hər platformanın nəticəsi `result.json`-da ayrıca yazılır, biri uğursuz olsa, o biri yenə paylaşılır.
2. Sonra: Story testi (`media_type=STORIES`; Business hesab tələb edə bilər), analitika toplayıcısı (statistika üçün **private** repo, çünki bu repo public-dir), həftəlik məzmun dövrü (Claude həftəni hazırlayır, istifadəçi təsdiqləyir), şərhlərə və DM-lərə avtomatik cavab («şərhdə LINK yaz → DM al»; Vercel webhook lazımdır, Constara saytından ayrıca).
3. Daha sonra: YouTube Shorts (Google audit tələb olunur, auditsiz videolar private qalır) və TikTok (audit tələb olunur, auditsiz postlar yalnız sahibinə görünür).
4. İkinci brend (istifadəçinin rəqəmsal bilik səhifəsi): bu reponun kopyası, ayrıca Meta app və portfolio, ayrıca Secrets və layihə.

## Constara tətbiqi ilə əlaqə
- Brend: tünd fon `#0A0E14`, mətn `#D6DEE8` / `#93A1B2`, aksent `#FF6B35`, yaşıl `#26D67F`, qızıl `#F7C04A`. Şrift Inter Display (Bold başlıq, Medium mətn). Dil Azərbaycanca.
- Video mühərriki və marketinq qaydaları `OrkhanMirab/life-analytics` reposundadır: `marketing/VIDEO-QAYDALARI.md`, `marketing/render.mjs`. Video lazım olanda o reponu sessiyaya qoş (`add_repo`). Tətbiqin yenilikləri: `docs/beyin/00-indi.md`.
- Bu sessiyada Claude məzmunu sabit kod ilə yox, hər dəfə Pillow (karusel) və ffmpeg (video, H.264/AAC, səssiz trek ilə) ilə yaradır.
