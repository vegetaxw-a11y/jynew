# -*- coding: utf-8 -*-
"""列出 .unity 场景里所有 prefab 实例：名字 / 局部坐标 / 父节点 / 源 prefab 路径。

为什么要这个工具：prefab 实例在场景里只留下 `stripped` 块，里面既没有 m_Name 也没有
m_LocalPosition —— 名字和坐标全都在 PrefabInstance(!u!1001) 的 m_Modifications 里。
只看层级树（inspect_node.py）永远是一堆 `<prefab内部/stripped>`，分不清谁是谁。

用法:
    python tools/shendiao/list_prefab_instances.py <scene.unity>
    python tools/shendiao/list_prefab_instances.py <scene.unity> --parent NPC
    python tools/shendiao/list_prefab_instances.py <scene.unity> --grep 桌
    python tools/shendiao/list_prefab_instances.py <scene.unity> --detail
"""
import io
import json
import os
import re
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(REPO, "jyx2", "Assets")
CACHE = os.path.join(tempfile.gettempdir(), "jyx2_guid_cache.json")

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)
MOD_RE = re.compile(r'propertyPath:\s*(\S+)\s*\n\s+value:\s*(.*?)\s*\n', re.M)
SRC_RE = re.compile(r'm_SourcePrefab:\s*\{fileID:\s*-?\d+,\s*guid:\s*([0-9a-f]{32})')
PARENT_RE = re.compile(r'm_TransformParent:\s*\{fileID:\s*(-?\d+)\}')
CHILD_RE = re.compile(r'- \{fileID: (-?\d+)\}')


def unescape(s):
    s = s.strip()
    while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)


def guid_index():
    """guid -> Assets 内相对路径（带磁盘缓存，首次较慢）"""
    if os.path.exists(CACHE):
        try:
            with io.open(CACHE, encoding='utf-8') as f:
                return json.load(f)
        except (OSError, ValueError):
            pass
    idx = {}
    for root, dirs, files in os.walk(ASSETS):
        dirs[:] = [d for d in dirs if d not in ('Library', 'Temp', 'obj')]
        for f in files:
            if not f.endswith('.meta'):
                continue
            p = os.path.join(root, f)
            try:
                with io.open(p, encoding='utf-8', errors='replace') as fh:
                    head = fh.read(400)
            except OSError:
                continue
            m = re.search(r'^guid:\s*([0-9a-f]{32})', head, re.M)
            if m:
                idx[m.group(1)] = os.path.relpath(p[:-5], REPO).replace('\\', '/')
    try:
        with io.open(CACHE, 'w', encoding='utf-8') as f:
            json.dump(idx, f)
    except OSError:
        pass
    return idx


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append({'cls': m.group(1), 'fid': m.group(2),
                    'stripped': bool(m.group(3)),
                    'start': m.start(), 'end': end,
                    'body': text[m.end():end]})
    return out


def parse_scene(text):
    blocks = split_blocks(text)

    go_name, go_tr, tr_go, tr_father, tr_pos = {}, {}, {}, {}, {}
    for b in blocks:
        body, cls = b['body'], b['cls']
        if cls == '1' and not b['stripped']:
            m = re.search(r'^  m_Name: (.*)$', body, re.M)
            if m:
                go_name[b['fid']] = unescape(m.group(1))
        if cls in ('4', '224'):
            g = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            if g:
                go_tr[g.group(1)] = b['fid']
                tr_go[b['fid']] = g.group(1)
            fa = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            if fa:
                tr_father[b['fid']] = fa.group(1)
            p = re.search(r'^  m_LocalPosition: \{x: ([-0-9.e]+), y: ([-0-9.e]+), '
                          r'z: ([-0-9.e]+)\}', body, re.M)
            if p:
                tr_pos[b['fid']] = tuple(float(p.group(k)) for k in (1, 2, 3))

    instances = []
    for b in blocks:
        if b['cls'] != '1001':
            continue
        mods = {}
        for k, v in MOD_RE.findall(b['body']):
            mods[k] = unescape(v)
        src = SRC_RE.search(b['body'])
        parent = PARENT_RE.search(b['body'])
        stripped_ids = [x['fid'] for x in blocks
                        if x['stripped']
                        and ('m_PrefabInstance: {fileID: %s}' % b['fid']) in x['body']]
        root_tr = next((x['fid'] for x in blocks
                        if x['stripped'] and x['cls'] == '4'
                        and ('m_PrefabInstance: {fileID: %s}' % b['fid']) in x['body']), None)

        pos = None
        if 'm_LocalPosition.x' in mods:
            def f(k):
                try:
                    return float(mods.get(k, 0))
                except ValueError:
                    return 0.0
            pos = (f('m_LocalPosition.x'), f('m_LocalPosition.y'), f('m_LocalPosition.z'))
        instances.append({
            'fid': b['fid'],
            'name': mods.get('m_Name', ''),
            'guid': src.group(1) if src else '',
            'parent_tr': parent.group(1) if parent else None,
            'pos': pos,
            'root_tr': root_tr,
            'stripped': stripped_ids,
            'mods': mods,
        })

    def tr_name(tr_fid):
        seen, cur = 0, tr_fid
        while cur and seen < 32:
            gid = tr_go.get(cur)
            if gid and gid in go_name:
                return go_name[gid]
            cur = tr_father.get(cur)
            seen += 1
        return '?' if tr_fid else '(场景根)'

    for inst in instances:
        inst['parent_name'] = tr_name(inst['parent_tr'])
        if inst['pos'] is None and inst['root_tr'] in tr_pos:
            inst['pos'] = tr_pos[inst['root_tr']]
    return instances, tr_go, go_name

def main():
    argv = sys.argv[1:]
    scene = argv[0]
    parent_filter = grep = None
    detail = '--detail' in argv
    if '--parent' in argv:
        parent_filter = argv[argv.index('--parent') + 1]
    if '--grep' in argv:
        grep = argv[argv.index('--grep') + 1]

    with io.open(scene, encoding='utf-8', errors='replace') as f:
        text = f.read()
    instances, _, _ = parse_scene(text)
    idx = guid_index()

    rows = []
    for inst in instances:
        prefab_path = idx.get(inst['guid'], '')
        short = os.path.basename(prefab_path) or inst['guid'][:8]
        rows.append({
            'parent': inst['parent_name'],
            'name': inst['name'] or ('<%s>' % short),
            'pos': inst['pos'],
            'prefab': short,
            'path': prefab_path,
            'fid': inst['fid'],
            'root_tr': inst['root_tr'],
            'n': len(inst['stripped']),
        })

    if parent_filter:
        rows = [r for r in rows if r['parent'] == parent_filter]
    if grep:
        rows = [r for r in rows
                if grep in r['name'] or grep in r['prefab'] or grep in r['parent']]

    rows.sort(key=lambda r: (r['parent'], r['name']))
    print('场景 %s' % scene)
    print('prefab 实例共 %d 个，显示 %d 个' % (len(instances), len(rows)))
    print()
    print('%-14s %-28s %-22s %-24s %s'
          % ('父节点', '实例名', '局部坐标', '源 prefab', 'instanceID'))
    print('-' * 126)
    for r in rows:
        ptxt = '(%.1f, %.1f, %.1f)' % r['pos'] if r['pos'] else '(继承)'
        print('%-14s %-28s %-22s %-24s &%s'
              % (r['parent'], r['name'], ptxt, r['prefab'], r['fid']))

    if detail:
        print()
        for r in rows:
            print('  %s / %s' % (r['parent'], r['name']))
            print('    instanceID  = %s' % r['fid'])
            print('    rootTr      = %s' % r['root_tr'])
            print('    stripped    = %d 块' % r['n'])
            print('    prefab      = %s' % r['path'])


if __name__ == '__main__':
    main()

