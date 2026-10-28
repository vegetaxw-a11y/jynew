"""神雕侠侣 MOD 的配置表生成脚本（可重复执行，幂等）。

把 SAMPLE 模板的配置表改造成《神雕侠侣》的世界：地图、人物、武功、物品，
并把大地图 1000_daditu 上用来匹配地图名的 GameObject 同步改名。

用法：
    python tools/shendiao/apply_configs.py
"""
from __future__ import annotations

import os
import re
import sys

import openpyxl
import xlsxwriter
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD_ID = "shendiao"
MOD_DIR = os.path.join(ROOT, "jyx2", "Assets", "Mods", MOD_ID)
CFG_DIR = os.path.join(MOD_DIR, "Configs")
DADITU = os.path.join(MOD_DIR, "Maps", "GameMaps", "1000_daditu.unity")
MOD_SETTING = os.path.join(MOD_DIR, "ModSetting.asset")

# ---------------------------------------------------------------------------
# 地图：Id -> 新名字（神雕侠侣的地理）
# 只改地图显示名，场景文件不动；大地图上同名 GameObject 会一起改名，
# 因为 MapTeleportor 是用 GameObject 名字去匹配 Map.Name 的。
# ---------------------------------------------------------------------------
MAP_RENAME = {
    0: "嘉兴·铁枪庙",
    1: "终南山·重阳宫",
    2: "终南山·活死人墓",
    3: "陆家庄",
    4: "襄阳城",
    5: "临安·醉仙楼",
    6: "襄阳·安抚使府",
    7: "绝情谷",
    8: "风陵渡",
    9: "华山之巅",
    10: "桃花岛",
    11: "大胜关",
    12: "终南山·后山",
    13: "万兽山庄",
    14: "黑沼",
    15: "断肠崖",
    16: "蒙古大营",
    17: "牛家村",
    18: "独孤剑冢",
    19: "重阳宫·藏经阁",
}

# ---------------------------------------------------------------------------
# 人物：Id -> (姓名, 模型文件名或 None 表示不改)
# 模型必须能在 Mods/shendiao/Models/*.asset 里找到，否则换了会白模。
# 模板里的女性模型只有 佟雯 / 牛妞妞 / 曼陀谷弟子 三个。
# ---------------------------------------------------------------------------
CHAR_RENAME = {
    0: ("杨过", "童四二"),            # 主角，少年
    10: ("郭靖", "王远"),
    11: ("黄蓉", "佟雯"),
    20: ("赵志敬", None),
    21: ("孙婆婆", None),
    22: ("小龙女", "牛妞妞"),
    30: ("柯镇恶", None),
    31: ("洪七公", None),
    40: ("欧阳锋", None),
    41: ("郭芙", "曼陀谷弟子"),
    42: ("武敦儒", None),
    60: ("鹿清笃", "何云多"),
    70: ("李莫愁", None),
    90: ("程英", None),
    111: ("庙祝", None),
    123: ("孙不二", None),
}

# 性别：0 男 1 女
CHAR_FEMALE = {11, 22, 41, 70, 90, 123}

# 外号（第 5 列，没有字段名，不参与游戏逻辑，只让人看表时清楚）
CHAR_NICKNAME = {
    0: "神雕大侠", 10: "北侠", 11: "桃花岛主之女", 20: "全真教三代首座",
    21: "古墓派老仆", 22: "古墓派掌门", 30: "江南七怪之首", 31: "北丐",
    40: "西毒", 41: "郭靖之女", 42: "郭靖弟子", 60: "全真教弟子",
    70: "赤练仙子", 90: "陆家庄表妹", 111: "铁枪庙庙祝", 123: "全真七子",
}

# ---------------------------------------------------------------------------
# 武功：Id -> 新名字（不碰 DisplayFileName，那里是特效/动作资源名）
# ---------------------------------------------------------------------------
SKILL_RENAME = {
    0: "普通攻击",
    1: "全真剑法",
    10: "玉女剑法",
    20: "玉女素心剑",
    30: "全真拳法",
    31: "蛤蟆功",
    32: "九阴疗伤篇",
    33: "黯然销魂掌",
    40: "玄铁剑法",
    41: "打狗棒法",
    42: "弹指神通",
    60: "落英神剑掌",
    61: "一阳指",
    62: "铁掌水上漂",
    70: "冰魄银针",
    71: "玉箫剑法",
    72: "五毒神掌",
    90: "美女拳法",
    91: "摧心掌",
    120: "天竺疗伤",
    181: "分花拂柳手",
    190: "金铃索法",
    93: "用毒",
    94: "解毒",
    95: "医疗",
    97: "暗器",
}

# ---------------------------------------------------------------------------
# 物品：Id -> (新名字, 新说明 or None 表示保留)
# ---------------------------------------------------------------------------
ITEM_RENAME = {
    0: ("铜钥匙", "一把普通的铜钥匙"),
    1: ("全真剑法秘籍", "全真教入门剑法，中正平和"),
    10: ("女儿红", "江南名酒，醇厚甘美"),
    11: ("铁钥匙", "锈迹斑斑的铁钥匙"),
    12: ("玉女剑法秘籍", "古墓派剑法，轻灵飘逸"),
    13: ("竹棒", "随手削成的竹棒"),
    14: ("轻软靴", "赶路用的软底靴"),
    20: ("玉女素心剑秘籍", "双剑合璧，天下无双"),
    21: ("君子剑", "古墓派珍藏的利剑"),
    22: ("软猬甲", "桃花岛至宝，刀枪难入"),
    23: ("石室钥匙", "活死人墓的石室钥匙"),
    24: ("酒坛", "半人高的酒坛"),
    30: ("九花玉露丸", "桃花岛灵药，服之百毒不侵"),
    31: ("玉女心经秘籍", "古墓派镇派内功"),
    32: ("天蚕宝甲", "天蚕丝织就的宝甲"),
    33: ("九阴真经", "武学总纲，天下奇书"),
    34: ("全真拳法秘籍", "全真教入门拳法"),
    35: ("蛤蟆功秘籍", "西毒欧阳锋的独门内功"),
    36: ("黯然销魂掌秘籍", "黯然销魂者，唯别而已矣"),
    37: ("玉蜂浆", "古墓玉蜂所酿，养气培元"),
    38: ("金疮药", "常见的伤药"),
    39: ("全真剑法残卷", "残缺的剑诀"),
    40: ("止血生肌丸", "伤重时救命的丹药"),
    41: ("玄铁重剑", "重剑无锋，大巧不工"),
    42: ("铁剑", "寻常铁剑"),
    43: ("朴刀", "江湖人常用的朴刀"),
    44: ("熟铜棍", "熟铜打造的长棍"),
    45: ("皮甲", "牛皮制成的护甲"),
    46: ("白虹剑", "剑光如虹"),
    47: ("金丝软甲", "金丝织成的软甲"),
    48: ("藏经阁钥匙", "重阳宫藏经阁的钥匙"),
    49: ("打狗棒法秘籍", "丐帮镇帮绝学"),
    50: ("琥珀杯", "盛酒用的琥珀杯"),
    60: ("玄铁战甲", "重逾百斤的铁甲"),
    61: ("淑女剑", "与君子剑成对的宝剑"),
    62: ("望月刀", "背厚刃宽的刀"),
    63: ("九转熊蛇丸", "灵药，可解百毒"),
    70: ("玉镯子", "素白的玉镯"),
    71: ("冰魄银针", "李莫愁的成名暗器"),
    72: ("解毒奇药", "解百毒"),
    73: ("五毒神掌秘籍", "五毒教掌法，掌风带毒"),
    74: ("紫粟花", "艳丽的毒花"),
    75: ("冰魄银针秘籍", "制作冰魄银针的法门"),
    76: ("玉箫剑法秘籍", "黄药师所创剑法"),
    77: ("古墓派心法", "古墓派的内功心法"),
    80: ("轻功秘籍", "提纵之术"),
    81: ("馒头", "干粮"),
    90: ("烤全羊", "大漠风味的烤肉"),
    91: ("美女拳法秘籍", "古墓派拳法，姿态曼妙"),
    92: ("解牛刀", "屠户用的刀"),
    93: ("摧心掌秘籍", "掌力透体，伤心脉"),
    110: ("雪梨", "清甜的梨子"),
    120: ("青竹补血膏", "外伤药膏"),
    121: ("青竹解毒丸", "解毒丸药"),
    122: ("情花", "绝情谷的情花，刺中有毒"),
    123: ("药材", "寻常草药"),
    124: ("江湖药鉴", "记载天下毒物的书"),
    140: ("貂皮裘", "保暖的貂裘"),
    141: ("冰魄银针", "淬毒的细针"),
    142: ("震狼一击秘籍", "匕首格斗之技"),
    160: ("熊皮袄", "厚实的熊皮衣"),
    161: ("熊胆固气丸", "补气灵药"),
    170: ("陈年花雕", "窖藏多年的好酒"),
    171: ("大饼", "粗面饼子"),
    174: ("银两", "通行天下的银钱"),
    180: ("蛇胆解毒丸", "解蛇毒"),
    181: ("蛇牙针", "淬了蛇毒的针"),
    182: ("分花拂柳手秘籍", "古墓派手法"),
    190: ("紫薇软剑", "软剑如蛇"),
    191: ("青钢剑", "寻常好剑"),
    192: ("青钢刀", "寻常好刀"),
    193: ("青钢棍", "寻常齐眉棍"),
    194: ("青钢甲", "寻常铁甲"),
    195: ("英雄帖", "大胜关英雄大会的请帖"),
    196: ("金铃索法秘籍", "小龙女的金铃索技"),
}


# ---------------------------------------------------------------------------
# 执行部分
# ---------------------------------------------------------------------------

def u_escape(s: str) -> str:
    """Unity 写 YAML 时对非 ASCII 用 \\uXXXX 转义（大写十六进制）"""
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append("\\u%04X" % ord(ch))
    return "".join(out)


def u_unescape(s: str) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


def open_sheet(filename: str):
    path = os.path.join(CFG_DIR, filename)
    wb = openpyxl.load_workbook(path)
    ws = wb[wb.sheetnames[0]]
    headers = {}
    for col in range(1, ws.max_column + 1):
        name = ws.cell(row=4, column=col).value
        if name:
            headers[str(name).strip()] = col
    rows = {}
    for row in range(5, ws.max_row + 1):
        value = ws.cell(row=row, column=1).value
        if value is None:
            continue
        try:
            rows[int(value)] = row
        except (TypeError, ValueError):
            continue
    return wb, ws, headers, rows


def repack_xlsx(path: str) -> None:
    """openpyxl 保存后会把 [Content_Types].xml 写到 zip 中间，
    而 Unity 侧用的 System.IO.Packaging 要求它必须是第一个条目，否则读不到工作表。"""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as src:
        names = src.namelist()
        order = [n for n in ("[Content_Types].xml", "_rels/.rels") if n in names]
        order += [n for n in names if n not in order]
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
            for name in order:
                dst.writestr(name, src.read(name))
    os.replace(tmp, path)


def rewrite_for_excel_reader(path: str) -> None:
    """工程里用的老版 Excel.dll(ExcelDataReader 2.x) 只认 sharedStrings，
    而 openpyxl 只会写 inlineStr。这里用 xlsxwriter 重写一遍（默认写 sharedStrings），
    确保 Unity 侧的「生成配置表」能正常读到内容。格式会丢失，配置表不需要。"""
    src = openpyxl.load_workbook(path, data_only=False)
    sheet_name = src.sheetnames[0]
    rows = [list(r) for r in src[sheet_name].iter_rows(values_only=True)]
    src.close()

    tmp = path + ".new.xlsx"
    book = xlsxwriter.Workbook(tmp)
    sheet = book.add_worksheet(sheet_name)
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            if value is None:
                sheet.write_blank(row_index, col_index, None)
            elif isinstance(value, bool):
                sheet.write_boolean(row_index, col_index, value)
            elif isinstance(value, (int, float)):
                sheet.write_number(row_index, col_index, value)
            else:
                sheet.write_string(row_index, col_index, str(value))
    book.close()
    os.replace(tmp, path)


def apply_map() -> int:
    wb, ws, headers, rows = open_sheet("场景.xlsx")
    changed = 0
    for map_id, new_name in MAP_RENAME.items():
        row = rows.get(map_id)
        if row is None:
            print(f"  [warn] 场景表缺少 Id={map_id}")
            continue
        ws.cell(row=row, column=headers["Name"]).value = new_name
        changed += 1
    path = os.path.join(CFG_DIR, "场景.xlsx")
    wb.save(path)
    rewrite_for_excel_reader(path)
    return changed


def apply_character() -> int:
    wb, ws, headers, rows = open_sheet("人物.xlsx")
    changed = 0
    for char_id, (name, model) in CHAR_RENAME.items():
        row = rows.get(char_id)
        if row is None:
            print(f"  [warn] 人物表缺少 Id={char_id}，跳过 {name}")
            continue
        ws.cell(row=row, column=headers["Name"]).value = name
        if char_id in CHAR_NICKNAME:
            ws.cell(row=row, column=5).value = CHAR_NICKNAME[char_id]
        if model:
            ws.cell(row=row, column=headers["ModelFileKey"]).value = model
        if char_id in CHAR_FEMALE:
            ws.cell(row=row, column=headers["Sexual"]).value = 1
        changed += 1
    path = os.path.join(CFG_DIR, "人物.xlsx")
    wb.save(path)
    rewrite_for_excel_reader(path)
    return changed


def apply_skill() -> int:
    wb, ws, headers, rows = open_sheet("武功.xlsx")
    changed = 0
    for skill_id, name in SKILL_RENAME.items():
        row = rows.get(skill_id)
        if row is None:
            print(f"  [warn] 武功表缺少 Id={skill_id}，跳过 {name}")
            continue
        ws.cell(row=row, column=headers["Name"]).value = name
        changed += 1
    path = os.path.join(CFG_DIR, "武功.xlsx")
    wb.save(path)
    rewrite_for_excel_reader(path)
    return changed


def apply_item() -> int:
    wb, ws, headers, rows = open_sheet("物品.xlsx")
    changed = 0
    for item_id, (name, desc) in ITEM_RENAME.items():
        row = rows.get(item_id)
        if row is None:
            print(f"  [warn] 物品表缺少 Id={item_id}，跳过 {name}")
            continue
        ws.cell(row=row, column=headers["Name"]).value = name
        if desc:
            ws.cell(row=row, column=headers["Desc"]).value = desc
        changed += 1
    path = os.path.join(CFG_DIR, "物品.xlsx")
    wb.save(path)
    rewrite_for_excel_reader(path)
    return changed


ORIGINAL_MAP_NAMES = {
    0: "莫穿林居", 1: "莫桥山庄", 2: "万烛书苑", 3: "茶恩寺", 4: "钟鸣阁",
    5: "怡麟楼", 6: "将军府", 7: "曼陀谷", 8: "鸽子楼", 9: "牛头岭",
    10: "滨湖茅庐", 11: "水果摊", 12: "隋仙堂", 13: "野狼谷", 14: "野狼洞",
    15: "鸽子笼台", 16: "黑熊谷", 17: "罗记饼行", 18: "无名窟", 19: "无际坊",
}


def rewrite_daditu() -> int:
    """大地图上按地图名匹配的 GameObject（入口标记 + 落点）一起改名"""
    text = open(DADITU, encoding="utf-8").read()
    old_to_new = {ORIGINAL_MAP_NAMES[i]: n for i, n in MAP_RENAME.items()}
    replaced = [0]

    def repl(m):
        name = u_unescape(m.group(1))
        mm = re.match(r"^(\d+_)?(.*)$", name, re.S)
        prefix, base = mm.group(1) or "", mm.group(2)
        new_name = old_to_new.get(base)
        if new_name is None:
            return m.group(0)
        replaced[0] += 1
        return '  m_Name: "%s"' % u_escape(prefix + new_name)

    text = re.sub(r'^  m_Name: "([^"]*)"', repl, text, flags=re.M)
    with open(DADITU, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return replaced[0]


def update_mod_setting() -> None:
    text = open(MOD_SETTING, encoding="utf-8").read().replace("\r\n", "\n")
    text = re.sub(r"^  PlayerName: .*$", lambda m: '  PlayerName: "%s"' % u_escape("杨过"),
                  text, flags=re.M)
    # 模板里的角色名修正表留着会盖住人物表的新名字，直接清空
    text = re.sub(r"^  StoryIdNameFixes:\n(?:  - Id: .*\n    Name: .*\n)+",
                  "  StoryIdNameFixes: []\n", text, flags=re.M)
    with open(MOD_SETTING, "w", encoding="utf-8", newline="") as fh:
        fh.write(text.replace("\n", "\r\n"))


def main() -> int:
    if not os.path.isdir(CFG_DIR):
        print(f"找不到配置表目录：{CFG_DIR}")
        return 1
    print(f"地图改名 {apply_map()} 条")
    print(f"人物改名 {apply_character()} 条")
    print(f"武功改名 {apply_skill()} 条")
    print(f"物品改名 {apply_item()} 条")
    print(f"大地图 GameObject 改名 {rewrite_daditu()} 处")
    update_mod_setting()
    print("ModSetting 已更新（PlayerName=杨过，清空 StoryIdNameFixes）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
