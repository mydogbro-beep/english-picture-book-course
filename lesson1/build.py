#!/usr/bin/env python3
"""Build Lesson 1 picture book single-file HTML with embedded images."""
import base64, io, os, sys

IMG_DIR = os.path.expanduser("~/workspace/english-book/lesson1/img")
OUT = os.path.expanduser("~/workspace/english-book/lesson1/hello-milo-l1.html")

FILES = {
    "cover": "media-generation-l1-cover-0-97139017-75da-4f90-9f8c-4b39dc7fe76c.webp",
    "morning": "media-generation-l1-p2-morning-0-4c2c5978-0b6a-4607-8197-c9ca8df6a2c0.webp",
    "meet": "media-generation-l1-p3-meet-0-c73ca4cb-69fa-4b5d-a9c6-8328a1de390a.webp",
    "name": "media-generation-l1-p4-name-0-2195a20b-968c-471f-ba46-627a20669905.webp",
    "apples": "media-generation-l1-p5-apples-0-3df20494-7fb9-4dae-bb70-dbda95e583ee.webp",
    "goodbye": "media-generation-l1-p6-goodbye-0-d10e2bd8-338d-4ef4-b0cf-74e18f69f0e1.webp",
}

def encode(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if im.width > 1280:
            im = im.resize((1280, int(im.height * 1280 / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        with open(path, "rb") as f:
            return "data:image/webp;base64," + base64.b64encode(f.read()).decode()

IMG = {k: encode(os.path.join(IMG_DIR, v)) for k, v in FILES.items()}
print({k: len(v) // 1024 for k, v in IMG.items()}, "KB each")

AUDIO_DIR = os.path.expanduser("~/workspace/english-book/lesson1/audio")
AUDIO_TEXT = {
    "s-hello-milo": "Hello, Milo!", "s-good-morning": "Good morning!", "s-hello": "Hello!",
    "s-whats-name": "What's your name?", "s-my-name": "My name is Milo.", "s-how-are-you": "How are you?",
    "s-im-fine": "I'm fine, thank you!", "s-goodbye": "Goodbye, Coco!", "s-see-you": "See you tomorrow!",
    "s-goodbye-excl": "Goodbye!",
    "w-morning": "morning", "w-hello": "hello", "w-name": "name", "w-friend": "friend", "w-fine": "fine",
    "w-apple": "apple", "w-cat": "cat", "w-dog": "dog", "w-sun": "sun", "w-goodbye": "goodbye",
    "g-hello-milo": "Hello! I am Milo!", "g-hello-coco": "Hello! I am Coco!",
}
import json as _json
AUDIO = {}
for slug, text in AUDIO_TEXT.items():
    with open(os.path.join(AUDIO_DIR, slug + ".mp3"), "rb") as f:
        AUDIO[text] = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()
AUDIO_JSON = _json.dumps(AUDIO, ensure_ascii=False)
print("audio clips:", len(AUDIO))

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Hello, Milo! · 第 1 课 打招呼</title>
<style>
  :root{ --paper:#f7efdd; --paper2:#fffaf0; --ink:#3d3125; --sage:#7d8c6f; --sage-d:#5c6b4f;
         --persim:#d97b4f; --gold:#c9973f; --card:#fffdf6; --line:#e4d5b8; }
  *{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{height:100%}
  body{ font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; background:#efe3c8;
        color:var(--ink); display:flex; flex-direction:column; align-items:center; min-height:100dvh; }
  header{ width:100%; max-width:880px; display:flex; align-items:center; gap:10px; padding:12px 18px 4px; }
  .badge{ background:var(--sage-d); color:#fff; font-weight:700; border-radius:9px; padding:5px 10px; font-size:14px; }
  header .crumb{ font-size:13px; color:#8a7a5c; }
  header .title{ font-size:15px; font-weight:700; }
  main{ width:100%; max-width:880px; flex:1; display:flex; flex-direction:column; padding:8px 14px 0; }
  .stage{ position:relative; background:var(--paper2); border:1px solid var(--line); border-radius:20px; overflow:hidden;
          box-shadow:0 12px 32px rgba(93,74,43,.16); }
  .stage img{ display:block; width:100%; aspect-ratio:4/3; object-fit:cover; background:#f3e9d2; }
  .spot{ position:absolute; z-index:3; border:none; background:transparent; cursor:pointer; border-radius:24px; padding:0; }
  .spot .ring{ position:absolute; inset:3%; border:3px dashed rgba(217,123,79,.9); border-radius:22px;
               box-shadow:0 0 0 2px rgba(255,255,255,.55), inset 0 0 0 2px rgba(255,255,255,.55);
               animation:spotpulse 1.8s ease-in-out infinite; pointer-events:none; }
  .spot.hit .ring{ display:none; }
  .spot.obj .ring{ border-color:rgba(92,107,79,.92); }
  .spot.talk{ animation:spotbounce .55s ease; }
  @keyframes spotpulse{ 0%,100%{ opacity:.3; transform:scale(.985);} 50%{ opacity:.9; transform:scale(1.008);} }
  @keyframes spotbounce{ 0%{ transform:scale(1);} 30%{ transform:scale(1.07) rotate(-1.2deg);} 60%{ transform:scale(.985);} 100%{ transform:scale(1);} }
  .spot-hint{ position:absolute; left:10px; top:10px; z-index:4; background:rgba(61,49,37,.74); color:#fff;
              font-size:13.5px; font-weight:700; padding:6px 12px; border-radius:999px; pointer-events:none; }
  .bubble{ position:absolute; z-index:5; top:12px; left:0; right:0; margin:0 auto; width:fit-content; max-width:82%;
           background:var(--card); border:2px solid var(--gold); border-radius:16px; padding:10px 16px;
           box-shadow:0 10px 24px rgba(93,74,43,.25); display:none; }
  .bubble.on{ display:block; animation:bubblepop .18s ease-out; }
  @keyframes bubblepop{ from{ transform:scale(.85); opacity:.4;} to{ transform:scale(1); opacity:1;} }
  .bubble .b-en{ font-family:Georgia,"Times New Roman",serif; font-size:22px; font-weight:700; line-height:1.25; }
  .bubble .b-zh{ font-size:13.5px; color:#97835f; margin-top:2px; }
  .panel{ padding:16px 20px 18px; background:var(--paper2); }
  .cover-title{ font-family:Georgia,"Times New Roman",serif; font-size:44px; font-weight:700; color:var(--ink); letter-spacing:.5px; }
  .cover-sub{ margin-top:6px; font-size:16px; color:#8a7a5c; }
  .narr{ font-size:15px; color:#8a7a5c; margin-bottom:10px; }
  .line-row{ display:flex; align-items:flex-start; gap:10px; margin:8px 0; }
  .who{ flex:none; margin-top:7px; font-size:12.5px; font-weight:700; color:#fff; border-radius:20px; padding:3px 10px; }
  .who.milo{ background:var(--persim); } .who.coco{ background:var(--sage); }
  .sent{ flex:1; text-align:left; background:var(--card); border:1.5px solid var(--line); border-radius:14px;
         padding:10px 14px; cursor:pointer; transition:border-color .15s, transform .1s; }
  .sent:active{ transform:scale(.985); } .sent:hover{ border-color:var(--gold); }
  .sent .en{ font-family:Georgia,"Times New Roman",serif; font-size:27px; font-weight:700; line-height:1.25; }
  .sent .zh{ font-size:14px; color:#97835f; margin-top:2px; }
  .sent .spk{ float:right; font-size:19px; color:var(--gold); }
  h2.sec{ font-size:21px; margin-bottom:4px; } .sec-sub{ font-size:14px; color:#97835f; margin-bottom:12px; }
  .words{ display:grid; grid-template-columns:repeat(auto-fill,minmax(118px,1fr)); gap:10px; }
  .word{ background:var(--card); border:1.5px solid var(--line); border-radius:14px; padding:12px 8px; text-align:center; cursor:pointer; }
  .word:active{ transform:scale(.97); } .word:hover{ border-color:var(--gold); }
  .word .w-en{ font-family:Georgia,serif; font-size:21px; font-weight:700; }
  .word .w-zh{ font-size:13px; color:#97835f; margin-top:3px; }
  .task{ background:var(--card); border:1.5px solid var(--line); border-radius:16px; padding:14px 16px; margin-bottom:14px; }
  .task h3{ font-size:16.5px; margin-bottom:8px; } .task p{ font-size:14px; color:#6d5c40; margin-bottom:10px; }
  .opts{ display:flex; flex-wrap:wrap; gap:9px; }
  .opt{ font-family:Georgia,serif; font-size:17.5px; font-weight:700; background:var(--paper2); border:1.5px solid var(--line);
        border-radius:12px; padding:9px 14px; cursor:pointer; }
  .opt.sel{ border-color:var(--persim); background:#fdf0e4; } .opt.right{ border-color:var(--sage-d); background:#edf2e4; }
  .opt.wrong{ border-color:#c0563f; background:#fbeae5; }
  .big-play{ font-size:16px; font-weight:700; background:var(--sage-d); color:#fff; border:none; border-radius:12px; padding:10px 18px; cursor:pointer; }
  .readrow{ display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px dashed var(--line); }
  .readrow:last-child{ border-bottom:none; }
  .readrow .sent{ padding:7px 12px; } .readrow .sent .en{ font-size:20px; }
  .check{ flex:none; width:30px; height:30px; border-radius:50%; border:2px solid var(--line); background:#fff; font-size:16px; cursor:pointer; color:transparent; }
  .check.done{ background:var(--sage-d); border-color:var(--sage-d); color:#fff; }
  .feedback{ font-size:14.5px; margin-top:9px; min-height:20px; color:var(--sage-d); font-weight:700; }
  .finish-badge{ display:inline-block; margin-top:10px; font-size:15px; font-weight:700; color:#fff; background:var(--gold);
                 border-radius:20px; padding:6px 16px; }
  .finish-badge.locked{ background:#cbbfa4; }
  .endnav{ display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin-top:24px; }
  .endbtn{ display:inline-block; text-decoration:none; font-weight:700; font-size:17px; border-radius:999px; padding:12px 24px; background:#fffdf7; color:#22303a; border:2px solid #d9c9a3; }
  .endbtn.go{ background:var(--gold); border-color:var(--gold); color:#fff; }

  nav{ width:100%; max-width:880px; display:flex; align-items:center; justify-content:space-between; padding:12px 18px 18px; }
  .navbtn{ font-size:16px; font-weight:700; border-radius:13px; padding:11px 20px; cursor:pointer; border:1.5px solid var(--line); background:var(--paper2); color:var(--ink); }
  .navbtn.primary{ background:var(--sage-d); border-color:var(--sage-d); color:#fff; }
  .navbtn:disabled{ opacity:.35; cursor:default; }
  .dots{ display:flex; gap:7px; } .dot{ width:9px; height:9px; border-radius:50%; background:#d8c9a6; cursor:pointer; }
  .dot.on{ background:var(--sage-d); transform:scale(1.25); }
  .pageno{ font-size:13px; color:#97835f; text-align:center; padding-bottom:10px; }
  .foot{ font-size:12px; color:#a08d64; text-align:center; padding:0 20px 16px; max-width:880px; }
  .page{ display:none; } .page.on{ display:block; }
  @media (max-width:560px){ .cover-title{font-size:34px} .sent .en{font-size:23px} }
</style>
</head>
<body>
<header>
  <div class="badge">1</div>
  <div>
    <div class="crumb">英文绘本课 · 第 1 课</div>
    <div class="title">Hello, Milo! 你好，米洛</div>
  </div>
</header>

<main>
  <!-- 0 COVER -->
  <section class="page" data-page>
    __STAGE_cover__
    <div class="panel">
      <div class="cover-title">Hello, Milo!</div>
      <div class="cover-sub">第 1 课 · 打招呼 — 一只小猫，交到了新朋友。</div>
      <div class="line-row"><div class="sent" data-say="Hello, Milo!"><span class="spk">🔊</span><div class="en">Hello, Milo!</div><div class="zh">你好，米洛！点句子可以听发音</div></div></div>
    </div>
  </section>

  <!-- 1 MORNING -->
  <section class="page" data-page>
    __STAGE_morning__
    <div class="panel">
      <div class="narr">早上，米洛醒来了，对着窗外的小鸟打招呼。</div>
      <div class="line-row"><div class="who milo">米洛</div><div class="sent" data-say="Good morning!"><span class="spk">🔊</span><div class="en">Good morning!</div><div class="zh">早上好！</div></div></div>
    </div>
  </section>

  <!-- 2 MEET -->
  <section class="page" data-page>
    __STAGE_meet__
    <div class="panel">
      <div class="narr">花园小路上，米洛遇见了一只小狗。米洛先开口啦。</div>
      <div class="line-row"><div class="who milo">米洛</div><div class="sent" data-say="Hello!"><span class="spk">🔊</span><div class="en">Hello!</div><div class="zh">你好！</div></div></div>
    </div>
  </section>

  <!-- 3 NAME -->
  <section class="page" data-page>
    __STAGE_name__
    <div class="panel">
      <div class="narr">小狗歪着头，好奇地问。</div>
      <div class="line-row"><div class="who coco">可可</div><div class="sent" data-say="What's your name?"><span class="spk">🔊</span><div class="en">What's your name?</div><div class="zh">你叫什么名字？</div></div></div>
      <div class="line-row"><div class="who milo">米洛</div><div class="sent" data-say="My name is Milo."><span class="spk">🔊</span><div class="en">My name is Milo.</div><div class="zh">我叫米洛。</div></div></div>
    </div>
  </section>

  <!-- 4 APPLES -->
  <section class="page" data-page>
    __STAGE_apples__
    <div class="panel">
      <div class="narr">苹果树下，两个新朋友一起分享红苹果。</div>
      <div class="line-row"><div class="who coco">可可</div><div class="sent" data-say="How are you?"><span class="spk">🔊</span><div class="en">How are you?</div><div class="zh">你好吗？</div></div></div>
      <div class="line-row"><div class="who milo">米洛</div><div class="sent" data-say="I'm fine, thank you!"><span class="spk">🔊</span><div class="en">I'm fine, thank you!</div><div class="zh">我很好，谢谢！</div></div></div>
    </div>
  </section>

  <!-- 5 GOODBYE -->
  <section class="page" data-page>
    __STAGE_goodbye__
    <div class="panel">
      <div class="narr">太阳下山了，该说再见啦。</div>
      <div class="line-row"><div class="who milo">米洛</div><div class="sent" data-say="Goodbye, Coco!"><span class="spk">🔊</span><div class="en">Goodbye, Coco!</div><div class="zh">再见，可可！</div></div></div>
      <div class="line-row"><div class="who coco">可可</div><div class="sent" data-say="See you tomorrow!"><span class="spk">🔊</span><div class="en">See you tomorrow!</div><div class="zh">明天见！</div></div></div>
    </div>
  </section>

  <!-- 6 WORDS -->
  <section class="page" data-page>
    <div class="panel" style="border:1px solid var(--line);border-radius:20px;">
      <h2 class="sec">今日小词卡</h2>
      <div class="sec-sub">点词卡，听一听这个词怎么读。</div>
      <div class="words" id="words"></div>
    </div>
  </section>

  <!-- 7 PRACTICE -->
  <section class="page" data-page>
    <div class="panel" style="border:1px solid var(--line);border-radius:20px;">
      <h2 class="sec">小练习</h2>
      <div class="sec-sub">三个小任务，做完这一课就通关啦。</div>

      <div class="task" id="taskA">
        <h3>① 听一听，选一选</h3>
        <p>点下面的按钮听句子，再选出你听到的那一句。</p>
        <button class="big-play" id="playA">🔊 播放句子</button>
        <div class="opts" style="margin-top:12px">
          <button class="opt" data-a="Good morning!">Good morning!</button>
          <button class="opt" data-a="What's your name?">What's your name?</button>
          <button class="opt" data-a="Goodbye, Coco!">Goodbye, Coco!</button>
        </div>
        <div class="feedback" id="fbA"></div>
      </div>

      <div class="task" id="taskB">
        <h3>② 问一问，答一答</h3>
        <p>先点一个问题，再点它的回答，配成一对。</p>
        <div class="opts" id="qB">
          <button class="opt" data-q="name" data-say="What's your name?">What's your name?</button>
          <button class="opt" data-q="how" data-say="How are you?">How are you?</button>
          <button class="opt" data-q="bye" data-say="Goodbye!">Goodbye!</button>
        </div>
        <div class="opts" id="aB" style="margin-top:9px">
          <button class="opt" data-a2="how" data-say="I'm fine, thank you!">I'm fine, thank you!</button>
          <button class="opt" data-a2="bye" data-say="See you tomorrow!">See you tomorrow!</button>
          <button class="opt" data-a2="name" data-say="My name is Milo.">My name is Milo.</button>
        </div>
        <div class="feedback" id="fbB"></div>
      </div>

      <div class="task" id="taskC">
        <h3>③ 跟我读</h3>
        <p>点句子听发音，自己大声读一遍，读完点右边的圆圈打勾。</p>
        <div id="readList"></div>
        <div class="feedback" id="fbC"></div>
      </div>
    </div>
  </section>

  <!-- 8 FINISH -->
  <section class="page" data-page>
    <div class="stage"><img src="__IMG_goodbye__" alt="米洛和可可挥手"></div>
    <div class="panel">
      <h2 class="sec">这一课，你学会了打招呼 🎉</h2>
      <div class="sec-sub">五句话，全都能点着听，再读一遍吧。</div>
      <div id="recap"></div>
      <div class="finish-badge locked" id="finishBadge">小练习还没做完哦</div>
      <div class="endnav"><a class="endbtn" href="index.html">🏠 回课程目录</a><a class="endbtn go" href="l2.html">下一课 →</a></div>
    </div>
  </section>
</main>

<nav>
  <button class="navbtn" id="prev">← 上一页</button>
  <div class="dots" id="dots"></div>
  <button class="navbtn primary" id="next">下一页 →</button>
</nav>
<div class="pageno" id="pageno"></div>
<div class="foot">英文绘本课 · 第 1 课《Hello, Milo!》｜插图为 AI 按水彩绘本风生成（风格库 FB-007 自然主义水彩动物绘本）｜发音为预生成的标准美式语音录音（Piper 合成），已放慢语速，不依赖设备朗读功能。</div>

<script>
const pages = [...document.querySelectorAll('[data-page]')];
let cur = 0;
const dotsBox = document.getElementById('dots');
pages.forEach((_, i) => { const d = document.createElement('div'); d.className = 'dot'; d.onclick = () => go(i); dotsBox.appendChild(d); });
function go(i){ cur = Math.max(0, Math.min(pages.length - 1, i));
  document.querySelectorAll('.bubble.on').forEach(b => b.classList.remove('on'));
  pages.forEach((p, j) => p.classList.toggle('on', j === cur));
  [...dotsBox.children].forEach((d, j) => d.classList.toggle('on', j === cur));
  document.getElementById('prev').disabled = cur === 0;
  document.getElementById('next').disabled = cur === pages.length - 1;
  document.getElementById('pageno').textContent = (cur + 1) + ' / ' + pages.length;
  window.scrollTo({ top: 0 }); }
document.getElementById('prev').onclick = () => go(cur - 1);
document.getElementById('next').onclick = () => go(cur + 1);

/* ---- speech: pre-generated clips first, device TTS as fallback ---- */
const AUDIO = __AUDIO_JSON__;
let player = null;
function speak(text){
  const src = AUDIO[text];
  if (src){
    try{
      if (!player) player = new Audio();
      player.pause(); player.src = src; player.currentTime = 0;
      const p = player.play(); if (p && p.catch) p.catch(() => ttsFallback(text));
      return;
    }catch(e){}
  }
  ttsFallback(text);
}
function ttsFallback(text){
  try{
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = 0.82;
    const v = speechSynthesis.getVoices().find(v => v.lang && v.lang.startsWith('en'));
    if (v) u.voice = v;
    speechSynthesis.speak(u);
  }catch(e){}
}
if ('speechSynthesis' in window) speechSynthesis.getVoices();
document.querySelectorAll('[data-say]').forEach(el => el.addEventListener('click', () => speak(el.dataset.say)));
document.querySelectorAll('.spot').forEach(sp => sp.addEventListener('click', () => {
  const stage = sp.closest('.stage'); if (!stage) return;
  const bubble = stage.querySelector('.bubble'); if (!bubble) return;
  bubble.querySelector('.b-en').textContent = sp.dataset.line;
  bubble.querySelector('.b-zh').textContent = sp.dataset.zh || '';
  bubble.classList.remove('on'); void bubble.offsetWidth; bubble.classList.add('on');
  sp.classList.add('hit', 'talk'); setTimeout(() => sp.classList.remove('talk'), 600);
  const hint = stage.querySelector('.spot-hint'); if (hint) hint.style.display = 'none';
  speak(sp.dataset.line);
}));

/* ---- words ---- */
const WORDS = [ ['morning','早上'],['hello','你好'],['name','名字'],['friend','朋友'],['fine','很好的'],
  ['apple','苹果'],['cat','猫'],['dog','小狗'],['sun','太阳'],['goodbye','再见'] ];
const wbox = document.getElementById('words');
WORDS.forEach(([en, zh]) => { const d = document.createElement('div'); d.className = 'word';
  d.innerHTML = '<div class="w-en">' + en + '</div><div class="w-zh">' + zh + ' 🔊</div>';
  d.onclick = () => speak(en); wbox.appendChild(d); });

/* ---- practice state ---- */
const state = { A:false, B:0, C:new Set() };
function refreshFinish(){
  const done = state.A && state.B >= 3 && state.C.size >= 5;
  const b = document.getElementById('finishBadge');
  b.textContent = done ? '🏅 第 1 课通关！' : '小练习还没做完哦';
  b.classList.toggle('locked', !done);
}

/* task A */
const targetA = "What's your name?";
document.getElementById('playA').onclick = () => speak(targetA);
document.querySelectorAll('#taskA .opt').forEach(o => o.onclick = () => {
  if (o.dataset.a === targetA){ o.classList.add('right'); state.A = true;
    document.getElementById('fbA').textContent = '对啦！这句是「你叫什么名字？」'; }
  else { o.classList.add('wrong'); setTimeout(() => o.classList.remove('wrong'), 700);
    document.getElementById('fbA').textContent = '再听一遍，仔细听第一个词。'; speak(targetA); }
  refreshFinish(); });

/* task B */
let selQ = null; const pairsDone = new Set();
document.querySelectorAll('#qB .opt').forEach(o => o.onclick = () => {
  if (pairsDone.has(o.dataset.q)) return;
  selQ = o; document.querySelectorAll('#qB .opt').forEach(x => x.classList.remove('sel')); o.classList.add('sel'); });
document.querySelectorAll('#aB .opt').forEach(o => o.onclick = () => {
  if (!selQ || pairsDone.has(o.dataset.a2)) return;
  if (o.dataset.a2 === selQ.dataset.q){ selQ.classList.add('right'); o.classList.add('right');
    pairsDone.add(selQ.dataset.q); state.B = pairsDone.size; selQ = null;
    document.getElementById('fbB').textContent = state.B >= 3 ? '三对全配上啦！' : '配对成功，还剩 ' + (3 - state.B) + ' 对。'; }
  else { o.classList.add('wrong'); setTimeout(() => o.classList.remove('wrong'), 700);
    document.getElementById('fbB').textContent = '这一对对不上，再想想。'; }
  refreshFinish(); });

/* task C + recap */
const KEY = [ ["Good morning!","早上好！"],["Hello!","你好！"],["What's your name?","你叫什么名字？"],
  ["My name is Milo.","我叫米洛。"],["How are you?","你好吗？"],["I'm fine, thank you!","我很好，谢谢！"],
  ["Goodbye, Coco!","再见，可可！"],["See you tomorrow!","明天见！"] ];
const rl = document.getElementById('readList');
KEY.slice(0, 5).forEach(([en, zh], i) => {
  const row = document.createElement('div'); row.className = 'readrow';
  row.innerHTML = '<div class="sent" data-say="' + en + '"><span class="spk">🔊</span><div class="en">' + en + '</div><div class="zh">' + zh + '</div></div>';
  const c = document.createElement('button'); c.className = 'check'; c.textContent = '✓';
  c.onclick = () => { if (state.C.has(i)){ state.C.delete(i); c.classList.remove('done'); }
    else { state.C.add(i); c.classList.add('done'); }
    document.getElementById('fbC').textContent = state.C.size >= 5 ? '五句都读过啦，跟读完成！' : '已读 ' + state.C.size + ' / 5 句。';
    refreshFinish(); };
  row.querySelector('[data-say]').addEventListener('click', () => speak(en));
  row.appendChild(c); rl.appendChild(row); });
const recap = document.getElementById('recap');
KEY.forEach(([en, zh]) => { const d = document.createElement('div'); d.className = 'line-row';
  d.innerHTML = '<div class="sent" data-say="' + en + '"><span class="spk">🔊</span><div class="en">' + en + '</div><div class="zh">' + zh + '</div></div>';
  d.querySelector('[data-say]').addEventListener('click', () => speak(en)); recap.appendChild(d); });

go(0); refreshFinish();
</script>
</body>
</html>
"""

# ---- interactive hotspots (2026-11-02 retrofit; same spec as build_lesson.py) ----
# box = fractions of the natural image, located per-image by visual grounding.
ALT = {
    "cover": "米洛在小屋窗边挥手", "morning": "米洛在床上伸懒腰", "meet": "米洛在花园小路上遇见可可",
    "name": "可可问米洛的名字", "apples": "米洛和可可在苹果树下分享苹果", "goodbye": "夕阳下米洛和可可在花园门口挥手道别",
}
SPOTS = {
    "cover": [
        {"kind": "obj", "who": "apple", "box": [0.140, 0.360, 0.215, 0.445], "say": "apple", "zh": "苹果"},
        {"kind": "obj", "who": "apple", "box": [0.156, 0.552, 0.231, 0.640], "say": "apple", "zh": "苹果"},
        {"who": "milo", "box": [0.688, 0.510, 0.850, 0.765], "say": "Hello! I am Milo!", "zh": "你好！我是米洛！"},
    ],
    "morning": [
        {"who": "milo", "box": [0.188, 0.322, 0.588, 0.744], "say": "Good morning!", "zh": "早上好！"},
    ],
    "meet": [
        {"who": "milo", "box": [0.125, 0.360, 0.463, 0.865], "say": "Hello!", "zh": "你好！"},
        {"who": "coco", "box": [0.524, 0.415, 0.831, 0.850], "say": "Hello! I am Coco!", "zh": "你好！我是可可！"},
    ],
    "name": [
        {"who": "coco", "box": [0.545, 0.318, 0.900, 0.932], "say": "What's your name?", "zh": "你叫什么名字？"},
        {"who": "milo", "box": [0.120, 0.093, 0.472, 0.922], "say": "My name is Milo.", "zh": "我叫米洛。"},
    ],
    "apples": [
        {"kind": "obj", "who": "apple", "box": [0.457, 0.140, 0.550, 0.258], "say": "apple", "zh": "苹果"},
        {"kind": "obj", "who": "apple", "box": [0.648, 0.094, 0.748, 0.211], "say": "apple", "zh": "苹果"},
        {"kind": "obj", "who": "apple", "box": [0.455, 0.624, 0.562, 0.767], "say": "apple", "zh": "苹果"},
        {"who": "milo", "box": [0.118, 0.272, 0.444, 0.863], "say": "I'm fine, thank you!", "zh": "我很好，谢谢！"},
        {"who": "coco", "box": [0.542, 0.285, 0.885, 0.860], "say": "How are you?", "zh": "你好吗？"},
    ],
    "goodbye": [
        {"who": "milo", "box": [0.117, 0.307, 0.459, 0.923], "say": "Goodbye, Coco!", "zh": "再见，可可！"},
        {"who": "coco", "box": [0.527, 0.347, 0.889, 0.921], "say": "See you tomorrow!", "zh": "明天见！"},
    ],
}

from PIL import Image as _PILImage
IMG_SIZE = {}
for _k, _fn in FILES.items():
    with _PILImage.open(os.path.join(IMG_DIR, _fn)) as _im:
        IMG_SIZE[_k] = _im.size

def _cover_map(box, iw, ih):
    """Map a bbox given as fractions of the natural image to fractions of the
    4/3 stage box, matching object-fit:cover centre-crop."""
    ca = 4.0 / 3.0
    ia = (iw / ih) if ih else ca
    x1, y1, x2, y2 = box
    if ia > ca:
        f = ca / ia; x0 = (1 - f) / 2.0
        dx1, dx2 = (x1 - x0) / f, (x2 - x0) / f
        dy1, dy2 = y1, y2
    elif ia < ca:
        f = ia / ca; y0 = (1 - f) / 2.0
        dx1, dx2 = x1, x2
        dy1, dy2 = (y1 - y0) / f, (y2 - y0) / f
    else:
        dx1, dy1, dx2, dy2 = x1, y1, x2, y2
    cl = lambda v: max(0.0, min(1.0, v))
    return cl(dx1), cl(dy1), cl(dx2), cl(dy2)

def stage_html(key):
    spots = SPOTS.get(key)
    img_tag = '<img src="%s" alt="%s">' % (IMG[key], ALT[key])
    if not spots:
        return '<div class="stage">%s</div>' % img_tag
    hint = '点一点图里的小动物和东西，听一听 👆' if any(sp.get("kind") == "obj" for sp in spots) else '点一点小动物，听它说话 👆'
    iw, ih = IMG_SIZE[key]
    parts = ['<div class="stage">%s' % img_tag,
             '<div class="spot-hint">%s</div>' % hint]
    for sp in spots:
        x1, y1, x2, y2 = _cover_map(sp["box"], iw, ih)
        parts.append(
            '<button class="spot%s" data-who="%s" data-line="%s" data-zh="%s" '
            'style="left:%.2f%%;top:%.2f%%;width:%.2f%%;height:%.2f%%"><span class="ring"></span></button>'
            % (' obj' if sp.get("kind") == "obj" else '', sp.get("who", ""), sp["say"].replace('"', '&quot;'),
               (sp.get("zh") or "").replace('"', '&quot;'),
               x1 * 100, y1 * 100, (x2 - x1) * 100, (y2 - y1) * 100))
    parts.append('<div class="bubble"><div class="b-en"></div><div class="b-zh"></div></div></div>')
    return "".join(parts)

for k in FILES:
    HTML = HTML.replace("__STAGE_%s__" % k, stage_html(k))
for k, v in IMG.items():
    HTML = HTML.replace("__IMG_%s__" % k, v)
HTML = HTML.replace("__AUDIO_JSON__", AUDIO_JSON)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print("WROTE", OUT, os.path.getsize(OUT) // 1024, "KB")
