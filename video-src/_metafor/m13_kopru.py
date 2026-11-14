"""M13 «Körpü» — dostluq vs iş (Metafor, 2026-11-14).

İstifadəçi: «dostluq və işlə bağlı yeni fikir, professional motion». Öz metaforumuz: iki sütun arasında kəndir körpü (dostluq).
Hər «next week» ilə sənin sütununa bir iş bloku gəlir (MEETING, OVERTIME…), səni yuxarı qaldırır, körpü gərilir və taxtalar
bir-bir qaranlığa düşür (−1). Zirvədə (PROMOTED) təksən. Bir mesaj → işıq kəndirlə enir → taxtalar qızılı yanır (+1),
dost qalxıb yanına gəlir. Çevrilmə: «Work will always want more hours. A friend only needs one.»
İşlətmə: python3 m13_kopru.py <scratch> [--no-audio] [--tts <kokoro qovluğu>] ; cp render.mjs <scratch>/ ; node render.mjs <scratch>
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_kino'))
import sound as S  # noqa: E402

FPS, DUR = 30, 26.0
BLOCKS = [  # (vaxt, etiket, dostun mesajı) — hər blokda sən qalxırsan, körpüdən taxta düşür
    (3.00, 'MEETING', 'dinner tonight?'), (4.05, 'OVERTIME', 'game night?'), (5.10, 'DEADLINE', 'my birthday sat?'),
    (6.15, 'LATE NIGHT', 'call this week?'), (7.20, 'EMAILS', None), (8.20, 'WEEKEND SHIFT', None),
    (9.25, 'ONE MORE TASK', None), (10.4, 'PROMOTED', None),
]
SNAP = 13.55     # məhəccər kəndiri qırılır
PHONE = 15.9     # telefonu çıxarır
SEND = 17.55     # mesaj göndərilir
ARRIVE = 18.55   # işıq dosta çatır
CLIMB = 19.7     # dost qalxmağa başlayır
MEET = 22.6
END = 21.2
TEXTS = [
    (0.05, 2.65, "YOU DON'T LOSE FRIENDS\nIN A FIGHT.", "IN A FIGHT.", "gold"),
    (2.75, 5.30, "YOU LOSE THEM TO\n\"NEXT WEEK.\"", "\"NEXT WEEK.\"", "red"),
    (5.40, 7.20, "ONE MORE DEADLINE.", "DEADLINE.", "red"),
    (7.30, 9.10, "ONE MORE LATE NIGHT.", "LATE NIGHT.", "red"),
    (9.20, 11.45, "ONE MORE\n\"SORRY, I'M BUSY.\"", "\"SORRY, I'M BUSY.\"", "red"),
    (11.60, 13.40, "YOU MAKE IT TO THE TOP...", "THE TOP", "gold"),
    (13.50, 15.75, "...AND NO ONE\nCAN REACH YOU.", "NO ONE", "red"),
    (15.90, 17.95, "WORK WILL ALWAYS WANT\nMORE HOURS.", "MORE HOURS.", "red"),
    (18.05, 21.00, "A FRIEND ONLY\nNEEDS ONE.", "ONE.", "gold"),
    (21.20, 25.80, "SEND THIS TO THE FRIEND\nYOU KEEP TELLING\n\"NEXT WEEK.\"", "\"NEXT WEEK.\"", "gold"),
]
VO = [
    (0.15, "You don't lose friends in a fight."), (2.80, "You lose them to next week."),
    (5.45, "One more deadline."), (7.35, "One more late night."), (9.25, "One more, sorry, I'm busy."),
    (11.65, "You make it to the top,"), (13.55, "and no one can reach you."),
    (15.95, "Work will always want more hours."), (18.10, "A friend only needs one."),
    (21.35, "Send this to the friend you keep telling, next week."),
]
FALL = [  # taxta indeksi → düşmə vaxtı (0 = sənin tərəf, 11 = dostun tərəfi); 7 qalır
    (2, 3.25), (9, 4.30), (5, 5.35), (11, 5.6), (0, 6.40), (4, 7.45), (10, 7.7), (1, 8.45), (6, 9.50), (3, 10.65), (8, 12.2),
]
TL = dict(fps=FPS, dur=DUR, blocks=BLOCKS, snap=SNAP, phone=PHONE, send=SEND, arrive=ARRIVE, climb=CLIMB, meet=MEET,
          end=END, texts=TEXTS, fall=FALL)


def noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n).astype(np.float32)


def voice_track(N):
    if '--tts' not in sys.argv:
        return None
    from kokoro_onnx import Kokoro
    from scipy.signal import resample_poly
    d = sys.argv[sys.argv.index('--tts') + 1]
    k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    v = np.zeros(N, np.float32)
    for t0, txt in VO:
        a, sr = k.create(txt, voice='am_michael', speed=0.92, lang='en-us')
        i = np.where(np.abs(a) > .01)[0]; a = a[max(0, i[0] - 200):i[-1] + 800]
        a = resample_poly(a, S.SR, sr).astype(np.float32)
        j = int(t0 * S.SR); v[j:j + len(a)] += a[:N - j]
    return S.voice_chain(v)


def creak(seed):  # kəndir/taxta cırıltısı
    d = .35; t = S.tarr(d); n = noise(len(t), seed)
    f = 180 + 120 * np.sin(2 * np.pi * 3 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / S.SR) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 34 * t)))
    return ((S.bp(n, 500, 2500) * .4 + s * .25) * np.sin(np.pi * t / d) * .16).astype(np.float32)


def thud(v=1.0):  # uzaqda düşən taxta
    t = S.tarr(.6)
    s = np.sin(2 * np.pi * (70 + 40 * np.exp(-t * 20)) * t) * np.exp(-t * 9)
    return (S.lp(s + noise(len(t), 3) * np.exp(-t * 30) * .3, 900) * v * .35).astype(np.float32)


def ping(v=1.0):  # mesaj bildirişi
    t = S.tarr(.9)
    s = np.sin(2 * np.pi * S.hz('E6') * t) * np.exp(-t * 6) + np.where(t > .11, np.sin(2 * np.pi * S.hz('B6') * (t - .11)) * np.exp(-(t - .11) * 5), 0)
    return (s * v * .09).astype(np.float32)


def audio(path):
    N = int(DUR * S.SR)
    mus, fx = S.Bus(DUR), S.Bus(DUR)
    tt = np.arange(N) / S.SR
    # külək: təklikdə güclənir, sonda sakitləşir
    wind = S.bp(noise(N, 7), 200, 1400) * np.interp(tt, [0, 10, 12, 13.6, 17.5, 20, 26], [.01, .03, .06, .12, .09, .02, .01])
    fx.add(0, wind.astype(np.float32))
    # iş blokları: zərbə + saat tıqqıltısı (təzyiq artır)
    for k, (bt, lab, msg) in enumerate(BLOCKS):
        fx.add(bt, S.kick(.5 + .05 * k)); fx.add(bt - .05, S.whoosh(.3, .4))
        if lab == 'PROMOTED':
            fx.add(bt, S.boom(.5))
        if msg:
            fx.add(bt - .3, ping(.6), pan=.4)
    for i in range(int(3.0 / .5), int(11.4 / .5)):
        fx.add(i * .5, S.tick(.55 + .3 * (i * .5 - 3) / 8))
    for j, (_, ft) in enumerate(FALL):
        fx.add(ft, creak(j), pan=(j % 3 - 1) * .3); fx.add(ft + .9, thud(.5), pan=.1)
    fx.add(SNAP, S.whoosh(.5, .8)); fx.add(SNAP, creak(40)); fx.add(SNAP + .02, (S.hp(noise(1200, 9), 2500) * .6).astype(np.float32))
    for i in range(10):  # yazır
        fx.add(PHONE + .5 + i * .11 + .03 * np.sin(i * 7), (S.hp(noise(500, 50 + i), 3000) * np.exp(-np.arange(500) / 80) * .18).astype(np.float32))
    fx.add(SEND, S.whoosh(.6, .6)); fx.add(ARRIVE, ping(1.0), pan=.4)
    # musiqi: isti (C–G) → iş: Am pulsu, getdikcə sıxlaşır → təklik: tək piano → mesaj: strings yüksəlir → C major
    mus.add(0, S.pad('C', 2.9, cut=1100, v=.7, att=.3)); mus.add(0, S.sub('C', 2.6, v=.3))
    for j, nm in enumerate(['E4', 'G4', 'C5', 'G4']):
        mus.add(.15 + j * .6, S.piano(S.hz(nm), 2.2, .4))
    for k, ch in enumerate(['Am', 'F', 'Am', 'F', 'Dm', 'Am', 'Em', 'Am']):
        t0 = 2.9 + k * 1.05
        mus.add(t0, S.pad(ch, 1.15, cut=700 + 70 * k, v=.55 + .04 * k, att=.05))
        mus.add(t0, S.sub(ch, 1.0, v=.45))
        for q in range(4):
            mus.add(t0 + q * .26, S.piano(S.hz(S.CHORDS[ch][1][2 + q % 2]), .5, .18 + .02 * k))
    mus.add(11.3, S.shimmer('Am', 2.2, .6))
    for j, nm in enumerate(['A4', 'E4', 'C4', 'B3', 'A3']):
        mus.add(11.6 + j * .95, S.piano(S.hz(nm), 3.0, .34))
    mus.add(13.5, S.pad('Am', 4.4, cut=380, v=.45, att=.8))
    mus.add(SEND, S.rev_swell(1.0, .6))
    mus.add(ARRIVE, S.shimmer('C', 2.6, 1.0))
    for k, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G', 'C']):
        t0 = ARRIVE + k * 1.2
        mus.add(t0, S.strings(ch, 1.4, v=.55 + .07 * k, att=.3))
        mus.add(t0, S.pad(ch, 1.4, cut=900 + 120 * k, v=.6, att=.15)); mus.add(t0, S.sub(ch, 1.2, v=.4))
    for i in range(12):  # taxtalar yanır: yuxarı qalxan pentatonik
        mus.add(ARRIVE + .3 + i * .1, S.piano(S.hz(['C5', 'D5', 'E5', 'G5', 'A5', 'C6'][i % 6]) * (1 if i < 6 else 2), 1.4, .16))
    for i, nm in enumerate(['C5', 'E5', 'G5', 'C6']):
        mus.add(MEET + i * .45, S.piano(S.hz(nm), 2.6, .34))
    m = S.apply_reverb(mus.x, S.reverb_ir(3.0), .3)[:N]
    f = S.apply_reverb(fx.x, S.reverb_ir(1.6, 5000, 5), .18)[:N]
    vo = voice_track(N)
    if vo is not None:
        out = S.mix(vo, m, f, duck_db=10.0)[:N]
    else:
        out = (m * .6 + f * .9)[:N]
        out = np.tanh(out * 1.1) / np.tanh(1.1); out = out / (np.max(np.abs(out)) + 1e-9) * .9
    fade = int(1.4 * S.SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    import soundfile as sf
    sf.write(path, out, S.SR)


def run(scr):
    os.makedirs(scr, exist_ok=True)
    html = open(os.path.join(HERE, 'm13_scene.html')).read().replace('/*TL*/', 'window.TL=' + json.dumps(TL) + ';')
    open(os.path.join(scr, 'index.html'), 'w').write(html)
    if '--no-audio' not in sys.argv:
        audio(os.path.join(scr, 'audio.wav'))
    print('hazır:', scr)


if __name__ == '__main__':
    run(sys.argv[1])
