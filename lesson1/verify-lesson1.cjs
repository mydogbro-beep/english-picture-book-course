const { chromium } = require('/home/hatch/workspace/tools/pw/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const shots = path.join(dir, 'shots');
  fs.mkdirSync(shots, { recursive: true });
  const html = 'file://' + path.join(dir, 'hello-milo-l1.html');
  const errors = [];
  const browser = await chromium.launch({
    executablePath: '/home/hatch/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell',
    args: ['--autoplay-policy=no-user-gesture-required'],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.addInitScript(() => {
    window.__plays = [];
    const proto = window.HTMLAudioElement.prototype;
    const origPlay = proto.play;
    proto.play = function () { window.__plays.push({ el: this }); return origPlay.call(this); };
  });
  await page.goto(html, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  const showPage = async i => {
    await page.evaluate(n => { document.querySelectorAll('[data-page]').forEach((p, j) => p.classList.toggle('on', j === n)); }, i);
    await page.waitForTimeout(250);
  };
  const lastPlayTail = () => page.evaluate(() => {
    const p = window.__plays[window.__plays.length - 1];
    return p ? { tail: p.el.src.slice(-80), count: window.__plays.length, readyState: p.el.readyState } : null;
  });
  const slugTail = slug => fs.readFileSync(path.join(dir, 'audio', slug + '.mp3')).toString('base64').slice(-80);
  const playsNow = () => page.evaluate(() => window.__plays.length);
  const bubbleOf = () => page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return b ? { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent } : null;
  });

  // --- geometry per visible page: every spot inside its stage ---
  const geomAll = [];
  for (let i = 0; i <= 5; i++) {
    await showPage(i);
    const g = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('[data-page].on .spot').forEach(sp => {
        const st = sp.closest('.stage').getBoundingClientRect();
        const r = sp.getBoundingClientRect();
        out.push({ who: sp.dataset.who, line: sp.dataset.line,
          inside: r.left >= st.left - 1 && r.top >= st.top - 1 && r.right <= st.right + 1 && r.bottom <= st.bottom + 1,
          w: Math.round(r.width), h: Math.round(r.height),
          cx: Math.round(r.left + r.width / 2 - st.left), cy: Math.round(r.top + r.height / 2 - st.top),
          sw: Math.round(st.width), sh: Math.round(st.height) });
      });
      return out;
    });
    geomAll.push({ page: i, spots: g });
  }
  const flat = geomAll.flatMap(x => x.spots);
  console.log('SPOTS', JSON.stringify({ n: flat.length, allInside: flat.every(g => g.inside), minW: Math.min(...flat.map(g => g.w)), minH: Math.min(...flat.map(g => g.h)) }));
  console.log('GEOM', JSON.stringify(geomAll.map(x => ({ p: x.page, s: x.spots.map(s => [s.who, s.cx, s.cy, s.sw, s.sh]) }))));

  // --- cover: tap Milo -> greeting bubble + g-hello-milo audio, exactly one play ---
  await showPage(0);
  let before = await playsNow();
  await page.click('[data-page].on .spot[data-who="milo"]');
  await page.waitForTimeout(600);
  let bub = await bubbleOf();
  let lp = await lastPlayTail();
  console.log('SPOT_COVER_MILO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === slugTail('g-hello-milo'), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '05-cover-spot.png'), fullPage: true });

  // --- cover: tap an apple -> "apple" + w-apple audio, one play ---
  before = await playsNow();
  await page.click('[data-page].on .spot.obj[data-who="apple"] >> nth=0');
  await page.waitForTimeout(600);
  bub = await bubbleOf();
  lp = await lastPlayTail();
  console.log('OBJ_COVER_APPLE', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === slugTail('w-apple'), playsDelta: lp && lp.count - before }));

  // --- story meet (page 2): tap Coco -> greeting g-hello-coco; tap Milo -> "Hello!" s-hello ---
  await showPage(2);
  before = await playsNow();
  await page.click('[data-page].on .spot[data-who="coco"]');
  await page.waitForTimeout(600);
  bub = await bubbleOf();
  lp = await lastPlayTail();
  console.log('SPOT_MEET_COCO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === slugTail('g-hello-coco'), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '06-meet-spot.png'), fullPage: true });
  before = await playsNow();
  await page.click('[data-page].on .spot[data-who="milo"]');
  await page.waitForTimeout(600);
  bub = await bubbleOf();
  lp = await lastPlayTail();
  console.log('SPOT_MEET_MILO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === slugTail('s-hello'), playsDelta: lp && lp.count - before }));

  // --- story apples (page 4): tap Milo -> his line s-im-fine ---
  await showPage(4);
  before = await playsNow();
  await page.click('[data-page].on .spot[data-who="milo"]');
  await page.waitForTimeout(600);
  bub = await bubbleOf();
  lp = await lastPlayTail();
  console.log('SPOT_APPLES_MILO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === slugTail('s-im-fine'), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '07-apples-spot.png'), fullPage: true });

  // --- regression: complete all three tasks (page 7) ---
  await showPage(7);
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="What\'s your name?"]');
  await page.waitForTimeout(200);
  for (const k of ['name', 'how', 'bye']) {
    await page.click(`#qB .opt[data-q="${k}"]`);
    await page.click(`#aB .opt[data-a2="${k}"]`);
    await page.waitForTimeout(150);
  }
  const checks = await page.$$('#readList .check');
  for (const c of checks) await c.click();
  await page.waitForTimeout(300);
  await showPage(8);
  await page.screenshot({ path: path.join(shots, '08-finish.png'), fullPage: true });
  const badge = await page.textContent('#finishBadge');
  const homeBtn = await page.$('a[href="index.html"]');
  const nextBtn = await page.$('a[href="l2.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
