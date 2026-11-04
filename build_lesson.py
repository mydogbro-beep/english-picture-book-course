#!/usr/bin/env python3
"""Generalized picture-book builder: reads <lesson_dir>/spec.json, emits single-file HTML.
Images: <lesson_dir>/img/*.webp|jpg|png (resized to 1280w JPEG q82, base64).
Audio:  <lesson_dir>/audio/aNN.mp3 in spec['audio_texts'] order (base64 mp3)."""
import base64, io, json, os, sys

def encode_img(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > 1280:
        im = im.resize((1280, int(im.height * 1280 / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def b64file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

CSS = """
  :root{ --paper:#f7efdd; --paper2:#fffaf0; --ink:#3d3125; --sage:#7d8c6f; --sage-d:#5c6b4f;
         --persim:#d97b4f; --gold:#c9973f; --card:#fffdf6; --line:#e4d5b8; --pip:#a5713d; }
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
  .who.milo{ background:var(--persim); } .who.coco{ background:var(--sage); } .who.pip{ background:var(--pip); } .who.benny{ background:#b07a3f; } .who.ruby{ background:#7aa7c7; } .who.felix{ background:#c65a2e; } .who.daisy{ background:#e9b949; }
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
"""

JS_TMPL = """
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

const WORDS = __WORDS_JSON__;
const wbox = document.getElementById('words');
WORDS.forEach(([en, zh]) => { const d = document.createElement('div'); d.className = 'word';
  d.innerHTML = '<div class="w-en">' + en + '</div><div class="w-zh">' + zh + ' 🔊</div>';
  d.onclick = () => speak(en); wbox.appendChild(d); });

const state = { A:false, B:0, C:new Set() };
const PAIRS_N = __PAIRS_N__;
function refreshFinish(){
  const done = state.A && state.B >= PAIRS_N && state.C.size >= 5;
  const b = document.getElementById('finishBadge');
  b.textContent = done ? '🏅 第 __NUM__ 课通关！' : '小练习还没做完哦';
  b.classList.toggle('locked', !done);
}

const targetA = __TARGET_A__;
document.getElementById('playA').onclick = () => speak(targetA);
document.querySelectorAll('#taskA .opt').forEach(o => o.onclick = () => {
  if (o.dataset.a === targetA){ o.classList.add('right'); state.A = true;
    document.getElementById('fbA').textContent = __RIGHT_A__; }
  else { o.classList.add('wrong'); setTimeout(() => o.classList.remove('wrong'), 700);
    document.getElementById('fbA').textContent = __WRONG_A__; speak(targetA); }
  refreshFinish(); });

let selQ = null; const pairsDone = new Set();
document.querySelectorAll('#qB .opt').forEach(o => o.onclick = () => {
  if (pairsDone.has(o.dataset.q)) return;
  selQ = o; document.querySelectorAll('#qB .opt').forEach(x => x.classList.remove('sel')); o.classList.add('sel'); });
document.querySelectorAll('#aB .opt').forEach(o => o.onclick = () => {
  if (!selQ || pairsDone.has(o.dataset.a2)) return;
  if (o.dataset.a2 === selQ.dataset.q){ selQ.classList.add('right'); o.classList.add('right');
    pairsDone.add(selQ.dataset.q); state.B = pairsDone.size; selQ = null;
    document.getElementById('fbB').textContent = state.B >= PAIRS_N ? __B_DONE__ : ('配对成功，还剩 ' + (PAIRS_N - state.B) + ' 对。'); }
  else { o.classList.add('wrong'); setTimeout(() => o.classList.remove('wrong'), 700);
    document.getElementById('fbB').textContent = '这一对对不上，再想想。'; }
  refreshFinish(); });

const KEY5 = __KEY5_JSON__;
const rl = document.getElementById('readList');
KEY5.forEach(([en, zh], i) => {
  const row = document.createElement('div'); row.className = 'readrow';
  row.innerHTML = '<div class="sent" data-say="' + en + '"><span class="spk">🔊</span><div class="en">' + en + '</div><div class="zh">' + zh + '</div></div>';
  const c = document.createElement('button'); c.className = 'check'; c.textContent = '✓';
  c.onclick = () => { if (state.C.has(i)){ state.C.delete(i); c.classList.remove('done'); }
    else { state.C.add(i); c.classList.add('done'); }
    document.getElementById('fbC').textContent = state.C.size >= 5 ? '五句都读过啦，跟读完成！' : '已读 ' + state.C.size + ' / 5 句。';
    refreshFinish(); };
  row.querySelector('[data-say]').addEventListener('click', () => speak(en));
  row.appendChild(c); rl.appendChild(row); });
const KEY = __KEY_JSON__;
const recap = document.getElementById('recap');
KEY.forEach(([en, zh]) => { const d = document.createElement('div'); d.className = 'line-row';
  d.innerHTML = '<div class="sent" data-say="' + en + '"><span class="spk">🔊</span><div class="en">' + en + '</div><div class="zh">' + zh + '</div></div>';
  d.querySelector('[data-say]').addEventListener('click', () => speak(en)); recap.appendChild(d); });

go(0); refreshFinish();
"""

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

def stage_html(img_src, spots, iw, ih):
    if not spots:
        return '<div class="stage"><img src="%s" alt=""></div>' % img_src
    hint = '点一点图里的小动物和东西，听一听 👆' if any(sp.get("kind") == "obj" for sp in spots) else '点一点小动物，听它说话 👆'
    parts = ['<div class="stage"><img src="%s" alt="">' % img_src,
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

def sent_row(line):
    who = line.get("who")
    chip = '<div class="who %s">%s</div>' % (who, line.get("who_name", "")) if who else ""
    return ('<div class="line-row">%s<div class="sent" data-say="%s"><span class="spk">🔊</span>'
            '<div class="en">%s</div><div class="zh">%s</div></div></div>'
            % (chip, line["en"].replace('"', '&quot;'), line["en"], line["zh"]))

def main():
    lesson_dir = os.path.abspath(sys.argv[1])
    spec = json.load(open(os.path.join(lesson_dir, "spec.json"), encoding="utf-8"))
    img = {}
    img_size = {}
    for name in os.listdir(os.path.join(lesson_dir, "img")):
        if name.rsplit(".", 1)[-1].lower() in ("webp", "jpg", "jpeg", "png"):
            p = os.path.join(lesson_dir, "img", name)
            from PIL import Image as _Im
            with _Im.open(p) as _im:
                img_size[name] = _im.size
            img[name] = encode_img(p)
    audio = {}
    for i, text in enumerate(spec["audio_texts"]):
        p = os.path.join(lesson_dir, "audio", "a%02d.mp3" % i)
        audio[text] = "data:audio/mpeg;base64," + b64file(p)

    pages_html = []
    cl = spec["cover_line"]
    _cw, _ch = img_size.get(spec["cover_img"], (4, 3))
    pages_html.append(
        '<section class="page" data-page>%s'
        '<div class="panel"><div class="cover-title">%s</div><div class="cover-sub">%s</div>%s</div></section>'
        % (stage_html(img[spec["cover_img"]], spec.get("cover_spots"), _cw, _ch),
           spec["title_en"], spec["cover_sub"], sent_row({"en": cl["en"], "zh": cl["zh"]})))
    for pg in spec["pages"]:
        lines = "".join(sent_row(l) for l in pg["lines"])
        narr = '<div class="narr">%s</div>' % pg["narr"] if pg.get("narr") else ""
        _pw, _ph = img_size.get(pg["img"], (4, 3))
        pages_html.append(
            '<section class="page" data-page>%s'
            '<div class="panel">%s%s</div></section>' % (stage_html(img[pg["img"]], pg.get("spots"), _pw, _ph), narr, lines))
    pages_html.append(
        '<section class="page" data-page><div class="panel" style="border:1px solid var(--line);border-radius:20px;">'
        '<h2 class="sec">今日小词卡</h2><div class="sec-sub">点词卡，听一听这个词怎么读。</div>'
        '<div class="words" id="words"></div></div></section>')
    tA, tB = spec["taskA"], spec["taskB"]
    optsA = "".join('<button class="opt" data-a="%s">%s</button>' % (o.replace('"', '&quot;'), o) for o in tA["options"])
    leftB = "".join('<button class="opt" data-q="%s" data-say="%s">%s</button>' % (o["k"], (o.get("say") or o["label"]).replace('"', '&quot;'), o["label"]) for o in tB["left"])
    rightB = "".join('<button class="opt" data-a2="%s" data-say="%s">%s</button>' % (o["k"], (o.get("say") or o["label"]).replace('"', '&quot;'), o["label"]) for o in tB["right"])
    pages_html.append(
        '<section class="page" data-page><div class="panel" style="border:1px solid var(--line);border-radius:20px;">'
        '<h2 class="sec">小练习</h2><div class="sec-sub">三个小任务，做完这一课就通关啦。</div>'
        '<div class="task" id="taskA"><h3>① 听一听，选一选</h3><p>点下面的按钮听句子，再选出你听到的那一句。</p>'
        '<button class="big-play" id="playA">🔊 播放句子</button><div class="opts" style="margin-top:12px">%s</div><div class="feedback" id="fbA"></div></div>'
        '<div class="task" id="taskB"><h3>② %s</h3><p>%s</p><div class="opts" id="qB">%s</div><div class="opts" id="aB" style="margin-top:9px">%s</div><div class="feedback" id="fbB"></div></div>'
        '<div class="task" id="taskC"><h3>③ 跟我读</h3><p>点句子听发音，自己大声读一遍，读完点右边的圆圈打勾。</p><div id="readList"></div><div class="feedback" id="fbC"></div></div>'
        '</div></section>' % (optsA, tB["title"], tB["instruction"], leftB, rightB))
    if spec["num"] < 32:
        nxt = '<a class="endbtn go" href="l%d.html">下一课 →</a>' % (spec["num"] + 1)
    else:
        nxt = '<a class="endbtn go" href="index.html">🏅 全部学完啦</a>'
    endnav = '<div class="endnav"><a class="endbtn" href="index.html">🏠 回课程目录</a>' + nxt + '</div>'
    pages_html.append(
        ('<section class="page" data-page><div class="stage"><img src="%s" alt=""></div>'
         '<div class="panel"><h2 class="sec">%s</h2><div class="sec-sub">核心句子，全都能点着听，再读一遍吧。</div>'
         '<div id="recap"></div><div class="finish-badge locked" id="finishBadge">小练习还没做完哦</div>'
         % (img[spec["pages"][-1]["img"]], spec["finish_title"]))
        + endnav + '</div></section>')

    js = (JS_TMPL
          .replace("__AUDIO_JSON__", json.dumps(audio, ensure_ascii=False))
          .replace("__WORDS_JSON__", json.dumps(spec["words"], ensure_ascii=False))
          .replace("__PAIRS_N__", str(len(tB["left"])))
          .replace("__TARGET_A__", json.dumps(tA["target"], ensure_ascii=False))
          .replace("__RIGHT_A__", json.dumps(tA["right_msg"], ensure_ascii=False))
          .replace("__WRONG_A__", json.dumps(tA["wrong_msg"], ensure_ascii=False))
          .replace("__B_DONE__", json.dumps(tB["done_msg"], ensure_ascii=False))
          .replace("__KEY5_JSON__", json.dumps(spec["taskC"], ensure_ascii=False))
          .replace("__KEY_JSON__", json.dumps(spec["key"], ensure_ascii=False))
          .replace("__NUM__", str(spec["num"])))

    html = ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, viewport-fit=cover\">\n"
            "<title>%s · 第 %d 课</title>\n<style>%s</style>\n</head>\n<body>\n"
            "<header><div class=\"badge\">%d</div><div><div class=\"crumb\">英文绘本课 · %s · 第 %d 课</div>"
            "<div class=\"title\">%s %s</div></div></header>\n<main>%s</main>\n"
            "<nav><button class=\"navbtn\" id=\"prev\">← 上一页</button><div class=\"dots\" id=\"dots\"></div>"
            "<button class=\"navbtn primary\" id=\"next\">下一页 →</button></nav>\n"
            "<div class=\"pageno\" id=\"pageno\"></div>\n"
            "<div class=\"foot\">英文绘本课 · 第 %d 课《%s》｜插图为 AI 按水彩绘本风生成（风格库 FB-007 自然主义水彩动物绘本）｜发音为预生成的标准美式语音录音（Piper 合成），已放慢语速。</div>\n"
            "<script>%s</script>\n</body>\n</html>"
            % (spec["title_en"], spec["num"], CSS, spec["num"], spec["chapter"], spec["num"],
               spec["title_en"], spec["title_zh"], "\n".join(pages_html), spec["num"], spec["title_en"], js))
    out = os.path.join(lesson_dir, "lesson.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("WROTE", out, os.path.getsize(out) // 1024, "KB")

if __name__ == "__main__":
    main()
