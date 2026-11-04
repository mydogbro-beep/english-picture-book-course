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

  // cover: Ruby -> "What day is it today?" a01
  await showPage(0);
  let before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="ruby"]');
  await page.waitForTimeout(600);
  let lp = await lastPlayTail();
  console.log('SPOT_COVER_RUBY', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(1), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '01-cover-spot.png'), fullPage: true });

  // p3: English book obj -> "English" a18; Ruby -> "On Monday, we have English." a03
  await showPage(2);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="book"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('OBJ_P3_BOOK', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(18), playsDelta: lp && lp.count - before }));
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot[data-who="ruby"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('SPOT_P3_RUBY', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(3), playsDelta: lp && lp.count - before }));
  await page.screenshot({ path: path.join(shots, '02-p3-book.png'), fullPage: true });

  // p5: tambourine obj -> "music" a20
  await showPage(4);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('[data-page].on .spot.obj[data-who="tambourine"]');
  await page.waitForTimeout(600);
  lp = await lastPlayTail();
  console.log('OBJ_P5_TAMBOURINE', JSON.stringify({ bubble: await bubble(), audioMatch: lp && lp.tail === audioTail(20), playsDelta: lp && lp.count - before }));

  // taskB spot-check: right card Monday -> a11 once
  await showPage(7);
  before = await page.evaluate(() => window.__plays.length);
  await page.click('#aB .opt[data-a2="c-monday"]');
  await page.waitForTimeout(500);
  lp = await lastPlayTail();
  console.log('TASKB_SPOT', JSON.stringify({ match: lp && lp.tail === audioTail(11), onlyOnce: lp && (lp.count - before) === 1, readyState: lp && lp.readyState }));

  // complete all three tasks
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="What day is it today?"]');
  await page.waitForTimeout(200);
  for (const k of ['c-monday', 'c-music', 'c-friday']) {
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
  const nextBtn = await page.$('a[href="l19.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
