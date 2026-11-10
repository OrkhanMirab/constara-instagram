# Gündəlik plan təlimatı (avtomatik sessiya üçün)

1. Tarix: Türkiyə saatı ilə bugün (UTC+3). Fayl: `plan/<tarix>.json`. Varsa — toxunma, yalnız yoxla.
2. Say: 26 karusel, 2 story. **Reels: `"reels": []` — kinetik format (gen/reel.py) istifadəçi tərəfindən RƏDD edildi (2026-11-10: «nə axıcılıq var, nə peşəkarlıq»). Yeni Reels yolu qurulana qədər Reels yazma.** ( (`python3 plan.py` ilə slotları gör).
3. **Təkrar YOX:** `ls posted/` + son 3 günün `plan/*.json`-larını oxu (başlıqlar) — eyni başlıq/mövzu olmasın.
   Mövzular: vərdiş, intizam, məhsuldarlıq, pis vərdişi buraxmaq (vape, şəkər, scroll, içki), yuxu, səhər/axşam rejimi, motivasiya, izləmə (tracking), burnout.
   Format qarışığı: karusellərin ~1/3-i `myth`, ~1/3-i `steps`, qalanı `list`; rənglər növbələşsin; 7–8 karuseldə `chart` slaydı.
4. Mətn İngiliscə, qısa və konkret (slaydda başlıq ≤ 8 söz, izah ≤ 25 söz). Elmi iddia uydurma (rəqəm verirsənsə ehtiyatlı: «around», «often»).
5. Caption: açar söz ilk cümlədə, 1–2 cümlə izah, sonra `Comment LINK 👇 and I'll DM you the free app.`, sonra ən çox 5 hashtag.
6. (Reels müvəqqəti yoxdur — yuxarıya bax.)
7. Story: sual kartı (`kicker`, `title`, `body`, `cta`) — emoji şəkildə görünmür, yazma.
8. Yoxla: hər elementi lokalda render et (`gen/*.py`), qapaqları `montage` ilə bir şəkildə bax (mətn sığır, kəsilmir).
9. Commit + `git push origin HEAD:main` (yalnız `plan/` faylı). Dünənki `failed/` qovluqlarına bax, xəta varsa (atlanmayan) qısa qeyd yaz.
