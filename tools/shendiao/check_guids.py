"""校验 shendiao MOD 里的 GUID 引用是否都能解析。

GUID 断了在 Unity 里只表现为「模型变空气 / 贴图丢失 / NPC 隐形」，不报错，
所以导出前跑一遍这个脚本兜底。

用法：python tools/shendiao/check_guids.py
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT = os.path.join(ROOT, "jyx2")
ASSETS = os.path.join(PROJECT, "Assets")
SHENDIAO = os.path.join(ASSETS, "Mods", "shendiao")

GUID_RE = re.compile(r"guid: ([0-9a-fA-F]{32})")
META_GUID_RE = re.compile(r"^guid: ([0-9a-fA-F]{32})\s*$", re.M)


def collect_all_guids() -> dict:
    """收集工程内 + Packages + PackageCache 里注册的所有 GUID。

    URP/TextMeshPro/PostProcessing 这些包的资源不在 Assets 下，只在 Packages 或
    Library/PackageCache 里注册，漏了它们会刷一堆误报。
    """
    known = {}
    scan_roots = [
        ASSETS,
        os.path.join(PROJECT, "Packages"),
        os.path.join(PROJECT, "Library", "PackageCache"),
    ]
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".meta"):
                    continue
                path = os.path.join(dirpath, name)
                try:
                    text = open(path, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                m = META_GUID_RE.search(text)
                if m:
                    known[m.group(1).lower()] = path[: -len(".meta")]
    return known


def main() -> int:
    known = collect_all_guids()
    print(f"工程内已注册 GUID：{len(known)} 个")

    targets = sys.argv[1:] or [SHENDIAO]
    bad = {}
    checked = 0
    for target in targets:
        paths = []
        if os.path.isdir(target):
            for dirpath, _dirs, files in os.walk(target):
                paths.extend(os.path.join(dirpath, f) for f in files)
        else:
            paths.append(target)
        for path in paths:
            if path.endswith(".meta"):
                continue
            try:
                text = open(path, encoding="utf-8", newline="").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "guid: " not in text:
                continue
            checked += 1
            for m in GUID_RE.finditer(text):
                guid = m.group(1).lower()
                if guid.strip("0") == "":
                    continue  # Unity 内置资源（default resources）都用全 0 GUID
                if guid not in known:
                    bad.setdefault(os.path.relpath(path, SHENDIAO), set()).add(guid)

    print(f"检查 {checked} 个资源文件，{len(bad)} 个文件存在无法解析的引用")
    for rel, guids in sorted(bad.items()):
        print(f"  [error] {rel}: {', '.join(sorted(guids))}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
