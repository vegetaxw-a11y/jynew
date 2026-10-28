# -*- coding: utf-8 -*-
"""查 prefab 实例的 stripped GameObject / Transform fileID。

为什么需要：GameEvent.m_EventTargets 必须引用 **stripped GameObject 的 fileID**，
不是 PrefabInstance(!u!1001) 的 instanceID（上一章的坑：填 instanceID 后
Unity 反序列化能过，但运行时 targets 解析成 null，交互永不弹）。

add_prefab.py 只管自己新建的实例（会打印），这里用来查**场景里原本就有的**
实例（石棺、门、模板 NPC），绑事件时经常要。

用法:
    python tools/shendiao/resolve_target.py --scene <scene.unity>            # 全列
    python tools/shendiao/resolve_target.py --scene <scene.unity> --name 郭芙
    python tools/shendiao/resolve_target.py --scene <scene.unity> --instance 480963067
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from list_prefab_instances import (guid_index, split_blocks, unescape, MOD_RE,  # noqa: E402
                                   SRC_RE)

PREFAB_INST_RE = re.compile(r'm_PrefabInstance:\s*\{fileID:\s*(-?\d+)\}')


def load(scene):
    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    guid = guid_index()

    insts = []
    for b in blocks:
        if b['cls'] != '1001':
            continue
        body = b['body']
        mods = dict((k, unescape(v)) for k, v in MOD_RE.findall(body))
        src = SRC_RE.search(body)
        insts.append({'instance': b['fid'],
                      'name': mods.get('m_Name', ''),
                      'prefab': guid.get(src.group(1), '?') if src else '?',
                      'go': None, 'tr': None})

    for b in blocks:
        if not b['stripped'] or b['cls'] not in ('1', '4', '224'):
            continue
        m = PREFAB_INST_RE.search(b['body'])
        if not m:
            continue
        for inst in insts:
            if inst['instance'] == m.group(1):
                if b['cls'] == '1':
                    inst['go'] = b['fid']
                else:
                    inst['tr'] = b['fid']
                break
    return insts


def main():
    argv = sys.argv[1:]
    scene = name = inst = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--scene':
            scene = argv[i + 1]
            i += 2
        elif a == '--name':
            name = argv[i + 1]
            i += 2
        elif a == '--instance':
            inst = argv[i + 1]
            i += 2
        else:
            i += 1

    if not scene:
        print(__doc__)
        return 2

    rows = load(scene)
    if name:
        rows = [r for r in rows if r['name'] == name or name in r['name']]
    if inst:
        rows = [r for r in rows if r['instance'] == inst]
    if not rows:
        print('没有匹配的实例')
        return 1

    print('%-20s %-16s %-22s %s' % ('instanceID', '名字', 'strippedGO', 'strippedTr'))
    for r in rows:
        print('%-20s %-16s %-22s %s'
              % (r['instance'], r['name'][:16] or '-', r['go'] or '【无】', r['tr'] or '【无】'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
