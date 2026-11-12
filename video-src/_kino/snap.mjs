// Açar kadrlar: node snap.mjs <index.html> <çıxış-qovluq> [t1,t2,...]  → kNN.png (540×960, dsf 1) + montage üçün
import { createRequire } from 'module';
import { execSync } from 'child_process';
import fs from 'fs';
const req = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = req('playwright');
const [html, out, ts] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 1 });
p.on('pageerror', e => { console.error('PAGEERR', e.message); });
p.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
await p.goto('file://' + html + '#render');
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(800);
const dur = await p.evaluate(() => window.VIDEO.dur);
const T = ts ? ts.split(',').map(Number) : Array.from({ length: 16 }, (_, i) => +(0.3 + i * (dur - .6) / 15).toFixed(2));
const st = await p.$('#stage');
for (const [i, t] of T.entries()) { await p.evaluate(t => window.VIDEO.render(t), t); await st.screenshot({ path: `${out}/k${String(i).padStart(2, '0')}_${t}.png` }); }
await b.close();
console.log(T.join(','));
