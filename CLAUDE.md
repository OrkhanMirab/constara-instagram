# constara-instagram

Constara tətbiqinin sosial şəbəkə avtomatlaşdırması. Hazırda **@constara.app** Instagram hesabına avtomatik paylaşma işləyir, Facebook səhifəsi **Constara.app**-a da (2026-11-08-dən) avtomatik paylaşır. İstifadəçi (Orxan) Azərbaycanca yazır və Türkiyədə yaşayır. Cavablar Azərbaycanca və qısa olsun. Format və axın `README.md`-dədir.

## 🚀 Yeni sessiyanın başlanğıcı
1. Bu faylı oxu (avtomatik yüklənir). «Yol xəritəsi» bölməsi növbəti işi göstərir (FB hazırdır; növbəti: yol xəritəsi §2).
2. **Tətbiqin məlumatı lazımdırsa** (yeni funksiya postu, video mühərriki, strategiyanın tam mətni), `OrkhanMirab/Constara` reposunu
   `add_repo` ilə **read** girişi ilə qoş və `/home/user/life-analytics` qovluğuna klonla. Adi karusel üçün aşağıdakı qısa məlumat kifayətdir.
3. Meta tərəfindəki addımları (Business Settings, use case, token) istifadəçi skrinşotlarla addım-addım edir. Hər dəfə bir addım ver,
   skrinşotu gözlə. Token və secret-ləri **heç vaxt** çata yazdırma: onlar yalnız GitHub Secrets-ə və istifadəçinin `.env` faylına gedir.
4. Bu sessiyada Python 3 + Pillow + ffmpeg + Inter Display şrifti (`/usr/share/fonts/opentype/inter/`) var. Karusel Pillow ilə, video ffmpeg ilə hazırlanır.
5. Hər real postu push etməzdən əvvəl **istifadəçiyə göstər** (montage önizləmə → SendUserFile), çünki API ilə silmək mümkün deyil.
6. Hər tamamlanmış addımdan sonra bu faylı yenilə (yol xəritəsində ✅). İstifadəçi istənilən an yeni sessiyaya keçə bilər.

## 🔎 Bilmədiyin şey çıxanda: TƏXMİN ETMƏ, GEDİB BAX
> Tətbiqin reposu: **`OrkhanMirab/Constara`** (köhnə adı `life-analytics`; klon qovluğu `/home/user/life-analytics` və ya `/home/user/Constara` ola bilər). Aşağıdakı «life-analytics» adları həmin repo deməkdir.
Söhbət zamanı tətbiq, brend, keçmiş qərarlar və ya marketinq barədə bilmədiyin bir məlumat lazım olsa (istifadəçi bunu açıq istəyib, 2026-11-08):
1. `/home/user/life-analytics` yoxdursa, `add_repo` (owner `OrkhanMirab`, repo `Constara`, access `read`) çağır, sonra
   `git clone --depth 1 https://github.com/OrkhanMirab/Constara /home/user/life-analytics`. Bu, bir dəfəlik işdir. İstifadəçidən icazə soruşma, sadəcə et.
2. `grep -rn` ilə axtar və yalnız lazım olan 20–40 sətri oxu. Faylı tam oxuma, çünki repo böyükdür.
3. **life-analytics-də heç nə dəyişmə** (o, başqa sessiyaların ərazisidir). Orada nəyisə dəyişmək lazımdırsa, istifadəçiyə de.

| Sual | Harada baxmalı (life-analytics) |
|---|---|
| Tətbiqin hazırkı vəziyyəti, yeni funksiyalar | `docs/beyin/00-indi.md` → oradakı mövzu jurnalları `docs/beyin/is-*.md` |
| Məhsul fikri, auditoriya, qiymət, modullar | `LAYIHE.md` (§1 məhsul, §2 auditoriya, §8 monetizasiya) |
| Keçmiş qərarlar | `docs/beyin/qerarlar.md` |
| Sosial/Instagram tarixçəsi, sayt statistikası | `docs/beyin/is-sosial.md`, `marketing/INSTAGRAM-STRATEGIYA.md` |
| Video hazırlamaq (mühərrik, şablon, üslub) | `marketing/VIDEO-QAYDALARI.md` (§6 başlanğıc), `marketing/render.mjs`, `marketing/sablon/` |
| Hazır videoların siyahısı | `marketing/videolar/README.md` (MP4-lər git-də yoxdur, istifadəçidədir: `D:\Constara Videolar\`) |
| Brend (logo, profil, personaj) | `marketing/brand/`, dizayn: `docs/dizayn-qanunlari.md`, rənglər: `src/index.css` (`@theme`) |
| Tətbiqdəki mətnlər/terminlər (az/tr/en/ru) | `src/i18n/` |
| Ekran görüntüsü lazımdır | `scripts/ui-tour/` (life-analytics CLAUDE.md «Tələlər»: emulyator + Playwright) |

İstifadəçinin kompüterindəki fayllara (`D:\...`) çıxış yoxdur. Onlar lazımdırsa, istifadəçidən repoya yükləməsini və ya çata atmasını istə.

## Constara nədir (qısa)
- Vərdiş + tapşırıq tətbiqi. Fərqi budur: həyatını **qrafiklə** (birja qrafiki kimi) analiz edirsən. Sual «bu gün etdinmi?» yox,
  **«özünə nə qədər sərmayə qoydun, nə qədər itirdin?»**-dır.
- Xal sistemi: yaxşı vərdiş +1/−1, pis vərdiş büdrəyəndə −5, tapşırıq +1. Analiz, MindMap (xəritə), xatırlatmalar var. Dillər az/tr/en/ru.
- Veb: https://life-analytics-jade.vercel.app. Qeydiyyatsız «qonaq rejimi» ilə sınamaq olar. Android (Play Store hələ buraxılmayıb).
- Free: 3 vərdiş, Pro: limitsiz (~$2, ödəniş hələ qurulmayıb). Hədəf: 20–40 yaş, özünü inkişaf etdirmək istəyən, rəqəmləri sevən istifadəçi.

## Instagram strategiyası: əsas qaydalar
Tam mətn: `life-analytics/marketing/INSTAGRAM-STRATEGIYA.md` (2026-11-04). Video qaydaları: `marketing/VIDEO-QAYDALARI.md`.
- Mövqe: geniş şəxsi inkişaf, amma **bir SİSTEM kimi** (vərdiş, intizam, məhsuldarlıq → ölçmək və qrafik).
- Güclü siqnallar: izləmə müddəti, reach başına bəyənmə, **göndərmə (DM-də paylaşma)**, saxlama. Reels və Kəşfet yeni auditoriyaya çatır.
- **Hashtag ən çox 5.** Açar söz caption-un ilk cümləsində və ekrandakı yazıda olsun (Instagram axtarışı onları oxuyur).
- Yalnız orijinal məzmun. Su nişanı və ya başqasının məzmunu olmasın.

## Post növbəyə qoymaq
- `queue/YYYY-MM-DD-ad/post.json` + media yaz, sonra `main`-ə push et. Actions özü paylaşır.
- Şəkil yalnız **JPEG**, karusel 1080×1350. Reels MP4 H.264 + AAC, yuv420p, 1080×1920.
- `publish_after` təbii saatlara qoyulsun (gündə 1–2 post, eyni dəqiqədə yox).
- **Limit:** `MAX_PER_24H=8` (2026-11-09: 4 → 5 → 8, istifadəçi gündə çox post istədi). Cron saatda iki dəfə (:23, :53), GitHub 5–30 dəq gecikdirə bilər (öz limitimiz, Meta-nınkı 100). Yalnız Instagram-a gedən postlar sayılır (yalnız FB postu sayılmır). Limitə dəyən post `queue/`-da gözləyir və log «⏸ Son 24 saatda…» yazır. Push `queue/`-ya toxunmursa, workflow-u `actions_run_trigger` (`paylas.yml`, `main`) ilə işə sal.
- Push-dan sonra nəticəni yoxla: `posted/<ad>/result.json` (permalink) və ya `failed/<ad>/result.json` (xəta).
- Xətalı postu düzəltmək üçün qovluğu `failed/`-dən `queue/`-ya köçür, `result.json`-ı sil və yenidən push et.
- Sınaq üçün `paylas.py`-ı urlopen mock ilə lokalda işlət. Real token heç vaxt repoya yazılmasın.

## Paylaşılan videolar
- **v15** «Scroll addiction: 3 signs you're beating it» (23,7 s, v08 formulası, M ara kadrı yox), 2026-11-08 ~21:08 TR: IG https://www.instagram.com/reel/DffXPO8ie0u/ · FB https://www.facebook.com/reel/2170089730287302/ . Mətnlər `queue`-da yox, `posted/2026-11-08-v15-scroll-signs/post.json`-da; TikTok/YouTube mətni istifadəçiyə `paylasim.md` kimi verildi. Mənbə (`marketing/v15-scroll-signs/`, `sablon/v15_body.html`) Constara reposuna commit OLUNMAYIB (bu sessiyadan yazmaq rədd edildi). Statistikanı ~20 saat sonra `VIDEO-QAYDALARI.md` §4 cədvəlinə yazmaq lazımdır.
- **v16** «Quitting vaping: 3 signs you're actually quitting» (21,5 s, v15 şablonu, vape nişi), 2026-11-09 15:38 TR: IG https://www.instagram.com/reel/DfhWQhHDJnm/ · FB https://www.facebook.com/reel/1820290745857449/ . Mənbə: `video-src/v16-quitting-vaping/` (body.html + vo.py; yığmaq üçün Constara `marketing/sablon/build.py`, render `marketing/render.mjs`).
- **Karusel** «A craving is a wave: the 10-minute rule» (7 slayd, Pillow, `video-src/carousel-craving-wave/car.py`), 2026-11-09 15:40 TR (istifadəçi «hazır olan kimi getsin» dedi): IG https://www.instagram.com/p/DfhWmkSk7lv/ · FB https://www.facebook.com/122097036609546687/posts/122097604197546687 — FB karuseli də real işlədi ✅.
- **Karusel** «5 signs you're more disciplined than you think» (7 slayd, `video-src/carousel-discipline-signs/car2.py`), istifadəçi «2 saat sonra birdə paylaş» dedi → `publish_after` 17:15 TR (cron :23-də → ~17:25–17:50). Eyni postu təkrar atma (dublikat) — həmişə yeni məzmun.
- Discipline karuseli 2026-11-09 18:09 TR paylaşıldı (cron gecikdi, əl ilə işə salındı): IG https://www.instagram.com/p/DfhnnvZF83F/ · FB https://www.facebook.com/122097036609546687/posts/122097711837546687
- **v17** «Quitting sugar: 3 signs» (21,9 s, v16 şablonu, narıncı başlıq), 2026-11-09 18:10 TR: IG https://www.instagram.com/reel/DfhntohjIEk/ · FB https://www.facebook.com/reel/1605105340912784/ . Mənbə `video-src/v17-quitting-sugar/`.
- **v18** «Quitting drinking: 3 signs» (22,4 s, göy başlıq), 2026-11-09 20:02 TR (cron gəlmədi, send_later + actions_run_trigger ilə): IG https://www.instagram.com/reel/Dfh0cb9iWTm/ · FB https://www.facebook.com/reel/1537239201763525/ . Mənbə `video-src/v18-quitting-drinking/`. Şablon generatoru: `mk.py` məntiqi — v16 body + başlıq/rəng/sətir/N1 caption + vo cümlələri.
- **Dərs:** GitHub schedule cron etibarlı deyil (14:23 UTC run gəlmədi) — vaxtlı post üçün `send_later` ilə özünə xatırlatma qoy və vaxtında `actions_run_trigger` et. Hər run yalnız BİR post paylaşır — növbədə 2 post varsa, ikinci dəfə işə sal.
- **Format müxtəlifliyi (2026-11-09, istifadəçi: «videolar hamısı eyni tərzdədir»):** v15–v18 eyni v08 şablonundandır. Təklif olunan yeni şablonlar: 1) **Xal testi** (canlı +1/−5 sayğacı, izləyici öz xalını sayır, nəticə sonda) — birinci qurulacaq; 2) **Telefon POV** (bildirişlər, ekran vaxtı sayğacı → Constara); 3) **Kinetik qrafik** (personajsız, 12–15 s, loop); 4) **Gün 1 vs Gün 30** (bölünmüş ekran). Rotasiya: «signs» ~40%, qalanları bərabər; ardıcıl iki video eyni formatda olmasın; yeni format 2 videoda sınanır, 3 s ≥50% saxlamırsa düzəlt/at. İstifadəçinin seçimi gözlənilir.
- **İstifadəçinin qərarı (2026-11-09):** «hamısını avtomatik et, vaxtım yoxdur, xoşuma gəlməsə silərəm» — yeni video/karusel üçün əvvəlcədən təsdiq gözləmə, hazırla və **hazır olan kimi** paylaş (`publish_after` qoyma, istifadəçi gecikdirməni istəmədi); sonra linkləri + TikTok/YouTube mətnini göndər.

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
- Sınanıb və işləyir: tək şəkil ✅ (2026-11-08, «stock chart» postu), karusel ✅, Reels (resumable upload) ✅. Post silmək ❌ (yuxarıya bax).
- Token yalnız GitHub Secrets-də və istifadəçinin kompüterindəki `D:\Ai\instagram-avto\.env` faylındadır. Heç vaxt çata yazdırma.

## Yol xəritəsi (istifadəçinin qərarı, 2026-11-08)
1. ✅ **Facebook Page avtomatik paylaşma (2026-11-08 HAZIR).** Tək şəkil real sınandı: https://www.facebook.com/122097036609546687/posts/122097036585546687 . Reels FB-də də real işlədi ✅ (v15, 2026-11-08). Karusel FB-də də real işlədi ✅ (2026-11-09). Hər üç növ hər iki platformada sınanıb.
   - ✅ (2026-11-08) FB səhifəsi **Constara.app**, Page ID `1466216953235938`, portfolio «constara.app»-ya (business_id `2195895974357884`) əlavə olundu; Instagram səhifəyə bağlandı. İstifadəçinin şəxsi FB hesabı (Orxan Mirabov) portfolio-da Full access-dir.
   - Səhifə Constara Portfolio-ya əlavə olunmalıdır. ✅
   - App-ə «Manage everything on your Page» use case-i əlavə olunur (`pages_manage_posts`, `pages_read_engagement`, `pages_show_list`).
   - ✅ Use case «Manage everything on your Page» əlavə olundu. Portfolio-da system user YOXDUR («Add» bağlıdır) → token yolu: Graph API Explorer (user token, «current Pages only» → Constara.app) → Access Token Debugger «Extend» (60 günlük user token) → `GET 1466216953235938?fields=access_token` → vaxtı bitməyən Page tokeni. Secrets: `FB_PAGE_ID`, `FB_PAGE_TOKEN` (istifadəçi əlavə edir). Page tokeni yoxlandı: Type Page, **Expires Never**, amma **Data Access Expires ~2027-02-06** — FB xətası çıxsa (data access expired), eyni 5 addımla yeni Page tokeni al. Token istifadəçinin `.env`-indədir (`FB_PAGE_TOKEN`).
   - ✅ Kod yazıldı və mock ilə sınandı (2026-11-08): `publish_instagram` / `publish_facebook`, `platforms` sahəsi, `result.json`-da hər platforma ayrıca. Real FB sınağı: tək şəkil ✅.
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
- Video mühərriki və marketinq qaydaları `OrkhanMirab/Constara` reposundadır: `marketing/VIDEO-QAYDALARI.md`, `marketing/render.mjs`. Video lazım olanda o reponu sessiyaya qoş (`add_repo`). Tətbiqin yenilikləri: `docs/beyin/00-indi.md`.
- Bu sessiyada Claude məzmunu sabit kod ilə yox, hər dəfə Pillow (karusel) və ffmpeg (video, H.264/AAC, səssiz trek ilə) ilə yaradır.
