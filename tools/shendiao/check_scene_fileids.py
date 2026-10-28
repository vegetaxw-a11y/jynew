# -*- coding: utf-8 -*-
"""检查 .unity 场景内部 fileID 自引用是否完整（不依赖 Unity 就能发现断链）。

add_prefab.py / edit_instance.py / patch_scene_events.py 都是**直接改 YAML 文本**，
写错一个 fileID 就要等 Unity 打开（或导出 AB 失败）才发现。本工具只看结构性的
自引用，覆盖手写块最常犯的错：

  1. m_TransformParent / m_Father 指向不存在的 Transform
  2. m_Children 里的 Transform 不存在
  3. stripped 块的 m_PrefabInstance 指向不存在的 PrefabInstance
  4. 场景里出现重复的 `--- !u!x &id`
  5. PrefabInstance 的 m_SourcePrefab guid 在本工程找不到对应文件

用法:
    python tools/shendiao/check_scene_fileids.py                 # 查全部 GameMaps 场景
    python tools/shendiao/check_scene_fileids.py 18_gumu.unity   # 只查一个
"""
import glob
import io
import json
import os
import re
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAPS = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps')
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)
GUID_CACHE = os.path.join(tempfile.gettempdir(), 'jyx2_guid_cache.json')


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    return [(m.group(1), m.group(2), bool(m.group(3)),
             text[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(text)])
            for i, m in enumerate(ms)]


def guid_index():
    if os.path.exists(GUID_CACHE):
        return json.load(io.open(GUID_CACHE, encoding='utf-8'))
    return {}


def check(path, idx):
    text = io.open(path, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    ids = {}
    probs = []
    for cls, fid, st, body in blocks:
        if fid in ids:
            probs.append('重复 fileID %s（%s 与 %s）' % (fid, ids[fid], cls))
        ids[fid] = cls

    tr_ids = {fid for cls, fid, st, body in blocks if cls in ('4', '224')}
    for cls, fid, st, body in blocks:
        if cls == '1001':
            m = re.search(r'm_TransformParent: \{fileID: (-?\d+)\}', body)
            if m and m.group(1) != '0' and m.group(1) not in tr_ids:
                probs.append('PrefabInstance &%s 的父 Transform %s 不存在'
                             % (fid, m.group(1)))
            g = re.search(r'm_SourcePrefab: \{fileID: 100100000, guid: ([0-9a-f]{32})',
                          body)
            if g and idx and g.group(1) not in idx:
                probs.append('PrefabInstance &%s 的源 prefab guid %s 找不到文件'
                             % (fid, g.group(1)))
        elif st:
            m = re.search(r'm_PrefabInstance: \{fileID: (-?\d+)\}', body)
            if m and ids.get(m.group(1)) != '1001':
                probs.append('stripped &%s 的 m_PrefabInstance %s 不存在'
                             % (fid, m.group(1)))
        if cls in ('4', '224'):
            for m in re.finditer(r'^  - \{fileID: (-?\d+)\}', body, re.M):
                if m.group(1) not in tr_ids:
                    probs.append('Transform &%s 的子节点 %s 不存在' % (fid, m.group(1)))
            m = re.search(r'm_Father: \{fileID: (-?\d+)\}', body)
            if m and m.group(1) != '0' and m.group(1) not in tr_ids:
                probs.append('Transform &%s 的 m_Father %s 不存在' % (fid, m.group(1)))
    return probs


def main():
    argv = sys.argv[1:]
    idx = guid_index()
    files = ([os.path.join(MAPS, a) for a in argv] if argv
             else sorted(glob.glob(os.path.join(MAPS, '*.unity'))))
    total = 0
    for f in files:
        if not os.path.exists(f):
            print('!! 找不到 %s' % f)
            total += 1
            continue
        probs = check(f, idx)
        if probs:
            total += len(probs)
            print('%s' % os.path.basename(f))
            for p in probs[:20]:
                print('    %s' % p)
            if len(probs) > 20:
                print('    …… 另有 %d 条' % (len(probs) - 20))
    print()
    print('检查 %d 个场景，问题 %d 条' % (len(files), total))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
