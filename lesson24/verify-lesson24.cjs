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
  const bubble = () => page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return b ? { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent } : null;
  });
  console.log('SPOTS', JSON.stringify({ n: await page.evaluate(() => document.querySelectorAll('.spot').length) }));

  // cover: umbrella obj -> a11; Felix (lower body, below canopy) -> "It is rainy today." a02
  await showPage(0);
  let before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="umbrella"]');
  await page.waitForTimeout(600);
  let lp = await lastPlayTail();
  console.log('OBJ_COVER_UMBRELLA', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(11), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '01-cover-spot.png'), fullPage: true });
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="felix"]', { position: { x: 170, y: 330 } });
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('SPOT_COVER_FELIX', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(2), playsDelta: lp && lp.count - before }));

  // p3: worn coat obj -> a14
  await showPage(2);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="coat"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('OBJ_P3_COAT', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(14), playsDelta: lp && lp.count - before }));

  // p5: friend -> "Thank you, Felix!" a08 (spec who mislabeled felix; who_name is friend)
  await showPage(4);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="friend"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('SPOT_P5_FRIEND', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(8), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '02-p5-friend.png'), fullPage: true });

  // taskB spot-check: right card umbrella -> a11 once
  await showPage(7);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('#aB .opt[data-a2="w-umbrella"]');
  await page.waitForTimeout(500);
  lp = await lastPlayTail();
  console.log('TASKB_SPOT', JSON.stringify({ match: lp && lp.tail === audioTail(11), onlyOnce: lp && (lp.count - before) === 1, readyState: lp && lp.readyState }));

  // complete all three tasks
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="It is rainy today."]');
  await page.waitForTimeout(200);
  for (const k of ['w-umbrella', 'w-rainy', 'w-coat']) {
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
  const nextBtn = await page.$('a[href="l25.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
