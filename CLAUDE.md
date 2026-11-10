# constara-instagram

Constara tətbiqinin sosial şəbəkə avtomatlaşdırması. Hazırda **@constara.app** Instagram hesabına avtomatik paylaşma işləyir, Facebook səhifəsi **Constara.app**-a da (2026-11-08-dən) avtomatik paylaşır. İstifadəçi (Orxan) Azərbaycanca yazır və Türkiyədə yaşayır. Cavablar Azərbaycanca və qısa olsun. Format və axın `README.md`-dədir.

## 🚀 Yeni sessiyanın başlanğıcı
1. Bu faylı oxu (avtomatik yüklənir). «Yol xəritəsi» bölməsi növbəti işi göstərir (FB hazırdır; növbəti: yol xəritəsi §2).
2. **Tətbiqin məlumatı lazımdırsa** (yeni funksiya postu, video mühərriki, strategiyanın tam mətni), `OrkhanMirab/Constara` reposunu
   `add_repo` ilə **read** girişi ilə qoş və `/home/user/life-analytics` qovluğuna klonla. Adi karusel üçün aşağıdakı qısa məlumat kifayətdir.
3. Meta tərəfindəki addımları (Business Settings, use case, token) istifadəçi skrinşotlarla addım-addım edir. Hər dəfə bir addım ver,
   skrinşotu gözlə. Token və secret-ləri **heç vaxt** çata yazdırma: onlar yalnız GitHub Secrets-ə və istifadəçinin `.env` faylına gedir.
4. Bu sessiyada Python 3 + Pillow + ffmpeg + Inter Display şrifti (`/usr/share/fonts/opentype/inter/`) var. Karusel Pillow ilə, video ffmpeg ilə hazırlanır.
5. ~~Hər real postu əvvəl göstər~~ → **2026-11-09-dan istifadəçi qərarı: göstərmədən hazırla və dərhal paylaş**, sonra linkləri + MP4 + TikTok/YouTube mətnini göndər (aşağıda «İstifadəçinin qərarı»). İstisna: Meta/token/kod dəyişikliyi kimi riskli işlər.
6. Hər tamamlanmış addımdan sonra bu faylı yenilə (yol xəritəsində ✅). İstifadəçi istənilən an yeni sessiyaya keçə bilər.

## 📍 Harada qaldıq (2026-11-09 axşam, sessiya bağlandı)
**Edilənlər:** FB avtomatik paylaşma hazır (şəkil/karusel/Reels hər iki platformada ✅). 2 gündə paylaşılanlar: stock chart şəkli, v15 (scroll), v16 (vape), v17 (şəkər), v18 (içki), 2 karusel (craving wave, discipline signs) — linklər «Paylaşılan videolar»-da.
**Növbəti işlər (prioritet sırası):**
1. **Yeni format: «Xal testi» videosu** (istifadəçi «başla» deyəndə; təklif qəbul edilməyib, amma gözlənilir). v15–v18 eyni şablondur — növbəti video fərqli formatda olsun.
2. **Statistika:** v14–v18 + karusellərin rəqəmləri yoxdur. İstifadəçi ya rəqəmləri göndərir, ya da private repo `constara-stats` açıb `IG_ACCESS_TOKEN`/`IG_USER_ID` secret-lərini qoyur → workflow insights çəkir (yol xəritəsi §2). Rəqəmlər gələndə Constara `marketing/VIDEO-QAYDALARI.md` §4-ə yazılmalıdır — bu sessiyadan Constara-ya yazmaq RƏDD edilir → istifadəçiyə de ki, Constara sessiyasında yazdırsın, ya da cədvəli burada `stats.md`-də saxla.
3. İstifadəçi səhərki 2 test postunu (test karusel, test Reels, 2026-11-08) telefondan silməlidir — xatırlat.
4. YouTube/TikTok-a istifadəçi əl ilə yükləyir: ümumi YouTube açıqlaması linksizdir (istifadəçi: «xarici bağlantı hələlik olmayacaq»); başlıq ≤100 simvol, hər videoya ayrıca başlıq.

**Video hazırlamaq (bulud, hər sessiyada, ~5 dəq qurulum):**
- Constara reposunu read ilə klonla (yuxarıdakı qayda) — `marketing/sablon/build.py`, `marketing/render.mjs`, `head.html`, `peep.json`, `rig.js`, `poses.json` oradadır.
- Diktor: `pip install kokoro-onnx soundfile` + `kokoro-v1.0.onnx` və `voices-v1.0.bin` (`https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/<fayl>`), səs `am_michael`, speed 0.95. `vo.py` → `vo.b64` + `cues.json`.
- Şablon: `video-src/v16-quitting-vaping/body.html` (v08 formulası, 7 cue). Yeni mövzu: `video-src/_alet/mk.py <scratch> <ad> <cfg.json>` (nümunə `v17.json`/`v18.json`: başlıq, şrift ölçüsü — uzun başlıqda 36–42px, rəng, tətbiq sətri, №1 caption, 7 diktor cümləsi).
- Yığ: Constara kökündən `python3 marketing/sablon/build.py <body> <cues.json> <vo.b64> <out/index.html> "<ad>"`. Yoxla: `video-src/_alet/snap.mjs` (qlobal playwright, yolu dəyiş) → montage.
- Render: `render.mjs`-i scratch qovluğuna köçür (`<scratch>/vid/render.mjs` + `<scratch>/vid/<ad>/index.html`), `NODE_PATH=$(npm root -g) node render.mjs <ad>` (~8 dəq) → ffmpeg crf 24 ilə kiçilt (~4,5 MB).
- **Tələ:** gözləmə döngəsində `pgrep -f "<fayl adı>"` öz-özünü tapır və sonsuz gözləyir — log faylında «Hazır» sözünü yoxla.
- Karusel: Pillow, `video-src/carousel-*/car*.py` nümunələri (tünd brend, 1080×1350, 7 slayd, son slayd saxlanılası checklist).

## 🤖 Avtomatik gündəlik sistem (2026-11-10, istifadəçi qərarı)
İstifadəçi: «10:00–23:00 arası hər 1,5 saatdan bir Reels, hər 30 dəqiqədən bir karusel, gündə 2 story» (risk izah olundu: spam/reach düşməsi; istifadəçi yenə istədi).
- **Tezlik:** `schedule.json` (TR saatı). **Reels gündə 4: 11:30, 14:30, 17:30, 20:30** (istifadəçi 11-10: «4 ədəd, 21:00-a qədər»), diktorlu v16 şablonu, `video-src/_alet/reels.py` → `reels/<tarix>` budağı → plan `reels` (`video_branch`, ID `<tarix>-vreel-NN`); **karusel gündə 3: 13:00, 16:00, 19:00** (istifadəçi 11-10: «cəmi 3 karusel, 4 reels, 2 story vəssəlam»), story 12:40 və 20:40. Azaltmaq üçün yalnız bu faylı dəyiş.
- **Məzmun = data:** `plan/YYYY-MM-DD.json` (`reels` / `carousels` / `stories` siyahıları; format `plan.py` və `gen/*.py` başında). i-ci element o növün i-ci slotuna düşür. `"from": "HH:MM"` ondan əvvəlki slotları boş saxlayır.
- **Generatorlar** (`gen/`): `carousel.py` (kind list/myth/steps, 2–10 slayd), `story.py`, `reel.py` (kinetik qrafik — **istifadəçi RƏDD etdi 11-10, işlətmə**). Media runner-də hazırlanır (git-ə düşmür); şəkillər `media` budağına tək commit kimi force-push olunur (raw URL), main-ə yalnız `posted/<id>/post.json + result.json`.
- **Paylaşma:** `paylas.yml` bir run ~5,5 saat dövrədə işləyir, hər 2 dəq-dən bir yoxlayır (GitHub cron saatlarla gəlmir — 11-10 səhər 04:48-dən sonra run yox idi); cron (:07, :37) yalnız dövrəni yenidən başladır; hər run ən çox 3 plan elementi; slotdan 120 dəq-dən çox gecikən element atlanır (`failed/<id>` «vaxt keçdi»). `MAX_PER_24H=45`. Köhnə `queue/` yolu da işləyir.
- **Gündəlik sessiya:** hər gecə scheduled task yeni sessiya açır → həmin günün planını yazır (`video-src/_alet/gun-plani.md` təlimatı), lokalda render edib baxır, `main`-ə push edir. Plan yoxdursa o gün heç nə paylaşılmır.
- **Meta bloku (11-10 14:00 TR, HƏLL OLUNDU):** IG `API access blocked` (code 200) + FB 190 — səbəb Meta-nın təsdiq tələbi idi; istifadəçi təsdiqləyəndən sonra tokenlər yenidən işlədi (yeni token lazım olmadı). Təkrarlansa: kökdə `PAUSE` faylı yarat (paylas.py heç nə etmir), istifadəçidən developers.facebook.com → Required actions yoxlamasını istə.
- Sınaq: `python3 plan.py plan/<tarix>.json` (cədvəl); generatoru lokalda `python3 gen/carousel.py c.json out/`.

## 🧠 Analiz agenti (2026-11-10, istifadəçi istədi: «hər 3–4 videodan bir Instagram-ı və videoları analiz etsin, videoları, animasiyaları, ssenariləri inkişaf etdirsin») — QURULACAQ
1. **Rəqəm toplayıcı:** Actions job (gündə 1–2 dəfə) hər post üçün insights çəkir (`instagram_manage_insights` icazəsi var): reach, plays/views, ortalama izləmə vaxtı (`ig_reels_avg_watch_time`), saxlama (`saved`), göndərmə (`shares`), şərh, bəyənmə, follows. Statistika **private** repoda (`constara-stats`) saxlanır — bu repo public-dir; istifadəçi private repo açıb `IG_ACCESS_TOKEN`/`IG_USER_ID` secret qoymalıdır (və ya bu repoda yalnız ümumiləşdirilmiş cədvəl).
2. **Analiz sessiyası:** scheduled task hər 4 Reels-dən sonra (≈ hər gün gecə planından əvvəl) yeni sessiya açır → son postların rəqəmlərini oxuyur, format/mövzu/hook/uzunluq/rəng müqayisəsi edir (hansı 3 s-də saxlayır, hansı göndərilir) → `analiz/YYYY-MM-DD.md` hesabat → nəticələri **`video-src/_alet/gun-plani.md` qaydalarına və Reels cfg şablonlarına** yazır (məs. «X tipli hook-lar 2× reach» → növbəti planda üstünlük). Böyük dəyişiklik (yeni animasiya şablonu, format) — təklif kimi istifadəçiyə; kiçik (mövzu, hook, caption, rəng, uzunluq) — avtomatik.
3. Sıra: əvvəl diktorlu Reels pipeline-ı (reels.py) işləsin → sonra toplayıcı → sonra analiz sessiyası. Ən azı ~10 post rəqəmi yığılmadan nəticə çıxarma.

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
- **v15** «Scroll addiction: 3 signs you're beating it» (23,7 s, v08 formulası, M ara kadrı yox), 2026-11-08 ~21:08 TR: IG https://www.instagram.com/reel/DffXPO8ie0u/ · FB https://www.facebook.com/reel/2170089730287302/ . Mətnlər `queue`-da yox, `posted/2026-11-08-v15-scroll-signs/post.json`-da; TikTok/YouTube mətni istifadəçiyə `paylasim.md` kimi verildi. Mənbə burada: `video-src/v15-scroll-signs/` (Constara reposuna yazmaq bu sessiyadan rədd edilir). Statistikanı ~20 saat sonra `VIDEO-QAYDALARI.md` §4 cədvəlinə yazmaq lazımdır.
- **v16** «Quitting vaping: 3 signs you're actually quitting» (21,5 s, v15 şablonu, vape nişi), 2026-11-09 15:38 TR: IG https://www.instagram.com/reel/DfhWQhHDJnm/ · FB https://www.facebook.com/reel/1820290745857449/ . Mənbə: `video-src/v16-quitting-vaping/` (body.html + vo.py; yığmaq üçün Constara `marketing/sablon/build.py`, render `marketing/render.mjs`).
- **Karusel** «A craving is a wave: the 10-minute rule» (7 slayd, Pillow, `video-src/carousel-craving-wave/car.py`), 2026-11-09 15:40 TR (istifadəçi «hazır olan kimi getsin» dedi): IG https://www.instagram.com/p/DfhWmkSk7lv/ · FB https://www.facebook.com/122097036609546687/posts/122097604197546687 — FB karuseli də real işlədi ✅.
- **Karusel** «5 signs you're more disciplined than you think» (7 slayd, `video-src/carousel-discipline-signs/car2.py`), istifadəçi «2 saat sonra birdə paylaş» dedi → `publish_after` 17:15 TR (cron :23-də → ~17:25–17:50). Eyni postu təkrar atma (dublikat) — həmişə yeni məzmun.
- Discipline karuseli 2026-11-09 18:09 TR paylaşıldı (cron gecikdi, əl ilə işə salındı): IG https://www.instagram.com/p/DfhnnvZF83F/ · FB https://www.facebook.com/122097036609546687/posts/122097711837546687
- **v17** «Quitting sugar: 3 signs» (21,9 s, v16 şablonu, narıncı başlıq), 2026-11-09 18:10 TR: IG https://www.instagram.com/reel/DfhntohjIEk/ · FB https://www.facebook.com/reel/1605105340912784/ . Mənbə `video-src/v17-quitting-sugar/`.
- **v18** «Quitting drinking: 3 signs» (22,4 s, göy başlıq), 2026-11-09 20:02 TR (cron gəlmədi, send_later + actions_run_trigger ilə): IG https://www.instagram.com/reel/Dfh0cb9iWTm/ · FB https://www.facebook.com/reel/1537239201763525/ . Mənbə `video-src/v18-quitting-drinking/`. Şablon generatoru: `mk.py` məntiqi — v16 body + başlıq/rəng/sətir/N1 caption + vo cümlələri.
- **Dərs:** GitHub schedule cron etibarlı deyil (14:23 UTC run gəlmədi) — vaxtlı post üçün `send_later` ilə özünə xatırlatma qoy və vaxtında `actions_run_trigger` et. Hər run yalnız BİR post paylaşır — növbədə 2 post varsa, ikinci dəfə işə sal.
- **Format müxtəlifliyi (2026-11-09, istifadəçi: «videolar hamısı eyni tərzdədir»):** v15–v18 eyni v08 şablonundandır. Təklif olunan yeni şablonlar: 1) **Xal testi** (canlı +1/−5 sayğacı, izləyici öz xalını sayır, nəticə sonda) — birinci qurulacaq; 2) **Telefon POV** (bildirişlər, ekran vaxtı sayğacı → Constara); 3) **Kinetik qrafik** (personajsız, 12–15 s, loop); 4) **Gün 1 vs Gün 30** (bölünmüş ekran). Rotasiya: «signs» ~40%, qalanları bərabər; ardıcıl iki video eyni formatda olmasın; yeni format 2 videoda sınanır, 3 s ≥50% saxlamırsa düzəlt/at. İstifadəçinin seçimi gözlənilir.
- **İstifadəçinin qərarı (2026-11-09):** «hamısını avtomatik et, vaxtım yoxdur, xoşuma gəlməsə silərəm» — yeni video/karusel üçün əvvəlcədən təsdiq gözləmə, hazırla və **hazır olan kimi** paylaş (`publish_after` qoyma, istifadəçi gecikdirməni istəmədi); sonra linkləri + TikTok/YouTube mətnini göndər.

- **«LINK yaz» çağırışı (2026-11-09, istifadəçi qərarı, BÜTÜN videolarda):** son diktor cümləsi + son kadrda ekran yazısı
  `Comment "LINK" and I'll send you the app.` Caption-da «link in bio» yerinə: `Comment LINK 👇 and I'll DM you the free app.` (bio linki yenə qalır).
  Platformalar: **Instagram** → avtomatik DM (qurulmayana qədər istifadəçi əl ilə yazır); **TikTok** → istifadəçi DM ilə atır; **YouTube** → istifadəçi şərhə linkli cavab yazır
  (2026-11-09 sınaq: bildiriş/Studio səhifəsində link mavi görünür, amma **Shorts pleyerində ağdır — BASILMIR**. Ona görə: link kanal profilinin
  Links bölməsində olsun, «LINK» yazana cavab: «Link is on my channel page 👆». Eyni linki təkrar-təkrar yazma — spam sayıla bilər). Səbəb (huni hesabı, 11-09): 3×500 baxış/gün indiki huni ilə ayda ~5–20 qeydiyyat; açar sözlü DM klikləri ~3–5× artırır.
  Instagram avtomatı üçün iki yol: (a) ManyChat pulsuz plan (kodsuz, ən tez); (b) öz kodumuz — Actions cron şərhləri oxuyur (`instagram_manage_comments`),
  «LINK» tapanda private reply DM (`instagram_manage_messages`, şərhdən sonra 7 gün ərzində). (b) development rejimində rolsuz istifadəçiyə DM göndərə
  bilməyə bilər (Advanced Access/App Review) — əvvəl real sınaq.

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
