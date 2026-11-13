"""Canlı HTML önizləmə (istifadəçi 11-13: «önizləməni html video şəklində proqramın içində görmək istəyirəm»).

python3 onizleme.py <scratch> <out.html>
<scratch>/index.html (window.draw/TL) + <scratch>/audio.wav → tək fayl: şriftlər və mp3 base64, ▶ Play + zolaq.
SendUserFile(display='render') ilə göndər. MP4 render-i YALNIZ istifadəçi «render et» deyəndən sonra.
"""
import base64, subprocess, sys

scr, out = sys.argv[1], sys.argv[2]
b = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{scr}/audio.wav', '-ac', '2', '-b:a', '112k', f'{scr}/a.mp3'], check=True)
html = open(f'{scr}/index.html').read()
html = html.replace('url(file:///usr/share/fonts/opentype/inter/Inter-Bold.otf)', 'url(data:font/otf;base64,' + b('/usr/share/fonts/opentype/inter/Inter-Bold.otf') + ')')
html = html.replace('url(file:///usr/share/fonts/opentype/inter/Inter-Medium.otf)', 'url(data:font/otf;base64,' + b('/usr/share/fonts/opentype/inter/Inter-Medium.otf') + ')')
html = html.replace('url(file:///usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf)', 'url(data:font/ttf;base64,' + b('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf') + ')')
html = html.replace('html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}',
    'html,body{margin:0;background:#111;height:100%}body{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;font-family:sans-serif;color:#ddd}'
    'canvas{display:block;height:calc(100vh - 70px);width:auto;max-width:100vw;aspect-ratio:9/16;border-radius:8px}'
    '#bar{display:flex;gap:10px;align-items:center;width:min(92vw,560px)}#bar button{padding:8px 16px;border-radius:8px;border:0;background:#F7C04A;color:#111;font-weight:700;font-size:15px}#bar input{flex:1}#tm{font:13px monospace;min-width:48px}')
player = '''<div id="bar"><button id="pp">▶ Play</button><input id="sc" type="range" min="0" step="0.01" value="0"><span id="tm">0.0</span></div>
<audio id="au" src="data:audio/mpeg;base64,''' + b(f'{scr}/a.mp3') + '''"></audio>
<script>
(function(){const au=document.getElementById('au'),pp=document.getElementById('pp'),sc=document.getElementById('sc'),tm=document.getElementById('tm');
let start=null,off=0,playing=false;const D=window.TL.dur;sc.max=D;
function frame(){if(!playing)return;let t=off+(performance.now()-start)/1000;if(t>=D){t=D-0.001;playing=false;pp.textContent='↺ Replay';au.pause();off=0;}
 window.draw(t);sc.value=t;tm.textContent=t.toFixed(1);if(playing)requestAnimationFrame(frame);}
pp.onclick=()=>{if(playing){playing=false;off+=(performance.now()-start)/1000;au.pause();pp.textContent='▶ Play';return;}
 start=performance.now();playing=true;au.currentTime=off;au.play().catch(()=>{});pp.textContent='❚❚ Pause';requestAnimationFrame(frame);};
sc.oninput=()=>{off=+sc.value;window.draw(off);tm.textContent=off.toFixed(1);if(playing){start=performance.now();au.currentTime=off;}};
const go=()=>window.draw(0); if(window.READY)go(); else document.fonts.ready.then(()=>setTimeout(go,100));})();
</script>'''
html = html.replace('</body></html>', player + '</body></html>')
open(out, 'w').write(html)
print(out, len(html) // 1024, 'KB')
