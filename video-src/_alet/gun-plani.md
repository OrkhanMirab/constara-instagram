# Gündəlik plan təlimatı (avtomatik sessiya üçün)

0. **ƏVVƏL ANALİZ** (hər gecə, planı yazmazdan əvvəl):
   a. `/home/user/constara-stats` yoxdursa: `add_repo` (OrkhanMirab/constara-stats, push) → `git clone --depth 1 https://github.com/OrkhanMirab/constara-stats /home/user/constara-stats`; varsa `git pull`.
   b. `cedvel.md` başlığındakı vaxt 4 saatdan köhnədirsə: `actions_run_trigger` (constara-stats, `topla.yml`, `main`) → ~1 dəq sonra `git pull`.
   c. `python3 analiz.py 14` oxu. Dünənki postları (q=erkən olsa da) bazayla müqayisə et: mövzu, format, hook, saat, share/save.
   d. `analiz/<tarix>.md` yaz (constara-stats, private): 5–10 sətir nəticə + nə dəyişdirildi. Commit + push.
   e. Nəticələri **`video-src/_alet/oyrenilenler.md`**-yə yaz (public: xam rəqəm YOX, yalnız nisbət/qayda, n=post sayı). Qayda yalnız ≥3 postla
      təsdiqlənəndə «aktiv» olur; ziddinə 3 sübut gəlsə — sil/düzəlt. Kiçik dəyişiklik (mövzu, hook, caption, rəng, uzunluq, karusel növü) — özün et.
      Böyük dəyişiklik (yeni video şablonu/format, gündəlik say/saat) — yalnız «Sınaqda / təkliflər»-ə yaz və sonda istifadəçiyə bildir.
   f. Aşağıdakı plan **oyrenilenler.md «Aktiv qaydalar»**-a əməl edir; ziddiyyət olsa, oyrenilenler.md qalib gəlir.

1. Tarix: Türkiyə saatı ilə bugün (UTC+3). Fayl: `plan/<tarix>.json`. Varsa — toxunma, yalnız yoxla.
2. Say `schedule.json`-dan (11-11-dən YÜNGÜL TEMP, istifadəçi: «radara düşməyək»): **yalnız 2 Reels** (14:30, 20:30), **karusel YOX, story YOX**. Bundan artıq yazma. Köhnə mətn: **4 diktorlu Reels** (11:30, 14:30, 17:30, 20:30). Kinetik `gen/reel.py` RƏDD edilib (istifadəçi 11-10) — işlətmə.
3. **Təkrar YOX:** `ls posted/` + son 3 günün `plan/*.json`-larını oxu (başlıqlar) — eyni başlıq/mövzu olmasın.
   Mövzular: vərdiş, intizam, məhsuldarlıq, pis vərdişi buraxmaq (vape, şəkər, scroll, içki), yuxu, səhər/axşam rejimi, motivasiya, izləmə (tracking), burnout.
   Format qarışığı: karusellərin ~1/3-i `myth`, ~1/3-i `steps`, qalanı `list`; rənglər növbələşsin; 1 karuseldə `chart` slaydı; günlər üzrə kind növbələşsin (list → steps → myth); karusel saxlanılası olsun (checklist/plan).
4. Mətn İngiliscə, qısa və konkret (slaydda başlıq ≤ 8 söz, izah ≤ 25 söz). Elmi iddia uydurma (rəqəm verirsənsə ehtiyatlı: «around», «often»).
5. Caption: açar söz ilk cümlədə, 1–2 cümlə izah, sonra `Comment LINK 👇 and I'll DM you the free app.`, sonra ən çox 5 hashtag.
6. **Reels (diktorlu, v16 «3 signs» şablonu):** `video-src/_alet/reels.py`-ın başındakı formatla 4 cfg yaz (`/tmp/.../reels.json`).
   Mövzu seçimi: **əvvəl oyrenilenler.md qayda 1** (2 sübut olunmuş niş + 2 kəşf, «Bazada qalanlar»-ı təkrarlama). Kəşf üçün nümunə: «Quitting X: 3 signs» (X: smoking, junk food, caffeine, energy drinks, gambling, online shopping, video games, soda, nail biting, late-night snacking…; posted/ və son planlarla təkrar olmasın).
   №1 cümləsi və `n1` ekran yazısı GECƏ ilə bağlı olsun (şablonun №1 kadrı ay/saat/gecədir). №2 = istək gəlir və keçir, №3 = bir dəfə sürüşürsən, sıfırdan başlamırsan (kadrlar sabitdir).
   **Xal testi (sınaq, 11-11-dən):** 2 Reels-dən biri (20:30), `"format": "xal"` olsun (oyrenilenler.md «Sınaqda») — 4 sual (3× +1, 1× −5 və ya 2/2),
   sual kartda ≤ 3 sətir, diktor cümləsi «… Plus one.» / «… Minus five.» ilə bitir, hook qısa iddia («Most people score below zero»). Caption-da «Comment your score 👇».
   `bg` rəngi hər videoda fərqli; başlıq uzunsa `fs` 38–42. Son cümlə və LINK kadrı avtomatikdir.
   **Kino formatı (sınaq, 11-13-dən, istifadəçi 11-12: «professional, hisslərə toxunan, 60% qalsın»):** 14:30 slotu `"format": "kino"` olsun
   (sübut olunmuş niş — p*rn/NoFap, vape/nikotin — ki, fərqi format yaratsın). Əvvəl `video-src/_kino/kino-arastirma.md` §2–§3 oxu, nümunə `video-src/_kino/ornek/k01-not-weak.json`.
   Ssenari 8 xətt, ~20–23 s: `hook` (birbaşa «sən» iddiası, ≤ 2,5 s, saat YOX) → `night` (konkret ağrı anı) → `count` (sayğac: rəqəm + vahid, uydurma statistika YOX) →
   `turn` («Here's what nobody tells you» tipli, 1 aksent sözü) → `rise` (şəxsiyyət/ümid) → `chart` ×2 (+1 / −5 / «can't erase») → `cta` (LINK, sabit cümlə: «Comment link, and I'll send you the app.»).
   Hər xəttdə 1 vurğu: `*söz*` aksent, `_söz_` serif emosiya, `~+1~` yaşıl, `!−5!` qırmızı. `tag` = niş adı (`QUITTING P*RN`, `QUITTING VAPING`). Hook və turn hər videoda YENİ olsun.
   Kino üçün əlavə: `pip install scipy`. Montage: `node video-src/_kino/snap.mjs <iş>/rNN/index.html <png-qovluq>`.
   Qurulum: Constara reposu (`/home/user/Constara`, yoxdursa add_repo read + clone), `pip install kokoro-onnx soundfile scipy`, iş qovluğuna `kokoro-v1.0.onnx` + `voices-v1.0.bin`
   (`https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/<fayl>`), qlobal playwright.
   Əmr (karusel/story planı yazılandan SONRA): `python3 video-src/_alet/reels.py <tarix> reels.json <iş-qovluğu>` (~15–20 dəq; videoları `reels/<tarix>` budağına yükləyir, plan faylına `reels` yazır).
   Bir neçə kadrı `ffmpeg -ss` ilə çıxarıb montage-də bax (mətn sığır).
7. Story: sual kartı (`kicker`, `title`, `body`, `cta`) — emoji şəkildə görünmür, yazma.
8. Yoxla: hər elementi lokalda render et (`gen/*.py`), qapaqları `montage` ilə bir şəkildə bax (mətn sığır, kəsilmir).
9. Commit + `git push origin HEAD:main` (yalnız `plan/` faylı). Dünənki `failed/` qovluqlarına bax, xəta varsa (atlanmayan) qısa qeyd yaz.
