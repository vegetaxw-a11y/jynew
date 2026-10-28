# -*- coding: utf-8 -*-
"""检查场景引用的 prefab（及关键资源）落在哪个 AssetBundle，找出加载不到的资源。

用法:
    python tools/shendiao/check_scene_ab.py jyx2/Assets/Mods/shendiao/Maps/GameMaps/62_pomiao.unity
    python tools/shendiao/check_scene_ab.py <scene> --prefabs-only
"""
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(REPO, "jyx2", "Assets")

GUID_RE = re.compile(r'guid:\s*([0-9a-f]{32})')
SRC_PREFAB_RE = re.compile(
    r'm_SourcePrefab:\s*\{fileID:\s*-?\d+,\s*guid:\s*([0-9a-f]{32})')


def build_index():
    """guid -> (相对路径, assetBundleName)"""
    idx = {}
    for root, dirs, files in os.walk(ASSETS):
        dirs[:] = [d for d in dirs if d not in ('Library', 'Temp', 'obj')]
        for f in files:
            if not f.endswith('.meta'):
                continue
            p = os.path.join(root, f)
            try:
                with io.open(p, encoding='utf-8', errors='replace') as fh:
                    head = fh.read(600)
            except OSError:
                continue
            m = re.search(r'^guid:\s*([0-9a-f]{32})', head, re.M)
            if not m:
                continue
            ab = re.search(r'^assetBundleName:\s*(\S*)', head, re.M)
            idx[m.group(1)] = (os.path.relpath(p[:-5], REPO), ab.group(1) if ab else '')
    return idx


def main():
    scene = sys.argv[1]
    prefabs_only = '--prefabs-only' in sys.argv

    with io.open(scene, encoding='utf-8', errors='replace') as f:
        text = f.read()

    src_guids = SRC_PREFAB_RE.findall(text)
    print('场景: %s' % scene)
    print('prefab 实例 %d 个（去重 %d）' % (len(src_guids), len(set(src_guids))))

    all_guids = set(GUID_RE.findall(text)) if not prefabs_only else set(src_guids)

    idx = build_index()
    print('资产索引 %d 条' % len(idx))
    print()

    missing, no_ab = [], []
    print('%-34s %-18s %s' % ('资源', 'AssetBundle', '说明'))
    print('-' * 100)
    for g in sorted(all_guids):
        info = idx.get(g)
        if not info:
            missing.append(g)
            print('%-34s %-18s %s' % (g, '<未找到>', 'GUID 在 Assets 里不存在'))
            continue
        rel, ab = info
        mark = ''
        if not ab:
            no_ab.append(rel)
            mark = '无 AB'
        print('%-34s %-18s %s %s' % (g, ab or '(none)', rel, mark))

    print()
    if missing:
        print('!! 未找到 %d 个 GUID' % len(missing))
    if no_ab:
        print('!! 无 AssetBundle 的资源 %d 个（依赖 base_assets，需确认打进主包）' % len(no_ab))


if __name__ == '__main__':
    main()
