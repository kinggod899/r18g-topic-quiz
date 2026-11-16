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
        "scenes": q.SCENES,
        "relations": q.RELATIONS,
        "povs": q.POVS,
        "tones": q.TONES,
        "lengths": q.LENGTHS,
        "shape": ["一次到底（单场景，冲到最高再停）", "长期日常（同样的伤口重复发生很多次）"],
        "ending": ["死（死是那一声钝响）", "活（活下来才是更长的刑）", "随便，看情节走到哪"],
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
.aitem-works{margin-top:12px;padding-top:12px;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:8px}
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
  main: [], soft: [], hooks: [], taboos: [], softTaboos: [],
  scene: null, relation: null, pov: null, tone: null, length: null,
  shape: null, ending: null
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
  if (S.step === 5) return result(app);

  const head = el("div", "stephead");
  head.appendChild(el("span", "steptag", ["", "第一轮 / 四", "第二轮 / 四", "第三轮 / 四", "第四轮 / 四"][S.step]));
  head.appendChild(el("h2", "", ["", "你被什么击中", "划掉不吃的东西", "成品配方", "定盘"][S.step]));
  app.appendChild(head);
  app.appendChild(el("div", "stepdesc", [
    "",
    "先说你在哪几处被击中。选两根最狠的，再挑几个具体画面，剩下的交给程序去算。",
    "把不能碰的先划掉。硬禁区一踩就整类作废，软偏好只让它往后排。",
    "同一个题材，放在宫廷和放在都市，写出来是两篇东西。这一轮定形状。",
    "最后两件：这一篇要多长一口气，结尾能不能死人。"
  ][S.step]));

  if (S.step === 1) step1(app);
  if (S.step === 2) step2(app);
  if (S.step === 3) step3(app);
  if (S.step === 4) step4(app);

  app.appendChild(navBar());
}

function cover(app) {
  const c = el("div", "step cover");
  c.innerHTML = `
    <div class="kicker">R18G 题材定位</div>
    <h1 class="serif">先量出你的<em>坐标</em>，<br>再谈写什么。</h1>
    <p class="lead">
      直接问「你喜欢哪个题材」，答出来的多半不是真的。人会挑自己觉得拿得出手的那些，
      把真正让自己坐不住的藏起来。所以这里换个问法：你在哪几处被击中，哪些碰都不能碰。
      十二道题，四轮。答完以后，68 个题材按你的坐标重新排一遍。
    </p>
    <div class="meta">
      <div><b>${D.topics.length}</b>题材</div>
      <div><b>${D.hooks.length}</b>钩子</div>
      <div><b>${D.axes.length}</b>轴</div>
      <div><b>12</b>题 / 约 2 分钟</div>
    </div>
    <div class="startrow">
      <button class="btn" id="btnStart">开始</button>
      <button class="btn ghost" id="btnAtlas">先看全部题材与解释</button>
    </div>
    <p class="note" style="margin-top:26px">
      全部内容留在本机浏览器里，不上传、不保存。关掉页面即清空。<br>
      所有角色与情节均为虚构，用于创作前的选题定位。
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
    "这条的权重是偏好项的三倍半。宁可少推一个，也别推一个你读到一半就想关掉的东西。");
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
  singleQ(app, "06", "场景 —— 故事发生在哪", null, D.scenes, "scene");
  singleQ(app, "07", "关系 —— 动手的与承受的是什么关系", null, D.relations, "relation");
  singleQ(app, "08", "视角 —— 镜头放在谁身上", null, D.povs, "pov");
  singleQ(app, "09", "笔法 —— 用哪种舌头说这件事", null, D.tones, "tone");
  singleQ(app, "10", "长度 —— 这次要多大一块", null, D.lengths, "length");
}

function step4(app) {
  singleQ(app, "11", "这一次，你要的是哪一种落法", "同一题材，单场景冲到顶，和日常化重复，是两篇完全不同的文。", D.shape, "shape");
  singleQ(app, "12", "结尾允许死吗", null, D.ending, "ending");
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
  const nx = el("button", "btn", S.step === 4 ? "算结果" : "下一步");
  nx.disabled = !ok;
  nx.onclick = () => { if (ok) go(S.step === 4 ? 5 : S.step + 1); };
  n.appendChild(nx);
  return n;
}

function canNext() {
  if (S.step === 1) return S.main.length === 2 && S.hooks.length >= 2;
  if (S.step === 2) return true;
  if (S.step === 3) return [S.scene, S.relation, S.pov, S.tone, S.length].every(v => v !== null);
  if (S.step === 4) return S.shape !== null && S.ending !== null;
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
    const rest = [["场景", S.scene], ["关系", S.relation], ["视角", S.pov], ["笔法", S.tone], ["长度", S.length]]
      .filter(x => x[1] === null).map(x => x[0]);
    return rest.length ? "还差：" + rest.join("、") : "可以继续";
  }
  if (S.step === 4) {
    const rest = [["落法", S.shape], ["结尾", S.ending]].filter(x => x[1] === null).map(x => x[0]);
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

  const w = el("div", "res");
  w.id = "resultShot";
  w.innerHTML = `<h2 class="serif">你的坐标</h2>
    <div class="sub">按这套坐标，${D.topics.length} 个题材重排如下。点任意一行展开名词解释。</div>`;

  // 坐标
  const co = el("div", "coords");
  const put = (k, v) => co.appendChild(el("div", "", `<dt>${k}</dt><dd>${v}</dd>`));
  put("主轴", S.main.map(k => AX[k]).join(" ／ "));
  put("副轴", S.soft.length ? S.soft.map(k => AX[k]).join(" ／ ") : "—");
  put("钩子", S.hooks.length ? S.hooks.map(k => HK[k]).join(" ／ ") : "—");
  put("硬禁区", S.taboos.length ? S.taboos.map(k => D.taboos.find(x => x.k === k).n).join(" ／ ") : "无");
  put("软偏好", S.softTaboos.length ? S.softTaboos.map(k => D.softTaboos.find(x => x.k === k).n).join(" ／ ") : "无");
  put("落法", D.shape[S.shape] + " ／ 结尾：" + D.ending[S.ending]).innerHTML;
  w.appendChild(co);

  if (!top.length) {
    w.appendChild(el("div", "card", `<span style="color:var(--red2)">禁区把所有题材都划掉了。</span>
      <div class="note" style="margin-top:8px">要么回上一步松开一条，要么这些确实不是你要的。</div>`));
    const acts = el("div", "acts");
    const b = el("button", "btn", "回上一步");
    b.onclick = () => go(2);
    acts.appendChild(b);
    w.appendChild(acts);
    app.appendChild(w);
    return;
  }

  // 排序
  w.appendChild(el("h2", "serif", "题材排序")).style.marginTop = "40px";
  w.appendChild(el("div", "sub", "分数只是相对你的坐标算出来的匹配度，不是什么绝对排名。前几名差 1.5 分以内，基本可以当并列看。"));
  const list = el("div", "rank");

  top.forEach((r, i) => {
    const row = el("div", "row");
    const head = el("div", "rowhead");
    head.innerHTML = `<span class="rk">${String(i + 1).padStart(2, "0")}</span>
      <span class="rname serif">${r.t.name}</span>
      <span class="rterm">${r.t.term}</span>
      <span class="rscore">${r.s.toFixed(1)}</span>`;
    const pct = hi > lo ? ((r.s - lo) / (hi - lo)) * 100 : 0;
    const bar = el("div", "rbar", `<i></i>`);
    row.appendChild(head);
    row.appendChild(bar);
    row.appendChild(el("div", "rcore", r.t.core));
    if (r.why.length) row.appendChild(el("div", "rwhy", r.why.join("；")));

    const exp = el("div", "exp");
    exp.innerHTML = `
      <div class="lab">术语</div><div class="val">${r.t.term}</div>
      <div class="lab">来历</div><div class="val">${r.t.origin}</div>
      <div class="lab">解释</div><div class="val txt">${r.t.explain}</div>
      <div class="lab">原生场景</div><div class="val">${r.t.scene}</div>
      <div class="lab">结构三拍</div><div class="val">${r.t.beat}</div>
      ${renderWorks(r.t.works)}`;
    row.appendChild(exp);

    head.onclick = () => exp.classList.toggle("open");
    list.appendChild(row);
    setTimeout(() => { bar.firstChild.style.width = pct + "%"; }, 60 + i * 55);
  });
  w.appendChild(list);

  // 定盘
  const best = top[0].t;
  let rec = best.hooks.filter(h => S.hooks.includes(h));
  if (!rec.length) rec = best.hooks.slice(0, 3);

  w.appendChild(el("h2", "serif", "首选定盘")).style.marginTop = "40px";
  const pick = el("div", "card pick");
  pick.innerHTML = `
    <div class="lab2">OPENING SHEET</div>
    <h3 class="serif">${best.name}</h3>
    <div style="font-size:11.5px;color:var(--gold);margin-bottom:14px">${best.term}</div>
    <div class="core">${best.core}</div>
    <div class="tbl">
      <dt>原生场景</dt><dd>${best.scene}</dd>
      <dt>结构三拍</dt><dd>${best.beat}</dd>
      <dt>必带钩子</dt><dd>${rec.map(h => HK[h]).join("、")}</dd>
      <dt>配方</dt><dd>${D.scenes[S.scene]} ／ ${D.relations[S.relation]} ／ ${D.povs[S.pov]}视角 ／ ${D.tones[S.tone]} ／ ${D.lengths[S.length]}</dd>
      <dt>落法</dt><dd>${D.shape[S.shape]}</dd>
      <dt>结尾</dt><dd>${D.ending[S.ending]}</dd>
    </div>
    <div class="todo">
      <li>先定三个具体细节，写的时候照着这个密度来，别停在形容词上</li>
      <li>每段都要有身体上的实况，别写作者自己的评语</li>
      <li>承受那一方要有自己的内在，不能只是个道具</li>
      <li>结尾别给救赎，情节走到哪儿就停在哪儿</li>
    </div>`;
  w.appendChild(pick);

  if (top.length > 1) {
    const alt = el("div", "card");
    alt.innerHTML = `<div class="note" style="margin-bottom:10px">次选搭子（做副线，或下一轮重跑时换这一组轴）</div>
      <div style="font-size:14px">${top.slice(1, 4).map(r => `<span class="serif" style="font-size:16px">${r.t.name}</span>
        <span style="color:var(--dim2);font-size:12px">　${r.t.term}</span>`).join("<br>")}</div>`;
    w.appendChild(alt);
  }

  const vetoed = rows.filter(r => r.veto).slice(0, 5);
  if (vetoed.length) {
    const v = el("div", "card vetoed");
    v.innerHTML = `<div class="note" style="margin-bottom:8px">这些被禁区划掉了。扫一眼，看是不是划得太狠</div>` +
      vetoed.map(r => `<b>${r.t.name}</b>　${r.why[r.why.length - 1] || "命中硬禁区"}`).join("<br>");
    w.appendChild(v);
  }

  const acts = el("div", "acts");
  const b0 = el("button", "btn", "保存为图片");
  b0.id = "btnShot";
  b0.onclick = () => shotResult(b0);
  const b1 = el("button", "btn ghost", "重新作答");
  b1.onclick = reset;
  const b2 = el("button", "btn ghost", "复制结果");
  b2.onclick = () => copyResult(rows, top, best, rec, b2);
  const b3 = el("button", "btn ghost", "看全部题材");
  b3.onclick = () => go("atlas");
  acts.append(b0, b1, b2, b3);
  w.appendChild(acts);

  app.appendChild(w);
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

function copyResult(rows, top, best, rec, btn) {
  const L = [];
  L.push("# R18G 选题结果\n");
  L.push("## 坐标");
  L.push("- 主轴：" + S.main.map(k => AX[k]).join(" / "));
  L.push("- 副轴：" + (S.soft.map(k => AX[k]).join(" / ") || "—"));
  L.push("- 钩子：" + (S.hooks.map(k => HK[k]).join(" / ") || "—"));
  L.push("- 硬禁区：" + (S.taboos.map(k => D.taboos.find(x => x.k === k).n).join(" / ") || "无"));
  L.push("- 软偏好：" + (S.softTaboos.map(k => D.softTaboos.find(x => x.k === k).n).join(" / ") || "无"));
  L.push("\n## 排序");
  top.forEach((r, i) => {
    L.push(`${i + 1}. **${r.t.name}**（${r.s.toFixed(1)}）— ${r.t.term}`);
    L.push(`   - ${r.t.core}`);
    if (r.why.length) L.push("   - " + r.why.join("；"));
  });
  L.push("\n## 开工单");
  L.push("- 定盘：" + best.name);
  L.push("- 核：" + best.core);
  L.push("- 场景：" + best.scene);
  L.push("- 三拍：" + best.beat);
  L.push("- 钩子：" + rec.map(h => HK[h]).join("、"));
  L.push(`- 配方：${D.scenes[S.scene]} ／ ${D.relations[S.relation]} ／ ${D.povs[S.pov]}视角 ／ ${D.tones[S.tone]} ／ ${D.lengths[S.length]}`);
  L.push("- 落法：" + D.shape[S.shape] + "；结尾：" + D.ending[S.ending]);

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
        ${t.works && t.works.length ? `<div class="aitem-works">${t.works.map(w => {
          const meta = [w.author, w.year, TYPE_CN[w.type] || w.type].filter(Boolean).join(" · ");
          const name = w.link ? `<a href="${w.link}" target="_blank" rel="noopener">${w.title}</a>` : w.title;
          return `<div class="work"><div class="wt">${name}</div>${meta ? `<div class="wm">${meta}</div>` : ""}${w.note ? `<div class="wn">${w.note}</div>` : ""}</div>`;
        }).join("")}</div>` : ""}
        <div class="ax">${Object.keys(t.axes).map(k => AX[k] + (t.axes[k] > 0 ? "+" : "") + t.axes[k]).join("　")}
          ｜ ${t.hooks.map(h => HK[h]).join("、")}</div>`;
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
  S.main = []; S.soft = []; S.hooks = []; S.taboos = []; S.softTaboos = [];
  S.scene = S.relation = S.pov = S.tone = S.length = S.shape = S.ending = null;
  updateBar(0);
  renderStep();
}

function updateBar(step) {
  const pct = step <= 0 ? 0 : step >= 5 ? 100 : (step / 4) * 100;
  $("#pbar").style.width = pct + "%";
  document.title = "R18G 题材定位 · " + (step <= 0 ? "封面" : step >= 5 ? "结果" : "第 " + step + " 步 / 4");
  $("#topbtn").textContent = step >= 5 ? "看全谱" : "题材全谱";
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
<title>R18G 题材定位问卷</title>
<style>__CSS__</style>
</head>
<body>
<div class="top">
  <div class="topin">
    <div class="brand"><b>R18G</b> 题材定位</div>
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