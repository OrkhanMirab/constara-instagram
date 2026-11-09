import sys, json, re
sp=sys.argv[1]; name=sys.argv[2]; cfg=json.load(open(sys.argv[3],encoding="utf-8"))
s=open(sp+"/v16/body.html",encoding="utf-8").read()
R=[('<span style="font-size:46px">QUITTING VAPING</span>','<span style="font-size:%dpx">%s</span>'%(cfg["fs"],cfg["title"])),
('<b>No vape</b>','<b>%s</b>'%cfg["row"]),
("""[['You', c(1, .12)], ['sleep', c(1, .2), 'or'], ['\\n'], ['through', c(1, .3)], ['it.', c(1, .45), 'grn']]""", cfg["n1"]),
(".title span { display: inline-block; font: 400 52px/1 \"Permanent Marker\", cursive; color: #FFFDF6; background: #1E9E5B;",
 ".title span { display: inline-block; font: 400 52px/1 \"Permanent Marker\", cursive; color: #FFFDF6; background: %s;"%cfg["bg"])]
for a,b in R:
    assert s.count(a)==1,a[:60]; s=s.replace(a,b)
import os; os.makedirs(sp+"/"+name,exist_ok=True)
open(sp+"/"+name+"/body.html","w",encoding="utf-8").write(s)
v=open(sp+"/v16/vo.py",encoding="utf-8").read()
v=re.sub(r"^L=.*$","L="+json.dumps(cfg["L"]),v,flags=re.M)
open(sp+"/"+name+"/vo.py","w",encoding="utf-8").write(v)
