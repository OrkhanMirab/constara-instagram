from PIL import Image, ImageDraw, ImageFont
W,H,S=1080,1350,2
F="/usr/share/fonts/opentype/inter/InterDisplay-"
def f(w,s): return ImageFont.truetype(F+w+".otf", s*S)
BG=(10,14,20); TX=(214,222,232); MU=(147,161,178); AC=(255,107,53); GR=(38,214,127); RD=(255,77,90); GO=(247,192,74); CARD=(19,25,34)
T=7
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
def slide(n):
    im=Image.new("RGB",(W*S,H*S),BG); d=ImageDraw.Draw(im)
    for i in range(T):
        x=(W/2-(T-1)*14+i*28)*S; c=AC if i==n-1 else (40,48,60)
        d.ellipse([x-6*S,1264*S,x+6*S,1276*S],fill=c)
    d.text((90*S,1252*S),"constara",font=f("Bold",28),fill=TX)
    d.text((990*S,1252*S),f"{n}/{T}",font=f("Medium",26),fill=MU,anchor="ra")
    return im,d
def save(im,n): im.resize((W,H),Image.LANCZOS).save(f"{n}.jpg",quality=92)
# cover
im,d=slide(1)
d.text((90*S,150*S),"5 signs",font=f("Bold",130),fill=GR)
d.text((90*S,300*S),"you're more",font=f("Bold",100),fill=TX)
d.text((90*S,415*S),"disciplined",font=f("Bold",100),fill=TX)
d.text((90*S,530*S),"than you think.",font=f("Bold",100),fill=TX)
y=720
for k in range(5):
    d.rounded_rectangle([90*S,y*S,990*S,(y+66)*S],radius=16*S,fill=CARD)
    d.ellipse([112*S,(y+15)*S,148*S,(y+51)*S],outline=GR,width=4*S)
    d.line([(121*S,(y+33)*S),(128*S,(y+41)*S),(141*S,(y+25)*S)],fill=GR,width=5*S)
    d.rounded_rectangle([175*S,(y+26)*S,(175+[520,430,600,380,480][k])*S,(y+40)*S],radius=7*S,fill=(44,52,64))
    y+=84
d.text((90*S,1150*S),"Count how many fit you →",font=f("Medium",36),fill=MU)
save(im,1)
signs=[("You start before you feel like it.","Motivation shows up after you begin, not before. You've stopped waiting for the mood."),
("You can sit with boredom.","A quiet minute doesn't send you straight to your phone. That's attention you own again."),
("You keep small promises to yourself.","Ten minutes of reading. One glass of water. Tiny, but kept. That's what self-trust is made of."),
("You don't quit after one bad day.","You slip, and you don't start over. One bad day is −5, not zero.")]
for i,(h,b) in enumerate(signs):
    im,d=slide(i+2)
    d.text((90*S,140*S),f"#{i+1}",font=f("Bold",120),fill=GR)
    y=330
    for ln in wrap(d,h,f("Bold",84),900): d.text((90*S,y*S),ln,font=f("Bold",84),fill=TX); y+=100
    y+=50
    for ln in wrap(d,b,f("Medium",46),900): d.text((90*S,y*S),ln,font=f("Medium",46),fill=MU); y+=64
    d.rounded_rectangle([90*S,1080*S,990*S,1150*S],radius=35*S,fill=CARD)
    d.rounded_rectangle([90*S,1080*S,(90+900*(i+1)/5)*S,1150*S],radius=35*S,fill=GR)
    d.text((540*S,1115*S),f"{i+1} of 5",font=f("Bold",34),fill=BG if i>=2 else TX,anchor="mm")
    save(im,i+2)
# 5 chart
im,d=slide(6)
d.text((90*S,140*S),"#5",font=f("Bold",120),fill=GR)
d.text((90*S,330*S),"You can see it.",font=f("Bold",84),fill=TX)
d.text((90*S,450*S),"You don't guess if you're improving.\nYou track it, and the line goes up.",font=f("Medium",46),fill=MU,spacing=18*S)
sc=[0]
for k in range(1,31): sc.append(sc[-1]+(-5 if k==13 else 1))
x0,x1,y0,y1=90,990,1150,690; mx=max(sc)
P=[((x0+(x1-x0)*(k-1)/29)*S,(y0-(y0-y1)*sc[k]/mx)*S) for k in range(1,31)]
for k in range(29): d.line([P[k],P[k+1]],fill=RD if k==11 else GR,width=7*S)
nx,ny=P[-1]; d.ellipse([nx-15*S,ny-15*S,nx+15*S,ny+15*S],fill=GO); d.text((nx-10*S,ny-60*S),"NEW HIGH",font=f("Bold",34),fill=GO,anchor="ra")
save(im,6)
# CTA
im,d=slide(7)
d.text((90*S,170*S),"How many",font=f("Bold",110),fill=TX)
d.text((90*S,295*S),"fit you?",font=f("Bold",110),fill=AC)
for j,t in enumerate(["Start before the mood","Sit with boredom","Keep small promises","Don't quit after one bad day","Track it"]):
    y=480+j*104
    d.rounded_rectangle([90*S,y*S,990*S,(y+84)*S],radius=18*S,fill=CARD)
    d.text((130*S,(y+42)*S),str(j+1),font=f("Bold",44),fill=GR,anchor="lm")
    d.text((195*S,(y+42)*S),t,font=f("Bold",40),fill=TX,anchor="lm")
d.text((90*S,1030*S),"Comment your number. Send this to a friend\nwho's harder on themselves than they should be.",font=f("Medium",36),fill=MU,spacing=12*S)
save(im,7)
