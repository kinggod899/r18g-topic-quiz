# -*- coding: utf-8 -*-
"""把 r18g_quiz.py 里的题库导出成一份可读的 Markdown 谱系。

    python 导出谱系.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import r18g_quiz as q

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    axname = dict((a[0], a[1]) for a in q.AXES)
    cols = [a[0] for a in q.AXES]
    out = []

    out.append("# R18G 题材谱系 · %d 题材 / %d 钩子 / %d 轴\n" % (len(q.TOPICS), len(q.HOOKS), len(q.AXES)))
    out.append("> 由 `r18g_quiz.py` 的题库自动导出。改了题库重跑 `python 导出谱系.py` 刷新。\n")

    out.append("## 一、七轴\n")
    out.append("| 代码 | 轴 | 含义 |")
    out.append("|---|---|---|")
    for k, n, d in q.AXES:
        out.append("| %s | %s | %s |" % (k, n, d))
    out.append("")

    out.append("## 二、钩子与它们的归属\n")
    out.append("| 钩子 | 名称 | 会被哪些题材带出来 |")
    out.append("|---|---|---|")
    for k, n in q.HOOKS.items():
        used = [t["name"] for t in q.TOPICS if k in t["hooks"]]
        out.append("| %s | %s | %s |" % (k, n, "、".join(used) if used else "—"))
    out.append("")

    out.append("## 三、题材 × 轴坐标\n")
    out.append("| # | 题材 | " + " | ".join(axname[c] for c in cols) + " | 钩子 |")
    out.append("|---|---|" + "---|" * len(cols) + "---|")
    for i, t in enumerate(q.TOPICS, 1):
        cells = []
        for c in cols:
            v = t["axes"].get(c, 0)
            cells.append("" if v == 0 else ("+%d" % v if v > 0 else "%d" % v))
        out.append("| %d | %s | %s | %s |" % (
            i, t["name"], " | ".join(cells), "、".join(q.HOOKS[h] for h in t["hooks"])))
    out.append("")

    out.append("## 四、题材细目\n")
    for i, t in enumerate(q.TOPICS, 1):
        out.append("### %d. %s\n" % (i, t["name"]))
        out.append("- 核：%s" % t["core"])
        out.append("- 轴：" + "　".join("%s%+d" % (axname[k], v) for k, v in t["axes"].items()))
        out.append("- 钩子：" + "、".join(q.HOOKS[h] for h in t["hooks"]))
        out.append("- 典型场景：%s" % t["scene"])
        out.append("- 结构三拍：%s" % t["beat"])
        out.append("")

    path = os.path.join(BASE, "题材谱系.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("已写：%s" % path)


if __name__ == "__main__":
    main()
