"""校验神雕侠侣 MOD 的剧情脚本引用是否合法。

运行时如果 Talk 用了人物表里没有的 Id，ChatUIPanel 会直接空引用崩掉；
TryBattle / AddItem / LearnMagic2 引用了不存在的表项也一样。这个脚本在
导出前把这些情况先抓出来。

用法：python tools/shendiao/check_story.py
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD_DIR = os.path.join(ROOT, "jyx2", "Assets", "Mods", "shendiao")
LUA_DIR = os.path.join(MOD_DIR, "Lua")
CFG_LUA = os.path.join(MOD_DIR, "Configs", "Lua")


def load_table_ids(filename: str) -> set:
    path = os.path.join(CFG_LUA, filename)
    if not os.path.exists(path):
        print(f"[warn] 缺少配置表 {path}，请先跑 jyx2mod.py configs")
        return set()
    ids = set()
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^\{(-?\d+),", line.strip())
        if m:
            ids.add(int(m.group(1)))
    return ids


def main() -> int:
    characters = load_table_ids("CharacterConfig.lua")
    items = load_table_ids("ItemConfig.lua")
    skills = load_table_ids("SkillConfig.lua")
    battles = load_table_ids("BattleConfig.lua")
    print(f"配置表：人物 {len(characters)} / 物品 {len(items)} / 武功 {len(skills)} / 战斗 {len(battles)}")

    errors = []
    warnings = []
    files = sorted(f for f in os.listdir(LUA_DIR) if f.endswith(".lua"))
    for name in files:
        path = os.path.join(LUA_DIR, name)
        text = open(path, encoding="utf-8").read()
        lines = text.split("\n")

        for lineno, line in enumerate(lines, 1):
            where = f"{name}:{lineno}"

            for m in re.finditer(r"\bTalk\(\s*(\d+)", line):
                if int(m.group(1)) not in characters:
                    errors.append(f"{where} Talk 引用不存在的人物 Id={m.group(1)}")

            for m in re.finditer(r"\bAddItem\(\s*(\d+)", line):
                if int(m.group(1)) not in items:
                    errors.append(f"{where} AddItem 引用不存在的物品 Id={m.group(1)}")

            for m in re.finditer(r"\bTryBattle\(\s*(\d+)", line):
                if int(m.group(1)) not in battles:
                    errors.append(f"{where} TryBattle 引用不存在的战斗 Id={m.group(1)}")

            for m in re.finditer(r"\bLearnMagic2\(\s*\d+\s*,\s*(\d+)", line):
                if int(m.group(1)) not in skills:
                    errors.append(f"{where} LearnMagic2 引用不存在的武功 Id={m.group(1)}")

            for m in re.finditer(r"\bUseItem\(\s*(\d+)", line):
                if int(m.group(1)) not in items:
                    errors.append(f"{where} UseItem 引用不存在的物品 Id={m.group(1)}")

        # goto / label 配对
        gotos = set(re.findall(r"\bgoto\s+(\w+)", text))
        labels = set(re.findall(r"^::(\w+)::", text, re.M))
        for label in gotos - labels:
            errors.append(f"{name} goto {label} 没有对应的 ::{label}::")

        # 顺带提醒：lua 里 goto 不能跳进 local 的作用域
        if "local " in text and "goto " in text:
            first_local = text.index("local ")
            for m in re.finditer(r"\bgoto\s+(\w+)", text):
                if m.start() > first_local:
                    warnings.append(f"{name} 在 local 之后还有 goto，注意别跳进作用域")

    for message in warnings:
        print(f"[warn] {message}")
    for message in errors:
        print(f"[error] {message}")
    print(f"检查 {len(files)} 个剧情脚本：{len(errors)} 个错误，{len(warnings)} 个提醒")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
