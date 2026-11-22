# -*- coding: utf-8 -*-
"""把题库 + 名词解释编成一个自包含的单页问卷。

    python build_site.py      ->  生成 index.html（双击即用，无外部依赖）

数据源单一：题库读 r18g_quiz.py，解释读 题材解释.py。
改任何一个，重跑本脚本即可刷新网页。
"""

import os
import sys
import json

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import r18g_quiz as q
from 题材解释 import EXPLAINS
import 作品推荐 as RECO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def build_data():
    topics = []
    for i, t in enumerate(q.TOPICS, 1):
        info = EXPLAINS.get(t["id"], {})
        topics.append({
            "n": i,
            "id": t["id"],
            "name": t["name"],
            "core": t["core"],
            "axes": t["axes"],
            "hooks": t["hooks"],
            "scene": t["scene"],
            "beat": t["beat"],
            "term": info.get("term", ""),
            "origin": info.get("origin", ""),
            "explain": info.get("explain", ""),
            "works": RECO.for_topic(t["id"]),
        })

    return {
        "axes": [{"k": k, "n": n, "d": d} for k, n, d in q.AXES],
        "hooks": [{"k": k, "n": v} for k, v in q.HOOKS.items()],
        "hookGroups": [{"g": g, "hooks": hs} for g, hs in q.HOOK_GROUPS.items()],
        "topics": topics,
        "taboos": [{"k": a, "n": b, "hooks": c} for a, b, c in q.TABOOS],
        "softTaboos": [{"k": a, "n": b, "axis": c} for a, b, c in q.SOFT_TABOOS],
        "orientations": [{"k": k, "n": n, "search": s} for k, n, s in q.ORIENTATIONS],
        "mediaOptions": q.MEDIA_OPTIONS,
        "mediaKeys": q.MEDIA_KEYS,
        "lengthOptions": q.LENGTH_OPTIONS,
        "lengthKeys": q.LENGTH_KEYS,
        "langOptions": q.LANG_OPTIONS,
        "hookTags": q.HOOK_TAGS,
        "defaultTaboo": "ORIENT_FEMDOM",
        "tagIndex": RECO.tag_index(),
        "tagAliases": RECO.aliases(),
        "recoBuckets": RECO.buckets(),
    }


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0a0d; --panel:#131119; --panel2:#1a1622; --line:#2b2633;
  --ink:#e9e3d9; --dim:#8e8699; --dim2:#625b70;
  --red:#b8432e; --red2:#d4553c; --gold:#c9a765;
}
html,body{background:var(--bg);color:var(--ink)}
body{
  font:15px/1.75 -apple-system,"Segoe UI","Microsoft YaHei",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
  padding:0 0 96px;
}
h1,h2,h3,.serif{font-family:"Songti SC","SimSun","Noto Serif SC",Georgia,serif;font-weight:400}
.wrap{max-width:900px;margin:0 auto;padding:0 22px}
a{color:var(--gold);text-decoration:none}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer}

/* ---------- 顶栏 ---------- */
.top{
  position:sticky;top:0;z-index:40;
  background:rgba(11,10,13,.94);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line);
}
.topin{max-width:900px;margin:0 auto;padding:12px 22px;display:flex;align-items:center;gap:16px}
.brand{font-size:13px;letter-spacing:.22em;color:var(--dim);white-space:nowrap}
.brand b{color:var(--ink);font-weight:400;letter-spacing:.14em}
.pbar{flex:1;height:2px;background:var(--line);position:relative;overflow:hidden}
.pbar i{position:absolute;inset:0 auto 0 0;width:0;background:var(--red2);transition:width .35s ease}
.tbtn{font-size:12px;color:var(--dim);border:1px solid var(--line);padding:5px 11px;border-radius:2px;white-space:nowrap}
.tbtn:hover{color:var(--ink);border-color:var(--dim2)}

/* ---------- 封面 ---------- */
.cover{padding:88px 0 0}
.kicker{font-size:11px;letter-spacing:.3em;color:var(--red2);margin-bottom:22px}
.cover h1{font-size:44px;line-height:1.28;letter-spacing:.04em;margin-bottom:20px}
.cover h1 em{font-style:normal;color:var(--gold)}
.cover .lead{color:var(--dim);max-width:600px;font-size:15px;line-height:1.95}
.meta{display:flex;gap:36px;margin:42px 0 0;flex-wrap:wrap}
.meta div{font-size:12px;color:var(--dim2);letter-spacing:.08em}
.meta b{display:block;font-size:26px;color:var(--ink);font-weight:400;font-family:"Songti SC",serif;margin-bottom:2px}
.startrow{margin-top:52px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.btn{
  display:inline-block;padding:13px 30px;border:1px solid var(--red);
  color:var(--ink);border-radius:2px;font-size:14px;letter-spacing:.1em;
  background:linear-gradient(180deg,#241417,#180f12);transition:.2s;
}
.btn:hover{border-color:var(--red2);background:#2a171b}
.btn[disabled]{opacity:.3;cursor:not-allowed;border-color:var(--line);background:var(--panel)}
.btn.ghost{border-color:var(--line);background:none;color:var(--dim)}
.btn.ghost:hover{color:var(--ink);border-color:var(--dim2)}
.note{font-size:12px;color:var(--dim2);line-height:1.9}

/* ---------- 题目 ---------- */
.step{padding-top:44px;animation:in .35s ease}
@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.stephead{display:flex;align-items:baseline;gap:14px;margin-bottom:6px}
.steptag{font-size:11px;letter-spacing:.24em;color:var(--red2)}
.stephead h2{font-size:26px;letter-spacing:.03em}
.stepdesc{color:var(--dim);font-size:13px;margin-bottom:34px;line-height:1.9}

.q{margin-bottom:40px}
.qh{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}
.qn{font-size:11px;color:var(--red2);font-family:ui-monospace,monospace;padding-top:3px}
.qt{font-size:16px;letter-spacing:.02em}
.qq{font-size:12px;color:var(--dim2);margin:2px 0 14px 30px}
.opts{display:flex;flex-direction:column;gap:7px;margin-left:30px}
.opts.grid2{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.hgroup{margin:0 0 16px 30px}
.gtitle{font-size:11px;letter-spacing:.24em;color:var(--red2);margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.hgroup .opt{padding:9px 12px}
.opt{
  display:flex;gap:12px;align-items:flex-start;padding:11px 14px;
  border:1px solid var(--line);background:var(--panel);border-radius:2px;
  transition:.14s;cursor:pointer;position:relative;
}
.opt:hover{border-color:var(--dim2);background:var(--panel2)}
.opt .idx{font:11px ui-monospace,monospace;color:var(--dim2);min-width:16px;padding-top:2px}
.opt .txt{flex:1;font-size:14px;line-height:1.6}
.opt .sub{display:block;font-size:11.5px;color:var(--dim2);margin-top:2px;line-height:1.6}
.opt .mark{
  width:14px;height:14px;border:1px solid var(--dim2);border-radius:50%;
  flex:0 0 auto;margin-top:5px;position:relative;
}
.opt.on{border-color:var(--red);background:#1e1316}
.opt.on .mark{border-color:var(--red2);background:var(--red2)}
.opt.on .mark::after{content:"";position:absolute;inset:3px;background:#160d0f;border-radius:50%}
.opt.on .idx{color:var(--red2)}
.counter{font-size:11.5px;color:var(--dim2);margin:9px 0 0 30px;letter-spacing:.04em}
.counter b{color:var(--gold);font-weight:400}
.counter.bad b{color:var(--red2)}

/* ---------- 步进 ---------- */
.nav{display:flex;gap:12px;align-items:center;margin-top:16px;padding-top:26px;border-top:1px solid var(--line)}
.nav .hint{font-size:12px;color:var(--dim2);flex:1}
.nav .hint.bad{color:var(--red2)}

/* ---------- 结果 ---------- */
.res{padding-top:38px}
.res h2{font-size:30px;margin-bottom:8px;letter-spacing:.02em}
.res .sub{color:var(--dim);font-size:13px;margin-bottom:34px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:2px;padding:20px 22px;margin-bottom:14px}
.coords{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.coords div{background:var(--panel);padding:14px 16px}
.coords dt{font-size:11px;color:var(--dim2);letter-spacing:.14em;margin-bottom:4px}
.coords dd{font-size:13.5px;line-height:1.7}
.rank{display:flex;flex-direction:column;gap:1px;background:var(--line);border:1px solid var(--line)}
.row{background:var(--panel);padding:15px 18px;transition:.15s}
.row:hover{background:var(--panel2)}
.rowhead{display:flex;align-items:baseline;gap:12px;cursor:pointer}
.rk{font:11px ui-monospace,monospace;color:var(--dim2);min-width:18px}
.rname{font-size:16px;letter-spacing:.02em;flex:0 0 auto}
.rterm{font-size:11.5px;color:var(--dim2);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rscore{font:11px ui-monospace,monospace;color:var(--gold);min-width:42px;text-align:right}
.rbar{height:2px;background:var(--line);margin:9px 0 0 30px;position:relative}
.rbar i{position:absolute;inset:0 auto 0 0;background:linear-gradient(90deg,var(--red),var(--gold));width:0;transition:width .6s ease}
.rcore{font-size:13px;color:var(--dim);margin:10px 0 0 30px;line-height:1.75}
.rwhy{font-size:11.5px;color:var(--dim2);margin:6px 0 0 30px}
.exp{display:none;margin:16px 0 0 30px;padding:16px 18px;background:#0e0c11;border-left:2px solid var(--red)}
.exp.open{display:block}
.exp .lab{font-size:10.5px;letter-spacing:.2em;color:var(--red2);margin-bottom:5px}
.exp .val{font-size:13px;color:var(--dim);line-height:1.9;margin-bottom:14px}
.exp .val:last-child{margin-bottom:0}
.exp .val.txt{color:var(--ink);font-size:13.5px}
.works{display:flex;flex-direction:column;gap:10px}
.work{padding:10px 12px;background:#121016;border-left:2px solid var(--line)}
.work .wt{font-size:13.5px;color:var(--ink);margin-bottom:2px}
.work .wt a{color:var(--gold)}
.work .wot{font-size:11.5px;color:var(--dim2);margin-left:4px}
.work .wm{font-size:11px;color:var(--dim2);letter-spacing:.04em}
.work .wn{font-size:12.5px;color:var(--dim);line-height:1.75;margin-top:3px}
.aworksToggle{font-size:11.5px;letter-spacing:.12em;color:var(--red2);cursor:pointer;user-select:none;padding:10px 0 2px;margin-top:8px;border-top:1px solid var(--line)}
.aworksToggle:hover{color:var(--gold)}
.aworksToggle .caret{font-size:10px;display:inline-block;margin-right:4px;transition:transform .2s ease}
.aworksToggle.collapsed .caret{transform:rotate(-90deg)}
.aitem-works{display:none;flex-direction:column;gap:8px;margin-top:8px}
.aitem-works.open{display:flex}
.pick{border:1px solid var(--red);background:linear-gradient(180deg,#1d1216,#141015)}
.pick .lab2{font-size:10.5px;letter-spacing:.26em;color:var(--red2);margin-bottom:12px}
.pick h3{font-size:24px;margin-bottom:6px}
.pick .core{color:var(--ink);font-size:14.5px;line-height:1.85;margin-bottom:20px}
.tbl{display:grid;grid-template-columns:88px 1fr;gap:2px 16px;font-size:13px}
.tbl dt{color:var(--dim2);font-size:11.5px;letter-spacing:.1em;padding-top:3px}
.tbl dd{color:var(--ink);line-height:1.8}
.todo{margin-top:20px;padding-top:16px;border-top:1px dashed var(--line)}
.todo li{list-style:none;font-size:12.5px;color:var(--dim);padding:5px 0 5px 22px;position:relative}
.todo li::before{content:"□";position:absolute;left:0;color:var(--dim2)}
.vetoed{font-size:12.5px;color:var(--dim2);line-height:2}
.vetoed b{color:var(--dim);font-weight:400}

/* ---- 阅读推荐结果页：作品清单 ---- */
.mediaSec{margin-bottom:34px}
.mediaHead{
  width:100%;display:flex;align-items:center;gap:9px;
  padding:0 0 10px;border-bottom:1px solid var(--line);
  cursor:pointer;user-select:none;text-align:left;
}
.mediaHead .caret{font-size:10px;color:var(--dim2);display:inline-block;transition:transform .2s ease}
.mediaSec.folded .mediaHead .caret{transform:rotate(-90deg)}
.mediaHead .mtName{font-size:17px;color:var(--ink);font-weight:400}
.mediaHead:hover .mtName{color:var(--gold)}
.mediaHead .mtCount{font-size:12px;color:var(--gold);margin-left:2px}
.mediaBody{margin-top:14px}
.mediaSec.folded .mediaBody{display:none}
.workCard{background:var(--panel);border:1px solid var(--line);border-radius:2px;padding:14px 18px;margin-bottom:10px}
.workCard .wt{font-size:14px;color:var(--ink);margin-bottom:3px}
.workCard .wt a{color:var(--gold);text-decoration:none}
.workCard .wt a:hover{text-decoration:underline}
.workCard .wm{font-size:11px;color:var(--dim2);letter-spacing:.04em}
.workCard .whit{font-size:11px;color:var(--red2);margin-top:6px;letter-spacing:.06em}
.workCard .wn{font-size:12.5px;color:var(--dim);line-height:1.75;margin-top:5px}
.workCard .wsearch{font-size:11px;color:var(--dim2);margin-top:6px;font-family:monospace;word-break:break-all}
.searchline{font-size:12.5px;color:var(--dim);line-height:2.2}
.searchline code{color:var(--gold);font-size:12px;word-break:break-all}
input{width:100%;background:var(--panel);border:1px solid var(--line);border-radius:2px;color:var(--ink);padding:11px 13px;font-size:13px;font-family:inherit;margin:6px 0 2px;outline:none}
input:focus{border-color:var(--gold)}
input::placeholder{color:var(--dim2)}

.acts{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}

/* ---------- 截图按钮反馈 ---------- */
#btnShot.busy{opacity:.55;pointer-events:none}

/* ---------- 全谱 ---------- */
.atlas{padding-top:38px}
.atlas input{
  width:100%;background:var(--panel);border:1px solid var(--line);color:var(--ink);
  padding:11px 14px;border-radius:2px;font:inherit;font-size:14px;outline:none;margin-bottom:20px;
}
.atlas input:focus{border-color:var(--dim2)}
.aitem{background:var(--panel);border:1px solid var(--line);padding:16px 18px;margin-bottom:8px}
.aitem h4{font-size:15px;font-weight:400;margin-bottom:3px}
.aitem .term{font-size:11.5px;color:var(--gold);margin-bottom:10px;letter-spacing:.03em}
.aitem .ex{font-size:13px;color:var(--dim);line-height:1.9}
.aitem .ax{font-size:11px;color:var(--dim2);margin-top:9px;font-family:ui-monospace,monospace}
.hide{display:none!important}

@media(max-width:680px){
  .cover h1{font-size:32px}
  .opts.grid2{grid-template-columns:1fr}
  .rname{font-size:15px}
}
@media print{
  .top,.nav,.acts{display:none}
  body{background:#fff;color:#000}
}
"""


JS = r"""
window.onerror = function (m, u, l) { console.error("[err]", m, "@", l); return false; };
const D = __DATA__;
const $ = s => document.querySelector(s);
const el = (t, c, h) => { const e = document.createElement(t); if(c) e.className = c; if(h!=null) e.innerHTML = h; return e; };

const S = {
  step: 0,
  main: [], soft: [], hooks: [], softTaboos: [],
  media: [], length: null, language: null,
  taboos: [D.defaultTaboo]
};

const AX = {}; D.axes.forEach(a => AX[a.k] = a.n);
const HK = {}; D.hooks.forEach(h => HK[h.k] = h.n);
const TX = {}; D.topics.forEach(t => TX[t.id] = t);

/* ---------------- 渲染 ---------------- */

function optRow(i, title, sub, on, onClick, single) {
  const d = el("div", "opt" + (on ? " on" : ""));
  d.dataset.i = String(i);
  d.appendChild(el("span", "idx", String(i).padStart(2, "0")));
  const txt = el("span", "txt", title + (sub ? `<span class="sub">${sub}</span>` : ""));
  d.appendChild(txt);
  d.appendChild(el("span", "mark"));
  d.onclick = onClick;
  return d;
}

function counter(id, cur, min, max) {
  return el("div", "counter", `已选 <b>${cur}</b>` + (max ? ` / 上限 ${max}` : "") + (min ? `　需 ${min}` : ""));
}

function qBlock(n, title, hint) {
  const box = el("div", "q");
  box.dataset.q = String(n);
  box.appendChild(el("div", "qh", `<span class="qn">${n}</span><span class="qt">${title}</span>`));
  if (hint) box.appendChild(el("div", "qq", hint));
  return box;
}

function renderStep() {
  const app = $("#app");
  app.innerHTML = "";

  if (S.step === 0) return cover(app);
  if (S.step === 4) return result(app);

  const head = el("div", "stephead");
  head.appendChild(el("span", "steptag", ["", "第一轮 / 三", "第二轮 / 三", "第三轮 / 三"][S.step]));
  head.appendChild(el("h2", "", ["", "你被什么击中", "划掉不吃的东西", "怎么读"][S.step]));
  app.appendChild(head);
  app.appendChild(el("div", "stepdesc", [
    "",
    "先说你在哪几处被击中。选两根最狠的，再挑几个具体画面，剩下的交给程序去算。",
    "把不能碰的先划掉。硬禁区一踩就整类作废，软偏好只让它往后排。",
    "最后定怎么取用：翻哪几类、多大块、什么语言。"
  ][S.step]));

  if (S.step === 1) step1(app);
  if (S.step === 2) step2(app);
  if (S.step === 3) step3(app);

  app.appendChild(navBar());
}

function cover(app) {
  const c = el("div", "step cover");
  c.innerHTML = `
    <div class="kicker">R18G 阅读推荐</div>
    <h1 class="serif">先量出你的<em>坐标</em>，<br>再找作品。</h1>
    <p class="lead">
      直接问「你喜欢哪个题材」，答出来的多半不是真的。人会挑自己觉得拿得出手的那些，
      把真正让自己坐不住的藏起来。所以这里换个问法：你在哪几处被击中，哪些碰都不能碰。
      十道题，三轮。答完以后，按坐标重排题材，并给出漫画 / 小说 / 电影三类作品清单。
    </p>
    <div class="meta">
      <div><b>${D.topics.length}</b>题材</div>
      <div><b>${D.hooks.length}</b>钩子</div>
      <div><b>${D.axes.length}</b>轴</div>
      <div><b>10</b>题 / 约 2 分钟</div>
    </div>
    <div class="startrow">
      <button class="btn" id="btnStart">开始</button>
      <button class="btn ghost" id="btnAtlas">先看全部题材与解释</button>
    </div>
    <p class="note" style="margin-top:26px">
      全部内容留在本机浏览器里，不上传、不保存。关掉页面即清空。<br>
      作品清单按标签匹配，力求方向大致对味，不保证逐条精准。女性向作品默认排除，可在禁区题取消。
    </p>`;
  app.appendChild(c);
  document.getElementById("btnStart").addEventListener("click", () => go(1));
  document.getElementById("btnAtlas").addEventListener("click", () => go("atlas"));
}

function step1(app) {
  // Q1 主轴
  const q1 = qBlock("01", "七根轴里，选 <b>2</b> 根最狠的", "选两根，不要多。多选会让排序失效。");
  const o1 = el("div", "opts");
  D.axes.forEach((a, i) => {
    o1.appendChild(optRow(i + 1, a.n, a.d, S.main.includes(a.k), () => {
      const k = a.k, at = S.main.indexOf(k);
      if (at >= 0) S.main.splice(at, 1);
      else { if (S.main.length >= 2) S.main.shift(); S.main.push(k); }
      renderStep();
    }));
  });
  q1.appendChild(o1);
  q1.appendChild(counter("c1", S.main.length, 2, 2));
  app.appendChild(q1);

  // Q2 副轴
  const left = D.axes.filter(a => !S.main.includes(a.k));
  const q2 = qBlock("02", "还有哪些你也吃得下（最多 <b>3</b> 根，可空）", "副轴按 1.5 倍计权，不选也行。");
  const o2 = el("div", "opts");
  left.forEach((a, i) => {
    o2.appendChild(optRow(i + 1, a.n, a.d, S.soft.includes(a.k), () => {
      const k = a.k, at = S.soft.indexOf(k);
      if (at >= 0) S.soft.splice(at, 1);
      else { if (S.soft.length >= 3) S.soft.shift(); S.soft.push(k); }
      renderStep();
    }));
  });
  q2.appendChild(o2);
  q2.appendChild(counter("c2", S.soft.length, 0, 3));
  app.appendChild(q2);

  // Q3 钩子（按组分栏）
  const q3 = qBlock("03", "下面这些具体的画面，哪几样会让你坐直（<b>2 到 5 个</b>）",
    "钩子是最小单位的画面元件。选具体的，不选听起来高级的。");
  D.hookGroups.forEach(grp => {
    const g = el("div", "hgroup");
    g.appendChild(el("div", "gtitle", grp.g));
    const o = el("div", "opts grid2");
    grp.hooks.forEach(hk => {
      const h = D.hooks.find(x => x.k === hk);
      if (!h) return;
      const row = el("div", "opt" + (S.hooks.includes(hk) ? " on" : ""));
      row.appendChild(el("span", "mark"));
      row.appendChild(el("span", "txt", h.n));
      row.onclick = () => {
        const at = S.hooks.indexOf(hk);
        if (at >= 0) S.hooks.splice(at, 1);
        else { if (S.hooks.length >= 5) S.hooks.shift(); S.hooks.push(hk); }
        renderStep();
      };
      o.appendChild(row);
    });
    g.appendChild(o);
    q3.appendChild(g);
  });
  q3.appendChild(counter("c3", S.hooks.length, 2, 5));
  app.appendChild(q3);
}

function step2(app) {
  const q4 = qBlock("04", "硬禁区 —— 踩中就整类作废（可多选，可空）",
    "女性向作品已默认排除。这条权重是偏好项的三倍半；想看女性向，点掉它即可。");
  const o4 = el("div", "opts grid2");
  D.taboos.forEach((t, i) => {
    o4.appendChild(optRow(i + 1, t.n, null, S.taboos.includes(t.k), () => {
      const at = S.taboos.indexOf(t.k);
      if (at >= 0) S.taboos.splice(at, 1); else S.taboos.push(t.k);
      renderStep();
    }));
  });
  q4.appendChild(o4);
  app.appendChild(q4);

  const q5 = qBlock("05", "软偏好 —— 不吃但不必废掉整个题材（可多选，可空）",
    "软偏好不否决，只把对应的那根轴压到 45% / 20%。");
  const o5 = el("div", "opts grid2");
  D.softTaboos.forEach((t, i) => {
    o5.appendChild(optRow(i + 1, t.n, "压：" + AX[t.axis], S.softTaboos.includes(t.k), () => {
      const at = S.softTaboos.indexOf(t.k);
      if (at >= 0) S.softTaboos.splice(at, 1); else S.softTaboos.push(t.k);
      renderStep();
    }));
  });
  q5.appendChild(o5);
  app.appendChild(q5);
}

function singleQ(app, no, title, hint, list, key) {
  const b = qBlock(no, title, hint);
  const o = el("div", "opts");
  list.forEach((v, i) => o.appendChild(optRow(i + 1, v, null, S[key] === i, () => { S[key] = i; renderStep(); })));
  b.appendChild(o);
  app.appendChild(b);
}

function step3(app) {
  // Q6 载体（多选）
  const q6 = qBlock("06", "今晚翻哪几类（<b>可多选，至少 1</b>）", "决定结果页展示哪几类清单。");
  const o6 = el("div", "opts");
  D.mediaOptions.forEach((v, i) => {
    const k = D.mediaKeys[i];
    o6.appendChild(optRow(i + 1, v, null, S.media.includes(k), () => {
      const at = S.media.indexOf(k);
      if (at >= 0) S.media.splice(at, 1); else S.media.push(k);
      renderStep();
    }));
  });
  q6.appendChild(o6);
  app.appendChild(q6);

  // Q7 篇幅 / Q8 语言（单选）
  function singleKey(no, title, list, key) {
    const b = qBlock(no, title, null);
    const o = el("div", "opts");
    list.forEach((v, i) => o.appendChild(optRow(i + 1, v, null, S[key] === i, () => { S[key] = i; renderStep(); })));
    b.appendChild(o);
    app.appendChild(b);
  }
  singleKey("07", "想看多大一块", D.lengthOptions, "length");
  singleKey("08", "语言范围", D.langOptions, "language");

}

function navBar() {
  const n = el("div", "nav");
  const ok = canNext();
  const hint = el("div", "hint" + (ok ? "" : " bad"), needText());
  n.appendChild(hint);
  if (S.step > 1) {
    const b = el("button", "btn ghost", "上一步");
    b.onclick = () => go(S.step - 1);
    n.appendChild(b);
  }
  const nx = el("button", "btn", S.step === 3 ? "出结果" : "下一步");
  nx.disabled = !ok;
  nx.onclick = () => { if (ok) go(S.step === 3 ? 4 : S.step + 1); };
  n.appendChild(nx);
  return n;
}

function canNext() {
  if (S.step === 1) return S.main.length === 2 && S.hooks.length >= 2;
  if (S.step === 2) return true;
  if (S.step === 3) return S.media.length >= 1 && S.length !== null && S.language !== null;
  return true;
}

function needText() {
  if (S.step === 1) {
    const a = [];
    if (S.main.length !== 2) a.push("主轴还差 " + (2 - S.main.length) + " 根");
    if (S.hooks.length < 2) a.push("钩子至少 2 个");
    return a.length ? "还差：" + a.join("，") : "可以继续";
  }
  if (S.step === 3) {
    const rest = [];
    if (S.media.length < 1) rest.push("载体至少 1 类");
    if (S.length === null) rest.push("篇幅");
    if (S.language === null) rest.push("语言");
    return rest.length ? "还差：" + rest.join("、") : "可以继续";
  }
  return "";
}

/* ---------------- 打分（与 r18g_quiz.py 等价） ---------------- */

function scoreAll() {
  const main = new Set(S.main), soft = new Set(S.soft), hooks = new Set(S.hooks);
  const tabooHooks = new Set();
  S.taboos.forEach(k => { const t = D.taboos.find(x => x.k === k); if (t) t.hooks.forEach(h => tabooHooks.add(h)); });
  const damp = {};
  S.softTaboos.forEach(k => { const t = D.softTaboos.find(x => x.k === k); if (t) damp[t.axis] = (damp[t.axis] || 0) + 1; });

  const rows = D.topics.map(t => {
    let s = 0, full = [];
    for (const ax in t.axes) {
      const w = t.axes[ax];
      let mult = 1;
      if (damp[ax]) mult = damp[ax] === 1 ? 0.45 : 0.2;
      if (main.has(ax)) { s += w * 3 * mult; if (w >= 2 && mult === 1) full.push(AX[ax]); }
      else if (soft.has(ax)) s += w * 1.5 * mult;
      else if (w > 0) s += w * 0.5 * mult;
    }
    const hit = t.hooks.filter(h => hooks.has(h));
    s += hit.length * 2;
    const veto = t.hooks.filter(h => tabooHooks.has(h));
    s -= veto.length * 7;
    const why = [];
    if (full.length) why.push("主轴上满格：" + full.join("、"));
    if (hit.length) why.push("命中钩子：" + hit.map(h => HK[h]).join("、"));
    if (veto.length) why.push("踩禁区：" + veto.map(h => HK[h]).join("、"));
    return { t, s, why, veto: veto.length > 0, hit };
  });

  rows.sort((a, b) => (b.s - a.s) || a.t.id.localeCompare(b.t.id));
  return rows;
}

/* ---------------- 结果 ---------------- */

function result(app) {
  const rows = scoreAll();
  const usable = rows.filter(r => !r.veto);
  const top = usable.slice(0, 8);
  const lo = Math.min(...rows.map(r => r.s));
  const hi = Math.max(...rows.map(r => r.s));
  const reco = computeReco(top);

  const w = el("div", "res");
  w.id = "resultShot";
  w.innerHTML = `<h2 class="serif">你的阅读坐标</h2>` +
    `<div class="sub">${D.topics.length} 个题材按坐标重排，下方按漫画 / 小说 / 电影给出作品清单。点题材行展开解释。</div>`;

  const co = el("div", "coords");
  const put = (k, v) => co.appendChild(el("div", "", `<dt>${k}</dt><dd>${v}</dd>`));
  put("主轴", S.main.map(k => AX[k]).join(" ／ "));
  put("副轴", S.soft.length ? S.soft.map(k => AX[k]).join(" ／ ") : "—");
  put("钩子", S.hooks.length ? S.hooks.map(k => HK[k]).join(" ／ ") : "—");
  put("硬禁区", S.taboos.map(k => (D.taboos.find(x => x.k === k) || {}).n || k).join(" ／ ") || "无");
  put("软偏好", S.softTaboos.length ? S.softTaboos.map(k => D.softTaboos.find(x => x.k === k).n).join(" ／ ") : "无");
  put("取用", D.mediaOptions[D.mediaKeys.indexOf(S.media[0])] + " 等 ／ " +
      D.lengthOptions[S.length] + " ／ " + D.langOptions[S.language]);
  w.appendChild(co);

  w.appendChild(el("h2", "serif", "作品清单")).style.marginTop = "40px";
  w.appendChild(el("div", "sub", "按标签匹配，方向大致对味，不保证逐条精准。链接可直接打开；无链接的按检索提示查找。"));
  let anyWork = false;
  D.mediaKeys.forEach((mk, mi) => {
    if (!S.media.includes(mk)) return;
    const sec = el("div", "mediaSec");
    const items = reco[mk] || [];
    anyWork = anyWork || items.length > 0;
    const head = el("button", "mediaHead",
      `<span class="caret">▾</span><span class="mtName">${D.mediaOptions[mi]}</span><span class="mtCount">${items.length}</span>`);
    head.type = "button";
    const body = el("div", "mediaBody");
    head.onclick = () => sec.classList.toggle("folded");
    sec.appendChild(head);
    if (!items.length) {
      body.appendChild(el("div", "note", "本类暂无条目，可按标签继续补充。"));
    } else {
      items.slice(0, 20).forEach(rec => {
        const wk = rec.work;
        const meta = [wk.author, wk.year].filter(Boolean).join(" · ");
        const name = wk.link ? `<a href="${wk.link}" target="_blank" rel="noopener">${wk.title}</a>` : wk.title;
        const card = el("div", "workCard");
        card.innerHTML = `<div class="wt">${name}${wk.origin_title ? ` <span class="wot">${wk.origin_title}</span>` : ""}</div>` +
          `${meta ? `<div class="wm">${meta}</div>` : ""}` +
          `<div class="whit">命中：${rec.why.join(" · ")}</div>` +
          `<div class="wn">${wk.note || ""}</div>` +
          `${wk.link ? "" : `<div class="wsearch">检索：${esc(rec.search || wk.title)}</div>`}`;
        body.appendChild(card);
      });
      if (items.length > 20) body.appendChild(el("div", "note", `仅显示前 20 条，共 ${items.length} 条。`));
    }
    sec.appendChild(body);
    w.appendChild(sec);
  });
  if (!anyWork) w.appendChild(el("div", "card", "作品库当前条目较少。按标签填入后，这里会自动出现对应作品。"));

  w.appendChild(el("h2", "serif", "推荐题材")).style.marginTop = "40px";
  w.appendChild(el("div", "sub", "解释为什么推这些作品：题材按你坐标的匹配度排序。前几名差 1.5 分以内可当并列看。"));
  const list = el("div", "rank");
  top.forEach((r, i) => {
    const row = el("div", "row");
    const head = el("div", "rowhead");
    head.innerHTML = `<span class="rk">${String(i + 1).padStart(2, "0")}</span>` +
      `<span class="rname serif">${r.t.name}</span>` +
      `<span class="rterm">${r.t.term}</span>` +
      `<span class="rscore">${r.s.toFixed(1)}</span>`;
    const pct = hi > lo ? ((r.s - lo) / (hi - lo)) * 100 : 0;
    const bar = el("div", "rbar", `<i></i>`);
    row.appendChild(head); row.appendChild(bar);
    row.appendChild(el("div", "rcore", r.t.core));
    if (r.why.length) row.appendChild(el("div", "rwhy", r.why.join("；")));
    const exp = el("div", "exp");
    exp.innerHTML = `<div class="lab">术语</div><div class="val">${r.t.term}</div>` +
      `<div class="lab">来历</div><div class="val">${r.t.origin}</div>` +
      `<div class="lab">解释</div><div class="val txt">${r.t.explain}</div>` +
      `<div class="lab">题材 id</div><div class="val">TP:${r.t.id}</div>`;
    row.appendChild(exp);
    head.onclick = () => exp.classList.toggle("open");
    list.appendChild(row);
    setTimeout(() => { bar.firstChild.style.width = pct + "%"; }, 60 + i * 55);
  });
  w.appendChild(list);

  const searchBox = el("div", "card");
  searchBox.style.marginTop = "40px";
  searchBox.innerHTML = `<div class="lab2">检索提示 · 英文标签词，可复制到 hitomi / AO3 搜索框继续挖</div>` +
    `<div class="searchline">漫画：<code>${esc(reco.search.manga)}</code></div>` +
    `<div class="searchline">小说：<code>${esc(reco.search.novel)}</code></div>` +
    `<div class="searchline">电影：<code>${esc(reco.search.film)}</code></div>`;
  w.appendChild(searchBox);

  const vetoed = rows.filter(r => r.veto).slice(0, 5);
  if (vetoed.length) {
    const v = el("div", "card vetoed");
    v.innerHTML = `<div class="note" style="margin-bottom:8px">这些被禁区划掉了。扫一眼，看是不是划得太狠</div>` +
      vetoed.map(r => `<b>${r.t.name}</b>　${r.why[r.why.length - 1] || "命中硬禁区"}`).join("<br>");
    w.appendChild(v);
  }

  const acts = el("div", "acts");
  const b0 = el("button", "btn", "保存为图片"); b0.id = "btnShot"; b0.onclick = () => shotResult(b0);
  const b1 = el("button", "btn ghost", "重新作答"); b1.onclick = reset;
  const b2 = el("button", "btn ghost", "复制结果"); b2.onclick = () => copyResult(rows, top, reco, b2);
  const b3 = el("button", "btn ghost", "看全部题材"); b3.onclick = () => go("atlas");
  acts.append(b0, b1, b2, b3); w.appendChild(acts);
  app.appendChild(w);
}

function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c])); }

function computeReco(top) {
  const topicIds = new Set(top.map(r => "TP:" + r.t.id));
  const main = new Set(S.main), soft = new Set(S.soft), hooks = new Set(S.hooks);
  const tabooHooks = new Set();
  S.taboos.forEach(k => { const t = D.taboos.find(x => x.k === k); if (t) t.hooks.forEach(h => tabooHooks.add(h)); });
  const out = { manga: [], novel: [], film: [] };
  const seen = {};
  for (const tag in D.recoBuckets) {
    const bucket = D.recoBuckets[tag];
    for (const mk of D.mediaKeys) {
      (bucket[mk] || []).forEach(wk => {
        if (!S.media.includes(mk)) return;
        if (S.taboos.includes("ORIENT_FEMDOM") && (wk.orientation || "FM") === "FEMDOM") return;
        if ((wk.avoid || []).some(h => tabooHooks.has(h))) return;
        if (S.language === 0 && wk.language === "ja") return;
        let sc = 0; const why = [];
        if (topicIds.has(tag)) { sc += 5; why.push("推荐题材"); }
        if (tag.indexOf("AX:") === 0) { const k = tag.slice(3);
          if (main.has(k)) { sc += 4; why.push("主轴"); }
          else if (soft.has(k)) { sc += 2; why.push("副轴"); } }
        if (tag.indexOf("HK:") === 0 && hooks.has(tag.slice(3))) { sc += 3; why.push("命中钩子"); }
        if (S.language === 0 && wk.language === "zh") sc += 1;
        if (D.lengthKeys[S.length] && wk.length === D.lengthKeys[S.length]) sc += 1;
        const id = wk.id || wk.title;
        const search = (D.tagIndex[tag] || {}).label || wk.title;
        const rec = { work: wk, score: sc, why: [...new Set(why)], tags: [tag], search };
        if (seen[id]) { seen[id].score += sc; seen[id].why = [...new Set(seen[id].why.concat(why))]; seen[id].tags.push(tag); }
        else { seen[id] = rec; out[mk].push(rec); }
      });
    }
  }
  for (const mk of D.mediaKeys) out[mk].sort((a, b) => (b.score - a.score) || ((b.work.year || 0) - (a.work.year || 0)) || a.work.title.localeCompare(b.work.title));
  const hookWords = S.hooks.map(h => D.hookTags[h] || HK[h]);
  const words = hookWords.join(" ");
  out.search = {
    manga: ("female: " + words).replace(/\s+/g, " ").trim(),
    novel: words,
    film: hookWords.slice(0, 4).join(" ") || "（按上方题材术语找同类片）",
  };
  return out;
}
const TYPE_CN = { film: "电影", novel: "小说", manga: "漫画", game: "游戏", art: "画集", other: "其他" };

function renderWorks(works) {
  if (!works || !works.length) return "";
  const items = works.map(w => {
    const meta = [w.author, w.year, TYPE_CN[w.type] || w.type].filter(Boolean).join(" · ");
    const name = w.link
      ? `<a href="${w.link}" target="_blank" rel="noopener">${w.title}</a>`
      : w.title;
    return `<div class="work">
      <div class="wt">${name}${w.origin_title ? ` <span class="wot">${w.origin_title}</span>` : ""}</div>
      ${meta ? `<div class="wm">${meta}</div>` : ""}
      ${w.note ? `<div class="wn">${w.note}</div>` : ""}
    </div>`;
  }).join("");
  return `<div class="lab">参考作品</div><div class="val works">${items}</div>`;
}

function copyResult(rows, top, reco, btn) {
  const L = [];
  L.push("# R18G 阅读推荐结果\n");
  L.push("## 坐标");
  L.push("- 主轴：" + S.main.map(k => AX[k]).join(" / "));
  L.push("- 副轴：" + (S.soft.map(k => AX[k]).join(" / ") || "—"));
  L.push("- 钩子：" + (S.hooks.map(k => HK[k]).join(" / ") || "—"));
  L.push("- 硬禁区：" + (S.taboos.map(k => (D.taboos.find(x => x.k === k) || {}).n || k).join(" / ") || "无"));
  L.push("- 取用：" + S.media.map((m) => D.mediaOptions[D.mediaKeys.indexOf(m)]).join(" / ") +
    " ／ " + D.lengthOptions[S.length] + " ／ " + D.langOptions[S.language]);
  L.push("\n## 作品清单");
  D.mediaKeys.forEach((mk, mi) => {
    if (!S.media.includes(mk)) return;
    L.push("\n### " + D.mediaOptions[mi]);
    const items = reco[mk] || [];
    if (!items.length) { L.push("_本类暂无_"); return; }
    items.forEach(rec => {
      const wk = rec.work;
      const meta = [wk.author, wk.year].filter(Boolean).join(" · ");
      L.push("- **" + wk.title + "**" + (meta ? "  " + meta : ""));
      L.push("  - 命中：" + rec.why.join("、"));
      L.push("  - " + (wk.note || ""));
      if (wk.link) L.push("  - " + wk.link);
    });
  });
  L.push("\n## 推荐题材");
  top.forEach((r, i) => L.push(`${i + 1}. **${r.t.name}**（${r.s.toFixed(1)}）— ${r.t.term}`));
  L.push("\n## 检索提示");
  L.push("- 漫画：" + reco.search.manga);
  L.push("- 小说：" + reco.search.novel);
  L.push("- 电影：" + reco.search.film);

  const txt = L.join("\n");
  const done = () => { const o = btn.textContent; btn.textContent = "已复制"; setTimeout(() => btn.textContent = o, 1400); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(txt).then(done).catch(() => fallbackCopy(txt, done));
  } else fallbackCopy(txt, done);
}

function fallbackCopy(txt, done) {
  const ta = document.createElement("textarea");
  ta.value = txt; ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  try { document.execCommand("copy"); done(); } catch (e) {}
  document.body.removeChild(ta);
}

/* ---------------- 结果截图（手工 canvas 绘制，file:// 下不污染画布） ---------------- */

const SHOT = (() => {
  const PAD = 28, SCALE = 2;
  const cvs = document.createElement("canvas");
  const ctx = cvs.getContext("2d");

  function parseColor(c) {
    if (!c || c === "transparent") return null;
    const m = c.match(/[\d.]+/g);
    if (!m || m.length < 3) return null;
    const a = m.length > 3 ? parseFloat(m[3]) : 1;
    if (a <= 0) return null;
    return `rgba(${m[0] | 0},${m[1] | 0},${m[2] | 0},${a})`;
  }

  function wrapText(str, maxW) {
    const lines = [];
    let cur = "";
    for (const ch of str) {
      const t = cur + ch;
      if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = ch; }
      else cur = t;
    }
    if (cur) lines.push(cur);
    return lines.length ? lines : [""];
  }

  function paint(node, ox, oy) {
    const cs = getComputedStyle(node);
    if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0) return;
    if (node.classList && node.classList.contains("acts")) return;
    const r = node.getBoundingClientRect();
    const x = r.left - ox, y = r.top - oy, w = r.width, h = r.height;
    if (w <= 0 || h <= 0) return;

    const pl = parseFloat(cs.paddingLeft) || 0;
    const pt = parseFloat(cs.paddingTop) || 0;
    const pr = parseFloat(cs.paddingRight) || 0;

    // 进度条 <i>：红到金的渐变实心
    const isBar = node.tagName === "I" && node.parentElement && node.parentElement.classList.contains("rbar");
    if (isBar) {
      const g = ctx.createLinearGradient(x, 0, x + w, 0);
      g.addColorStop(0, "#b8432e"); g.addColorStop(1, "#c9a765");
      ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
    } else {
      const bg = parseColor(cs.backgroundColor);
      if (bg) { ctx.fillStyle = bg; ctx.fillRect(x, y, w, h); }
      const bw = parseFloat(cs.borderTopWidth) || 0;
      if (bw > 0) {
        const bc = parseColor(cs.borderTopColor);
        if (bc) {
          ctx.fillStyle = bc;
          ctx.fillRect(x, y, w, bw);
          ctx.fillRect(x, y + h - bw, w, bw);
          const bl = parseFloat(cs.borderLeftWidth) || bw;
          const br = parseFloat(cs.borderRightWidth) || bw;
          ctx.fillRect(x, y, bl, h);
          ctx.fillRect(x + w - br, y, br, h);
        }
      }
    }

    // 该元素的直接文本节点
    let own = "";
    for (const c of node.childNodes) if (c.nodeType === 3) own += c.nodeValue;
    own = own.replace(/\s+/g, " ").trim();
    if (own && node.parentElement && node.parentElement.classList.contains("todo")) own = "□　" + own;
    if (own) {
      const fs = parseFloat(cs.fontSize) || 14;
      const lh = parseFloat(cs.lineHeight) || fs * 1.6;
      ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${fs}px ${cs.fontFamily}`;
      const fg = parseColor(cs.color);
      ctx.fillStyle = fg || "#e9e3d9";
      ctx.textBaseline = "top";
      ctx.textAlign = "left";
      const lines = wrapText(own, Math.max(12, w - pl - pr));
      const ty = y + pt + (lh - fs) / 2;
      lines.forEach((ln, i) => ctx.fillText(ln, x + pl, ty + i * lh));
    }

    for (const kid of node.children) paint(kid, ox, oy);
  }

  function capture(root) {
    const r = root.getBoundingClientRect();
    const w = Math.ceil(r.width) + PAD * 2;
    const h = Math.ceil(r.height) + PAD * 2;
    cvs.width = w * SCALE;
    cvs.height = h * SCALE;
    ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0);
    ctx.fillStyle = "#0b0a0d";
    ctx.fillRect(0, 0, w, h);
    ctx.save();
    ctx.translate(PAD - r.left, PAD - r.top);
    paint(root, 0, 0);
    ctx.restore();
    return cvs.toDataURL("image/png");
  }

  function download(dataUrl) {
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = "R18G选题结果_" + new Date().toISOString().slice(0, 10) + ".png";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  }

  return { capture, download };
})();

function shotResult(btn) {
  const root = document.getElementById("resultShot");
  if (!root) return;
  const old = btn.textContent;
  btn.textContent = "生成中…";
  btn.classList.add("busy");
  setTimeout(() => {
    try {
      SHOT.download(SHOT.capture(root));
      btn.textContent = "已保存";
    } catch (e) {
      console.error("[shot]", e);
      btn.textContent = "保存失败";
    }
    setTimeout(() => { btn.textContent = old; btn.classList.remove("busy"); }, 1600);
  }, 30);
}

/* ---------------- 全谱 ---------------- */

function atlas(app) {
  const w = el("div", "atlas");
  w.innerHTML = `<div class="stephead"><span class="steptag">附录</span><h2 class="serif">题材全谱 · ${D.topics.length}</h2></div>
    <div class="stepdesc">每个题材的轴坐标、钩子、名词解释和结构三拍。搜名称或术语都能过滤。</div>`;

  const inp = el("input", "");
  inp.placeholder = "搜索题材名、术语、关键词……";
  w.appendChild(inp);
  const box = el("div", "");
  w.appendChild(box);

  const draw = (kw) => {
    box.innerHTML = "";
    const q = kw.trim().toLowerCase();
    D.topics.forEach(t => {
      const hay = (t.name + t.term + t.explain + t.core + Object.keys(t.axes).map(k => AX[k]).join("")).toLowerCase();
      if (q && !hay.includes(q)) return;
      const it = el("div", "aitem");
      it.innerHTML = `<h4 class="serif">${String(t.n).padStart(2, "0")}　${t.name}</h4>
        <div class="term">${t.term}</div>
        <div class="ex">${t.explain}</div>
        ${t.works && t.works.length ? `<div class="aworksToggle"><span class="caret">▾</span> 参考作品 ${t.works.length}</div><div class="aitem-works">${t.works.map(w => {
          const meta = [w.author, w.year, TYPE_CN[w.type] || w.type].filter(Boolean).join(" · ");
          const name = w.link ? `<a href="${w.link}" target="_blank" rel="noopener">${w.title}</a>` : w.title;
          return `<div class="work"><div class="wt">${name}</div>${meta ? `<div class="wm">${meta}</div>` : ""}${w.note ? `<div class="wn">${w.note}</div>` : ""}</div>`;
        }).join("")}</div>` : ""}
        <div class="ax">${Object.keys(t.axes).map(k => AX[k] + (t.axes[k] > 0 ? "+" : "") + t.axes[k]).join("　")}
          ｜ ${t.hooks.map(h => HK[h]).join("、")}</div>`;
      const awt = it.querySelector(".aworksToggle");
      if (awt) awt.onclick = () => {
        const body = it.querySelector(".aitem-works");
        body.classList.toggle("open");
        awt.classList.toggle("collapsed");
      };
      box.appendChild(it);
    });
    if (!box.children.length) box.innerHTML = `<div class="note">没有匹配的题材。</div>`;
  };
  inp.oninput = () => draw(inp.value);
  draw("");

  const acts = el("div", "acts");
  const b = el("button", "btn ghost", "回到问卷");
  b.onclick = () => go(S.step === 0 ? 0 : S.step);
  acts.appendChild(b);
  w.appendChild(acts);
  app.appendChild(w);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ---------------- 路由 ---------------- */

let lastStep = 0;

function go(step) {
  if (step === "atlas") {
    lastStep = S.step;
    $("#app").innerHTML = "";
    atlas($("#app"));
    updateBar(-1);
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  S.step = step;
  updateBar(step);
  renderStep();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function reset() {
  S.step = 0;
  S.main = []; S.soft = []; S.hooks = []; S.softTaboos = [];
  S.taboos = [D.defaultTaboo];
  S.media = []; S.length = S.language = null;
  updateBar(0);
  renderStep();
}

function updateBar(step) {
  const pct = step <= 0 ? 0 : step >= 4 ? 100 : (step / 3) * 100;
  document.title = "R18G 阅读推荐 · " + (step <= 0 ? "封面" : step >= 4 ? "结果" : "第 " + step + " 步 / 3");
  $("#topbtn").textContent = step >= 4 ? "看全谱" : "题材全谱";
  $("#topbtn").onclick = () => go("atlas");
}

updateBar(0);
renderStep();
"""


HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>R18G 阅读推荐问卷</title>
<style>__CSS__</style>
</head>
<body>
<div class="top">
  <div class="topin">
    <div class="brand"><b>R18G</b> 阅读推荐</div>
    <div class="pbar"><i id="pbar"></i></div>
    <button class="tbtn" id="topbtn">题材全谱</button>
  </div>
</div>
<div class="wrap"><div id="app"></div></div>
<script>__JS__</script>
</body>
</html>
"""


def main():
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    js = JS.replace("__DATA__", payload)
    html = HTML.replace("__CSS__", CSS).replace("__JS__", js)

    path = os.path.join(BASE, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("已写：%s  (%.1f KB)" % (path, len(html.encode("utf-8")) / 1024))

    # 只留 index.html，方便双击
    return path


if __name__ == "__main__":
    main()