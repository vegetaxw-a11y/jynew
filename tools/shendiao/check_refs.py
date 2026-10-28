# -*- coding: utf-8 -*-
"""MOD 资源引用体检：扫描 MOD 内所有资源，检查它们引用的 guid 是否可用。

分类:
  SELF      本 MOD 内（会打进 mod bundle）
  BUILD     Assets/BuildSource/**（随 base_assets 打包）
  GLOBAL    Assets/{Prefabs,3DScene,3D,Scripts,Resources,...}（引擎侧全局资源）
  OTHERMOD  其他 Assets/Mods/<x>/**  ← 危险：别的 MOD 的资源，本 MOD bundle 不含
  MISSING   .meta 里找不到          ← 断裂引用

用法: python tools/shendiao/check_refs.py [MOD 目录]
"""
import io
import os
import re
import sys
import collections

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNITY = os.path.join(REPO, "jyx2")
ASSETS = os.path.join(UNITY, "Assets")

SCAN_EXT = (".unity", ".prefab", ".mat", ".asset", ".controller", ".anim", ".playable")
BUILTIN_RE = re.compile(r"^0{16}[0-9a-f]0{15}$")
GUID_RE = re.compile(r"guid:\s*([0-9a-f]{32})")


def build_index():
    idx = {}
    for dirpath, _d, files in os.walk(ASSETS):
        for fn in files:
            if not fn.endswith(".meta"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                head = io.open(p, encoding="utf-8", errors="replace").read(200)
            except OSError:
                continue
            m = re.search(r"^guid:\s*([0-9a-f]{32})", head, re.M)
            if m:
                idx[m.group(1)] = p[:-5]
    return idx


def classify(path, mod_dir):
    rel = os.path.relpath(path, ASSETS).replace("\\", "/")
    if rel.startswith(mod_dir + "/"):
        return "SELF"
    if rel.startswith("BuildSource/"):
        return "BUILD"
    m = re.match(r"Mods/([^/]+)/", rel)
    if m:
        return "OTHERMOD:" + m.group(1)
    return "GLOBAL"


def main():
    mod_dir = sys.argv[1] if len(sys.argv) > 1 else "Mods/shendiao"
    mod_abs = os.path.join(ASSETS, *mod_dir.split("/"))
    idx = build_index()

    files = []
    for dirpath, _d, names in os.walk(mod_abs):
        for fn in names:
            if fn.endswith(SCAN_EXT):
                files.append(os.path.join(dirpath, fn))

    stats = collections.Counter()
    other = collections.defaultdict(set)
    missing = collections.defaultdict(set)

    for f in files:
        try:
            text = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        rel = os.path.relpath(f, UNITY).replace("\\", "/")
        for g in set(GUID_RE.findall(text)):
            if BUILTIN_RE.match(g):
                stats["BUILTIN"] += 1
                continue
            target = idx.get(g)
            if target is None:
                stats["MISSING"] += 1
                missing[rel].add(g)
                continue
            kind = classify(target, mod_dir)
            stats[kind] += 1
            if kind.startswith("OTHERMOD"):
                other[rel].add((g, os.path.relpath(target, UNITY).replace("\\", "/")))

    print("扫描 %d 个资源文件（%s）" % (len(files), mod_dir))
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print("  %-16s %d" % (k, v))

    if other:
        print("\n!! 跨 MOD 引用（本 MOD bundle 不含，运行时会丢资源）:")
        for rel, items in sorted(other.items()):
            print("  " + rel)
            for g, p in sorted(items):
                print("      %s -> %s" % (g[:10], p))
    if missing:
        print("\n!! 断裂引用（.meta 不存在）:")
        for rel, gs in sorted(missing.items()):
            print("  %s: %s" % (rel, ", ".join(sorted(x[:10] for x in gs))))

    if not other and not missing:
        print("\n[OK] 没有跨 MOD 或断裂引用")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
