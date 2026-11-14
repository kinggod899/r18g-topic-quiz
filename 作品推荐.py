# -*- coding: utf-8 -*-
"""
作品推荐接口。

按题材 id 索引，每个题材挂一个列表，元素是 dict：

    {
        "title":  "作品名",
        "author": "作者",          # 可空
        "year":   1999,            # 可空
        "type":   "film",          # film / novel / manga / game / art / other
        "note":   "一句话说明它为什么对得上这个题材",
        "tags":   ["日本", "90年代"],   # 可空
        "link":   "https://...",   # 可空
    }

设计约定：
    - 这里只放「已公开出版 / 公开发行」的作品，不放无来源的私人作品。
    - note 写具体点：不要写「很经典」，写「它把 X 这件事拍成了 Y」。
    - 一个题材没有合适的推荐，就留空列表，不要硬凑。

维护方式：
    直接往对应 id 的列表里加 dict，重跑 build_site.py 即可。
    新增题材时，如果推荐还没想好，加一个空列表占位。
"""

RECOMMEND = {
    # ---- 示例：验证渲染链路，正式内容按题材逐个补 ----
    "RUIN_WIFE": [
        {
            "title": "铁男",
            "origin_title": "鉄男 TETSUO",
            "author": "塚本晋也",
            "year": 1989,
            "type": "film",
            "note": "身体被异物侵入后一点点不再是人的过程，全片用黑白和金属噪音堆出来。",
            "tags": ["日本", "身体恐怖"],
            "link": "",
        },
    ],
    "COLD_RECORD": [
        {
            "title": "《验尸官》",
            "origin_title": "",
            "author": "（待补）",
            "year": None,
            "type": "novel",
            "note": "用卷宗体写非正常死亡，重点全在表格与编号上，读的人自己补画面。",
            "tags": [],
            "link": "",
        },
    ],
}


def for_topic(topic_id):
    """取某题材的推荐列表，没有就返回空列表。"""
    return RECOMMEND.get(topic_id, [])


def ensure_all(topics):
    """给还没建条目的题材补空列表，方便维护时一眼看出哪些还空着。"""
    for t in topics:
        RECOMMEND.setdefault(t["id"], [])
    return RECOMMEND


def stats():
    """当前填充情况，构建时打印。"""
    total = len(RECOMMEND)
    filled = sum(1 for v in RECOMMEND.values() if v)
    items = sum(len(v) for v in RECOMMEND.values())
    return total, filled, items
