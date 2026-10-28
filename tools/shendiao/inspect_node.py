# -*- coding: utf-8 -*-
"""精确查看某个节点的子物体（包含 prefab 实例内部的 stripped Transform）。

用法: python tools/shendiao/inspect_node.py <scene.unity> <节点名> [--depth N]
"""
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
        # 再处理一层转义（有些场景是双转义）
        s = s.replace('\\u5C0F', '小')
    return s


def main():
    path, target = sys.argv[1], sys.argv[2]
    depth = 4
    if '--depth' in sys.argv:
        depth = int(sys.argv[sys.argv.index('--depth') + 1])

    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    ms = list(BLOCK_RE.finditer(text))
    blocks = {}
    order = []
    for i, m in enumerate(ms):
        cls, fid, stripped = m.group(1), m.group(2), m.group(3)
        body = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        blocks[fid] = (cls, stripped is not None, body)
        order.append(fid)

    # GameObject -> 名字
    go_name = {}
    for fid, (cls, stripped, body) in blocks.items():
        if cls == '1' and not stripped:
            m = re.search(r'^  m_Name: (.*)$', body, re.M)
            if m:
                go_name[fid] = unquote(m.group(1))

    # GameObject -> Transform
    go_tr = {}
    tr_go = {}
    tr_children = {}
    tr_pos = {}
    for fid, (cls, stripped, body) in blocks.items():
        if cls not in ('4', '224'):
            continue
        g = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
        if g:
            go_tr[g.group(1)] = fid
            tr_go[fid] = g.group(1)
        ch = re.search(r'^  m_Children:(.*?)(?=^  m_Father:)', body, re.M | re.S)
        if ch:
            tr_children[fid] = re.findall(r'fileID: (-?\d+)', ch.group(1))
        p = re.search(r'^  m_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+)\}',
                      body, re.M)
        if p:
            tr_pos[fid] = tuple(round(float(p.group(k)), 2) for k in (1, 2, 3))

    # 找目标 GameObject
    target_go = None
    for fid, name in go_name.items():
        if name == target:
            target_go = fid
            break
    if not target_go:
        print('找不到同名 GameObject: %s' % target)
        print('已知名字样例: %s' % ', '.join(list(go_name.values())[:20]))
        return

    root_tr = go_tr.get(target_go)
    print('目标 %s: GameObject %s / Transform %s' % (target, target_go, root_tr))

    def walk(tr, level):
        if level > depth:
            return
        gid = tr_go.get(tr)
        name = go_name.get(gid, '<prefab内部/stripped>')
        cls = blocks.get(tr, ('?', True, ''))[0]
        print('%s- %s  [tr %s, pos %s%s]'
              % ('  ' * level, name, tr, tr_pos.get(tr), ', stripped' if blocks.get(tr, ('', False))[1] else ''))
        for c in tr_children.get(tr, []):
            walk(c, level + 1)

    walk(root_tr, 0)


if __name__ == '__main__':
    main()
