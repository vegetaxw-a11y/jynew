# -*- coding: utf-8 -*-
"""体检大地图场景：主角落点、相机跟随、传送点、关键节点缺失情况。

用法：python tools/shendiao/inspect_worldmap.py [场景.unity ...]
"""
import io
import json
import os
import re
import sys

HEADER = re.compile(r'^--- !u!(\d+) &(-?\d+)(.*)$')
TARGET = re.compile(r'^\s*- target: \{fileID: (-?\d+), guid: ([0-9a-fA-F]+), type: (\d+)\}')
PROP = re.compile(r'^\s*propertyPath: (.*)$')
VALUE = re.compile(r'^\s*value: (.*)$')
REF = re.compile(r'\{fileID: (-?\d+)\}')


def load_scene(path):
    """把 .unity 按 --- !u! 文档切开，返回 fileID -> {cls, stripped, lines}。"""
    docs = {}
    cur = None
    with io.open(path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.rstrip('\r\n')
            m = HEADER.match(line)
            if m:
                cur = {'cls': int(m.group(1)), 'stripped': 'stripped' in m.group(3), 'lines': []}
                docs[m.group(2)] = cur
            elif cur is not None:
                cur['lines'].append(line)
    return docs


def field(doc, key):
    pat = re.compile(r'^\s*' + re.escape(key) + r':\s*(.*)$')
    for ln in doc['lines']:
        m = pat.match(ln)
        if m:
            return m.group(1).strip()
    return None


def ref(doc, key):
    v = field(doc, key)
    if not v:
        return None
    m = REF.search(v)
    if not m:
        return None
    return None if m.group(1) == '0' else m.group(1)


def unquote(v):
    """把 YAML 双引号字符串（含 \\uXXXX 转义）还原成明文。"""
    if not v:
        return v
    v = v.strip()
    if v.startswith('"') and v.endswith('"') and len(v) >= 2:
        try:
            return json.loads(v)
        except ValueError:
            return v[1:-1]
    return v


def flatten_refs(doc, key):
    """解析 m_Children 这类逐行 {fileID: x} 的列表。"""
    out = []
    started = False
    for ln in doc['lines']:
        if re.match(r'^\s*' + re.escape(key) + r':', ln):
            started = True
            out += REF.findall(ln.split(':', 1)[1])
            continue
        if started:
            if re.match(r'^\s*- \{fileID:', ln):
                out += REF.findall(ln)
            else:
                break
    return out


def parse_mods(doc):
    """PrefabInstance 的 m_Modifications -> [{fid, guid, prop, value}]。"""
    mods = []
    cur = None
    for ln in doc['lines']:
        m = TARGET.match(ln)
        if m:
            cur = {'fid': m.group(1), 'guid': m.group(2), 'prop': None, 'value': None}
            mods.append(cur)
            continue
        if cur is None:
            continue
        m = PROP.match(ln)
        if m:
            cur['prop'] = m.group(1).strip()
            continue
        m = VALUE.match(ln)
        if m:
            cur['value'] = m.group(1).strip()
    return mods


class Scene(object):
    """索引 GameObject / Transform / PrefabInstance 之间的引用关系。"""

    def __init__(self, path, docs):
        self.path = path
        self.docs = docs
        self.go = {}
        self.tr = {}
        self.inst = {}
        self.stripped_tr_owner = {}
        self._index()

    def _index(self):
        for fid, d in self.docs.items():
            if d['cls'] == 1 and not d['stripped']:
                self.go[fid] = {'name': unquote(field(d, 'm_Name')), 'active': field(d, 'm_IsActive')}
            elif d['cls'] == 4 and not d['stripped']:
                self.tr[fid] = {
                    'go': ref(d, 'm_GameObject'),
                    'father': ref(d, 'm_Father'),
                    'children': flatten_refs(d, 'm_Children'),
                    'pos': field(d, 'm_LocalPosition'),
                    'scale': field(d, 'm_LocalScale'),
                }
            elif d['cls'] == 1001:
                mods = parse_mods(d)
                name = None
                for m in mods:
                    if m['prop'] == 'm_Name':
                        name = unquote(m['value'])
                self.inst[fid] = {
                    'parent': ref(d, 'm_TransformParent'),
                    'name': name,
                    'mods': mods,
                    'source': field(d, 'm_SourcePrefab'),
                }
            elif d['cls'] == 4 and d['stripped']:
                self.stripped_tr_owner[fid] = ref(d, 'm_PrefabInstance')

    def all_nodes(self):
        return list(self.tr) + list(self.stripped_tr_owner) + list(self.inst)

    def tr_name(self, fid):
        if fid is None:
            return '<null>'
        if fid in self.tr:
            return self.go.get(self.tr[fid]['go'] or '', {}).get('name') or '<unnamed>'
        if fid in self.inst:
            return self.inst[fid]['name'] or '<prefab#%s>' % fid
        owner = self.stripped_tr_owner.get(fid)
        if owner and owner in self.inst:
            return self.inst[owner]['name'] or '<prefab#%s>' % owner
        return '<%s>' % fid

    def parent_of(self, fid):
        if fid in self.tr:
            return self.tr[fid]['father']
        if fid in self.inst:
            return self.inst[fid]['parent']
        owner = self.stripped_tr_owner.get(fid)
        if owner and owner in self.inst:
            return self.inst[owner]['parent']
        return None

    def tr_path(self, fid, limit=8):
        parts = []
        seen = set()
        cur = fid
        while cur and cur not in seen and len(parts) < limit:
            seen.add(cur)
            parts.append(self.tr_name(cur))
            cur = self.parent_of(cur)
        return '/'.join(reversed(parts))

    def roots(self):
        out = [f for f, t in self.tr.items() if not t['father']]
        out += [f for f, i in self.inst.items() if not i['parent']]
        return out

    def find_tr_by_name(self, name):
        for fid in self.all_nodes():
            if self.tr_name(fid) == name:
                return fid
        return None

    def children_of(self, fid):
        if fid in self.tr:
            return list(self.tr[fid]['children'])
        return [iid for iid, i in self.inst.items() if i['parent'] == fid]

    def _mod_axes(self, fid, prop):
        d = {'x': None, 'y': None, 'z': None}
        if fid in self.inst:
            for m in self.inst[fid]['mods']:
                for axis in 'xyz':
                    if m['prop'] == '%s.%s' % (prop, axis):
                        d[axis] = m['value']
        return d

    def instance_pos(self, fid):
        return self._mod_axes(fid, 'm_LocalPosition')

    def instance_scale(self, fid):
        return self._mod_axes(fid, 'm_LocalScale')


SCRIPT_GUIDS = {}


def build_script_map(root):
    if SCRIPT_GUIDS:
        return SCRIPT_GUIDS
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith('.cs.meta'):
                try:
                    with io.open(os.path.join(dirpath, fn), 'r', encoding='utf-8', errors='ignore') as f:
                        for _ in range(4):
                            ln = f.readline()
                            if ln.startswith('guid:'):
                                SCRIPT_GUIDS[ln.split(':', 1)[1].strip()] = fn[:-7]
                                break
                except IOError:
                    pass
    return SCRIPT_GUIDS


def scripts_on(sc, go_fid, smap):
    """某个 GameObject 上挂的脚本名。"""
    out = []
    if not go_fid:
        return out
    for d in sc.docs.values():
        if d['cls'] != 114 or ref(d, 'm_GameObject') != go_fid:
            continue
        v = field(d, 'm_Script') or ''
        m = re.search(r'guid: ([0-9a-fA-F]+)', v)
        g = m.group(1) if m else None
        out.append(smap.get(g, 'script:%s' % (g or '?')))
    return out


def report(path, smap):
    docs = load_scene(path)
    sc = Scene(path, docs)
    o = []
    o.append('=' * 68)
    o.append('场景：%s' % path)
    kinds = {}
    for d in docs.values():
        kinds[d['cls']] = kinds.get(d['cls'], 0) + 1
    o.append('  文档数 %d ｜ 类型 %s' % (len(docs), ', '.join('cls%d=%d' % (k, v) for k, v in sorted(kinds.items()))))

    o.append('')
    o.append('-- 根节点')
    for fid in sc.roots():
        o.append('   %s  (%s)' % (sc.tr_name(fid), 'PrefabInstance' if fid in sc.inst else 'GameObject'))

    level = sc.find_tr_by_name('Level')
    o.append('')
    o.append('-- Level 节点：%s' % ('存在 fid=%s' % level if level else '[X] 缺失'))
    if level:
        for c in sc.children_of(level):
            o.append('   %s' % sc.tr_name(c))
            if sc.tr_name(c) in ('Player', 'Triggers', 'Dynamic'):
                for gc in sc.children_of(c):
                    o.append('        * %s' % sc.tr_name(gc))

    o.append('')
    o.append('-- 主角 Player')
    pl = sc.find_tr_by_name('Player')
    if not pl:
        o.append('   [X] 找不到名为 Player 的节点')
    else:
        o.append('   路径：%s' % sc.tr_path(pl))
        inst = pl if pl in sc.inst else sc.stripped_tr_owner.get(pl)
        if inst:
            o.append('   PrefabInstance：%s' % inst)
            o.append('   位置：%s' % (sc.instance_pos(inst),))
            o.append('   缩放：%s' % (sc.instance_scale(inst),))
            o.append('   源 prefab：%s' % (sc.inst[inst]['source'],))
            mods = sc.inst[inst]['mods']
            o.append('   覆写条数：%d' % len(mods))
            for m in mods:
                p = m['prop'] or ''
                if p.split('.')[0] in ('m_LocalPosition', 'm_LocalScale', 'm_LocalRotation', 'm_Name'):
                    o.append('      %-22s = %s' % (p, unquote(m['value'])))
        elif pl in sc.tr:
            o.append('   位置：%s' % (sc.tr[pl]['pos'],))
            o.append('   缩放：%s' % (sc.tr[pl]['scale'],))

    o.append('')
    o.append('-- 相机 Follow')
    for d in docs.values():
        if d['cls'] != 114:
            continue
        f = field(d, 'm_Follow')
        if not f:
            continue
        tr = REF.search(f)
        trid = tr.group(1) if tr else None
        o.append('   m_Follow = %s -> %s' % (f, sc.tr_name(trid)))

    trig = sc.find_tr_by_name('Triggers')
    o.append('')
    o.append('-- 传送点 Level/Triggers：%s' % ('存在' if trig else '[X] 缺失'))
    if trig:
        kids = sc.children_of(trig)
        o.append('   共 %d 个' % len(kids))
        for c in kids:
            gof = sc.tr.get(c, {}).get('go')
            sname = scripts_on(sc, gof, smap) if gof else []
            pos = sc.instance_pos(c) if c in sc.inst else sc.tr.get(c, {}).get('pos')
            o.append('   - %-24s %s  %s' % (sc.tr_name(c), pos, ','.join(sname) or '(无脚本)'))

    o.append('')
    o.append('-- 关键节点')
    for key in ('CameraGroup', 'CM vcam1', 'BattleboxRoot', 'Dynamic', 'LevelMaster', 'NavMeshSurface'):
        o.append('   %-16s %s' % (key, '[OK]' if sc.find_tr_by_name(key) else '[X]'))
    return '\n'.join(o)


def main():
    try:
        # Windows 控制台是 GBK，emoji 无法编码 -> 用 '?' 兜底而不是崩溃
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    assets = os.path.join(root, 'jyx2', 'Assets')
    smap = build_script_map(assets)

    args = sys.argv[1:]
    if not args:
        args = [os.path.join(assets, 'Mods', 'shendiao', 'Maps', 'GameMaps', '1000_daditu.unity')]
    out = [report(p, smap) for p in args]
    sys.stdout.write('\n\n'.join(out))


if __name__ == '__main__':
    main()


