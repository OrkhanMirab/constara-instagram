from PIL import Image, ImageDraw, ImageFont
W,H,S=1080,1350,2
F="/usr/share/fonts/opentype/inter/InterDisplay-"
def f(w,s): return ImageFont.truetype(F+w+".otf", s*S)
BG=(10,14,20); TX=(214,222,232); MU=(147,161,178); AC=(255,107,53); GR=(38,214,127); RD=(255,77,90); GO=(247,192,74); CARD=(19,25,34)
def wrap(d,text,font,maxw):
    out=[]
    for para in text.split("\n"):
        line=""
        for w in para.split():
            t=(line+" "+w).strip()
            if d.textlength(t,font=font)<=maxw*S: line=t
            else: out.append(line); line=w
        out.append(line)
    return out
def slide(n,total):
    im=Image.new("RGB",(W*S,H*S),BG); d=ImageDraw.Draw(im)
    # progress dots
    for i in range(total):
        x=(W/2-(total-1)*14+i*28)*S; c=AC if i==n-1 else (40,48,60)
        d.ellipse([x-6*S,1270*S-6*S,x+6*S,1270*S+6*S],fill=c)
    d.text((90*S,1252*S),"constara",font=f("Bold",28),fill=TX)
    d.text((990*S,1252*S),f"{n}/{total}",font=f("Medium",26),fill=MU,anchor="ra")
    return im,d
def wave(d,x0,y0,w,h,col,prog=1.0,width=8):
    import math
    pts=[]
    for i in range(201):
        t=i/200
        if t>prog: break
        y=math.exp(-((t-.42)/.2)**2)
        pts.append(((x0+w*t)*S,(y0+h-h*y)*S))
    if len(pts)>1: d.line(pts,fill=col,width=width*S,joint="curve")
    return pts
T=7
# 1 cover
im,d=slide(1,T)
d.text((90*S,150*S),"A craving",font=f("Bold",112),fill=TX)
d.text((90*S,275*S),"is a wave.",font=f("Bold",112),fill=AC)
d.text((90*S,425*S),"Learn to surf it.",font=f("Bold",64),fill=TX)
pts=wave(d,90,560,900,380,RD)
d.line([(90*S,940*S),(990*S,940*S)],fill=(40,48,60),width=3*S)
for x,l in [(90,"0"),(540,"10 min"),(990,"20 min")]:
    d.text((x*S,965*S),l,font=f("Medium",28),fill=MU,anchor="ma" if x==540 else ("la" if x==90 else "ra"))
px,py=pts[150]; d.ellipse([px-18*S,py-18*S,px+18*S,py+18*S],fill=GO)
d.text((px+30*S,py-60*S),"you",font=f("Bold",34),fill=GO)
d.text((90*S,1060*S),"The 10-minute rule for quitting vaping,\nsmoking, scrolling, any bad habit →",font=f("Medium",36),fill=MU,spacing=14*S)
im.resize((W,H),Image.LANCZOS).save("1.jpg",quality=92)
steps=[("1","Name it.","Say it out loud or in your head: \"This is a craving.\"\n\nNaming it puts a gap between you and the urge. You're watching the wave, not drowning in it.",GR),
("2","Set a 10-minute timer.","Don't fight it. Just delay it.\n\nCravings rise, peak and fade. Your only job is to still be standing when it does.",GR),
("3","Change the place.","Stand up. Walk. Drink a glass of water.\n\nCravings stick to places and routines. Move your body and the trigger loses its grip.",GR),
("4","Log the win.","Craving survived = +1.\n\nEvery wave you ride trains the habit. Watch the line go up and you'll want to protect it.",GR)]
for i,(num,head,body,c) in enumerate(steps):
    im,d=slide(i+2,T)
    d.ellipse([90*S,140*S,230*S,280*S],outline=c,width=6*S)
    d.text((160*S,210*S),num,font=f("Bold",80),fill=c,anchor="mm")
    y=340
    for ln in wrap(d,head,f("Bold",84),900):
        d.text((90*S,y*S),ln,font=f("Bold",84),fill=TX); y+=100
    y+=40
    for ln in wrap(d,body,f("Medium",44),900):
        d.text((90*S,y*S),ln,font=f("Medium",44),fill=MU if ln else MU); y+=62
    # mini wave at bottom shrinking with progress
    wave(d,90,1000,900,160,(60,70,84),1,5); wave(d,90,1000,900,160,c,(i+1)/4*0.42+0.1,6)
    im.resize((W,H),Image.LANCZOS).save(f"{i+2}.jpg",quality=92)
# 6 slipped
im,d=slide(6,T)
d.text((90*S,140*S),"Slipped?",font=f("Bold",100),fill=TX)
d.text((90*S,260*S),"It's −5, not zero.",font=f("Bold",84),fill=RD)
d.text((90*S,390*S),"One bad day can't erase thirty good ones.\nLog it, and climb back.",font=f("Medium",42),fill=MU,spacing=16*S)
sc=[0]
for k in range(1,31): sc.append(sc[-1]+(-5 if k==13 else 1))
x0,x1,y0,y1=90,990,1130,620
mx=max(sc)
P=[((x0+(x1-x0)*(k-1)/29)*S,(y0-(y0-y1)*sc[k]/mx)*S) for k in range(1,31)]
oy=P[11][1]; d.line([(x0*S,oy),(x1*S,oy)],fill=(70,80,95),width=2*S)
d.text((x0*S,oy-44*S),"OLD HIGH",font=f("Bold",26),fill=MU)
for k in range(29):
    d.line([P[k],P[k+1]],fill=RD if k==11 else GR,width=7*S)
rx,ry=P[12]; d.ellipse([rx-13*S,ry-13*S,rx+13*S,ry+13*S],fill=RD); d.text((rx+20*S,ry*1+0),"−5",font=f("Bold",40),fill=RD)
nx,ny=P[-1]; d.ellipse([nx-15*S,ny-15*S,nx+15*S,ny+15*S],fill=GO); d.text((nx-10*S,ny-62*S),"NEW HIGH",font=f("Bold",34),fill=GO,anchor="ra")
im.resize((W,H),Image.LANCZOS).save("6.jpg",quality=92)
# 7 CTA
im,d=slide(7,T)
d.text((90*S,170*S),"Save this",font=f("Bold",104),fill=TX)
d.text((90*S,290*S),"for your next craving.",font=f("Bold",72),fill=AC)
for j,(n,t) in enumerate([("1","Name it"),("2","10-minute timer"),("3","Change the place"),("4","Log the win")]):
    y=470+j*120
    d.rounded_rectangle([90*S,y*S,990*S,(y+96)*S],radius=20*S,fill=CARD)
    d.text((130*S,(y+48)*S),n,font=f("Bold",48),fill=GR,anchor="lm")
    d.text((200*S,(y+48)*S),t,font=f("Bold",46),fill=TX,anchor="lm")
d.text((90*S,980*S),"Send it to a friend who's quitting.",font=f("Bold",44),fill=TX)
d.text((90*S,1050*S),"Track every wave like a stock chart:\nConstara, free habit tracker, link in bio.",font=f("Medium",36),fill=MU,spacing=12*S)
im.resize((W,H),Image.LANCZOS).save("7.jpg",quality=92)
