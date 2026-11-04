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

  // cover: Felix -> "When is your birthday?" a01; candle obj -> a18
  await showPage(0);
  let before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="felix"]');
  await page.waitForTimeout(600);
  let lp = await lastPlayTail();
  console.log('SPOT_COVER_FELIX', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(1), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '01-cover-spot.png'), fullPage: true });
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="candle"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('OBJ_COVER_CANDLE', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(18), playsDelta: lp && lp.count - before }));

  // p5: Felix -> "In May, I have a birthday cake." a07
  await showPage(4);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="felix"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('SPOT_P5_FELIX', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(7), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '02-p5-cake.png'), fullPage: true });

  // p6: present obj -> a20
  await showPage(5);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="present"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('OBJ_P6_PRESENT', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(20), playsDelta: lp && lp.count - before }));

  // taskB spot-check: right card candle -> a18 once
  await showPage(7);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('#aB .opt[data-a2="w-candle"]');
  await page.waitForTimeout(500);
  lp = await lastPlayTail();
  console.log('TASKB_SPOT', JSON.stringify({ match: lp && lp.tail === audioTail(18), onlyOnce: lp && (lp.count - before) === 1, readyState: lp && lp.readyState }));

  // complete all three tasks
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="When is your birthday?"]');
  await page.waitForTimeout(200);
  for (const k of ['w-birthday', 'w-may', 'w-candle']) {
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
  const nextBtn = await page.$('a[href="l24.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
