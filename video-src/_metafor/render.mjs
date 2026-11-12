// Metafor render: node render.mjs <scratch> [snap t1,t2,...]
// <scratch>/index.html (window.draw(t), window.TL) → <scratch>/frames/f%05d.jpg  (və ya snap_*.png)
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
import path from 'path';

const dir = path.resolve(process.argv[2]);
const snap = process.argv[3] === 'snap' ? process.argv[4].split(',').map(Number) : null;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await p.goto('file://' + path.join(dir, 'index.html'));
await p.waitForFunction(() => window.READY === true);
await p.waitForTimeout(300);
const { fps, dur } = await p.evaluate(() => ({ fps: window.TL.fps, dur: window.TL.dur }));
if (snap) {
  for (const t of snap) {
    await p.evaluate(t => window.draw(t), t);
    await p.screenshot({ path: path.join(dir, `snap_${t.toFixed(2)}.png`) });
  }
} else {
  fs.mkdirSync(path.join(dir, 'frames'), { recursive: true });
  const n = Math.round(fps * dur);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.draw(t), i / fps);
    await p.screenshot({ path: path.join(dir, 'frames', `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 94 });
    if (i % 60 === 0) console.log(`${i}/${n}`);
  }
  console.log('Hazır');
}
await b.close();
