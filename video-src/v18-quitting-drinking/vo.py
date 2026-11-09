import soundfile as sf, numpy as np, subprocess, base64, json
from kokoro_onnx import Kokoro
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
L=["Three signs you're actually quitting drinking.", "One. Friday night, and you wake up Saturday with no hangover.", "Two. The urge for just one drink hits. You let it pass.", "Three. You slip once, and you don't start over.", "Clean day, plus one. Slip, minus five.", "One slip can't erase thirty clean days.", "Which sign are you on?"]
gap=[.3,.3,.3,.35,.3,.35,0]
clips=[]
for t in L:
    s,sr=k.create(t,voice="am_michael",speed=0.95,lang="en-us"); i=np.where(np.abs(s)>0.01)[0]; clips.append(s[max(0,i[0]-200):i[-1]+600])
t=.15;C=[];D=[]
for i,s in enumerate(clips): C.append(round(t,2)); D.append(round(len(s)/sr,2)); t+=len(s)/sr+gap[i]
dur=round(t+1.5,2); buf=np.zeros(int(sr*(dur+.2)),dtype=np.float32)
for i,s in enumerate(clips): a=int(C[i]*sr); buf[a:a+len(s)]+=s
buf=buf/np.max(np.abs(buf))*.95; sf.write("vo.wav",buf,sr)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","vo.wav","-ac","1","-b:a","64k","vo.mp3"],check=True)
open("vo.b64","w").write(base64.b64encode(open("vo.mp3","rb").read()).decode())
json.dump({"C":C,"D":D,"dur":dur},open("cues.json","w")); print(C,D,dur)
