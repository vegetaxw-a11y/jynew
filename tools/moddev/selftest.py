"""
自测脚本：用 Lua 运行时（lupa）执行 excel2lua.py 生成的配置表，
逐字段比对 Excel 原始值，验证导出器行为与游戏侧一致。

用法：
    python -m pip install openpyxl lupa
    python tools/moddev/selftest.py [Mod目录...]

默认测试仓库里已有的三个 Mod：JYX2 / SAMPLE / xiastart_roguelike。
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import excel2lua  # noqa: E402

try:
    import lupa
except ImportError:  # pragma: no cover
    lupa = None

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_MODS = [
    os.path.join(REPO, "jyx2", "Assets", "Mods", "JYX2"),
    os.path.join(REPO, "jyx2", "Assets", "Mods", "SAMPLE"),
    os.path.join(REPO, "jyx2", "Assets", "Mods", "xiastart_roguelike"),
]

STUB_LUA = """
captured = {}
jy_utils = { prequire = function(name) return {} end }
Jyx2 = {
    GetModule = function(self, name)
        return {
            AddConfigTable = function(self2, cfgName, data)
                if captured[cfgName] then error('duplicated config table: '..cfgName) end
                captured[cfgName] = data
            end
        }
    end
}
"""


def compile_only(lua, source: str) -> bool:
    """只编译不执行，检查 Lua 语法"""
    fn = lua.eval("function(s) local f, err = load(s) return f, err end")
    func, err = fn(source)
    if func is None:
        print(f"    [FAIL] Lua 语法错误: {err}")
        return False
    return True


def parse_cell(col, raw: str):
    """独立于 excel2lua 的取值解析（按表头类型）"""
    if col.type == excel2lua.L_STRING:
        return raw.strip()
    if col.type == excel2lua.L_BOOLEAN:
        return excel2lua.string_to_boolean(raw)
    if col.type == excel2lua.L_NUMBER:
        return None if raw == "" else float(raw)
    return raw


def compare_value(col, expected, actual) -> str | None:
    if col.type == excel2lua.L_NUMBER:
        if expected is None:
            return None if actual is None else f"期望 nil 实际 {actual!r}"
        ok = actual is not None and abs(float(actual) - expected) < 1e-9
        return None if ok else f"期望 {expected} 实际 {actual!r}"
    if col.type == excel2lua.L_BOOLEAN:
        return None if bool(actual) == expected else f"期望 {expected} 实际 {actual!r}"
    if col.type == excel2lua.L_STRING:
        return None if (actual or "") == expected else f"期望 {expected!r} 实际 {actual!r}"
    return None


def conv_one(type_name: str, value: str):
    if type_name == excel2lua.L_NUMBER:
        return None if value == "" else float(value)
    if type_name == excel2lua.L_BOOLEAN:
        return excel2lua.string_to_boolean(value)
    return value


def expected_value(col, raw: str):
    """按 ExcelToLua 的规则，从原始单元格文本推导期望值"""
    if col.is_array:
        items = [x for x in raw.strip().split("|") if x != ""]
        result = []
        for item in items:
            if col.type == excel2lua.L_STRUCT:
                parts = item.split(",")
                values = tuple(
                    conv_one(col.sub_type[k] if k < len(col.sub_type) else excel2lua.L_NUMBER, p)
                    for k, p in enumerate(parts)
                )
                # C# 里复合型只有 1 个元素时不会加花括号
                result.append(values[0] if len(values) == 1 else values)
            else:
                result.append(conv_one(col.type, item))
        return tuple(result)

    if col.type == excel2lua.L_STRUCT:
        parts = raw.strip().split(",")
        values = tuple(
            conv_one(col.sub_type[k] if k < len(col.sub_type) else excel2lua.L_NUMBER, p)
            for k, p in enumerate(parts)
        )
        return values[0] if len(values) == 1 else values

    return conv_one(col.type, raw.strip())


def lua_to_py(col, value):
    if value is None:
        return None
    if col.is_array:
        result = []
        for item in value.values():
            if col.type == excel2lua.L_STRUCT and hasattr(item, "values"):
                result.append(tuple(item.values()))
            else:
                result.append(item)
        return tuple(result)
    if col.type == excel2lua.L_STRUCT:
        inner = tuple(value.values())
        return inner[0] if len(inner) == 1 else inner
    return value


def norm(value):
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, (list, tuple)):
        return tuple(norm(v) for v in value)
    return value


def collect_bad_cols(cols, rows, row_num) -> set[str]:
    """找出“数据与声明的类型对不上”的列（游戏里这类列会被写成非法/扁平 Lua，跳过比对）"""
    bad: set[str] = set()

    def check(col, value: str) -> bool:
        if col.type == excel2lua.L_NUMBER:
            if value != "":
                try:
                    float(value)
                except ValueError:
                    return False
        elif col.type == excel2lua.L_STRUCT:
            parts = value.split(",")
            for k, part in enumerate(parts):
                t = col.sub_type[k] if k < len(col.sub_type) else excel2lua.L_NUMBER
                if not check_type(t, part):
                    return False
        return True

    def check_type(t: str, value: str) -> bool:
        if t == excel2lua.L_NUMBER:
            if value == "":
                return True
            try:
                float(value)
                return True
            except ValueError:
                return False
        return True

    for i in range(4, row_num):
        for col in cols:
            raw = rows[i][col.index] if col.index < len(rows[i]) else ""
            items = [x for x in raw.strip().split("|") if x != ""] if col.is_array else [raw.strip()]
            for item in items:
                if not check(col, item):
                    bad.add(col.name)
                    break
    return bad


def check_table(cfg_name, cols, rows, row_num, table, lua) -> int:
    data_rows = [
        i for i in range(4, row_num)
        if rows[i][0].strip() and not rows[i][0].strip().startswith("#")
    ]
    actual_count = int(lua.eval("function(t) return #t end")(table))
    if actual_count != len(data_rows):
        print(f"    [FAIL] {cfg_name}: 行数不一致 Excel={len(data_rows)} Lua={actual_count}")
        return 1

    errors = 0
    bad_cols = collect_bad_cols(cols, rows, row_num)
    if bad_cols:
        print(f"    [warn] {cfg_name}: 数据与声明类型不符，跳过比对 {sorted(bad_cols)}")
    for pos, row_idx in enumerate(data_rows):
        lua_row = table[pos + 1]
        row_id = rows[row_idx][0].strip()
        for col in cols:
            if col.name in bad_cols:
                continue
            raw = rows[row_idx][col.index] if col.index < len(rows[row_idx]) else ""
            expected = norm(expected_value(col, raw))
            actual = norm(lua_to_py(col, lua_row[col.name]))
            if expected != actual:
                print(f"    [FAIL] {cfg_name}.{col.name}[Id={row_id}]: 期望 {expected!r} 实际 {actual!r}")
                errors += 1
                if errors >= 20:
                    return errors
    return errors



def find_excel_for(cfg_dir: str, cfg_name: str):
    for root, _dirs, names in os.walk(cfg_dir):
        for name in names:
            if not name.lower().endswith(".xlsx") or "~$" in name:
                continue
            rows, col_num, row_num = excel2lua.read_sheet(os.path.join(root, name))
            if rows and col_num > 1 and rows[0][0] == "LuaConfigGen" and rows[0][1] == cfg_name:
                return rows, col_num, row_num
    return None


def run_mod(mod_dir: str) -> int:
    cfg_dir = os.path.join(mod_dir, "Configs")
    if not os.path.isdir(cfg_dir):
        print(f"[skip] {mod_dir} 没有 Configs 目录")
        return 0

    print(f"== {os.path.basename(mod_dir)} ==")
    out_dir = os.path.join(tempfile.mkdtemp(prefix="jyx2_lua_"), "Lua")
    files = excel2lua.export_all_lua_file(cfg_dir, out_dir)
    if not files:
        print("  [skip] 没有生成任何配置表")
        return 0
    if lupa is None:
        print("  [skip] 未安装 lupa，无法执行 Lua 校验")
        return 0

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUB_LUA)
    captured = lua.globals().captured
    errors = 0

    for lua_path in files:
        cfg_name = os.path.basename(lua_path)[: -len("Config.lua")]
        with open(lua_path, encoding="utf-8") as f:
            source = f.read()
        print(f"  - {os.path.basename(lua_path)}")
        if not compile_only(lua, source):
            errors += 1
            continue
        lua.execute(source)
        found = find_excel_for(cfg_dir, cfg_name)
        if found is None:
            print(f"    [FAIL] 找不到 {cfg_name} 对应的 Excel")
            errors += 1
            continue
        rows, col_num, row_num = found
        cols = excel2lua.get_col_desc(rows, col_num)
        errors += check_table(cfg_name, cols, rows, row_num, captured[cfg_name], lua)

    print(f"  -> {len(files)} 张表，错误 {errors}")
    return errors


def main(argv: list[str]) -> int:
    mods = argv[1:] or DEFAULT_MODS
    total = 0
    for mod in mods:
        total += run_mod(os.path.abspath(mod))
    print("全部通过" if total == 0 else f"共 {total} 处错误")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

