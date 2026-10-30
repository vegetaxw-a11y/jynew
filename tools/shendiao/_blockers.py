"""dump 场景里的所有阻挡物（NavMeshObstacle / Collider）与传送器，带世界坐标。

用法：
    python tools/shendiao/_blockers.py <场景相对路径> [--teleport]

输出 Logs/_blockers.txt（UTF-8），字段：
    类型 物体名 世界坐标 尺寸 enabled carve/islTrigger

世界坐标只累加平移（忽略旋转/缩放），够用来判断"哪个在门口"。
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
LOG = os.path.join(ROOT, 'Logs', '_blockers.txt')

# Unity 内置组件的 classID -> 名字
KIND = {
    '208': 'NavMeshObstacle',
    '65': 'BoxCollider',
    '64': 'MeshCollider',
    '135': 'SphereCollider',
    '136': 'CapsuleCollider',
    '143': 'CharacterController',
}


def vec(block, key):
    m = re.search(r'%s: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}' % key, block)
    return tuple(float(g) for g in m.groups()) if m else None


def load(fp):
    t = io.open(fp, encoding='utf-8', errors='replace').read()
    return re.split(r'^--- ', t, flags=re.M)


def index(blocks):
    goname, tr = {}, {}
    for b in blocks:
        m = re.match(r'!u!1 &(-?\d+)', b)
        if m:
            nm = re.search(r'^  m_Name: (.*)$', b, re.M)
            goname[m.group(1)] = (nm.group(1) if nm else '?').strip('"')
        m = re.match(r'!u!4 &(-?\d+)', b)
        if not m:
            continue
        go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
        fa = re.search(r'm_Father: \{fileID: (-?\d+)\}', b)
        pos = vec(b, 'm_LocalPosition') or (0.0, 0.0, 0.0)
        tr[m.group(1)] = (go.group(1) if go else '0', fa.group(1) if fa else '0', pos)
    return goname, tr


def world(go, tr):
    """沿 father 链累加平移。"""
    tid = next((k for k, v in tr.items() if v[0] == go), None)
    p = [0.0, 0.0, 0.0]
    hop = 0
    while tid and hop < 16:
        _g, fa, pos = tr[tid]
        p = [p[0] + pos[0], p[1] + pos[1], p[2] + pos[2]]
        if fa == '0':
            break
        tid = fa
        hop += 1
    return p


def main():
    rel = sys.argv[1]
    fp = os.path.join(ROOT, rel)
    if not os.path.exists(fp):
        print('文件不存在: %s' % fp)
        return 1
    blocks = load(fp)
    goname, tr = index(blocks)
    out = ['=== %s ===' % os.path.basename(fp), '']

    out.append('--- 阻挡物 ---')
    rows = []
    for b in blocks:
        m = re.match(r'!u!(\d+) &(-?\d+)', b)
        if not m or m.group(1) not in KIND:
            continue
        kind = KIND[m.group(1)]
        go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
        gid = go.group(1) if go else '0'
        name = goname.get(gid, '?')
        en = re.search(r'm_Enabled: (\d)', b)
        sz = vec(b, 'm_Extents') or vec(b, 'm_Size')
        ctr = vec(b, 'm_Center') or (0.0, 0.0, 0.0)
        carve = re.search(r'm_Carve: (\d)', b)
        trig = re.search(r'm_IsTrigger: (\d)', b)
        wp = world(gid, tr)
        extra = ''
        if kind == 'NavMeshObstacle':
            shape = re.search(r'm_Shape: (\d)', b)
            extra = 'shape=%s carve=%s' % (shape.group(1) if shape else '?',
                                           carve.group(1) if carve else '?')
        elif trig:
            extra = 'isTrigger=%s' % trig.group(1)
        rows.append((kind, name, wp, sz, en.group(1) if en else '?', extra, ctr))

    for kind, name, wp, sz, en, extra, ctr in rows:
        szs = '(%.2f,%.2f,%.2f)' % sz if sz else '-'
        out.append('%-16s %-24s pos=(%8.2f,%7.2f,%8.2f) size=%s en=%s %s ctr=(%.2f,%.2f,%.2f)' % (
            kind, name[:24], wp[0], wp[1], wp[2], szs, en, extra, ctr[0], ctr[1], ctr[2]))

    if '--teleport' in sys.argv:
        out.append('')
        out.append('--- MapTeleportor / 触发器 ---')
        for b in blocks:
            if 'MapTeleportor' not in b and 'm_EnterEventId' not in b:
                continue
            go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
            gid = go.group(1) if go else '0'
            wp = world(gid, tr)
            fields = {}
            for k in ('TransportTriggerName', 'm_EnterEventId', 'm_InteractiveEventId',
                      'Target', 'NeedKey', 'm_ShowTarget', 'ShowTarget'):
                mm = re.search(r'%s: (.*)$' % k, b, re.M)
                if mm:
                    fields[k] = mm.group(1).strip()
            out.append('%-24s pos=(%.2f,%.2f,%.2f) %s' % (
                goname.get(gid, '?')[:24], wp[0], wp[1], wp[2], fields))

    io.open(LOG, 'w', encoding='utf-8').write('\n'.join(out))
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
