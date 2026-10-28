# -*- coding: utf-8 -*-
"""改场景里 prefab 实例的显示名 / 位置 / 朝yaw（都写在 m_Modifications 覆盖里）。

为什么需要：
- add_scene_npc.py / add_prefab.py 从模板拷实例时，名字会沿用模板（QZhenDiZi、
  qiuchuji…）。名字不影响交互（m_EventTargets 指向 stripped GameObject），
  但 audit_scene_npcs.py 的「剧情点名的人物在不在场上」靠名字匹配，会误报；
  人也看不出这是谁。
- 交互判定在 Jyx2Player.CanSee()：玩家 NavMeshAgent 要站进触发器 BoxCollider，
  所以 NPC 必须摆到触发器附近（一般 ≤2m），摆错了就得挪。

用法:
    python tools/shendiao/edit_instance.py --scene <scene.unity> --list
    python tools/shendiao/edit_instance.py --scene <scene.unity> \
        --instance 2150000002 --name 鹿清笃 --pos -13.6,0,-12.6 --rot-y 0 --apply
默认 dry-run。--pos 是**局部坐标**（父节点一般就在原点，等于世界坐标）。
"""
import io
import math
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    return [(m.group(1), m.group(2), bool(m.group(3)), m.start(), m.end(),
             ms[i + 1].start() if i + 1 < len(ms) else len(text))
            for i, m in enumerate(ms)]


def parse_args(argv):
    opt = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            k = a[2:]
            if k in ('apply', 'list'):
                opt[k] = True
                i += 1
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def set_mod(body, path, value, guid):
    """在 m_Modifications 里设置（或追加）一条 propertyPath 覆盖。"""
    pat = re.compile(r'(      propertyPath: %s\n      value: )[^\n]*' % re.escape(path))
    if pat.search(body):
        return pat.sub(lambda m: m.group(1) + value, body, count=1)
    tm = re.search(r'    - target: \{fileID: (-?\d+), guid: %s, type: 3\}\n'
                   r'      propertyPath: m_LocalPosition\.x\n' % guid, body)
    if not tm:
        raise SystemExit('实例里找不到 m_LocalPosition.x 覆盖，无法定位根节点 fileID')
    head = ('    - target: {fileID: %s, guid: %s, type: 3}\n'
            '      propertyPath: %s\n'
            '      value: %s\n'
            '      objectReference: {fileID: 0}\n' % (tm.group(1), guid, path, value))
    return body.replace('    m_RemovedComponents:',
                        head + '    m_RemovedComponents:', 1)


def main():
    opt = parse_args(sys.argv[1:])
    if 'scene' not in opt:
        sys.stderr.write(__doc__.strip() + '\n')
        raise SystemExit(2)
    if not opt.get('list') and 'instance' not in opt:
        sys.stderr.write('要么 --list，要么给 --instance <PrefabInstance fileID>\n\n')
        sys.stderr.write(__doc__.strip() + '\n')
        raise SystemExit(2)
    scene = opt['scene']
    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)

    if opt.get('list'):
        print('%-14s %-12s %-28s %s' % ('instanceID', '名字', '局部坐标', '位置覆盖'))
        for cls, fid, st, s, h, e in blocks:
            if cls != '1001':
                continue
            body = text[h:e]
            nm = re.search(r'propertyPath: m_Name\n      value: (.*)', body)
            px = re.search(r'propertyPath: m_LocalPosition\.x\n      value: (.*)', body)
            py = re.search(r'propertyPath: m_LocalPosition\.y\n      value: (.*)', body)
            pz = re.search(r'propertyPath: m_LocalPosition\.z\n      value: (.*)', body)
            pos = '(%s, %s, %s)' % (px.group(1) if px else '?',
                                    py.group(1) if py else '?',
                                    pz.group(1) if pz else '?')
            print('%-14s %-12s %-28s %s'
                  % (fid, (nm.group(1).strip() if nm else '<无>'), pos,
                     'yes' if px else 'no'))
        return

    fid = opt['instance']
    hit = [b for b in blocks if b[0] == '1001' and b[1] == fid]
    if not hit:
        raise SystemExit('找不到 PrefabInstance &%s（用 --list 看现有实例）' % fid)
    cls, bfid, st, s, h, e = hit[0]
    body = text[h:e]
    gm = re.search(r'm_SourcePrefab: \{fileID: 100100000, guid: ([0-9a-f]{32})', body)
    guid = gm.group(1)

    print('%s' % scene)
    print('实例 &%s  guid %s' % (fid, guid))

    if opt.get('name'):
        old = re.search(r'propertyPath: m_Name\n      value: (.*)', body)
        body = set_mod(body, 'm_Name', opt['name'], guid)
        print('  名字  %s -> %s' % (old.group(1).strip() if old else '<无>', opt['name']))

    if opt.get('pos'):
        px, py, pz = [float(v) for v in opt['pos'].split(',')]
        body = set_mod(body, 'm_LocalPosition.x', '%g' % px, guid)
        body = set_mod(body, 'm_LocalPosition.y', '%g' % py, guid)
        body = set_mod(body, 'm_LocalPosition.z', '%g' % pz, guid)
        print('  位置  -> (%.2f, %.2f, %.2f)' % (px, py, pz))

    if opt.get('rot-y'):
        deg = float(opt['rot-y'])
        qy = math.sin(math.radians(deg) / 2.0)
        qw = math.cos(math.radians(deg) / 2.0)
        body = set_mod(body, 'm_LocalRotation.w', '%.6f' % qw, guid)
        body = set_mod(body, 'm_LocalRotation.y', '%.6f' % qy, guid)
        body = set_mod(body, 'm_LocalEulerAnglesHint.y', '%g' % deg, guid)
        print('  朝向  -> yaw %g' % deg)

    if opt.get('apply'):
        text = text[:h] + body + text[e:]
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape',
                newline='').write(text)
        print('已写入')
    else:
        print('（dry-run，加 --apply 生效）')


if __name__ == '__main__':
    main()
