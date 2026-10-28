"""把 人物.xlsx 的「模型文件名」列从 =D{row} 公式落成字面值，并校验模型存在。

SAMPLE 模板原本用公式「模型名 = 姓名」来少写一列，但 xlsxwriter 重写工作簿时
不会保留公式缓存值，openpyxl(data_only=True) 只能读到 "=D8" 这样的文本，
最后原样漏进 CharacterConfig.lua，运行时按这个鬼名字找不到 ModelAsset。

这个脚本把公式换成姓名本身（正好是 SAMPLE 的原始语义），并逐条检查
Mods/shendiao/Models/<姓名>.asset 是否真的存在。

用法：
    python tools/shendiao/fix_char_models.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apply_configs import CFG_DIR, MOD_DIR, open_sheet, rewrite_for_excel_reader  # noqa: E402

MODELS_DIR = os.path.join(MOD_DIR, "Models")


def main() -> int:
    path = os.path.join(CFG_DIR, "人物.xlsx")
    wb, ws, headers, rows = open_sheet("人物.xlsx")
    mcol, ncol = headers["ModelFileKey"], headers["Name"]
    models = {f[:-len(".asset")] for f in os.listdir(MODELS_DIR) if f.endswith(".asset")}

    fixed = missing = 0
    for char_id, row in sorted(rows.items()):
        cur = ws.cell(row=row, column=mcol).value
        name = ws.cell(row=row, column=ncol).value
        if isinstance(cur, str) and cur.startswith("="):
            if name not in models:
                print("  [miss] Id=%-4s %s -> 没有 Models/%s.asset" % (char_id, name, name))
                missing += 1
                continue
            ws.cell(row=row, column=mcol).value = name
            fixed += 1
        elif cur and cur not in models:
            print("  [miss] Id=%-4s 模型 %s 不存在" % (char_id, cur))
            missing += 1

    wb.save(path)
    rewrite_for_excel_reader(path)
    print("公式落地 %d 条，缺失 %d 条" % (fixed, missing))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
