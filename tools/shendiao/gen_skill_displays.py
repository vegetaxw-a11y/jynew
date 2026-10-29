#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为武功表里每个技能补齐 Skills/<技能名>.asset（Jyx2SkillDisplayAsset）。

## 为什么需要这个工具

`Jyx2SkillDisplayAsset.Get(name)` 是按**资源名精确匹配**的：

    public static Jyx2SkillDisplayAsset Get(string skillName)
    {
        var displayAsset = All.FirstOrDefault(s => s.name == skillName);
        if (displayAsset == null) Debug.LogErrorFormat("目标技能展现配置不存在, 技能名:[{0}]", skillName);
        return displayAsset;
    }

而 `BattleRole.RefreshModel()` 是这么用的：

    DataInstance.SwitchAnimationToSkill(DataInstance.Wugongs[0]);   // → SwitchSkillTo(skill)
    var display = skill.GetDisplay();      // 找不到就是 null
    var weaponCode = display.weaponCode;   // → NullReferenceException

异常发生在 `BattleLoader.InitBattle` 的协程里，协程当场中断，
后面的 `BattleManager.Instance.StartBattle()` 不会执行 —— **战场一个人都没有**，
日志里只有一行 `目标技能展现配置不存在, 技能名:[xxx]`，很容易被忽略。

`SkillConfig` 的 DisplayFileName 为空时会回退用技能名，所以最省事的做法是
「技能名 = Skills 下同名 asset」。SAMPLE 就是这么填的（`[[普通攻击]]`）。

## 用法

    python tools/shendiao/gen_skill_displays.py --mod shendiao            # 只报告缺哪些
    python tools/shendiao/gen_skill_displays.py --mod shendiao --apply     # 真的生成

生成方式是复制同武器类型的模板 asset（动画 clip 指向 BuildSource/Animations 的通用动画，
被依赖带进 MOD 包），改 m_Name，配新 GUID 的 .meta，并写上 `assetBundleName: <mod>_mod`
—— 少了这一步 AssetBundle 里就没有它，运行期等于不存在。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODS_DIR = os.path.join(REPO, "jyx2", "Assets", "Mods")

# 显式映射：这些技能的动画语义要人工定，别让哈希轮转决定（可重现、可维护）
PREFERRED_TEMPLATES = {
    "全真剑法": "扫叶剑法",
    "玉女剑法": "落红剑法",
    "玉女素心剑": "翔云双飞剑",
    "全真拳法": "罗汉拳",
    "蛤蟆功": "伏虎拳",
    "九阴疗伤篇": "青竹医术",
    "黯然销魂掌": "隔山打牛掌",
    "玄铁剑法": "醉灯剑法",
    "打狗棒法": "破军枪法",
    "弹指神通": "无名指法",
    "落英神剑掌": "疾风烈焰掌",
    "一阳指": "摩柯观音泪",
    "铁掌水上漂": "震狼一击",
    "冰魄银针": "暗器",
    "玉箫剑法": "桥风剑法",
    "五毒神掌": "紫罂毒术",
    "美女拳法": "牛角拳",
    "摧心掌": "驱魔神掌",
    "天竺疗伤": "医疗",
    "分花拂柳手": "护花功",
    "金铃索法": "破军枪法",
}

# 兜底规则：按技能名关键字挑模板：先匹配到的先赢（「落英神剑掌」是掌法，要排在「剑」前面）
TEMPLATE_RULES = [
    (("疗伤", "医疗"), ["医疗", "青竹医术"]),
    (("针", "镖", "暗器"), ["暗器"]),
    (("掌", "拳", "指", "手", "功"), ["罗汉拳", "伏虎拳", "牛角拳", "隔山打牛掌",
                                    "疾风烈焰掌", "震狼一击", "驱魔神掌", "摩柯观音泪",
                                    "无名指法", "护花功", "紫罂毒术"]),
    (("剑",), ["扫叶剑法", "桥风剑法", "翔云双飞剑", "落红剑法", "醉灯剑法"]),
    (("刀",), ["卷山狂刀", "惊鹭刀法"]),
    (("棒", "枪", "索", "鞭", "杖"), ["破军枪法", "天星满月弓"]),
]
FALLBACK_TEMPLATES = ["普通攻击", "罗汉拳"]

META_TMPL = """fileFormatVersion: 2
guid: {guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 11400000
  userData:
  assetBundleName: {bundle}
  assetBundleVariant:
"""


def unity_escape(text: str) -> str:
    """Unity YAML 里的中文字符串一律写成 \\uXXXX（大写十六进制）"""
    out = []
    for ch in text:
        out.append(ch if ord(ch) < 128 else "\\u%04X" % ord(ch))
    return "".join(out)


def read_skill_names(xlsx_path: str) -> list[str]:
    """从武功表读技能名（第 5 行开始，B 列为 Name）"""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb.worksheets[0]
    names: list[str] = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=5, max_col=2, values_only=True), start=5):
        if not row or row[1] is None:
            continue
        name = str(row[1]).strip()
        if name:
            names.append(name)
    wb.close()
    return names


def pick_template(skill_name: str) -> str:
    """先查显式映射表，再按关键字兜底（兜底用确定性哈希，内置 hash() 每个进程随机）"""
    if skill_name in PREFERRED_TEMPLATES:
        return PREFERRED_TEMPLATES[skill_name]
    seed = sum(ord(ch) for ch in skill_name)
    for keywords, pool in TEMPLATE_RULES:
        if any(k in skill_name for k in keywords):
            return pool[seed % len(pool)]
    return FALLBACK_TEMPLATES[seed % len(FALLBACK_TEMPLATES)]


def mod_dir(mod_id: str) -> str:
    for name in os.listdir(MODS_DIR):
        if name.lower() == mod_id.lower():
            return os.path.join(MODS_DIR, name)
    raise SystemExit(f"找不到 MOD 目录：{mod_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="补齐技能的 Jyx2SkillDisplayAsset")
    parser.add_argument("--mod", required=True, help="MOD id，例如 shendiao")
    parser.add_argument("--apply", action="store_true", help="真的写文件（默认只报告）")
    args = parser.parse_args()

    root = mod_dir(args.mod)
    skills_dir = os.path.join(root, "Skills")
    xlsx = os.path.join(root, "Configs", "武功.xlsx")
    if not os.path.isfile(xlsx):
        raise SystemExit(f"找不到武功表：{xlsx}")
    if not os.path.isdir(skills_dir):
        raise SystemExit(f"找不到 Skills 目录：{skills_dir}")

    existing = {os.path.splitext(f)[0] for f in os.listdir(skills_dir) if f.endswith(".asset")}
    names = read_skill_names(xlsx)

    missing = [n for n in names if n not in existing]
    print(f"武功表技能 {len(names)} 个，Skills 已有 {len(existing)} 个，缺 {len(missing)} 个")
    if not missing:
        print("全部齐了，无需生成。")
        return 0

    bundle = f"{args.mod.lower()}_mod"
    generated = []
    for name in missing:
        template = pick_template(name)
        template_asset = os.path.join(skills_dir, template + ".asset")
        if not os.path.isfile(template_asset):
            print(f"  [跳过] {name}：模板 {template}.asset 不存在")
            continue
        print(f"  {name:<12} ← 模板 {template}")
        generated.append((name, template_asset))

    if not args.apply:
        print("\n（没加 --apply，未写文件）")
        return 0

    for name, template_asset in generated:
        text = open(template_asset, encoding="utf-8").read()
        text = re.sub(r'^(\s*m_Name: ).*$', lambda m: m.group(1) + '"' + unity_escape(name) + '"',
                      text, count=1, flags=re.M)
        asset_path = os.path.join(skills_dir, name + ".asset")
        with open(asset_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        guid = uuid.uuid4().hex
        with open(asset_path + ".meta", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(META_TMPL.format(guid=guid, bundle=bundle))
        print(f"  写出 {name}.asset  guid={guid}")

    print(f"\n完成，生成 {len(generated)} 个。记得：")
    print("  1. python tools/moddev/jyx2mod.py configs " + args.mod + "   （重导 Lua）")
    print("  2. python tools/moddev/jyx2mod.py check " + args.mod)
    print("  3. 重新导出 AssetBundle 并 install")
    return 0


if __name__ == "__main__":
    sys.exit(main())
