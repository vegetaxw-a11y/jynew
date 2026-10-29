#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为人物表里每个角色补齐 Models/<ModelFileKey>.asset（ModelAsset）。

## 为什么需要这个工具

`RoleInstance` 取模型是这样：

    if (!string.IsNullOrWhiteSpace(Data.ModelFileKey))
        return ModelAsset.Get(Data.ModelFileKey);
    else
        return ModelAsset.Get(Data.Name);

而 `ModelAsset.Get(name)` 按资源名精确匹配，找不到就 LogError 然后
**随机挑一个模型**（Tools.GetRandomElement(All)）。表现是「公孙绿萼变成了大胡子」，
不报显眼错误，很容易以为是场景配错了。

所以人物表里出现的每个 `ModelFileKey`（留空则用角色名）都必须有同名 ModelAsset。

## 用法

    python tools/shendiao/gen_model_assets.py --mod shendiao            # 只报告
    python tools/shendiao/gen_model_assets.py --mod shendiao --apply     # 生成

生成方式：复制一个外观相近的现有 ModelAsset（连带武器部件 references），
改 m_Name，配新 GUID 的 .meta，并写 `assetBundleName: <mod>_mod`。
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

# 新角色借用哪个现有模型（外观相近即可，之后想换脸改这里重跑）
PREFERRED_TEMPLATES = {
    "公孙绿萼": "程英",
    "樊一翁": "庙祝",
    "裘千尺": "孙婆婆",
    "陆无双": "郭芙",
    "周伯通": "柯镇恶",
    "瑛姑": "李莫愁",
    "一灯": "寿眉大师",
    "华山派弟子": "鹿清笃",
}

# 兜底：按关键字猜性别/年龄，猜不出就用主角
FALLBACK_RULES = [
    (("姑", "娘", "婆", "女", "婢", "妃", "妇"), ["孙婆婆", "李莫愁", "程英"]),
    (("僧", "大师", "禅师", "老", "翁"), ["寿眉大师", "柯镇恶", "洪七公"]),
    (("弟子", "道士", "兵", "众"), ["鹿清笃", "将军府士兵", "曼陀谷弟子"]),
]

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
    return "".join(ch if ord(ch) < 128 else "\\u%04X" % ord(ch) for ch in text)


def read_character_keys(xlsx_path: str) -> list[tuple[str, str]]:
    """返回 [(角色名, ModelFileKey)]；列位置按表头第 4 行的字段名定位"""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = rows[3]
    try:
        name_col = header.index("Name")
    except ValueError as exc:
        raise SystemExit(f"表头里找不到 Name 列：{header}") from exc
    key_col = header.index("ModelFileKey") if "ModelFileKey" in header else name_col

    result: list[tuple[str, str]] = []
    for row in rows[4:]:
        if not row or len(row) <= max(name_col, key_col):
            continue
        name = row[name_col]
        if name is None or not str(name).strip():
            continue
        key = row[key_col]
        key = str(key).strip() if key is not None else ""
        result.append((str(name).strip(), key or str(name).strip()))
    return result


def pick_template(model_key: str, available: set[str]) -> str:
    if model_key in PREFERRED_TEMPLATES:
        return PREFERRED_TEMPLATES[model_key]
    seed = sum(ord(ch) for ch in model_key)
    for keywords, pool in FALLBACK_RULES:
        if any(k in model_key for k in keywords):
            usable = [p for p in pool if p in available]
            if usable:
                return usable[seed % len(usable)]
    for candidate in ("杨过", "郭靖"):
        if candidate in available:
            return candidate
    raise SystemExit("找不到可用的兜底模板（Models 目录是空的？）")


def mod_dir(mod_id: str) -> str:
    for name in os.listdir(MODS_DIR):
        if name.lower() == mod_id.lower():
            return os.path.join(MODS_DIR, name)
    raise SystemExit(f"找不到 MOD 目录：{mod_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="补齐角色的 ModelAsset")
    parser.add_argument("--mod", required=True, help="MOD id，例如 shendiao")
    parser.add_argument("--apply", action="store_true", help="真的写文件（默认只报告）")
    args = parser.parse_args()

    root = mod_dir(args.mod)
    models_dir = os.path.join(root, "Models")
    xlsx = os.path.join(root, "Configs", "人物.xlsx")
    if not os.path.isfile(xlsx):
        raise SystemExit(f"找不到人物表：{xlsx}")
    if not os.path.isdir(models_dir):
        raise SystemExit(f"找不到 Models 目录：{models_dir}")

    existing = {os.path.splitext(f)[0] for f in os.listdir(models_dir) if f.endswith(".asset")}
    chars = read_character_keys(xlsx)
    missing = [(name, key) for name, key in chars if key not in existing]

    print(f"人物表 {len(chars)} 行，Models 已有 {len(existing)} 个，缺 {len(missing)} 个")
    if not missing:
        print("全部齐了，无需生成。")
        return 0

    bundle = f"{args.mod.lower()}_mod"
    plan = []
    for name, key in missing:
        template = pick_template(key, existing)
        print(f"  {name:<12} ModelFileKey={key:<12} ← 模板 {template}")
        plan.append((name, key, template))

    if not args.apply:
        print("\n（没加 --apply，未写文件）")
        return 0

    for name, key, template in plan:
        template_asset = os.path.join(models_dir, template + ".asset")
        text = open(template_asset, encoding="utf-8").read()
        text = re.sub(r'^(\s*m_Name: ).*$', lambda m: m.group(1) + '"' + unity_escape(key) + '"',
                      text, count=1, flags=re.M)
        asset_path = os.path.join(models_dir, key + ".asset")
        with open(asset_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        guid = uuid.uuid4().hex
        with open(asset_path + ".meta", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(META_TMPL.format(guid=guid, bundle=bundle))
        print(f"  写出 {key}.asset  guid={guid}   （{name}）")

    print(f"\n完成，生成 {len(plan)} 个。记得重新导出 AssetBundle 并 install。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
