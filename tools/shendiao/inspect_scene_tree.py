# -*- coding: utf-8 -*-
"""导出 Unity 场景的 GameObject 层级树（摘要）。

Unity 的 .unity 是 YAML 文本，几 MB 直接读会爆上下文，所以先用它压缩成树。
用法：
    python tools/shendiao/inspect_scene_tree.py <scene.unity> [--depth N] [--filter KEY] [--roots N]

注意：Unity YAML 里的中文是 "\\uXXXX" 转义形式，这里会解码成真中文。
"""
import re
import sys

# 块头形如 `--- !u!4 &123456`，Prefab 实例的引用块会多一个 ` stripped` 后缀
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
        s = s.replace('\\"', '"').replace('\\\\', '\\')
    return s


def parse(text):
    """返回 (gos, transforms, comps)
    gos: fileID -> name
    transforms: fileID -> {'go': id, 'father': id, 'children': [ids]}
    comps: go_id -> [class_id, ...]
    """
    gos, trs, comps = {}, {}, {}
    n_stripped = 0
    blocks = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(blocks):
        if m.group(3):  # `stripped` 块是 Prefab 实例的引用占位，没有 m_Name、没有真实数据
            n_stripped += 1
            continue
        cls, fid = m.group(1), m.group(2)
        start = m.end()
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        body = text[start:end]
        if cls == '1':  # GameObject
            nm = re.search(r'^  m_Name: (.*)$', body, re.M)
            gos[fid] = unquote(nm.group(1)) if nm else '(unnamed)'
        elif cls in ('4', '224'):  # Transform / RectTransform
            go = re.search(r'^  m_GameObject: \{fileID: (\d+)\}', body, re.M)
            fa = re.search(r'^  m_Father: \{fileID: (\d+)\}', body, re.M)
            kids = []
            ch = re.search(r'^  m_Children:(.*?)(?=^  \w|\Z)', body, re.M | re.S)
            if ch:
                kids = re.findall(r'fileID: (\d+)', ch.group(1))
            trs[fid] = {
                'go': go.group(1) if go else None,
                'father': fa.group(1) if fa else '0',
                'children': kids,
            }
        else:  # 其它组件，挂到所属 GameObject
            go = re.search(r'^  m_GameObject: \{fileID: (\d+)\}', body, re.M)
            if go:
                comps.setdefault(go.group(1), []).append(int(cls))
    return gos, trs, comps, n_stripped


CLASS_NAME = {
    20: 'Camera', 33: 'MeshFilter', 23: 'MeshRenderer', 64: 'MeshCollider',
    65: 'BoxCollider', 136: 'CapsuleCollider', 135: 'SphereCollider',
    108: 'Light', 218: 'Terrain', 154: 'TerrainCollider', 195: 'NavMeshAgent',
    114: 'MonoBehaviour', 81: 'AudioListener', 82: 'AudioSource',
    222: 'CanvasRenderer', 223: 'Canvas', 1001: 'PrefabInstance',
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]

    def opt(flag, default=None):
        if flag in sys.argv:
            return sys.argv[sys.argv.index(flag) + 1]
        return default

    depth = int(opt('--depth', '99'))
    key = opt('--filter')
    max_roots = int(opt('--roots', '999'))

    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    gos, trs, comps, n_stripped = parse(text)

    # 根 Transform：父为 0，或父指向 stripped 占位块（即 Prefab 实例内部的物体）
    roots, n_orphan = [], 0
    for tid, t in trs.items():
        if t['go'] is None:
            continue
        fa = t['father']
        if fa in ('0', ''):
            roots.append(tid)
        elif fa not in trs:
            n_orphan += 1
            roots.append(tid)

    def weight(tid):
        cls = comps.get(trs[tid]['go'], [])
        w = 0
        if 218 in cls:      # Terrain 排最前
            w -= 100
        if 20 in cls:       # 相机次之
            w -= 50
        return w - len(trs[tid]['children'])

    roots.sort(key=weight)

    out = []
    out.append('场景: %s' % path)
    out.append('GameObject %d 个 / Transform %d 个 / 根节点 %d 个（其中 %d 个来自 Prefab 实例内部）'
               % (len(gos), len(trs), len(roots), n_orphan))
    out.append('跳过 stripped 占位块 %d 个' % n_stripped)

    stat = {}
    for go, cls in comps.items():
        for c in cls:
            stat[c] = stat.get(c, 0) + 1
    pretty = sorted(stat.items(), key=lambda kv: -kv[1])
    out.append('组件统计: ' + ', '.join(
        '%s x%d' % (CLASS_NAME.get(c, '!u!%d' % c), n) for c, n in pretty if n > 3))
    out.append('')

    shown = [0]

    def walk(tid, ind, shown_flag):
        t = trs.get(tid)
        if not t:
            return
        go = t['go']
        name = gos.get(go, '(missing)')
        hit = (key is None) or (key in name)
        if hit and shown_flag[0] < max_roots:
            tags = []
            cls = comps.get(go, [])
            for c in (218, 20, 195, 154, 108, 223):
                if c in cls:
                    tags.append(CLASS_NAME[c])
            suffix = ('  [%s]' % ','.join(tags)) if tags else ''
            out.append('%s%s%s' % ('  ' * ind, name, suffix))
        if ind + 1 < depth:
            for k in t['children']:
                walk(k, ind + 1, [shown_flag[0] + 1])

    for r in roots[:max_roots]:
        walk(r, 0, shown)

    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
