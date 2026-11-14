# -*- coding: utf-8 -*-
"""R18G 题材匹配问卷 —— 题库驱动的选择题程序。

用法：
    python r18g_quiz.py            交互式问卷（四轮 12 题，约 40 秒）
    python r18g_quiz.py list       打印全部轴 / 钩子 / 题材
    python r18g_quiz.py topic 12   打印第 12 个题材的细分

设计要点：
    题材不是一个平面列表，而是七根轴上的坐标。问卷不去问"你喜欢哪个题材"
    （人答不出来），而是问"你在哪几根轴上被击中"，再回算题材排序。
    禁忌是负向过滤器，权重高于正向偏好——踩一条雷就能废掉一整个题材。
"""

import os
import sys
import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 轴定义

AXES = [
    ("POC", "权力落差", "上位者可以毫无代价地处置下位者"),
    ("BODY", "身体越界", "内脏、骨骼、器官、切割——身体不再完整"),
    ("PROX", "羞辱亲密", "羞耻本身就是最深的亲密"),
    ("MIND", "意识剥夺", "被使用者的内在被抹掉，或者反过来吞掉使用者"),
    ("DEATH", "死亡在场", "尸、濒死、下葬、腐朽——死的重量压在活人身上"),
    ("SOC", "秩序崩解", "公开、围观、律法失效、看客的沉默"),
    ("AES", "题材位置", "文体与视角本身就是快感来源"),
]

# ---------------------------------------------------------------- 钩子池

HOOKS = {
    "REGICIDE": "仪式化处刑",
    "STRANGLE": "绞杀 / 窒息",
    "DEFILE_BODY": "尸体的性使用",
    "INCEST": "亲缘禁忌",
    "PREGNANT": "孕体",
    "MISCARRIAGE": "流产 / 死胎",
    "BIRTH": "生产 / 难产",
    "BEAST": "兽性 / 异种",
    "AMPUTATE": "切割 / 截肢",
    "EYE": "眼部",
    "INSECT": "虫",
    "NEEDLE": "穿刺 / 针",
    "DISFIGURE": "毁容",
    "DINNER": "食人 / 宴席",
    "WITNESS": "公开目击",
    "SERVANT": "仆从合围",
    "DELUSION": "爱之妄念",
    "MECHANICAL": "器械 / 刑具",
    "WET": "体液（汗 / 泪 / 分泌 / 奶水 / 羊水）",
    "INCONT": "活人失禁 / 排泄",
    "CORPSE_WET": "死后失禁 / 尸水",
    "INFANT": "幼体在场",
    "CORPSE_BRIDE": "婚配死者",
    "SACRIFICE": "献祭",
    "MEDICAL": "医 / 手术",
    "PRIEST": "神职 / 教权",
    "MOTHER": "母职",
    "TWIN": "双生替身",
    "SILENCE": "彻底的沉默",
    "LAUGH": "笑 / 温柔在场",
    "SELF": "自毁",
    "TIME": "时间 / 年岁 / 反复的日子",
    "ROT": "腐烂 / 腐败 / 分解",
    "COLD": "冷静记录体",
    "VORE": "整吞 / 活体吞食",
    "UNBIRTH": "归胎 / 逆向生产",
    "INFLATE": "膨胀 / 撑破",
    "REMODEL": "改造 / 重塑",
    "OBJECT": "物化 / 变成东西",
    "HOOKPULL": "肉钩 / 悬吊",
    "BRAND": "烙印 / 归属标记",
    "TOOTH": "牙与口腔",
    "WOUND_SEX": "伤口性交",
    "TAXIDERM": "剥制 / 标本",
    "DEPRIVE": "感官剥夺",
    "BURN": "灼烧 / 火",
    "CRUSH": "碾压 / 挤碎",
    "PARASITE": "寄生 / 宿主",
    "MIND_BREAK": "心智崩坏",
    "DOLL": "人偶 / 摆布",
    "BLUNT": "钝击 / 内出血",
    "FLAY": "剥皮 / 去皮",
    "IMPALE": "贯穿 / 穿刺固定",
    "BURY": "活埋 / 幽闭",
    "FREEZE": "冻伤 / 低温",
    "DEFORM": "畸形 / 天生异形",
    "HEMICORP": "半身 / 腰下切除",
    "VOMIT": "呕吐 / 反流",
    "NAIL": "指甲 / 甲床",
    "DILATE": "过度扩张 / 撑到极限",
    "THROAT": "深喉 / 食管",
    "ANESTH": "麻醉 / 无痛切割",
}

# 钩子分组：只影响网页上的排版，不参与打分。
HOOK_GROUPS = {
    "身体": ["AMPUTATE", "EYE", "NEEDLE", "DISFIGURE", "TOOTH", "WOUND_SEX", "BURN",
             "BLUNT", "FLAY", "IMPALE", "HEMICORP", "NAIL", "FREEZE", "ANESTH",
             "DILATE", "CRUSH", "REMODEL", "INFLATE", "HOOKPULL", "BRAND", "MEDICAL"],
    "入口": ["VORE", "UNBIRTH", "DINNER", "PARASITE", "INSECT", "BEAST", "PREGNANT",
             "MISCARRIAGE", "BIRTH", "INFANT", "THROAT", "VOMIT"],
    "死亡": ["REGICIDE", "STRANGLE", "DEFILE_BODY", "CORPSE_BRIDE", "CORPSE_WET",
             "TAXIDERM", "ROT", "SACRIFICE", "BURY"],
    "关系": ["INCEST", "MOTHER", "DELUSION", "SERVANT", "TWIN", "OBJECT", "DOLL",
             "MIND_BREAK", "DEPRIVE", "SELF", "DEFORM"],
    "场域": ["WITNESS", "PRIEST", "MECHANICAL", "WET", "INCONT", "SILENCE",
             "LAUGH", "COLD", "TIME"],
}
# 去掉占位名，补上真实存在的键
HOOK_GROUPS["身体"] = [h for h in HOOK_GROUPS["身体"] if h in HOOKS]
HOOK_GROUPS["场域"] = [h for h in HOOK_GROUPS["场域"] if h in HOOKS] + ["WITNESS"]

# ---------------------------------------------------------------- 题材库
# axes 权重范围 -2..2；hooks 用于钩子命中加分与禁忌否决。

TOPICS = [
    {
        "id": "RUIN_WIFE",
        "name": "被毁弃的至亲",
        "core": "处决一个人，然后当着幸存者的面继续使用她。暴力终结于死亡，占有不终结。",
        "axes": {"POC": 2, "PROX": 2, "DEATH": 2, "BODY": 1, "MIND": 1, "SOC": 1},
        "hooks": ["REGICIDE", "STRANGLE", "DEFILE_BODY", "INCEST", "WITNESS"],
        "scene": "处刑台、偏殿、灵堂",
        "beat": "断颈的钝响 → 尸体的翻动 → 幸存者被按住看完",
    },
    {
        "id": "PREGNANT_VESSEL",
        "name": "孕体重压",
        "core": "怀孕在这里不是恩典，是刑期。肚腹一天天变大，权力一天天变重。",
        "axes": {"BODY": 2, "DEATH": 1, "MIND": 2, "POC": 1, "PROX": 1},
        "hooks": ["PREGNANT", "BIRTH", "MISCARRIAGE", "WET", "MOTHER"],
        "scene": "产房、卧榻、晨吐的铜盆边",
        "beat": "确诊 → 身体被逐月撑开 → 床单上的血水",
    },
    {
        "id": "CHILDBED",
        "name": "产房即刑场",
        "core": "生产本身就是一场公开的行刑。人命从裂口里出来，谁活着由别人决定。",
        "axes": {"BODY": 2, "DEATH": 2, "PROX": 1, "SOC": 1},
        "hooks": ["BIRTH", "MEDICAL", "WET", "MOTHER", "INFANT"],
        "scene": "血泊、银剪、两日夜不灭的灯",
        "beat": "胎位不正 → 侧切 → 婴儿落地那一声",
    },
    {
        "id": "CORPSE_WED",
        "name": "与死者成婚",
        "core": "合法的婚姻，对象已经凉了。仪式照常进行，宾客照常举杯。",
        "axes": {"DEATH": 2, "PROX": 1, "SOC": 2, "MIND": 1},
        "hooks": ["CORPSE_BRIDE", "DEFILE_BODY", "TIME", "INCEST", "PRIEST"],
        "scene": "殡仪馆、喜堂、双份的香烛",
        "beat": "拜堂 → 扶不住的脖颈 → 喜被下的僵硬",
    },
    {
        "id": "TWIN_ECHO",
        "name": "双生替身",
        "core": "一个被使用，另一个必须看着。她们共享同一张脸，这就是刑罚。",
        "axes": {"MIND": 2, "PROX": 2, "POC": 1, "SOC": 1},
        "hooks": ["TWIN", "WITNESS", "DELUSION", "SILENCE"],
        "scene": "镜前、并排的两张榻",
        "beat": "点错人 → 认错人的沉默 → 被换上去的那一个",
    },
    {
        "id": "BODY_SWAP",
        "name": "借壳",
        "core": "身体是可以被搬走的东西。住进去的人用它做完了所有事，原主只能旁观。",
        "axes": {"MIND": 2, "BODY": 1, "AES": 1, "PROX": 1},
        "hooks": ["SELF", "MECHANICAL", "SILENCE", "TWIN"],
        "scene": "手术台、镜中、出租的身体",
        "beat": "签字 → 醒来不是自己 → 看着自己被人用",
    },
    {
        "id": "LIVESTOCK",
        "name": "豢养",
        "core": "人被当成畜产：编栏号、称重、配种、宰杀。制度越完整越恐怖。",
        "axes": {"POC": 2, "BODY": 1, "SOC": 1, "MIND": 1},
        "hooks": ["BEAST", "SERVANT", "MECHANICAL", "INCONT", "COLD"],
        "scene": "栏舍、检疫站、编号的铁牌",
        "beat": "称重 → 烙印 → 第一次配种",
    },
    {
        "id": "AUCTION",
        "name": "牲口拍卖",
        "core": "验货、开价、落槌。人被摊开在台上，买家伸手翻检。",
        "axes": {"POC": 2, "SOC": 2, "PROX": 1},
        "hooks": ["SERVANT", "WITNESS", "MECHANICAL", "INCONT", "COLD"],
        "scene": "拍卖台、验货的皮手套、木槌",
        "beat": "开牙 → 摸身 → 落槌",
    },
    {
        "id": "RITUAL_SACRIFICE",
        "name": "献祭",
        "core": "毁形是有程序的。每一步都有颂词，每一步都为了让人活着被拆开。",
        "axes": {"DEATH": 2, "SOC": 2, "BODY": 1, "POC": 1},
        "hooks": ["SACRIFICE", "PRIEST", "REGICIDE", "DEFILE_BODY", "MECHANICAL"],
        "scene": "祭坛、石槽、诵经声",
        "beat": "净身 → 开口 → 血顺着槽走",
    },
    {
        "id": "PRIEST_CELL",
        "name": "忏悔室与教权",
        "core": "罪被说出来，然后被用来交换。赦免是有价钱的，付的是身体。",
        "axes": {"SOC": 1, "MIND": 2, "PROX": 2, "POC": 1},
        "hooks": ["PRIEST", "DELUSION", "WITNESS", "SILENCE"],
        "scene": "告解格、烛、看不见脸的窗",
        "beat": "说出罪 → 隔板打开 → 赎罪的姿势",
    },
    {
        "id": "SURGEON",
        "name": "医者与病体",
        "core": "白布、器械、知情同意。最文明的场景承载最原始的权力。",
        "axes": {"BODY": 2, "POC": 1, "PROX": 1, "MIND": 1},
        "hooks": ["MEDICAL", "MECHANICAL", "AMPUTATE", "WOUND_SEX", "WET"],
        "scene": "无影灯、脱毛的皮肤、托盘",
        "beat": "划开 → 止血钳 → 缝合线穿过皮肉",
    },
    {
        "id": "NEEDLE",
        "name": "针刺与经络",
        "core": "细密的侵入，一寸一寸。疼是准时的，快感是迟到的。",
        "axes": {"BODY": 2, "MIND": 1, "PROX": 1},
        "hooks": ["NEEDLE", "MECHANICAL", "MEDICAL", "SILENCE"],
        "scene": "银针、穴位图、被固定住的手腕",
        "beat": "下针 → 捻转 → 拔出来的那一下",
    },
    {
        "id": "EYE_SCENE",
        "name": "眼部",
        "core": "剥夺目睹权。看不见的人，才最清楚正在发生什么。",
        "axes": {"BODY": 2, "MIND": 1, "DEATH": 1},
        "hooks": ["EYE", "MECHANICAL", "DISFIGURE", "WITNESS"],
        "scene": "蒙眼的布、困住的眼皮、镜片",
        "beat": "被撑开 → 不能眨 → 光",
    },
    {
        "id": "LIMB",
        "name": "切割与残缺",
        "core": "少了一部分的身体更好用。残肢成了新的接口。",
        "axes": {"BODY": 2, "DEATH": 1, "POC": 1},
        "hooks": ["AMPUTATE", "MEDICAL", "DISFIGURE", "MECHANICAL"],
        "scene": "锯、止血带、地上的形状",
        "beat": "捆紧 → 锯 → 剩下的那截怎么办",
    },
    {
        "id": "GELDING",
        "name": "去势",
        "core": "不是杀死，是把某种可能性永久摘掉。人还活着，只是从此不一样了。",
        "axes": {"BODY": 2, "POC": 2, "PROX": 1, "MIND": 1},
        "hooks": ["AMPUTATE", "MEDICAL", "MECHANICAL", "SERVANT", "COLD"],
        "scene": "宫刑房、烧红的铁、验身的人",
        "beat": "按住 → 割 → 之后他怎么称呼自己",
    },
    {
        "id": "DISFIGURE",
        "name": "毁容",
        "core": "美被当场销毁。销毁者通常最爱这张脸。",
        "axes": {"BODY": 1, "PROX": 2, "SOC": 1, "MIND": 1},
        "hooks": ["DISFIGURE", "WITNESS", "DELUSION", "SELF"],
        "scene": "铜镜、炭火、撕开的布",
        "beat": "照镜子 → 抬手 → 之后她还愿不愿照",
    },
    {
        "id": "DINNER",
        "name": "宴席",
        "core": "人被端上桌。席间所有人都在谈别的，这就是最狠的一层。",
        "axes": {"SOC": 2, "POC": 2, "DEATH": 1, "PROX": 1},
        "hooks": ["DINNER", "WITNESS", "SERVANT", "PRIEST"],
        "scene": "长桌、银盖、祝酒词",
        "beat": "揭盖 → 举筷 → 说好吃",
    },
    {
        "id": "BEAST",
        "name": "异种与兽性",
        "core": "不是人的东西拥有人的身体。反抗没有对象，求饶没有语言。",
        "axes": {"BODY": 2, "MIND": 1, "PROX": 1},
        "hooks": ["BEAST", "WET", "PARASITE", "SILENCE"],
        "scene": "厩、林、被拴住的颈圈",
        "beat": "靠近 → 气味 → 无法交流的那部分",
    },
    {
        "id": "INSECT",
        "name": "虫",
        "core": "数量就是暴力。个体太小，所以无处可挡。",
        "axes": {"BODY": 2, "MIND": 1},
        "hooks": ["INSECT", "PARASITE", "WET", "MECHANICAL"],
        "scene": "缝隙、皮下、灯下的一层",
        "beat": "第一只 → 一整片 → 不再驱赶",
    },
    {
        "id": "MACHINE",
        "name": "器械",
        "core": "人退出以后，程序还在继续。谁是施害者已经说不清。",
        "axes": {"BODY": 2, "POC": 1, "AES": 1},
        "hooks": ["MECHANICAL", "WITNESS", "COLD", "MEDICAL"],
        "scene": "滑轮、刻度、定时",
        "beat": "上架 → 启动 → 记录员在旁边写字",
    },
    {
        "id": "GALLOWS",
        "name": "绞杀与悬吊",
        "core": "呼吸是可以被收取的东西。收的人不急，被收的人很急。",
        "axes": {"DEATH": 2, "POC": 1, "BODY": 1, "PROX": 1},
        "hooks": ["STRANGLE", "REGICIDE", "WITNESS", "CORPSE_WET"],
        "scene": "白绫、绳结、脚下那块木板",
        "beat": "收紧 → 失禁 → 松开以后的第一口气",
    },
    {
        "id": "PUBLIC_SQUARE",
        "name": "公开处刑",
        "core": "围观者才是刑具。他们什么都不做，这就是参与。",
        "axes": {"SOC": 2, "POC": 2, "PROX": 1, "DEATH": 1},
        "hooks": ["WITNESS", "REGICIDE", "SERVANT", "DISFIGURE"],
        "scene": "广场、告示、挤到前面的人",
        "beat": "宣读 → 剥衣 → 底下有人笑",
    },
    {
        "id": "WATCHER",
        "name": "目击者的位置",
        "core": "不参与的人也在被改造。看，是一种缓慢的性。",
        "axes": {"MIND": 2, "PROX": 2, "AES": 1},
        "hooks": ["WITNESS", "DELUSION", "SILENCE", "COLD"],
        "scene": "门缝、帘后、隔着屏风的椅子",
        "beat": "看见 → 不动 → 事后自己手上的反应",
    },
    {
        "id": "COLD_RECORD",
        "name": "冷记录",
        "core": "用卷宗、验尸单、日记的口吻写最脏的事。距离感就是快感。",
        "axes": {"AES": 2, "MIND": 1, "SOC": 1},
        "hooks": ["COLD", "MECHANICAL", "MEDICAL", "TIME"],
        "scene": "卷宗、判词、编号的物证袋",
        "beat": "编号 → 记录 → 签字的那个人的呼吸",
    },
    {
        "id": "LOVE_DELUSION",
        "name": "爱之妄念",
        "core": "加害者坚信自己在爱。这份确信比任何刑具都锋利。",
        "axes": {"MIND": 2, "PROX": 2, "SOC": 1},
        "hooks": ["DELUSION", "LAUGH", "MOTHER", "SILENCE"],
        "scene": "温柔的手、做过头的照顾、收拾干净的屋子",
        "beat": "他说爱我 → 他做的事 → 两者之间没有缝",
    },
    {
        "id": "SERVANT_RING",
        "name": "仆从合围",
        "core": "动手的都是下人。主子只需要坐在那里，说一句「别弄死了」。",
        "axes": {"POC": 2, "SOC": 2, "PROX": 1},
        "hooks": ["SERVANT", "WITNESS", "MECHANICAL", "SILENCE"],
        "scene": "廊下、按住四肢的手、主位上的茶",
        "beat": "吩咐 → 按住 → 主子没有抬头",
    },
    {
        "id": "RIVAL",
        "name": "同侪在场",
        "core": "被比较是比被使用更难忍的。两个人都在，才是完整刑具。",
        "axes": {"PROX": 2, "MIND": 1, "SOC": 1},
        "hooks": ["WITNESS", "TWIN", "DELUSION", "SILENCE"],
        "scene": "并排的膝、谁先出声",
        "beat": "被点名 → 比较 → 输的那个还得谢恩",
    },
    {
        "id": "HUNGER",
        "name": "饥饿",
        "core": "胃口就是身体。饿到一定程度，什么都能吃，什么都能做。",
        "axes": {"BODY": 1, "SOC": 1, "POC": 1, "MIND": 1},
        "hooks": ["DINNER", "BEAST", "TIME", "SELF"],
        "scene": "空锅、啃过的骨头、数着的日子",
        "beat": "断粮 → 第一个提议 → 没人反对",
    },
    {
        "id": "PLAGUE",
        "name": "疫病",
        "core": "秩序先于人体崩坏。腐烂是慢的，慢得足够发生很多事。",
        "axes": {"DEATH": 1, "SOC": 2, "BODY": 1, "MIND": 1},
        "hooks": ["TIME", "ROT", "CORPSE_WET", "MECHANICAL", "COLD"],
        "scene": "封条、石灰、来不及埋的人",
        "beat": "封门 → 里面的日子 → 最后一个还活着的",
    },
    {
        "id": "MOTHER_DAUGHTER",
        "name": "母女",
        "core": "爱的形式就是继承下来的暴力。她把受过的全套交给女儿。",
        "axes": {"PROX": 2, "MIND": 2, "SOC": 1},
        "hooks": ["INCEST", "MOTHER", "DELUSION", "SILENCE"],
        "scene": "梳头、束胸、教她怎么忍",
        "beat": "教会 → 用上 → 她说「我这是为你好」",
    },
    {
        "id": "FATHER_SON",
        "name": "父子",
        "core": "继承、阉割与取代。最像自己的人，必须被自己先动一次手。",
        "axes": {"PROX": 2, "POC": 1, "MIND": 1, "BODY": 1},
        "hooks": ["INCEST", "AMPUTATE", "DELUSION", "WITNESS"],
        "scene": "祠堂、家法、递过来的刀",
        "beat": "跪下 → 自己动手 → 他照做了",
    },
    {
        "id": "MARRIAGE_BED",
        "name": "婚床",
        "core": "合法的地方最没有退路。所有的礼貌都只是慢一点。",
        "axes": {"PROX": 2, "SOC": 1, "POC": 1, "MIND": 1},
        "hooks": ["MOTHER", "PREGNANT", "DELUSION", "WET"],
        "scene": "喜帐、合卺酒、窗外听房的人",
        "beat": "关门 → 熄灯 → 天亮要见人",
    },
    {
        "id": "SILENT_SLAVE",
        "name": "彻底的沉默",
        "core": "她不再说话。不是因为不能说，是因为说出来没有用。",
        "axes": {"MIND": 2, "BODY": 1, "PROX": 1, "AES": 1},
        "hooks": ["SILENCE", "INCONT", "COLD", "SELF"],
        "scene": "空白的脸、按时的动作",
        "beat": "问 → 没有回答 → 继续",
    },
    {
        "id": "SELF_DESTRUCT",
        "name": "自毁",
        "core": "她自己动的手。这一层永远比外人施暴更让人合不上眼。",
        "axes": {"MIND": 2, "BODY": 1, "PROX": 1, "DEATH": 1},
        "hooks": ["SELF", "DISFIGURE", "SILENCE", "NEEDLE"],
        "scene": "碎瓷、掌心、半夜的盆",
        "beat": "她划下去 → 看着血 → 说没事",
    },
    {
        "id": "BODY_HISTORY",
        "name": "身体编年",
        "core": "用疤痕、妊娠、伤口做时间轴。身体是唯一不会说谎的记录。",
        "axes": {"BODY": 2, "AES": 1, "MIND": 1, "DEATH": 1},
        "hooks": ["TIME", "WET", "MISCARRIAGE", "COLD"],
        "scene": "同一件旧衣、逐年松掉的系带",
        "beat": "第一道疤 → 第十道 → 她数得清",
    },
    {
        "id": "FLUID_DIARY",
        "name": "污物与失禁",
        "core": "羞耻的实况：控制不住的那一部分，才是最诚实的证词。",
        "axes": {"BODY": 2, "PROX": 2, "MIND": 1},
        "hooks": ["INCONT", "WET", "SERVANT", "SILENCE"],
        "scene": "床单、地砖缝、来不及的那一步",
        "beat": "忍不住 → 被看见 → 没人提",
    },
    {
        "id": "DROWNING",
        "name": "溺与沉",
        "core": "臣服是一种缺氧。下去的人不再挣扎，因为挣扎也没有用。",
        "axes": {"DEATH": 1, "BODY": 1, "MIND": 2, "PROX": 1},
        "hooks": ["STRANGLE", "WET", "SILENCE", "BEAST"],
        "scene": "水面、浴桶、按住后颈的手",
        "beat": "沉 → 冒泡 → 提起来的那口气",
    },
    {
        "id": "AFTERMATH",
        "name": "事后",
        "core": "最狠的一段在门关上以后：收拾、洗手、吃饭、明天照常。",
        "axes": {"DEATH": 2, "AES": 1, "SOC": 1, "MIND": 1},
        "hooks": ["DEFILE_BODY", "TIME", "COLD", "SILENCE"],
        "scene": "水盆、拖把、第二天的早饭",
        "beat": "收拾 → 洗手 → 照常",
    },
    {
        "id": "LULLABY",
        "name": "摇篮与产声",
        "core": "最软的东西被用最狠的方式。婴儿的哭声能给任何场景加压。",
        "axes": {"PROX": 2, "DEATH": 1, "BODY": 1, "SOC": 1},
        "hooks": ["INFANT", "BIRTH", "MOTHER", "WET"],
        "scene": "摇篮、奶渍、被打断的那一次",
        "beat": "孩子哭 → 伸手被按住 → 继续",
    },
    {
        "id": "WINTER_FAST",
        "name": "荒年",
        "core": "资源就是身体。冬天很长，春天未必来。",
        "axes": {"SOC": 1, "BODY": 1, "POC": 1, "MIND": 1},
        "hooks": ["DINNER", "TIME", "BEAST", "SELF"],
        "scene": "雪、空仓、烧掉的家具",
        "beat": "算粮 → 少一个人 → 谁先",
    },
    {
        "id": "VORE",
        "name": "整吞",
        "core": "一个人被完整地吞进去，还活着。消化是接下来几天的事。",
        "axes": {"BODY": 2, "DEATH": 1, "MIND": 1, "POC": 1},
        "hooks": ["VORE", "DINNER", "BEAST", "SILENCE"],
        "scene": "喉咙、胃袋、被撑起的轮廓",
        "beat": "含住 → 咽下 → 里面的动静渐渐没有",
    },
    {
        "id": "UNBIRTH",
        "name": "归胎",
        "core": "被塞回子宫，重做一次未出生的东西。出口就是入口。",
        "axes": {"BODY": 2, "MIND": 2, "PROX": 1},
        "hooks": ["UNBIRTH", "VORE", "MOTHER", "SILENCE"],
        "scene": "产道、暗处、被合拢的腿",
        "beat": "推进去 → 合拢 → 等她自己出来，或者不出来",
    },
    {
        "id": "INFLATION",
        "name": "膨胀",
        "core": "往身体里灌，直到它不再像身体。破裂是可预期的终点。",
        "axes": {"BODY": 2, "POC": 1, "PROX": 1},
        "hooks": ["INFLATE", "WET", "MECHANICAL", "BIRTH"],
        "scene": "皮下的纹路、灌口、量尺",
        "beat": "接上 → 灌 → 皮肤开始发亮",
    },
    {
        "id": "REMODEL",
        "name": "改造",
        "core": "身体被重新设计成另一个用途。原来的功能是错的。",
        "axes": {"BODY": 2, "MIND": 2, "POC": 1},
        "hooks": ["REMODEL", "MEDICAL", "MECHANICAL", "OBJECT"],
        "scene": "图纸、缝合线、被标出的接口",
        "beat": "画线 → 切开 → 装上去试一次",
    },
    {
        "id": "OBJECTIFY",
        "name": "物化",
        "core": "她是一件家具。这个说法不是比喻，是使用说明。",
        "axes": {"MIND": 2, "POC": 2, "PROX": 1},
        "hooks": ["OBJECT", "DOLL", "SERVANT", "SILENCE"],
        "scene": "椅背、脚凳、被擦干净的表面",
        "beat": "摆好 → 坐上去 → 用完不管",
    },
    {
        "id": "MEATHOOK",
        "name": "肉钩",
        "core": "用钩子把人挂起来，然后像处理牲口一样处理。重量全落在皮肉上。",
        "axes": {"BODY": 2, "DEATH": 1, "POC": 1, "SOC": 1},
        "hooks": ["HOOKPULL", "WOUND_SEX", "AMPUTATE", "WITNESS"],
        "scene": "冷库、铁钩、离地的脚",
        "beat": "下钩 → 挂起 → 开始分割",
    },
    {
        "id": "BRANDING",
        "name": "烙印",
        "core": "在皮肤上留下归属的证明。烧进去的字，一辈子洗不掉。",
        "axes": {"PROX": 2, "BODY": 1, "POC": 1, "MIND": 1},
        "hooks": ["BRAND", "BURN", "DISFIGURE", "SERVANT"],
        "scene": "烧红的铁、压住肩的手、焦味",
        "beat": "按住 → 压下去 → 之后她自己去摸那道疤",
    },
    {
        "id": "DENTAL",
        "name": "齿与口",
        "core": "嘴是唯一能咬人的器官。所以先处理牙。",
        "axes": {"BODY": 2, "PROX": 2, "POC": 1},
        "hooks": ["TOOTH", "MEDICAL", "SILENCE", "NEEDLE"],
        "scene": "开口器、钳子、托盘里的白",
        "beat": "撑开 → 拔 → 她还能不能咬",
    },
    {
        "id": "WOUND",
        "name": "伤口",
        "core": "伤口不是意外，是入口。它比任何孔洞都更属于你。",
        "axes": {"BODY": 2, "PROX": 2, "DEATH": 1},
        "hooks": ["WOUND_SEX", "AMPUTATE", "MEDICAL", "WET"],
        "scene": "敞开的创面、渗出的边、手指",
        "beat": "划开 → 进去 → 缝起来留着下次",
    },
    {
        "id": "TAXIDERMY",
        "name": "剥制",
        "core": "把一个人做成标本，姿势由制作者决定。她会一直保持这个姿势。",
        "axes": {"DEATH": 2, "BODY": 2, "AES": 1, "MIND": 1},
        "hooks": ["TAXIDERM", "ROT", "OBJECT", "DOLL"],
        "scene": "支架、玻璃眼、填充的棉",
        "beat": "剥 → 撑起来 → 摆成他喜欢的样子",
    },
    {
        "id": "SENSORY",
        "name": "感官剥夺",
        "core": "先拿走眼睛，再拿走耳朵。剩下的人只能靠皮肤活着。",
        "axes": {"MIND": 2, "BODY": 1, "PROX": 1},
        "hooks": ["DEPRIVE", "SILENCE", "MECHANICAL", "EYE"],
        "scene": "眼罩、耳塞、被绑住的手",
        "beat": "蒙上 → 等 → 她开始自己数时间",
    },
    {
        "id": "IMMOLATION",
        "name": "火",
        "core": "烧是唯一会自己继续下去的伤害。你点着以后就可以走开。",
        "axes": {"BODY": 2, "DEATH": 2, "SOC": 1},
        "hooks": ["BURN", "DISFIGURE", "WITNESS", "SACRIFICE"],
        "scene": "油、火把、焦黑的边",
        "beat": "浇上 → 点着 → 退开看",
    },
    {
        "id": "CRUSHING",
        "name": "碾压",
        "core": "不是切割，是压。骨头先断，形状随后改变。",
        "axes": {"BODY": 2, "DEATH": 1, "POC": 1},
        "hooks": ["CRUSH", "MECHANICAL", "WITNESS", "BEAST"],
        "scene": "石碾、车轮、脚下的地",
        "beat": "放进去 → 压 → 声音先变，形状后变",
    },
    {
        "id": "PARASITISM",
        "name": "寄生",
        "core": "身体里住进了别的东西。它需要她活着，但只需要她活着。",
        "axes": {"BODY": 2, "MIND": 2, "PROX": 1},
        "hooks": ["PARASITE", "INSECT", "BIRTH", "SILENCE"],
        "scene": "皮下走动的线、鼓起的腹、吐出",
        "beat": "进去 → 长大 → 出来，或者不出来",
    },
    {
        "id": "MIND_BREAK",
        "name": "心智崩坏",
        "core": "不打身体，打里面那根轴。崩了以后她会笑着说谢谢。",
        "axes": {"MIND": 2, "PROX": 2, "POC": 1},
        "hooks": ["MIND_BREAK", "DELUSION", "SILENCE", "DOLL"],
        "scene": "重复的问话、被拿走的睡眠、空掉的眼睛",
        "beat": "追问 → 拆开 → 她开始自己替他说完",
    },
    {
        "id": "PUPPET",
        "name": "人偶",
        "core": "关节被换掉，动作由别人给。她还在里面，只是不再指挥。",
        "axes": {"MIND": 2, "BODY": 1, "POC": 2},
        "hooks": ["DOLL", "OBJECT", "REMODEL", "MECHANICAL"],
        "scene": "绳、关节、被摆好的坐姿",
        "beat": "穿线 → 拉起 → 让她自己走两步",
    },
    {
        "id": "BLUNT_TRAUMA",
        "name": "钝击",
        "core": "没有破口，没有血。打进去的东西在皮下继续坏。",
        "axes": {"BODY": 2, "POC": 1, "PROX": 1},
        "hooks": ["BLUNT", "CRUSH", "WITNESS", "MEDICAL"],
        "scene": "拳、靴底、腹部那块正在变色的皮肤",
        "beat": "打上去 → 她还没倒 → 三天后内出血才要命",
    },
    {
        "id": "FLAYING",
        "name": "剥皮",
        "core": "皮是器官，不是包装。取下来以后人还活着，只是不能再被碰。",
        "axes": {"BODY": 2, "DEATH": 1, "PROX": 1, "SOC": 1},
        "hooks": ["FLAY", "AMPUTATE", "MEDICAL", "WITNESS"],
        "scene": "钩子、刀锋走向、翻起来的那一层",
        "beat": "划开 → 分离 → 她开始怕风",
    },
    {
        "id": "IMPALEMENT",
        "name": "贯穿",
        "core": "东西留在里面，从另一头出来。她从此被固定在某个位置。",
        "axes": {"BODY": 2, "DEATH": 1, "POC": 1, "SOC": 1},
        "hooks": ["IMPALE", "HOOKPULL", "WITNESS", "MECHANICAL"],
        "scene": "木桩、铁杆、被钉住的影子",
        "beat": "对准 → 贯穿 → 她还得自己撑着不掉下去",
    },
    {
        "id": "BURIAL",
        "name": "活埋与幽闭",
        "core": "刑具是空间本身。她动不了，也不知道外面过了多久。",
        "axes": {"DEATH": 2, "MIND": 2, "BODY": 1},
        "hooks": ["BURY", "DEPRIVE", "SILENCE", "STRANGLE"],
        "scene": "土、箱壁、越来越少的空气",
        "beat": "盖住 → 等 → 她开始数自己的呼吸",
    },
    {
        "id": "FREEZING",
        "name": "冻",
        "core": "低温不制造伤口，它只是让一切慢下来，然后停下。",
        "axes": {"BODY": 2, "DEATH": 2, "MIND": 1},
        "hooks": ["FREEZE", "AMPUTATE", "TIME", "SILENCE"],
        "scene": "霜、发黑的指尖、开始不觉得冷的那一刻",
        "beat": "降温 → 冻伤 → 她以为暖和了，那才是最危险的信号",
    },
    {
        "id": "DEFORMITY",
        "name": "畸形",
        "core": "没有凶手。身体自己长成了不该长的样子，而这就是全部。",
        "axes": {"BODY": 2, "SOC": 1, "MIND": 1, "AES": 1},
        "hooks": ["DEFORM", "MEDICAL", "OBJECT", "WITNESS"],
        "scene": "标本罐、幕布、不敢看的接生婆",
        "beat": "生下来 → 被展示 → 她自己学着怎么遮",
    },
    {
        "id": "HEMICORPORE",
        "name": "半身",
        "core": "腰以下没有了。她还活着，只是从此只能看着别人走路。",
        "axes": {"BODY": 2, "DEATH": 1, "MIND": 1},
        "hooks": ["HEMICORP", "AMPUTATE", "MEDICAL", "DEPRIVE"],
        "scene": "手术台、齐整的断面、轮椅",
        "beat": "截断 → 缝合 → 她学会用手撑着自己移动",
    },
    {
        "id": "VOMITING",
        "name": "呕吐",
        "core": "反向的排出。身体拒绝接受，而拒绝的样子本身被拿去用了。",
        "axes": {"BODY": 2, "PROX": 2, "MIND": 1},
        "hooks": ["VOMIT", "THROAT", "INCONT", "SILENCE"],
        "scene": "喉咙的痉挛、地上的那摊、被按回去的头",
        "beat": "灌 → 拒绝 → 按回去继续",
    },
    {
        "id": "NAIL_BED",
        "name": "指甲",
        "core": "最小的面积，最密的神经。取下来以后她连握都握不住。",
        "axes": {"BODY": 2, "PROX": 1},
        "hooks": ["NAIL", "NEEDLE", "MEDICAL", "SILENCE"],
        "scene": "指尖、钳口、地上的十片",
        "beat": "掀开 → 拔出 → 她试着握拳，握不上",
    },
    {
        "id": "DILATION",
        "name": "过度扩张",
        "core": "孔洞被撑到解剖学的极限之外，然后继续。",
        "axes": {"BODY": 2, "PROX": 2, "POC": 1},
        "hooks": ["DILATE", "WOUND_SEX", "MEDICAL", "WET"],
        "scene": "拳、器械、被撑到发白的边缘",
        "beat": "进入 → 再加 → 那里不再能合上",
    },
    {
        "id": "THROAT",
        "name": "深喉与食道",
        "core": "喉咙是一条管子。它被当成管子用的时候，呼吸是别人的。",
        "axes": {"BODY": 2, "POC": 2, "PROX": 1},
        "hooks": ["THROAT", "STRANGLE", "VOMIT", "INCONT"],
        "scene": "颈部的凸起、不行了的手势、被按住的后脑",
        "beat": "推进 → 干呕 → 他等她适应，再继续",
    },
    {
        "id": "ANESTHESIA",
        "name": "麻醉",
        "core": "全程清醒，只是感觉不到。她看着自己被打开。",
        "axes": {"MIND": 2, "BODY": 2, "AES": 1},
        "hooks": ["ANESTH", "MEDICAL", "AMPUTATE", "DEPRIVE"],
        "scene": "无影灯、说不出口的嘴、自己抬不起来的手",
        "beat": "注射 → 看着刀落下 → 没有痛，只有位移感",
    },
]

TOPIC_BY_ID = {t["id"]: t for t in TOPICS}

# ---------------------------------------------------------------- 禁忌表
# 用轴与钩子描述负向过滤器。

TABOOS = [
    ("BLOOD", "血 / 伤口 / 见血的疼", ["AMPUTATE", "DISFIGURE", "NEEDLE", "REGICIDE"]),
    ("CORPSE", "尸体 / 与死者有关的事（不含腐烂）", ["DEFILE_BODY", "CORPSE_BRIDE", "CORPSE_WET", "TAXIDERM"]),
    ("PUTREFY", "腐烂 / 腐朽 / 分解", ["ROT"]),
    ("PREGNANT", "怀孕 / 生产 / 流产", ["PREGNANT", "BIRTH", "MISCARRIAGE", "INFANT"]),
    ("KIN", "亲缘 / 家人之间", ["INCEST"]),
    ("CHILD", "幼体在场 / 未成年", ["INFANT"]),
    ("BEAST", "兽交 / 异种", ["BEAST", "INSECT"]),
    ("PUBLIC", "公开 / 被看见 / 围观", ["WITNESS", "SERVANT"]),
    ("SUBMIT", "被剥夺意志 / 催眠 / 洗脑", ["SILENCE", "SELF"]),
    ("HUMILIATE", "排泄 / 污物（不含体液）", ["INCONT"]),
]

# 软禁区：不做否决，只压分。用来表达"这个我不吃，但不必因此废掉整个题材"。
SOFT_TABOOS = [
    ("NO_SEX", "不要性的部分（只要暴力、恐怖与权力）", "PROX"),
    ("NO_ROMANCE", "不要内在戏（只要外部实况与制度）", "MIND"),
]

# ---------------------------------------------------------------- 呈现配方

SCENES = ["古代宫廷 / 王朝", "当代都市", "近未来 / 机构", "乡土 / 荒野", "无明确地点"]
RELATIONS = ["血亲", "配偶 / 契约", "主仆 / 上对下", "陌生 / 捕获", "敌我", "自己与另一个自己"]
POVS = ["施害者", "受害者", "旁观者", "双线交替"]
TONES = ["冷叙述（档案体）", "慢镜（生理实况）", "诗性（意象稠密）", "白描（不修饰）"]
LENGTHS = ["短篇（单场景）", "中篇（三到五幕）", "章节（长篇的一段）"]


# ---------------------------------------------------------------- 交互

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def rule(ch="=", n=64):
    print(ch * n)


def title(s):
    print()
    rule()
    print("  " + s)
    rule()


def ask_multi(prompt, n_items, max_pick=None, min_pick=1, allow_empty=False):
    """读一行编号，返回 0-based 索引集合。"""
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            sys.exit(0)
        if raw.lower() in ("q", "quit", "exit"):
            sys.exit(0)
        if raw == "":
            if allow_empty:
                return set()
            print("  这里必须给编号（至少 %d 个）。" % min_pick)
            continue
        parts = [p for p in raw.replace(",", " ").replace("，", " ").replace("、", " ").split() if p]
        idx = set()
        bad = False
        for p in parts:
            if not p.isdigit():
                bad = True
                break
            i = int(p) - 1
            if i < 0 or i >= n_items:
                bad = True
                break
            idx.add(i)
        if bad:
            print("  只输入 1 到 %d 之间的编号，用空格或逗号分开。" % n_items)
            continue
        if max_pick and len(idx) > max_pick:
            print("  最多 %d 个，你给了 %d 个。删掉一些。" % (max_pick, len(idx)))
            continue
        if len(idx) < min_pick:
            print("  至少 %d 个，你给了 %d 个。" % (min_pick, len(idx)))
            continue
        return idx


def ask_single(prompt, n_items):
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            sys.exit(0)
        if raw.lower() in ("q", "quit", "exit"):
            sys.exit(0)
        if raw.isdigit() and 1 <= int(raw) <= n_items:
            return int(raw) - 1
        print("  输入 1 到 %d 之间的一个编号。" % n_items)


def menu(items_lines):
    for i, line in enumerate(items_lines, 1):
        print("  %2d  %s" % (i, line))


# ---------------------------------------------------------------- 主流程

def run_quiz():
    clear()
    title("R18G 题材匹配问卷  ·  v2")
    print("""
  这套问卷不问你"喜欢哪个题材"——没有人答得出来。
  它问的是：你在哪几根轴上被击中，又绝对不能碰什么。
  答完我把 40 个题材按你的坐标重新排一遍，再给出一个能直接开写的配方。

  规则：输入编号，空格或逗号分隔；q 退出。
""")

    # ---- 第一轮：坐标
    title("第一轮 / 三题  ·  你被什么击中")
    print("\n【1】七根轴里，选 2 个最狠的（选 2 个，不要多）\n")
    menu(["%s —— %s（%s）" % (a[1], a[2], a[0]) for a in AXES])
    main_idx = ask_multi("\n  > 主选两根轴： ", len(AXES), min_pick=2, max_pick=2)

    print("\n【2】接下来是副力区：还有哪些你也吃得下（最多 3 个，可空）\n")
    menu(["%s —— %s" % (a[1], a[2]) for a in AXES])
    soft_idx = ask_multi("\n  > 副选： ", len(AXES), max_pick=3, allow_empty=True)

    print("\n【3】钩子：下面这些具体的画面，哪几样会让你坐直（2 到 5 个）\n")
    hook_list = list(HOOKS.items())
    menu(["%s" % h[1] for h in hook_list])
    hook_idx = ask_multi("\n  > 钩子： ", len(hook_list), min_pick=2, max_pick=5)

    # ---- 第二轮：禁忌
    title("第二轮 / 两题  ·  划掉不吃的东西")
    print("\n【4】硬禁区 —— 踩中就整类作废（可多选，可空）\n")
    menu(["%s" % t[1] for t in TABOOS])
    taboo_idx = ask_multi("\n  > 硬禁区： ", len(TABOOS), allow_empty=True)

    print("\n【5】软偏好 —— 不吃但不必废掉整个题材，只往后压（可多选，可空）\n")
    menu(["%s" % t[1] for t in SOFT_TABOOS])
    soft_idx2 = ask_multi("\n  > 软偏好： ", len(SOFT_TABOOS), allow_empty=True)

    # ---- 第三轮：配方
    title("第三轮 / 五题  ·  成品配方")
    print("\n【6】场景  ——  故事发生在哪\n")
    menu(SCENES)
    sc = ask_single("\n  > 场景： ", len(SCENES))

    print("\n【7】关系  ——  动手的与承受的是什么关系\n")
    menu(RELATIONS)
    rel = ask_single("\n  > 关系： ", len(RELATIONS))

    print("\n【8】视角  ——  镜头放在谁身上\n")
    menu(POVS)
    pov = ask_single("\n  > 视角： ", len(POVS))

    print("\n【9】笔法  ——  用哪种舌头说这件事\n")
    menu(TONES)
    tone = ask_single("\n  > 笔法： ", len(TONES))

    print("\n【10】长度  ——  这次要多大一块\n")
    menu(LENGTHS)
    ln = ask_single("\n  > 长度： ", len(LENGTHS))

    # ---- 第四轮：定盘取舍
    title("第四轮 / 两题  ·  定盘")
    print("\n【11】这一次，你要的是哪一种落法\n")
    menu(["一次到底（单场景，冲到最高再停）", "长期日常（同样的伤口重复发生很多次）"])
    shape = ask_single("\n  > 形状： ", 2)

    print("\n【12】结尾允许死吗\n")
    menu(["死（死是那一声钝响）", "活（活下来才是更长的刑）", "随便，看情节走到哪"])
    ending = ask_single("\n  > 结尾： ", 3)

    return {
        "main": [AXES[i][0] for i in main_idx],
        "soft": [AXES[i][0] for i in soft_idx],
        "hooks": [hook_list[i][0] for i in hook_idx],
        "taboos": [TABOOS[i][0] for i in taboo_idx],
        "soft_taboos": [SOFT_TABOOS[i][0] for i in soft_idx2],
        "scene": SCENES[sc],
        "relation": RELATIONS[rel],
        "pov": POVS[pov],
        "tone": TONES[tone],
        "length": LENGTHS[ln],
        "shape": ["一次到底", "长期日常"][shape],
        "ending": ["死", "活", "看情节"][ending],
    }


# ---------------------------------------------------------------- 打分

def score(ans):
    main = set(ans["main"])
    soft = set(ans["soft"])
    hooks = set(ans["hooks"])

    taboo_hooks = set()
    for tid in ans["taboos"]:
        for h in dict((t[0], t[2]) for t in TABOOS)[tid]:
            taboo_hooks.add(h)

    damp = {}
    for sid in ans.get("soft_taboos", []):
        axis = dict((t[0], t[2]) for t in SOFT_TABOOS)[sid]
        damp[axis] = damp.get(axis, 0) + 1

    rows = []
    axname = dict((a[0], a[1]) for a in AXES)
    for t in TOPICS:
        s = 0.0
        reasons = []
        full = []

        for ax, w in t["axes"].items():
            mult = 1.0
            if ax in damp:
                mult = 0.45 if damp[ax] == 1 else 0.2
            if ax in main:
                s += w * 3.0 * mult
                if w >= 2 and mult == 1.0:
                    full.append(axname[ax])
            elif ax in soft:
                s += w * 1.5 * mult
            elif w > 0:
                s += w * 0.5 * mult

        if full:
            reasons.append("主轴上满格：" + "、".join(full))

        hit = [h for h in t["hooks"] if h in hooks]
        s += len(hit) * 2.0
        if hit:
            reasons.append("命中钩子：" + "、".join(HOOKS[h] for h in hit))

        veto = [h for h in t["hooks"] if h in taboo_hooks]
        s -= len(veto) * 7.0
        if veto:
            reasons.append("踩禁区：" + "、".join(HOOKS[h] for h in veto))

        rows.append({"topic": t, "score": s, "reasons": reasons, "veto": bool(veto), "hit": hit})

    rows.sort(key=lambda r: (-r["score"], r["topic"]["id"]))
    return rows


def band(score, top, bottom):
    if top <= bottom:
        return 0.0
    v = (score - bottom) / (top - bottom)
    return max(0.0, min(1.0, v))


def render(ans, rows):
    usable = [r for r in rows if not r["veto"]]
    top = usable[:8]
    lo = min(r["score"] for r in rows)
    hi = max(r["score"] for r in rows)

    axname = dict((a[0], a[1]) for a in AXES)

    title("匹配结果")

    print("\n  坐标：")
    print("    主轴  " + " / ".join(axname[a] for a in ans["main"]))
    if ans["soft"]:
        print("    副轴  " + " / ".join(axname[a] for a in ans["soft"]))
    print("    钩子  " + (" / ".join(HOOKS[h] for h in ans["hooks"]) if ans["hooks"] else "（未选）"))
    print("    禁硬  " + (" / ".join(dict((t[0], t[1]) for t in TABOOS)[x] for x in ans["taboos"]) if ans["taboos"] else "（无）"))
    if ans.get("soft_taboos"):
        print("    禁软  " + " / ".join(dict((t[0], t[1]) for t in SOFT_TABOOS)[x] for x in ans["soft_taboos"]))

    print("\n  题材排序：\n")
    for i, r in enumerate(top, 1):
        t = r["topic"]
        pct = band(r["score"], lo, hi)
        bar = "#" * int(round(pct * 28))
        print("  %2d  %-12s %5.1f  %s" % (i, t["name"], r["score"], bar))
        print("      %s" % t["core"])
        if r["reasons"]:
            print("      · " + "；".join(r["reasons"]))
        print()

    vetoed = [r for r in rows if r["veto"]][:3]
    if vetoed:
        print("  ── 被禁区划掉的（供你确认是否划得太狠）──")
        for r in vetoed:
            why = "、".join(r["reasons"][-1:]) or "命中硬禁区"
            print("     %s（%s）" % (r["topic"]["name"], why))
        print()

    if not top:
        print("  禁区把所有题材都划掉了。要么放松一条，要么这真不是你的场子。\n")
        return

    best = top[0]["topic"]
    rec_hooks = [HOOKS[h] for h in best["hooks"] if h in set(ans["hooks"])] or [HOOKS[h] for h in best["hooks"][:3]]

    print("  " + "=" * 60)
    print("  首选定盘：" + best["name"])
    print("  " + "=" * 60)
    print("""
  一句话核  %s

  原生场景   %s
  结构三拍   %s
  必带钩子   %s
  配方        %s ／ %s ／ %s视角 ／ %s ／ %s
  规模        %s ／ 结尾%s
""" % (best["core"], best["scene"], best["beat"],
       "、".join(rec_hooks),
       ans["scene"], ans["relation"], ans["pov"], ans["tone"], ans["length"],
       ans["shape"], ans["ending"]))

    if len(top) > 1:
        print("  次选搭子（做副线或下一轮）：" + "、".join(r["topic"]["name"] for r in top[1:4]))

    return best, rec_hooks


# ---------------------------------------------------------------- 落盘

def save(ans, rows, best, rec_hooks):
    usable = [r for r in rows if not r["veto"]][:8]
    axname = dict((a[0], a[1]) for a in AXES)
    now = datetime.datetime.now()
    path = os.path.join(BASE, "选题结果_%s.md" % now.strftime("%m%d_%H%M"))

    lines = []
    lines.append("# R18G 选题结果  %s\n" % now.strftime("%Y-%m-%d %H:%M"))
    lines.append("## 一、坐标\n")
    lines.append("| 项 | 内容 |")
    lines.append("|---|---|")
    lines.append("| 主轴 | %s |" % " / ".join(axname[a] for a in ans["main"]))
    lines.append("| 副轴 | %s |" % (" / ".join(axname[a] for a in ans["soft"]) or "—"))
    lines.append("| 钩子 | %s |" % (" / ".join(HOOKS[h] for h in ans["hooks"]) or "—"))
    lines.append("| 禁区 | %s |" % (" / ".join(dict((t[0], t[1]) for t in TABOOS)[x] for x in ans["taboos"]) or "无"))
    lines.append("| 软禁区 | %s |" % (" / ".join(dict((t[0], t[1]) for t in SOFT_TABOOS)[x] for x in ans.get("soft_taboos", [])) or "无"))
    lines.append("| 规模 | %s |" % ans["shape"])
    lines.append("| 结尾 | %s |" % ans["ending"])
    lines.append("")
    lines.append("## 二、排序\n")
    for i, r in enumerate(usable, 1):
        lines.append("%d. **%s**（%.1f）" % (i, r["topic"]["name"], r["score"]))
        lines.append("   - %s" % r["topic"]["core"])
        if r["reasons"]:
            lines.append("   - " + "；".join(r["reasons"]))
    lines.append("")

    if best:
        lines.append("## 三、开工单\n")
        lines.append("- 定盘题材：**%s**" % best["name"])
        lines.append("- 一句话核：%s" % best["core"])
        lines.append("- 原生场景：%s" % best["scene"])
        lines.append("- 结构三拍：%s" % best["beat"])
        lines.append("- 必带钩子：%s" % "、".join(rec_hooks))
        lines.append("- 配方：%s ／ %s ／ %s视角 ／ %s ／ %s" % (
            ans["scene"], ans["relation"], ans["pov"], ans["tone"], ans["length"]))
        lines.append("- 规模：%s" % ans["shape"])
        lines.append("- 结尾：%s" % ans["ending"])
        lines.append("")
        lines.append("### 三个必须写到的细节（照这个密度写，不许抽象）")
        lines.append("1. ")
        lines.append("2. ")
        lines.append("3. ")
        lines.append("")
        lines.append("### 本单自检")
        lines.append("- [ ] 每一段都有身体实况，没有一句是作者在评价")
        lines.append("- [ ] 承受者有自己的内在，不只是道具")
        lines.append("- [ ] 结尾没有救赎，情节自己耗尽")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ---------------------------------------------------------------- 命令行

def cmd_list():
    print("\n  ── 七轴 ──")
    for a in AXES:
        print("  %-5s %-10s %s" % (a[0], a[1], a[2]))
    print("\n  ── 钩子 %d ──" % len(HOOKS))
    for k, v in HOOKS.items():
        print("  %-14s %s" % (k, v))
    print("\n  ── 题材 %d ──" % len(TOPICS))
    for i, t in enumerate(TOPICS, 1):
        print("  %2d  %-12s %s" % (i, t["name"], t["core"]))
    print()


def cmd_topic(n):
    i = n - 1
    if i < 0 or i >= len(TOPICS):
        print("  没有第 %d 个题材。" % n)
        return
    t = TOPICS[i]
    axname = dict((a[0], a[1]) for a in AXES)
    print("\n  【%d】%s" % (n, t["name"]))
    print("  核：%s" % t["core"])
    print("  轴：" + "  ".join("%s%+d" % (axname[k], v) for k, v in t["axes"].items()))
    print("  钩：" + "、".join(HOOKS[h] for h in t["hooks"]))
    print("  景：%s" % t["scene"])
    print("  拍：%s\n" % t["beat"])


def main():
    args = sys.argv[1:]
    if args and args[0] == "list":
        cmd_list()
        return
    if args and args[0] == "topic" and len(args) > 1 and args[1].isdigit():
        cmd_topic(int(args[1]))
        return

    ans = run_quiz()
    rows = score(ans)
    out = render(ans, rows)
    best, rec_hooks = (out if out else (None, []))

    title("已落盘")
    print("  题库自检：%d 题材 / %d 钩子 / %d 轴" % (len(TOPICS), len(HOOKS), len(AXES)))
    if best:
        p = save(ans, rows, best, rec_hooks)
        print("  结果：%s" % p)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  中断。\n")
