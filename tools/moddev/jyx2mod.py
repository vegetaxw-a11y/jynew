#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jyx2mod.py —— 群侠传，启动！(jynew) MOD 开发命令行工具

把过去必须在 Unity 编辑器/资源管理器里点来点去的事情搬到命令行，
方便脚本化、自动化，也方便 AI 参与 MOD 开发。

子命令：
    new       从模板（默认 SAMPLE）复制出一个新 MOD，并改好 ModSetting / .meta
    configs   把 <Mod>/Configs/*.xlsx 导出成 <Mod>/Configs/Lua/*Config.lua（无需 Unity）
    xml       生成 MOD 描述文件 <id>.xml（等价于 Unity 导出时生成的 GameModInfo）
    check     体检：ModSetting、AssetBundle 标记、配置表、Lua 语法
    install   把导出好的 MOD 安装进游戏目录（<游戏>/<exe>_Data/mods/<id>）
    uninstall 从游戏目录卸载 MOD
    list      列出工程里的 MOD 和游戏目录里已安装的 MOD
    logs      查看游戏 Player.log
    run       启动游戏（可顺便看日志）
    unity     调用 Unity 命令行导出 MOD（AssetBundle + xml，需要本机装 Unity）

示例：
    python tools/moddev/jyx2mod.py new mymod --name 我的MOD --author 我
    python tools/moddev/jyx2mod.py configs mymod
    python tools/moddev/jyx2mod.py check mymod
    python tools/moddev/jyx2mod.py install mymod --src Export/mymod
    python tools/moddev/jyx2mod.py logs -f
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import excel2lua  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
UNITY_PROJECT = os.path.join(REPO, "jyx2")
ASSETS_DIR = os.path.join(UNITY_PROJECT, "Assets")
MODS_DIR = os.path.join(UNITY_PROJECT, "Assets", "Mods")
PROJECT_VERSION_FILE = os.path.join(UNITY_PROJECT, "ProjectSettings", "ProjectVersion.txt")
PROJECT_SETTINGS_FILE = os.path.join(UNITY_PROJECT, "ProjectSettings", "ProjectSettings.asset")
GAME_EXE = "wuxia_launch.exe"
DEFAULT_TEMPLATE = "SAMPLE"


def abs_path(path: str | None) -> str | None:
    """相对路径统一按仓库根目录解析，保证脚本在任何工作目录下运行行为一致"""
    if not path:
        return path
    return os.path.normpath(path if os.path.isabs(path) else os.path.join(REPO, path))

MOD_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,31}$")


def log(msg: str = "") -> None:
    print(msg, flush=True)


def ok(msg: str) -> None:
    log(f"[ok] {msg}")


def warn(msg: str) -> None:
    log(f"[warn] {msg}")


def error(msg: str) -> None:
    log(f"[error] {msg}")


def die(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[valid-type]
    error(msg)
    raise SystemExit(code)


# --------------------------------------------------------------------------------------
# 通用工具
# --------------------------------------------------------------------------------------

def read_text(path: str) -> str:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return f.read()


def write_text(path: str, content: str, crlf: bool = False) -> None:
    """写 UTF-8（无 BOM）文本，Unity 的 .asset/.meta 用 CRLF，其他用 LF"""
    if crlf:
        content = content.replace("\r\n", "\n").replace("\n", "\r\n")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def new_guid() -> str:
    return uuid.uuid4().hex


def escape_yaml_string(value: str) -> str:
    """按 Unity 的 YAML 习惯转义字符串（非 ASCII 写成 \\uXXXX，大写十六进制）"""
    out: list[str] = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04X}")
        elif ord(ch) > 0x7E:
            out.append(f"\\u{ord(ch):04X}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def escape_xml_attr(value: str) -> str:
    """模拟 .NET XmlSerializer 写属性：\\r\\n 归一化成 \\n，再转义"""
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return text.replace("\n", "&#xA;").replace("\t", "&#x9;")


def unescape_yaml_string(value: str) -> str:
    """还原 Unity YAML 里的字符串字面量（"\\uXXXX\\r\\n" 之类）"""
    text = value.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    out: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch != "\\" or i + 1 >= len(text):
            out.append(ch)
            i += 1
            continue
        nxt = text[i + 1]
        if nxt == "u" and i + 5 < len(text):
            out.append(chr(int(text[i + 2:i + 6], 16)))
            i += 6
        elif nxt == "n":
            out.append("\n")
            i += 2
        elif nxt == "r":
            out.append("\r")
            i += 2
        elif nxt == "t":
            out.append("\t")
            i += 2
        elif nxt in "\\\"":
            out.append(nxt)
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def normalize_mod_id(raw: str) -> str:
    """校验 MOD Id / 目录名。注意：游戏里拼 AssetBundle 名时会 ToLower()"""
    mod_id = raw.strip()
    if not MOD_ID_RE.match(mod_id):
        die(f"非法 MOD Id：{raw!r}（要求：字母开头，只含字母/数字/下划线，长度 2-32）")
    return mod_id


def bundle_names(mod_id: str) -> tuple[str, str]:
    """对应 Jyx2ModTool.GetModMainBundleName / GetModMapBundleName（都是小写）"""
    lowered = mod_id.lower()
    return f"{lowered}_mod", f"{lowered}_maps"


def require_mod_dir(mod_id: str) -> str:
    path = os.path.join(MODS_DIR, mod_id)
    if os.path.isdir(path):
        return path
    if os.path.isdir(MODS_DIR):
        for name in sorted(os.listdir(MODS_DIR)):
            if name.lower() == mod_id.lower() and os.path.isdir(os.path.join(MODS_DIR, name)):
                return os.path.join(MODS_DIR, name)
    die(f"找不到 MOD 目录：{path}（可用：{', '.join(list_project_mods()) or '无'}）")


def list_project_mods() -> list[str]:
    if not os.path.isdir(MODS_DIR):
        return []
    return sorted(
        d for d in os.listdir(MODS_DIR)
        if os.path.isdir(os.path.join(MODS_DIR, d)) and os.path.isfile(os.path.join(MODS_DIR, d, "ModSetting.asset"))
    )


def project_version() -> str:
    try:
        text = read_text(PROJECT_VERSION_FILE)
    except OSError:
        return ""
    m = re.search(r"m_EditorVersion:\s*(\S+)", text)
    return m.group(1) if m else ""


def client_version() -> str:
    """对应 Unity 的 Application.version（ProjectSettings 里的 bundleVersion）"""
    try:
        text = read_text(PROJECT_SETTINGS_FILE)
    except OSError:
        return ""
    m = re.search(r"^\s*bundleVersion:\s*(.+)$", text, re.M)
    return m.group(1).strip().strip('"') if m else ""



# --------------------------------------------------------------------------------------
# 游戏目录定位
# --------------------------------------------------------------------------------------

STEAM_DEFAULT = r"C:\Program Files (x86)\Steam"


def _steam_libraries() -> list[str]:
    libs = [STEAM_DEFAULT]
    vdf = os.path.join(STEAM_DEFAULT, "steamapps", "libraryfolders.vdf")
    if os.path.isfile(vdf):
        for m in re.finditer(r'"path"\s+"([^"]+)"', read_text(vdf)):
            libs.append(m.group(1).replace("\\\\", "\\"))
    return libs


def is_game_dir(path: str | None) -> bool:
    return bool(path) and os.path.isfile(os.path.join(path, GAME_EXE))


def detect_game_dir(explicit: str | None = None) -> str | None:
    """按 参数 -> 环境变量 -> Steam 库 的顺序找游戏根目录"""
    candidates: list[str] = []
    if explicit:
        candidates.append(abs_path(explicit))
    if os.environ.get("JYX2_GAME_DIR"):
        candidates.append(abs_path(os.environ["JYX2_GAME_DIR"]))
    for lib in _steam_libraries():
        common = os.path.join(lib, "steamapps", "common")
        if not os.path.isdir(common):
            continue
        try:
            for name in os.listdir(common):
                candidates.append(os.path.join(common, name))
        except OSError:
            continue
    for path in candidates:
        if is_game_dir(path):
            return os.path.abspath(path)
    return None


def require_game_dir(explicit: str | None) -> str:
    game = detect_game_dir(explicit)
    if not game:
        die(
            "找不到游戏目录，请用 --game 指定，或设置环境变量 JYX2_GAME_DIR\n"
            "        例如：$env:JYX2_GAME_DIR='C:\\Program Files (x86)\\Steam\\steamapps\\common\\群侠传，启动！'"
        )
    return game


def game_data_dir(game_dir: str) -> str:
    """Unity 的 Application.dataPath，即 <游戏>/<exe>_Data"""
    return os.path.join(game_dir, os.path.splitext(GAME_EXE)[0] + "_Data")


def game_mods_dir(game_dir: str) -> str:
    """手动安装 MOD 的目录之一：<游戏>/<exe>_Data/mods"""
    return os.path.join(game_data_dir(game_dir), "mods")


def game_persistent_mods_dir(game_dir: str) -> str:
    """另一个手动安装目录：Application.persistentDataPath/mods（LocalLow/<公司>/<产品>/mods）"""
    return os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", *game_local_low_subpath(game_dir), "mods")


def game_local_low_subpath(game_dir: str) -> tuple[str, str]:
    """推导 Application.persistentDataPath 所在的 <LocalLow>/<公司>/<产品> 目录名"""
    base = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow")
    company = "jynew"
    product = None
    try:
        text = read_text(PROJECT_SETTINGS_FILE)
        m = re.search(r"^\s*companyName:\s*(.+)$", text, re.M)
        if m and m.group(1).strip():
            company = m.group(1).strip().strip('"')
        m = re.search(r"^\s*productName:\s*(.+)$", text, re.M)
        if m:
            product = unescape_yaml_string(m.group(1).strip())
    except OSError:
        pass

    if product and os.path.isdir(os.path.join(base, company, product)):
        return company, product
    if product:
        for name in glob.glob(os.path.join(base, "*", product)):
            return os.path.basename(os.path.dirname(name)), product
    logs = glob.glob(os.path.join(base, "*", "*", "Player.log"))
    if logs:
        newest = max(logs, key=os.path.getmtime)
        parts = os.path.normpath(newest).split(os.sep)
        return parts[-3], parts[-2]
    return company, product or "群侠传启动"



def player_log_path(game_dir: str) -> str:
    company, product = game_local_low_subpath(game_dir)
    return os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", company, product, "Player.log")



# --------------------------------------------------------------------------------------
# ModSetting.asset 解析 / <id>.xml 生成
# --------------------------------------------------------------------------------------

PLATFORM_NAMES = {0: "Unknown", 1: "Windows", 2: "Android", 3: "IOS", 4: "MacOS"}


def read_yaml_double_quoted(text: str, pos: int) -> tuple[str, int]:
    """从 pos（开引号之后）读取 YAML 双引号标量，按 YAML 规则折叠换行"""
    out: list[str] = []
    i, n = pos, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            return "".join(out), i + 1
        if ch == "\\" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "u" and i + 5 < n:
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
            elif nxt == "x" and i + 3 < n:
                out.append(chr(int(text[i + 2:i + 4], 16)))
                i += 4
            elif nxt == "n":
                out.append("\n")
                i += 2
            elif nxt == "r":
                out.append("\r")
                i += 2
            elif nxt == "t":
                out.append("\t")
                i += 2
            elif nxt == "0":
                out.append("\0")
                i += 2
            else:
                out.append(nxt)
                i += 2
            continue
        if ch == "\n" or (ch == "\r" and i + 1 < n and text[i + 1] == "\n"):
            i += 2 if ch == "\r" else 1
            blanks = 0
            while i < n:
                j = i
                while j < n and text[j] in " \t":
                    j += 1
                if j < n and text[j] == "\n":
                    blanks += 1
                    i = j + 1
                    continue
                i = j
                break
            out.append("\n" * blanks if blanks else " ")
            continue
        out.append(ch)
        i += 1
    raise ValueError("YAML 双引号字符串没有闭合")


def parse_mod_setting(path: str) -> dict:
    """把 ModSetting.asset（MonoBehaviour YAML）解析成 dict，只关心常用字段"""
    text = read_text(path)
    data: dict = {"_raw": text}

    def scalar(name: str) -> str | None:
        m = re.search(rf"^  {name}:(.*)$", text, re.M)
        return None if m is None else m.group(1).strip()

    for key in ("ModId", "ModRootDir", "IsNativeMod", "Version", "PlayerName", "LuaFilePatten", "ModArchiveVersion"):
        value = scalar(key)
        if value is not None:
            data[key] = unescape_yaml_string(value) if value.startswith('"') else value
    for key in ("ModName", "Author"):
        value = scalar(key)
        if value is not None:
            data[key] = unescape_yaml_string(value)

    # Desc 可能是跨多行的双引号标量
    m = re.search(r"^  Desc:[ \t]*", text, re.M)
    if m:
        if text[m.end():m.end() + 1] == '"':
            data["Desc"] = read_yaml_double_quoted(text, m.end() + 1)[0]
        else:
            end = text.find("\n", m.end())
            data["Desc"] = unescape_yaml_string(text[m.end():end if end > 0 else len(text)])

    if "  PreloadedLua:" in text:
        block = text[text.find("  PreloadedLua:"):].split("  EnableSaveBigMapOnly")[0]
        data["PreloadedLua"] = [m.strip() for m in re.findall(r"^  - (.*?)[ \t]*\r?$", block, re.M)]
    else:
        data["PreloadedLua"] = []
    return data


def load_mod_info(mod_id: str) -> dict:
    """按 Unity 里 MODRootConfig.CreateModInfo() 的规则组装 GameModInfo"""
    mod_dir = require_mod_dir(mod_id)
    setting = parse_mod_setting(os.path.join(mod_dir, "ModSetting.asset"))
    return {
        "Id": (setting.get("ModId") or mod_id).lower(),
        "Name": setting.get("ModName", ""),
        "Author": setting.get("Author", ""),
        "Version": setting.get("Version", ""),
        "ClientVersion": client_version(),
        "CreateTime": time.strftime("%Y%m%d ") + f"{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}",
        "Desc": setting.get("Desc", ""),
        "BuildPlatform": 1,
    }


def render_mod_xml(info: dict) -> str:
    """模拟 Tools.SerializeXML(GameModInfo)：单行、无 XML 声明、无命名空间"""
    order = ("Id", "Name", "Author", "Version", "ClientVersion", "ModMD5", "MapsMD5", "CreateTime", "Desc", "Welcome")
    parts = ["<GameModInfo"]
    for key in order:
        value = info.get(key)
        if value is None:
            continue
        parts.append(f' {key}="{escape_xml_attr(str(value))}"')
    platform = int(info.get("BuildPlatform", 1))
    parts.append(f' BuildPlatform="{platform}"')
    parts.append(f"><Platform>{PLATFORM_NAMES.get(platform, 'Unknown')}</Platform></GameModInfo>")
    return "".join(parts)



# --------------------------------------------------------------------------------------
# new：从模板创建 MOD
# --------------------------------------------------------------------------------------

SKIP_DIRS = {"Library", "Temp", "obj", ".git", ".svn", "__pycache__"}


def copy_template(src: str, dst: str, with_buildsource: bool) -> int:
    def ignore(dirpath: str, names: list[str]) -> set[str]:
        rel = os.path.relpath(dirpath, src)
        skipped = {n for n in names if n in SKIP_DIRS}
        if not with_buildsource and rel == ".":
            skipped.add("BuildSource")
        if rel == "Configs" and "Lua" in names:
            skipped.add("Lua")  # 生成的配置表 Lua 重新生成即可
        # 被跳过的目录/文件，其 .meta 也一起跳过，否则 Unity 里会留下孤儿 meta
        skipped |= {n + ".meta" for n in list(skipped) if n + ".meta" in names}
        return skipped

    shutil.copytree(src, dst, ignore=ignore)
    return sum(len(files) for _r, _d, files in os.walk(dst))


def rewrite_metas(mod_dir: str, old_id: str, new_id: str) -> tuple[int, int]:
    """给所有 .meta 换新 GUID，并把模板的 AssetBundle 名换成新 MOD 的"""
    bundles = {f"{old_id}_mod": f"{new_id}_mod", f"{old_id}_maps": f"{new_id}_maps"}
    guid_count = bundle_count = 0
    for dirpath, _dirs, files in os.walk(mod_dir):
        for name in files:
            if not name.endswith(".meta"):
                continue
            path = os.path.join(dirpath, name)
            text = read_text(path)
            original = text
            crlf = "\r\n" in text

            m = re.search(r"^guid: ([0-9a-fA-F]{32})\s*$", text, re.M)
            if m:
                text = text[:m.start(1)] + new_guid() + text[m.end(1):]
                guid_count += 1

            m = re.search(r"^(  assetBundleName: ?)(\S+)\s*$", text, re.M)
            if m:
                bundle = m.group(2).lower()
                if bundle in bundles:
                    text = text[:m.start(2)] + bundles[bundle] + text[m.end(2):]
                    bundle_count += 1

            if text != original:
                write_text(path, text, crlf=crlf)
    return guid_count, bundle_count


def rewrite_mod_setting(path: str, *, mod_id: str, name: str, author: str, desc: str, native: bool) -> None:
    lines = read_text(path).replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("ModId:"):
            out.append(f"  ModId: {mod_id}")
        elif stripped.startswith("IsNativeMod:"):
            out.append(f"  IsNativeMod: {1 if native else 0}")
        elif stripped.startswith("ModName:"):
            out.append(f"  ModName: {escape_yaml_string(name)}")
        elif stripped.startswith("Author:"):
            out.append(f"  Author: {escape_yaml_string(author)}")
        elif stripped.startswith("ModRootDir:"):
            out.append(f"  ModRootDir: Assets/Mods/{mod_id}")
        elif stripped.startswith("Desc:"):
            out.append(f"  Desc: {escape_yaml_string(desc)}")
            i += 1
            while i < len(lines) and lines[i].startswith("    ") and not lines[i].startswith("  - "):
                i += 1
            continue
        else:
            out.append(line)
        i += 1
    write_text(path, "\n".join(out).rstrip("\n") + "\n", crlf=True)


def cmd_new(args) -> int:
    mod_id = normalize_mod_id(args.mod_id).lower()
    template = args.template
    template_dir = os.path.join(MODS_DIR, template)
    if not os.path.isdir(template_dir):
        die(f"模板不存在：{template_dir}（可用模板：{', '.join(list_project_mods())}）")

    target = os.path.join(MODS_DIR, mod_id)
    if os.path.exists(target):
        die(f"目标目录已存在：{target}")

    name = args.name or mod_id
    author = args.author or "无名"
    desc = args.desc or f"{name}，由 jyx2mod 从 {template} 模板创建。"

    log(f"从 {template} 复制到 {target} ...")
    file_count = copy_template(template_dir, target, args.with_buildsource)

    guid_count, bundle_count = rewrite_metas(target, template.lower(), mod_id)
    rewrite_mod_setting(
        os.path.join(target, "ModSetting.asset"),
        mod_id=mod_id, name=name, author=author, desc=desc, native=args.native,
    )

    ok(f"创建完成：{file_count} 个文件，重写 {guid_count} 个 GUID、{bundle_count} 处 AssetBundle 名")
    log("")
    log("接下来的步骤：")
    log(f"  1) 改配置表：{os.path.join(target, 'Configs')}")
    log(f"  2) 导出 Lua：python tools/moddev/jyx2mod.py configs {mod_id}")
    log(f"  3) 体检：    python tools/moddev/jyx2mod.py check {mod_id}")
    log(f"  4) 导出 AB：python tools/moddev/jyx2mod.py unity {mod_id} --output Export")
    log(f"  5) 安装：    python tools/moddev/jyx2mod.py install {mod_id} --src Export/{mod_id}")
    return 0



# --------------------------------------------------------------------------------------
# configs / xml
# --------------------------------------------------------------------------------------

def list_excel_files(cfg_dir: str) -> list[str]:
    result = []
    for root, _dirs, files in os.walk(cfg_dir):
        for name in files:
            if name.lower().endswith(".xlsx") and not name.startswith("~$"):
                result.append(os.path.join(root, name))
    return sorted(result)


def cmd_configs(args) -> int:
    mod_id = normalize_mod_id(args.mod_id)
    mod_dir = require_mod_dir(mod_id)
    cfg_dir = abs_path(args.dir) or os.path.join(mod_dir, "Configs")
    if not os.path.isdir(cfg_dir):
        die(f"找不到配置表目录：{cfg_dir}")

    out_dir = abs_path(args.out) or os.path.join(cfg_dir, "Lua")
    excel_files = list_excel_files(cfg_dir)
    if not excel_files:
        die(f"{cfg_dir} 里没有 xlsx")

    files = excel2lua.export_all_lua_file(cfg_dir, out_dir, clean=not args.no_clean)
    exported = {os.path.basename(f) for f in files}
    for path in excel_files:
        rows, col_num, _row_num = excel2lua.read_sheet(path)
        name = os.path.basename(path)
        if not rows or col_num < 2 or rows[0][0] != "LuaConfigGen":
            warn(f"跳过 {name}：A1 不是 LuaConfigGen（不是配置表）")
            continue
        lua_name = rows[0][1] + "Config.lua"
        if lua_name in exported:
            ok(f"{name} -> {lua_name}")
        else:
            warn(f"跳过 {name}：没有数据行或表头为空")

    log(f"共 {len(files)} 张表 -> {out_dir}")
    return 0 if files else 1


def cmd_xml(args) -> int:
    mod_id = normalize_mod_id(args.mod_id)
    info = load_mod_info(mod_id)
    if args.name:
        info["Name"] = args.name
    if args.author:
        info["Author"] = args.author
    if args.desc:
        info["Desc"] = args.desc
    if args.version:
        info["Version"] = args.version
    if args.platform:
        info["BuildPlatform"] = {"windows": 1, "android": 2, "ios": 3, "macos": 4}.get(args.platform.lower(), 1)

    out = abs_path(args.out)
    if out:
        # -o 既可以是文件路径，也可以是目录（目录就自动补 <id>.xml）
        if os.path.isdir(out) or not os.path.splitext(out)[1]:
            out = os.path.join(out, info["Id"] + ".xml")
    else:
        out = os.path.join(REPO, "Export", info["Id"], info["Id"] + ".xml")

    write_text(out, render_mod_xml(info))
    ok(f"生成 {out}")
    log(f"    Id={info['Id']} Name={info['Name']} Author={info['Author']} ClientVersion={info['ClientVersion']}")
    return 0



# --------------------------------------------------------------------------------------
# check：MOD 体检
# --------------------------------------------------------------------------------------

def collect_bundle_names(mod_dir: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for dirpath, _dirs, files in os.walk(mod_dir):
        for name in files:
            if not name.endswith(".meta"):
                continue
            path = os.path.join(dirpath, name)
            m = re.search(r"^  assetBundleName: ?(\S+)\s*$", read_text(path), re.M)
            if m and m.group(1):
                rel = os.path.relpath(path, mod_dir)
                result.setdefault(m.group(1).lower(), []).append(rel)
    return result


def check_lua_syntax(paths: list[str]) -> list[str]:
    try:
        import lupa
    except ImportError:
        return []
    runtime = lupa.LuaRuntime()
    loader = runtime.eval("function(s) local f, err = load(s, 'chunk') return f, err end")
    bad = []
    for path in paths:
        try:
            with open(path, encoding="utf-8-sig") as f:
                source = f.read()
        except OSError as e:
            bad.append(f"{path}: 读取失败 {e}")
            continue
        func, err = loader(source)
        if func is None:
            bad.append(f"{path}: {err}")
    return bad


def cmd_check(args) -> int:
    mod_id = normalize_mod_id(args.mod_id)
    mod_dir = require_mod_dir(mod_id)
    errors: list[str] = []
    warnings: list[str] = []

    log(f"[MOD] {os.path.basename(mod_dir)}  ({mod_dir})")

    # 1. ModSetting.asset
    setting_path = os.path.join(mod_dir, "ModSetting.asset")
    setting = parse_mod_setting(setting_path)
    declared_id = (setting.get("ModId") or "").lower()
    if declared_id != mod_id.lower():
        errors.append(f"ModSetting.asset 里 ModId={declared_id!r}，与目录名 {mod_id!r} 不一致")
    expected_root = "Assets/Mods/" + os.path.basename(mod_dir)
    if (setting.get("ModRootDir") or "") != expected_root:
        errors.append(f"ModRootDir={setting.get('ModRootDir')!r}，应为 {expected_root!r}")
    if not setting.get("ModName"):
        errors.append("ModName 为空")
    if not setting.get("Author"):
        warnings.append("Author 为空")
    if (setting.get("IsNativeMod") or "0") not in ("0", ""):
        warnings.append("IsNativeMod=1：这个 MOD 会被打进游戏本体（StreamingAssets），分发时建议改成 0")
    log(f"  ModSetting: Name={setting.get('ModName')} Author={setting.get('Author')} "
        f"Version={setting.get('Version')} Native={setting.get('IsNativeMod')}")

    # 2. AssetBundle 标记
    bundles = collect_bundle_names(mod_dir)
    main_bundle, map_bundle = bundle_names(mod_id)
    for bundle in (main_bundle, map_bundle):
        if bundle not in bundles:
            errors.append(f"没有任何资源标记为 AssetBundle {bundle!r}（导出后缺包，游戏加载会失败）")
    for bundle, files in sorted(bundles.items()):
        if bundle not in (main_bundle, map_bundle):
            warnings.append(f"多余的 AssetBundle 标记 {bundle!r}（{len(files)} 个文件），导出时不会被处理")
    log(f"  AssetBundle: {', '.join(f'{k}({len(v)})' for k, v in sorted(bundles.items())) or '无'}")


    # 3. 配置表
    cfg_dir = os.path.join(mod_dir, "Configs")
    lua_dir = os.path.join(cfg_dir, "Lua")
    excel_files = list_excel_files(cfg_dir) if os.path.isdir(cfg_dir) else []
    config_names: dict[str, str] = {}
    for path in excel_files:
        rows, col_num, _row_num = excel2lua.read_sheet(path)
        name = os.path.relpath(path, mod_dir)
        if not rows or col_num < 2 or rows[0][0] != "LuaConfigGen":
            warnings.append(f"{name} 不是配置表（A1 不是 LuaConfigGen），导出时会被跳过")
            continue
        cfg_name = rows[0][1]
        if cfg_name in config_names:
            errors.append(f"配置表重名：{cfg_name}（{config_names[cfg_name]} 与 {name}），后者会覆盖前者")
        config_names[cfg_name] = name
        lua_path = os.path.join(lua_dir, cfg_name + "Config.lua")
        if not os.path.isfile(lua_path):
            warnings.append(f"没有生成 {os.path.basename(lua_path)}，请运行 configs 子命令")
        elif os.path.getmtime(lua_path) + 1 < os.path.getmtime(path):
            warnings.append(f"{os.path.basename(lua_path)} 比 {name} 旧，请重新运行 configs 子命令")
    log(f"  配置表: {len(config_names)} 张 ({', '.join(config_names) or '无'})")

    # 4. Lua
    lua_files: list[str] = []
    preloaded = setting.get("PreloadedLua") or []
    for name in preloaded:
        path = os.path.join(mod_dir, "Lua", f"{name}.lua")
        if not os.path.isfile(path):
            errors.append(f"PreloadedLua 里列了 {name}，但找不到 {path}")
    if os.path.isdir(lua_dir):
        lua_files += [os.path.join(lua_dir, f) for f in sorted(os.listdir(lua_dir)) if f.endswith(".lua")]
    mod_lua_dir = os.path.join(mod_dir, "Lua")
    if args.all_lua and os.path.isdir(mod_lua_dir):
        lua_files += [os.path.join(mod_lua_dir, f) for f in sorted(os.listdir(mod_lua_dir)) if f.endswith(".lua")]
    syntax_errors: list[str] = []
    if lua_files:
        try:
            import lupa  # noqa: F401
        except ImportError:
            warnings.append("没有安装 lupa，跳过 Lua 语法检查（python -m pip install lupa）")
        else:
            syntax_errors = check_lua_syntax(lua_files)
    errors.extend(syntax_errors)
    log(f"  Lua: 检查 {len(lua_files)} 个文件（Preloaded: {', '.join(preloaded) or '无'}）")

    # 5. 汇总
    log("")
    for msg in warnings:
        warn(msg)
    for msg in errors:
        error(msg)
    if not errors and not warnings:
        ok("一切正常")
    elif not errors:
        ok(f"没有错误，{len(warnings)} 条提醒")
    else:
        log("")
        error(f"{len(errors)} 个错误，{len(warnings)} 条提醒")
    return 1 if errors else 0



# --------------------------------------------------------------------------------------
# install / uninstall / list
# --------------------------------------------------------------------------------------

def resolve_export_dir(src: str, mod_id: str) -> str:
    """允许 --src 指向导出根目录（里面是 <id>/）或直接指向 <id>/"""

    def has_bundles(path: str) -> bool:
        # 有 xml 且主资源包在，才算一个真正可用的导出目录
        return os.path.isfile(os.path.join(path, mod_id + ".xml")) and os.path.isfile(
            os.path.join(path, f"{mod_id}_mod"))

    if has_bundles(src):
        return src
    nested = os.path.join(src, mod_id)
    if has_bundles(nested):
        return nested
    if os.path.isfile(os.path.join(src, mod_id + ".xml")):
        return src
    if os.path.isfile(os.path.join(nested, mod_id + ".xml")):
        return nested
    die(f"{src} 里找不到 {mod_id}.xml，请先导出 MOD（unity 子命令）")


def installed_mods(root: str) -> list[str]:
    if not os.path.isdir(root):
        return []
    found = []
    for dirpath, _dirs, files in os.walk(root):
        found.extend(os.path.splitext(f)[0] for f in files if f.endswith(".xml"))
    return sorted(set(found))


def cmd_install(args) -> int:
    mod_id = normalize_mod_id(args.mod_id).lower()
    src = resolve_export_dir(abs_path(args.src) or os.path.join(REPO, "Export"), mod_id)
    game = require_game_dir(args.game)
    root = game_persistent_mods_dir(game) if args.persistent else game_mods_dir(game)
    dest = os.path.join(root, mod_id)

    main_bundle = os.path.join(src, f"{mod_id}_mod")
    map_bundle = os.path.join(src, f"{mod_id}_maps")
    if not os.path.isfile(main_bundle):
        die(f"缺少资源包：{main_bundle}")
    if not os.path.isfile(map_bundle):
        warn(f"缺少地图资源包：{map_bundle}（大地图场景相关功能会失效）")

    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    ok(f"已安装到 {dest}")
    log("    启动游戏后在 MOD 选择界面即可看到（手动安装）")
    return 0


def cmd_uninstall(args) -> int:
    mod_id = normalize_mod_id(args.mod_id).lower()
    game = require_game_dir(args.game)
    removed = 0
    for root in (game_mods_dir(game), game_persistent_mods_dir(game)):
        dest = os.path.join(root, mod_id)
        if os.path.isdir(dest):
            shutil.rmtree(dest)
            ok(f"已删除 {dest}")
            removed += 1
    if not removed:
        warn(f"游戏目录里没有安装 {mod_id}")
    return 0


def cmd_list(args) -> int:
    log("[工程里的 MOD]")
    for mod_id in list_project_mods():
        setting = parse_mod_setting(os.path.join(MODS_DIR, mod_id, "ModSetting.asset"))
        log(f"  {mod_id:<24} {setting.get('ModName', ''):<20} Native={setting.get('IsNativeMod', '0')}")

    game = detect_game_dir(args.game)
    if not game:
        warn("找不到游戏目录，跳过已安装 MOD 列表（可用 --game 指定）")
        return 0
    log("")
    log(f"[游戏里已安装的 MOD]  {game}")
    for root in (game_mods_dir(game), game_persistent_mods_dir(game)):
        mods = installed_mods(root)
        log(f"  {root}: {', '.join(mods) or '无'}")
    return 0



# --------------------------------------------------------------------------------------
# logs / run / unity
# --------------------------------------------------------------------------------------

def print_log_tail(path: str, lines: int, follow: bool) -> None:
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.readlines()
    for line in content[-lines:] if lines > 0 else content:
        print(line, end="", flush=True)
    if not follow:
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        try:
            while True:
                chunk = f.readline()
                if chunk:
                    print(chunk, end="", flush=True)
                else:
                    time.sleep(0.3)
        except KeyboardInterrupt:
            log("")


def cmd_logs(args) -> int:
    game = require_game_dir(args.game)
    path = player_log_path(game)
    if not os.path.isfile(path):
        die(f"找不到日志：{path}\n        先运行一次游戏（或 run 子命令）")
    log(f"# {path}")
    print_log_tail(path, args.lines, args.follow)
    return 0


def cmd_run(args) -> int:
    game = require_game_dir(args.game)
    exe = os.path.join(game, GAME_EXE)
    cmd = [exe] + list(args.game_args)
    if args.console:
        cmd += ["-logFile", "-"]
    log("启动：" + " ".join(cmd))
    proc = subprocess.Popen(cmd, cwd=game)
    if args.wait:
        return proc.wait()
    ok(f"已启动，PID={proc.pid}")
    if args.follow:
        time.sleep(args.delay)
        path = player_log_path(game)
        if os.path.isfile(path):
            print_log_tail(path, args.lines, True)
    return 0


UNITY_TARGETS = {
    "windows": "StandaloneWindows64",
    "win": "StandaloneWindows64",
    "android": "Android",
    "macos": "StandaloneOSX",
    "mac": "StandaloneOSX",
    "ios": "iOS",
}

# batchmode 常见失败的日志特征 -> 人话提示
UNITY_LOG_HINTS = (
    ("another Unity instance is running",
     "Unity 编辑器正打开着 jyx2 工程，请先完全关闭编辑器再重试（batchmode 不能和 GUI 共用同一工程）"),
    ("No valid Unity Editor license",
     "Unity 没有可用许可证，请打开 Unity Hub 登录 / 激活后重试"),
    ("executeMethod class",
     "Unity 没找到 Jyx2ModCli，通常是工程有编译错误，请先在编辑器里把 Console 的红字修掉"),
    ("executeMethod method",
     "Unity 没找到 BuildMod 方法，通常是工程有编译错误，请先在编辑器里把 Console 的红字修掉"),
    ("Scripts have compiler errors",
     "工程有编译错误，先去 Unity 编辑器里修好再打包"),
)


def unity_process_running() -> bool:
    """Windows 上确认是否真的有 Unity.exe 在跑（锁文件可能是上次崩溃留下的）"""
    if os.name != "nt":
        return True
    try:
        proc = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Unity.exe", "/NH"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return True  # 探测不了就按"在跑"处理，宁可拦住也别去抢工程
    return b"Unity.exe" in proc.stdout


def unity_project_locked() -> bool:
    """编辑器打开工程时会创建 Temp/UnityLockfile；崩溃残留的锁文件不算占用"""
    if not os.path.isfile(os.path.join(UNITY_PROJECT, "Temp", "UnityLockfile")):
        return False
    return unity_process_running()


def unity_log_hint(log_file: str) -> str | None:
    if not os.path.isfile(log_file):
        return None
    text = read_text(log_file)
    for pattern, hint in UNITY_LOG_HINTS:
        if pattern in text:
            return hint
    return None


def unity_log_has_unrecognized(log_file: str) -> bool:
    return os.path.isfile(log_file) and "Unrecognized assets cannot be included" in read_text(log_file)


def cleanup_manifest_bundle(out_dir: str) -> None:
    """Unity 会额外生成一个以输出目录名命名的 manifest 包，对分发无用，顺手删掉"""
    name = os.path.basename(os.path.normpath(out_dir))
    for path in (os.path.join(out_dir, name), os.path.join(out_dir, name + ".manifest")):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass


BASE_STAMP_NAME = ".base_assets.stamp"


def assets_fingerprint() -> str:
    """base_assets 是否变过的廉价指纹：Assets 下（排除 Mods）每个文件的 路径 + 大小。

    不用 mtime 是有原因的：Unity 每次打包都会重写少量 .mat，mtime 一脏就永远判定
    「资源变了」，跳过逻辑会失效。改用路径 + 大小，打包自身产生的重写基本不会误判。
    """
    digest = hashlib.sha1()
    for root, dirs, files in os.walk(ASSETS_DIR):
        dirs[:] = sorted(d for d in dirs if d != "Mods")
        for name in sorted(files):
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            rel = os.path.relpath(path, ASSETS_DIR).replace("\\", "/")
            digest.update(f"{rel}|{size}\n".encode("utf-8"))
    return digest.hexdigest()


def base_stamp_path(out_dir: str) -> str:
    return os.path.join(out_dir, BASE_STAMP_NAME)


def should_skip_base(out_dir: str) -> bool:
    """base_assets 已经打好了，且工程本体资源没动过 -> 这次不用重打（省 1.8GB 压缩）"""
    if not os.path.isfile(os.path.join(out_dir, "base_assets")):
        return False
    stamp = base_stamp_path(out_dir)
    if not os.path.isfile(stamp):
        return False
    return read_text(stamp).strip() == assets_fingerprint()


def mod_artifacts(mod_id: str, out_dir: str) -> list[str]:
    folder = os.path.join(out_dir, mod_id)
    return [os.path.join(folder, mod_id + ".xml"), os.path.join(folder, f"{mod_id}_mod")]


def mod_is_fresh(mod_id: str, mod_dir: str, out_dir: str) -> bool:
    """产物齐全且都比 MOD 源目录新 -> 没必要再启动 Unity（光启动 + 导入就要 1 分钟）"""
    artifacts = mod_artifacts(mod_id, out_dir)
    if not all(os.path.isfile(path) for path in artifacts):
        return False

    newest_src = 0.0
    for root, _dirs, files in os.walk(mod_dir):
        for name in files:
            try:
                newest_src = max(newest_src, os.path.getmtime(os.path.join(root, name)))
            except OSError:
                pass

    try:
        oldest_out = min(os.path.getmtime(path) for path in artifacts)
    except OSError:
        return False
    return oldest_out >= newest_src


def find_unity(explicit: str | None) -> str | None:
    version = project_version()
    candidates = [explicit, os.environ.get("JYX2_UNITY")]
    editor_roots = [
        r"C:\Program Files\Unity\Hub\Editor",
        r"C:\Program Files (x86)\Unity\Hub\Editor",
        r"D:\Program Files\Unity\Hub\Editor",
        r"D:\Unity\Hub\Editor",
        os.path.expanduser("~/Unity/Hub/Editor"),
    ]

    # Unity Hub 里配置过的自定义安装目录
    hub_cfg = os.path.join(os.environ.get("APPDATA", ""), "UnityHub", "secondaryInstallPath.json")
    if os.path.isfile(hub_cfg):
        try:
            extra = json.loads(read_text(hub_cfg).strip() or "[]")
        except ValueError:
            extra = []
        if isinstance(extra, str):
            extra = [extra]
        editor_roots.extend(str(p) for p in extra if p)

    if version:
        for root in editor_roots:
            candidates.append(os.path.join(root, version, "Editor", "Unity.exe"))

    # 独立安装：Unity 中国版默认装在 C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe
    for base in (r"C:\Program Files", r"C:\Program Files (x86)", r"D:\Program Files", "D:\\"):
        if version:
            candidates.append(os.path.join(base, f"Unity {version}", "Editor", "Unity.exe"))
        candidates.append(os.path.join(base, "Unity", "Editor", "Unity.exe"))
        if version:
            candidates.extend(
                os.path.join(path, "Editor", "Unity.exe")
                for path in sorted(glob.glob(os.path.join(base, f"Unity*{version}*")))
            )

    for path in candidates:
        if path and os.path.isfile(path):
            return os.path.abspath(path)
    return None


def cmd_unity(args) -> int:
    mod_id = normalize_mod_id(args.mod_id).lower()
    mod_dir = require_mod_dir(mod_id)
    unity = find_unity(args.unity)
    if not unity:
        die(
            f"找不到 Unity（工程版本 {project_version() or '未知'}）。\n"
            "        请用 --unity 指定 Unity.exe，或设置环境变量 JYX2_UNITY，例如：\n"
            r'        $env:JYX2_UNITY="C:\Program Files\Unity\Hub\Editor\2020.3.32f1c1\Editor\Unity.exe"'
        )

    target = UNITY_TARGETS.get(args.target.lower())
    if not target:
        die(f"不支持的平台 {args.target!r}，可用：{', '.join(sorted(UNITY_TARGETS))}")

    if unity_project_locked():
        die(
            "Unity 编辑器正打开着 jyx2 工程，batchmode 无法和它共用同一个工程。\n"
            "        请先完全退出 Unity 编辑器（保存好场景），再重新运行 unity 子命令。"
        )

    out_dir = abs_path(args.output) or os.path.join(REPO, "Export")
    os.makedirs(out_dir, exist_ok=True)
    log_dir = os.path.join(REPO, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"unity_build_{mod_id}.log")

    force = getattr(args, "force", False)

    # 1) MOD 源和产物比时间：没改动就整个跳过（Unity 光启动 + 导入就要 1 分钟）
    if not force and mod_is_fresh(mod_id, mod_dir, out_dir):
        ok(f"没有检测到改动，跳过构建：{os.path.join(out_dir, mod_id)}")
        log("    确实要重新打包就加 --force")
        return 0

    # 2) base_assets 只在工程本体资源变化时才重打，它是打包耗时的大头（1.8GB 未压缩）
    if getattr(args, "no_base", False):
        skip_base = True
    elif getattr(args, "with_base", False):
        skip_base = False
    else:
        skip_base = not force and should_skip_base(out_dir)

    cmd = [
        unity, "-batchmode", "-nographics", "-quit", "-silent-crashes",
        "-projectPath", UNITY_PROJECT,
        "-executeMethod", "Jyx2Editor.BuildTool.Jyx2ModCli.BuildMod",
        "-logFile", log_file,
        "-modId", mod_id,
        "-exportPath", out_dir,
        "-buildTarget", target,
    ]
    if skip_base:
        cmd += ["-skipBase", "1"]
    log("执行：" + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    if skip_base:
        log("    base_assets 无变化，本次跳过（省掉约 1.8GB 序列化 + 压缩）")
        log("    注意：跳过时共享资源会被复制进 MOD 包（包更大）。最终分发想要更小的包，")
        log("          用 --with-base 全量打一次即可。")
    code = subprocess.call(cmd)
    if code != 0:
        error(f"Unity 退出码 {code}，日志：{log_file}")
        hint = unity_log_hint(log_file)
        if hint:
            warn(hint)
        if os.path.isfile(log_file):
            print_log_tail(log_file, 40, False)
        return code

    xml_path = os.path.join(out_dir, mod_id, mod_id + ".xml")
    if os.path.isfile(xml_path):
        cleanup_manifest_bundle(out_dir)
        # 记下「这次打包时工程资源的指纹」，下次 should_skip_base() 靠它判断
        try:
            write_text(base_stamp_path(out_dir), assets_fingerprint())
        except OSError:
            pass
        ok(f"导出完成：{os.path.join(out_dir, mod_id)}")
        if unity_log_has_unrecognized(log_file):
            log(
                "    提示：日志里的 \"Unrecognized assets cannot be included\" 是无害的 ——\n"
                "          Configs/Lua 目录的 .meta 上打了 AssetBundle 名，使 .xlsx/.md 也被算进包，\n"
                "          Unity 会跳过它们，不影响产物（官方 Jyx2ModTool 行为一致）。"
            )
        log(f"    安装：python tools/moddev/jyx2mod.py install {mod_id} --src {out_dir}")
        return 0
    error(f"Unity 执行结束但没有生成 {xml_path}，请查看日志 {log_file}")
    return 1



# --------------------------------------------------------------------------------------
# 命令行入口
# --------------------------------------------------------------------------------------

EPILOG = """常用流程：
  # 1. 新建 MOD（从 SAMPLE 复制，改好 ModSetting / .meta / AssetBundle 名）
  python tools/moddev/jyx2mod.py new mymod --name 我的MOD --author 我

  # 2. 改完 Configs/*.xlsx 后导出 Lua（不需要 Unity）
  python tools/moddev/jyx2mod.py configs mymod

  # 3. 体检
  python tools/moddev/jyx2mod.py check mymod

  # 4. 用 Unity 命令行导出 AssetBundle + xml（需要本机 Unity 2020.3.32f1c1）
  python tools/moddev/jyx2mod.py unity mymod --output Export

  # 5. 安装进游戏并启动，边玩边看日志
  python tools/moddev/jyx2mod.py install mymod --src Export/mymod
  python tools/moddev/jyx2mod.py run --follow
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jyx2mod",
        description="群侠传，启动！(jynew) MOD 开发命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="子命令")

    p = sub.add_parser("new", help="从模板创建新 MOD")
    p.add_argument("mod_id", help="MOD Id（小写字母/数字/下划线）")
    p.add_argument("--template", default=DEFAULT_TEMPLATE, help=f"模板 MOD，默认 {DEFAULT_TEMPLATE}")
    p.add_argument("--name", help="显示名（ModName）")
    p.add_argument("--author", help="作者")
    p.add_argument("--desc", help="MOD 简介")
    p.add_argument("--native", action="store_true", help="设成原生 MOD（IsNativeMod=1）")
    p.add_argument("--with-buildsource", action="store_true", help="连模板的 BuildSource 一起复制（约 50MB）")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("configs", help="导出 Excel 配置表为 Lua")
    p.add_argument("mod_id")
    p.add_argument("--dir", help="配置表目录，默认 <MOD>/Configs")
    p.add_argument("-o", "--out", help="输出目录，默认 <MOD>/Configs/Lua")
    p.add_argument("--no-clean", action="store_true", help="不清空输出目录")
    p.set_defaults(func=cmd_configs)

    p = sub.add_parser("xml", help="生成 <id>.xml（GameModInfo）")
    p.add_argument("mod_id")
    p.add_argument("-o", "--out", help="输出文件或目录，默认 Export/<id>/<id>.xml")
    p.add_argument("--name")
    p.add_argument("--author")
    p.add_argument("--desc")
    p.add_argument("--version")
    p.add_argument("--platform", default="windows", help="windows/android/macos/ios")
    p.set_defaults(func=cmd_xml)

    p = sub.add_parser("check", help="MOD 体检")
    p.add_argument("mod_id")
    p.add_argument("--all-lua", action="store_true", help="连 <MOD>/Lua 下所有脚本一起做语法检查")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("install", help="把导出的 MOD 安装进游戏")
    p.add_argument("mod_id")
    p.add_argument("--src", help="导出目录，默认 Export（里面是 <id>/）")
    p.add_argument("--game", help="游戏根目录")
    p.add_argument("--persistent", action="store_true", help="装到 persistentDataPath/mods 而不是 <exe>_Data/mods")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("uninstall", help="从游戏里卸载 MOD")
    p.add_argument("mod_id")
    p.add_argument("--game")
    p.set_defaults(func=cmd_uninstall)

    p = sub.add_parser("list", help="列出工程内 / 游戏内已安装的 MOD")
    p.add_argument("--game")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("logs", help="查看游戏 Player.log")
    p.add_argument("--game")
    p.add_argument("-n", "--lines", type=int, default=200, help="显示最后 N 行，默认 200")
    p.add_argument("-f", "--follow", action="store_true", help="持续跟踪（Ctrl+C 退出）")
    p.set_defaults(func=cmd_logs)

    p = sub.add_parser("run", help="启动游戏")
    p.add_argument("--game")
    p.add_argument("--console", action="store_true", help="日志输出到控制台（-logFile -）")
    p.add_argument("-f", "--follow", action="store_true", help="启动后跟踪 Player.log")
    p.add_argument("-n", "--lines", type=int, default=50)
    p.add_argument("--delay", type=float, default=8.0, help="跟踪日志前等待秒数，默认 8")
    p.add_argument("--wait", action="store_true", help="等待游戏退出")
    p.add_argument("game_args", nargs=argparse.REMAINDER, help="透传给游戏的参数")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("unity", help="用 Unity 命令行导出 MOD（AssetBundle + xml）")
    p.add_argument("mod_id")
    p.add_argument("-o", "--output", help="导出目录，默认 Export")
    p.add_argument("-t", "--target", default="windows", help="windows/android/macos/ios")
    p.add_argument("--unity", help="Unity.exe 路径（默认自动查找 / 环境变量 JYX2_UNITY）")
    p.add_argument("--force", action="store_true", help="忽略增量判断，全量重建")
    base_group = p.add_mutually_exclusive_group()
    base_group.add_argument("--with-base", dest="with_base", action="store_true",
                            help="强制重建 base_assets（默认仅在工程本体资源变化时才重建）")
    base_group.add_argument("--no-base", dest="no_base", action="store_true", help="强制跳过 base_assets")
    p.set_defaults(func=cmd_unity)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "game_args", None) is not None:
        args.game_args = [a for a in args.game_args if a]
    return args.func(args) or 0


if __name__ == "__main__":
    raise SystemExit(main())

