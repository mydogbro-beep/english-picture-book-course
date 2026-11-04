const { chromium } = require('/home/hatch/workspace/tools/pw/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const shots = path.join(dir, 'shots');
  fs.mkdirSync(shots, { recursive: true });
  const html = 'file://' + path.join(dir, 'lesson.html');
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
  const audioTail = idx => fs.readFileSync(path.join(dir, 'audio', 'a' + String(idx).padStart(2, '0') + '.mp3')).toString('base64').slice(-80);

  // --- geometry: every spot inside its stage ---
  const geom = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.spot').forEach(sp => {
      const st = sp.closest('.stage').getBoundingClientRect();
      const r = sp.getBoundingClientRect();
      out.push({ who: sp.dataset.who, say: sp.dataset.say,
        inside: r.left >= st.left - 1 && r.top >= st.top - 1 && r.right <= st.right + 1 && r.bottom <= st.bottom + 1,
        w: Math.round(r.width), h: Math.round(r.height) });
    });
    return out;
  });
  console.log('SPOTS', JSON.stringify({ n: geom.length, allInside: geom.every(g => g.inside), minW: Math.min(...geom.map(g => g.w)), minH: Math.min(...geom.map(g => g.h)) }));

  // --- cover: tap Milo -> bubble "Let's count!" + a01 audio, exactly one play ---
  await showPage(0);
  let before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="milo"]');
  await page.waitForTimeout(600);
  let bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent };
  });
  let lp = await lastPlayTail();
  console.log('SPOT_COVER_MILO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(1), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '01-cover-spot.png'), fullPage: true });

  // --- story p2: tap Coco -> "How many apples?" + a03 ---
  await showPage(1);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="coco"]');
  await page.waitForTimeout(600);
  bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent };
  });
  lp = await lastPlayTail();
  console.log('SPOT_P2_COCO', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(3), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '02-story-spot.png'), fullPage: true });

  // --- story p5: tap Pip -> "Seven, eight, nine!" + a06; tap Coco (no line) -> greeting a24 ---
  await showPage(4);
  await page.click('[data-page].on .spot[data-who="pip"]');
  await page.waitForTimeout(600);
  bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { en: b.querySelector('.b-en').textContent };
  });
  lp = await lastPlayTail();
  console.log('SPOT_P5_PIP', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(6) }));
  await page.click('[data-page].on .spot[data-who="coco"]');
  await page.waitForTimeout(600);
  bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent };
  });
  lp = await lastPlayTail();
  console.log('SPOT_P5_COCO_GREET', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(24) }));

  // --- objects: cover apple -> "apple" a26; p2 basket -> "basket" a27 ---
  await showPage(0);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="apple"]');
  await page.waitForTimeout(600);
  bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent };
  });
  lp = await lastPlayTail();
  console.log('OBJ_COVER_APPLE', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(26), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '03-cover-apple.png'), fullPage: true });
  await showPage(1);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="basket"]');
  await page.waitForTimeout(600);
  bub = await page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent };
  });
  lp = await lastPlayTail();
  console.log('OBJ_P2_BASKET', JSON.stringify({ bubble: bub, audioMatch: lp && lp.tail === audioTail(27), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '04-p2-basket.png'), fullPage: true });

  // --- regression: taskB card spot-check (right "7" says seven = a19) ---
  await showPage(7);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('#aB .opt[data-a2="n7"]');
  await page.waitForTimeout(500);
  lp = await lastPlayTail();
  console.log('TASKB_SPOT', JSON.stringify({ sevenMatch: lp && lp.tail === audioTail(19), onlyOnce: lp && (lp.count - before) === 1, readyState: lp && lp.readyState }));

  // --- regression: complete all three tasks ---
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="How many apples?"]');
  await page.waitForTimeout(200);
  for (const k of ['n3', 'n7', 'n10']) {
    await page.click(`#qB .opt[data-q="${k}"]`);
    await page.click(`#aB .opt[data-a2="${k}"]`);
    await page.waitForTimeout(150);
  }
  const checks = await page.$$('#readList .check');
  for (const c of checks) await c.click();
  await page.waitForTimeout(300);
  await showPage(8);
  await page.screenshot({ path: path.join(shots, '05-finish.png'), fullPage: true });
  const badge = await page.textContent('#finishBadge');
  const homeBtn = await page.$('a[href="index.html"]');
  const nextBtn = await page.$('a[href="l3.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
