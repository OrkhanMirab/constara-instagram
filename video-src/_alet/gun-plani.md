# Gündəlik plan təlimatı (avtomatik sessiya üçün)

1. Tarix: Türkiyə saatı ilə bugün (UTC+3). Fayl: `plan/<tarix>.json`. Varsa — toxunma, yalnız yoxla.
2. Say: 26 karusel, 2 story, **4 diktorlu Reels** (11:30, 14:30, 17:30, 20:30). Kinetik `gen/reel.py` RƏDD edilib (istifadəçi 11-10) — işlətmə.
3. **Təkrar YOX:** `ls posted/` + son 3 günün `plan/*.json`-larını oxu (başlıqlar) — eyni başlıq/mövzu olmasın.
   Mövzular: vərdiş, intizam, məhsuldarlıq, pis vərdişi buraxmaq (vape, şəkər, scroll, içki), yuxu, səhər/axşam rejimi, motivasiya, izləmə (tracking), burnout.
   Format qarışığı: karusellərin ~1/3-i `myth`, ~1/3-i `steps`, qalanı `list`; rənglər növbələşsin; 7–8 karuseldə `chart` slaydı.
4. Mətn İngiliscə, qısa və konkret (slaydda başlıq ≤ 8 söz, izah ≤ 25 söz). Elmi iddia uydurma (rəqəm verirsənsə ehtiyatlı: «around», «often»).
5. Caption: açar söz ilk cümlədə, 1–2 cümlə izah, sonra `Comment LINK 👇 and I'll DM you the free app.`, sonra ən çox 5 hashtag.
6. **Reels (diktorlu, v16 «3 signs» şablonu):** `video-src/_alet/reels.py`-ın başındakı formatla 4 cfg yaz (`/tmp/.../reels.json`).
   Mövzu: «Quitting X: 3 signs» (X: smoking, junk food, caffeine, energy drinks, gambling, online shopping, video games, soda, nail biting, late-night snacking…; posted/ və son planlarla təkrar olmasın).
   №1 cümləsi və `n1` ekran yazısı GECƏ ilə bağlı olsun (şablonun №1 kadrı ay/saat/gecədir). №2 = istək gəlir və keçir, №3 = bir dəfə sürüşürsən, sıfırdan başlamırsan (kadrlar sabitdir).
   `bg` rəngi hər videoda fərqli; başlıq uzunsa `fs` 38–42. Son cümlə və LINK kadrı avtomatikdir.
   Qurulum: Constara reposu (`/home/user/Constara`, yoxdursa add_repo read + clone), `pip install kokoro-onnx soundfile`, iş qovluğuna `kokoro-v1.0.onnx` + `voices-v1.0.bin`
   (`https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/<fayl>`), qlobal playwright.
   Əmr (karusel/story planı yazılandan SONRA): `python3 video-src/_alet/reels.py <tarix> reels.json <iş-qovluğu>` (~15–20 dəq; videoları `reels/<tarix>` budağına yükləyir, plan faylına `reels` yazır).
   Bir neçə kadrı `ffmpeg -ss` ilə çıxarıb montage-də bax (mətn sığır).
7. Story: sual kartı (`kicker`, `title`, `body`, `cta`) — emoji şəkildə görünmür, yazma.
8. Yoxla: hər elementi lokalda render et (`gen/*.py`), qapaqları `montage` ilə bir şəkildə bax (mətn sığır, kəsilmir).
9. Commit + `git push origin HEAD:main` (yalnız `plan/` faylı). Dünənki `failed/` qovluqlarına bax, xəta varsa (atlanmayan) qısa qeyd yaz.
