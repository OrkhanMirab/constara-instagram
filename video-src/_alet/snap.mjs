import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
p.on('pageerror', e => console.error('ERR', e.message));
await p.goto('file:///tmp/claude-0/-home-user/35a6392c-0707-5df1-b96a-2068eeba452f/scratchpad/vid/v16/index.html#render'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
console.log('fonts', await p.evaluate(() => [...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).join(',')));
for (const t of process.argv.slice(2).map(Number)) { await p.evaluate(t => window.VIDEO.render(t), t); await (await p.$('#stage')).screenshot({ path: `k_${String(t).padStart(5,'0')}.png` }); }
await b.close();
