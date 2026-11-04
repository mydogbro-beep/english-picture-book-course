const { chromium } = require('/home/hatch/workspace/tools/pw/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');
(async () => {
  const dir = process.argv[2];
  const cfg = JSON.parse(fs.readFileSync(process.argv[3], 'utf-8'));
  const spec = JSON.parse(fs.readFileSync(path.join(dir, 'spec.json'), 'utf-8'));
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
  const lastPlay = () => page.evaluate(() => {
    const p = window.__plays[window.__plays.length - 1];
    return p ? { tail: p.el.src.slice(-80), count: window.__plays.length, readyState: p.el.readyState } : null;
  });
  const audioTail = text => {
    const idx = spec.audio_texts.indexOf(text);
    if (idx < 0) return null;
    return fs.readFileSync(path.join(dir, 'audio', 'a' + String(idx).padStart(2, '0') + '.mp3')).toString('base64').slice(-80);
  };
  const bubbleOf = () => page.evaluate(() => {
    const b = document.querySelector('[data-page].on .bubble');
    return b ? { on: b.classList.contains('on'), en: b.querySelector('.b-en').textContent, zh: b.querySelector('.b-zh').textContent } : null;
  });
  const spotCount = await page.evaluate(() => document.querySelectorAll('.spot').length);
  console.log('SPOT_COUNT', spotCount);
  async function checkSpot(pageIdx, selector, sayText, tag, shotName) {
    await showPage(pageIdx);
    const before = await page.evaluate(() => window.__plays.length);
    await page.click('[data-page].on ' + selector);
    await page.waitForTimeout(600);
    const bub = await bubbleOf();
    const lp = await lastPlay();
    const ok = bub && bub.on && bub.en === sayText && lp && lp.tail === audioTail(sayText) && (lp.count - before) === 1;
    console.log(tag, JSON.stringify({ ok, bubble: bub, audioMatch: lp && lp.tail === audioTail(sayText), playsDelta: lp && lp.count - before }));
    if (shotName) await page.screenshot({ path: path.join(shots, shotName), fullPage: true });
    return ok;
  }
  if (cfg.coverChar) await checkSpot(0, `.spot[data-who="${cfg.coverChar.who}"]:not(.obj)`, cfg.coverChar.say, 'COVER_CHAR', '01-cover-spot.png');
  if (cfg.coverObj) await checkSpot(0, `.spot.obj[data-who="${cfg.coverObj.who}"]`, cfg.coverObj.say, 'COVER_OBJ', '02-cover-obj.png');
  if (cfg.storyChar) await checkSpot(cfg.storyChar.page, `.spot[data-who="${cfg.storyChar.who}"]:not(.obj)`, cfg.storyChar.say, 'STORY_CHAR', '03-story-spot.png');
  if (cfg.storyObj) await checkSpot(cfg.storyObj.page, `.spot.obj[data-who="${cfg.storyObj.who}"]`, cfg.storyObj.say, 'STORY_OBJ', '04-story-obj.png');
  // taskB spot-check: first right option that has a say
  const rb = spec.taskB.right.find(x => x.say);
  await showPage(7);
  if (rb) {
    const before = await page.evaluate(() => window.__plays.length);
    await page.click(`#aB .opt[data-a2="${rb.k}"]`);
    await page.waitForTimeout(500);
    const lp = await lastPlay();
    console.log('TASKB_SPOT', JSON.stringify({ say: rb.say, match: lp && lp.tail === audioTail(rb.say), onlyOnce: lp && (lp.count - before) === 1, readyState: lp && lp.readyState }));
  }
  // complete all tasks
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click(`#taskA .opt[data-a="${spec.taskA.target}"]`);
  await page.waitForTimeout(200);
  for (const item of spec.taskB.left) {
    await page.click(`#qB .opt[data-q="${item.k}"]`);
    await page.click(`#aB .opt[data-a2="${item.k}"]`);
    await page.waitForTimeout(150);
  }
  const checks = await page.$$('#readList .check');
  for (const c of checks) await c.click();
  await page.waitForTimeout(300);
  await showPage(8);
  await page.screenshot({ path: path.join(shots, '05-finish.png'), fullPage: true });
  const badge = await page.textContent('#finishBadge');
  console.log('BADGE', JSON.stringify(badge), 'expectContains', '第 ' + spec.num + ' 课通关');
  const homeBtn = await page.$('a[href="index.html"]');
  const nextBtn = await page.$('a[href="l' + (spec.num + 1) + '.html"]');
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
