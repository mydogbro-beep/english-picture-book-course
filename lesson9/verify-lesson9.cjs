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
    proto.play = function () {
      window.__plays.push({ el: this });
      return origPlay.call(this);
    };
  });
  await page.goto(html, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  const shot = async (name, i) => {
    await page.evaluate(n => { document.querySelectorAll('[data-page]').forEach((p, j) => p.classList.toggle('on', j === n)); }, i);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(shots, name), fullPage: true });
  };
  await shot('01-cover.png', 0);
  await shot('02-story.png', 1);
  await shot('03-words.png', 6);
  await shot('04-practice.png', 7);
  // TaskB spot check: click right card "面包" (r-bread, say=bread) BEFORE pairing, verify it plays bread audio (a14) exactly once
  await page.evaluate(() => document.querySelectorAll('[data-page]').forEach((p, j) => p.classList.toggle('on', j === 7)));
  await page.waitForTimeout(200);
  const breadB64 = fs.readFileSync(path.join(dir, 'audio', 'a14.mp3')).toString('base64');
  const playsBefore = await page.evaluate(() => window.__plays.length);
  await page.click('#aB .opt[data-a2="r-bread"]');
  await page.waitForTimeout(800);
  const lastPlay = await page.evaluate(() => {
    const p = window.__plays[window.__plays.length - 1];
    if (!p) return null;
    return { srcTail: p.el.src.slice(-80), readyState: p.el.readyState, duration: p.el.duration, count: window.__plays.length };
  });
  const breadMatch = lastPlay && lastPlay.srcTail === breadB64.slice(-80);
  const onlyOnce = lastPlay && (lastPlay.count - playsBefore) === 1;
  console.log('TASKB_SPOT', JSON.stringify({ lastPlay, breadMatch, onlyOnce }));
  // TaskA
  await page.click('#playA');
  await page.waitForTimeout(300);
  await page.click('#taskA .opt[data-a="I want an apple."]');
  await page.waitForTimeout(200);
  // TaskB: pair all three
  for (const k of ['r-apple', 'r-milk', 'r-bread']) {
    await page.click(`#qB .opt[data-q="${k}"]`);
    await page.click(`#aB .opt[data-a2="${k}"]`);
    await page.waitForTimeout(150);
  }
  // TaskC
  const checks = await page.$$('#readList .check');
  for (const c of checks) await c.click();
  await page.waitForTimeout(300);
  // Audio playback check
  await page.evaluate(() => document.querySelectorAll('[data-page]').forEach((p, j) => p.classList.toggle('on', j === 1)));
  await page.waitForTimeout(200);
  await page.click('[data-page].on .sent[data-say="Hello! I am Benny."]');
  await page.waitForTimeout(1500);
  const audioState = await page.evaluate(() => {
    const p = window.__plays[window.__plays.length - 1];
    return p ? { readyState: p.el.readyState, duration: p.el.duration, plays: window.__plays.length } : null;
  });
  console.log('AUDIO_STATE', JSON.stringify(audioState));
  await page.evaluate(() => document.querySelectorAll('[data-page]').forEach((p, j) => p.classList.toggle('on', j === 8)));
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(shots, '05-finish.png'), fullPage: true });
  const badge = await page.textContent('#finishBadge');
  const homeBtn = await page.$('a[href="index.html"]');
  const nextBtn = await page.$('a[href="l10.html"]');
  console.log('BADGE', JSON.stringify(badge));
  console.log('EXIT_BTNS', JSON.stringify({ home: !!homeBtn, next: !!nextBtn }));
  console.log('ERRORS', JSON.stringify(errors));
  await browser.close();
})();
