# -*- coding: utf-8 -*-
"""往 .unity 场景里插入任意 prefab 的实例（不依赖"模板场景里已有同款实例"）。

add_scene_npc.py 的做法是从别的场景拷一份现成的 PrefabInstance 块，所以只能摆
「别的场景恰好摆过的」prefab。而 shendiao 需要金轮法王、洪七公、李莫愁、程英……
这些模型在 Assets/BuildSource/ModelCharacters/BattleNpc/ 里都有 prefab，
但没有任何场景摆过 → 拷不到模板。

本工具直接读 prefab 文件，找出根 GameObject / 根 Transform 的 fileID，然后按
Unity 的标准序列化格式手写三块：
    !u!1001  PrefabInstance（m_Modifications 里写 m_Name / 位置 / 朝向）
    !u!4     stripped Transform  （m_CorrespondingSourceObject → prefab 根 Transform）
    !u!1     stripped GameObject （m_CorrespondingSourceObject → prefab 根 GameObject）
最后把 stripped Transform 挂进父节点的 m_Children。

stripped GameObject 的 fileID 就是 GameEvent.m_EventTargets 要引用的值，
所以本工具会把它打印出来，配合 patch_scene_events.py 绑定交互事件。

用法:
    python tools/shendiao/add_prefab.py \
        --scene   jyx2/Assets/Mods/shendiao/Maps/GameMaps/75_taohuadao.unity \
        --prefab  jyx2/Assets/BuildSource/ModelCharacters/BattleNpc/Azi.prefab \
        --parent  NPC --name 郭芙 --pos 36.3,0,-4.2 --rot-y 180 --apply

默认 dry-run。加 --apply 才写盘。
"""
import io
import math
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append((m.group(1), m.group(2), bool(m.group(3)), text[m.end():end]))
    return out


def parse_args(argv):
    opt = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            k = a[2:]
            if k == 'apply':
                opt[k] = True
                i += 1
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def prefab_roots(text):
    """返回 (根 GameObject fileID, 根 Transform fileID)。"""
    trs = []
    for cls, fid, st, body in split_blocks(text):
        if cls == '4' and not st:
            fa = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            if fa and fa.group(1) == '0' and go:
                trs.append((fid, go.group(1)))
    if not trs:
        raise SystemExit('prefab 里找不到根 Transform（m_Father: {fileID: 0}）')
    tr_fid, go_fid = trs[0]
    return go_fid, tr_fid


def find_parent_tr(blocks, want):
    """按节点名找父 Transform。"""
    for cls, fid, st, body in blocks:
        if cls == '1' and not st:
            m = re.search(r'^  m_Name: (.*)$', body, re.M)
            if m and m.group(1).strip('"') == want:
                for c2, f2, s2, b2 in blocks:
                    if c2 in ('4', '224') and not s2 and \
                            'm_GameObject: {fileID: %s}' % fid in b2:
                        return f2, want
    return None, None


def main():
    opt = parse_args(sys.argv[1:])
    if 'scene' not in opt or 'prefab' not in opt:
        sys.stderr.write(__doc__.strip() + '\n')
        raise SystemExit(2)
    scene = opt['scene']
    prefab = opt['prefab']
    if not os.path.isabs(prefab):
        prefab = os.path.join(REPO, prefab)
    name = opt.get('name', os.path.basename(prefab)[:-7])
    pos = [float(v) for v in opt.get('pos', '0,0,0').split(',')]
    rot_y = float(opt.get('rot-y', '0'))
    parent_name = opt.get('parent', 'NPC')
    apply = opt.get('apply', False)

    meta = prefab + '.meta'
    if not os.path.exists(meta):
        raise SystemExit('找不到 %s（没有 .meta 就拿不到 guid）' % meta)
    guid = re.search(r'^guid: ([0-9a-f]{32})',
                     io.open(meta, encoding='utf-8').read(), re.M).group(1)

    pf_text = io.open(prefab, encoding='utf-8', errors='surrogateescape').read()
    root_go, root_tr = prefab_roots(pf_text)

    dst = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(dst)

    parent_tr, pname = find_parent_tr(blocks, parent_name)
    if parent_tr is None:
        names = [re.search(r'^  m_Name: (.*)$', b[3], re.M).group(1)
                 for b in blocks
                 if b[0] == '1' and not b[2]
                 and re.search(r'^  m_Name: (.*)$', b[3], re.M)]
        raise SystemExit('场景里找不到父节点 m_Name=%s\n现有节点: %s'
                         % (parent_name, ', '.join(names)[:400]))

    used = {int(b[1]) for b in blocks}
    # 用固定段位（2.15e9 起）而不是 max+1：场景里存在 64-bit fileID，
    # max+1 会飘到 6e18，Unity 侧有些工具按 float 处理会丢精度。
    base = 2150000000
    while any((base + k) in used for k in (0, 1, 2)):
        base += 3
    inst_fid, tr_fid, go_fid = base, base + 1, base + 2

    qy = math.sin(math.radians(rot_y) / 2.0)
    qw = math.cos(math.radians(rot_y) / 2.0)
    G = guid

    def mod(target, path, value):
        return ('    - target: {fileID: %s, guid: %s, type: 3}\n'
                '      propertyPath: %s\n'
                '      value: %s\n'
                '      objectReference: {fileID: 0}\n' % (target, G, path, value))

    mods = (mod(root_go, 'm_Name', name)
            + mod(root_tr, 'm_RootOrder', '0')
            + mod(root_tr, 'm_LocalPosition.x', '%g' % pos[0])
            + mod(root_tr, 'm_LocalPosition.y', '%g' % pos[1])
            + mod(root_tr, 'm_LocalPosition.z', '%g' % pos[2])
            + mod(root_tr, 'm_LocalRotation.w', '%.6f' % qw)
            + mod(root_tr, 'm_LocalRotation.x', '0')
            + mod(root_tr, 'm_LocalRotation.y', '%.6f' % qy)
            + mod(root_tr, 'm_LocalRotation.z', '0')
            + mod(root_tr, 'm_LocalEulerAnglesHint.x', '0')
            + mod(root_tr, 'm_LocalEulerAnglesHint.y', '%g' % rot_y)
            + mod(root_tr, 'm_LocalEulerAnglesHint.z', '0'))

    chunk = (
        '--- !u!1001 &%d\n'
        'PrefabInstance:\n'
        '  m_ObjectHideFlags: 0\n'
        '  serializedVersion: 2\n'
        '  m_Modification:\n'
        '    m_TransformParent: {fileID: %s}\n'
        '    m_Modifications:\n'
        '%s'
        '    m_RemovedComponents: []\n'
        '  m_SourcePrefab: {fileID: 100100000, guid: %s, type: 3}\n'
        '--- !u!4 &%d stripped\n'
        'Transform:\n'
        '  m_CorrespondingSourceObject: {fileID: %s, guid: %s, type: 3}\n'
        '  m_PrefabInstance: {fileID: %d}\n'
        '  m_PrefabAsset: {fileID: 0}\n'
        '--- !u!1 &%d stripped\n'
        'GameObject:\n'
        '  m_CorrespondingSourceObject: {fileID: %s, guid: %s, type: 3}\n'
        '  m_PrefabInstance: {fileID: %d}\n'
        '  m_PrefabAsset: {fileID: 0}\n'
        % (inst_fid, parent_tr, mods, G, tr_fid, root_tr, G, inst_fid,
           go_fid, root_go, G, inst_fid))

    patched = False
    for cls, fid, st, body in blocks:
        if fid != parent_tr:
            continue
        head_end = dst.index('--- !u!%s &%s' % (cls, fid))
        head_end = dst.index(body, head_end)
        m = re.search(r'^  m_Children:( \[\])?\n((?:  - \{fileID: -?\d+\}\n)*)', body, re.M)
        if not m:
            raise SystemExit('父节点没有 m_Children 字段')
        if m.group(1):
            new = '  m_Children:\n  - {fileID: %d}\n' % tr_fid
        else:
            new = body[m.start():m.end()] + '  - {fileID: %d}\n' % tr_fid
        body2 = body[:m.start()] + new + body[m.end():]
        dst = dst[:head_end] + body2 + dst[head_end + len(body):]
        patched = True
        break
    if not patched:
        raise SystemExit('未能 patch 父节点 m_Children')

    dst = dst.rstrip('\n') + '\n\n' + chunk

    print('prefab   %s' % os.path.relpath(prefab, REPO))
    print('guid     %s   根GO=%s  根Tr=%s' % (guid, root_go, root_tr))
    print('父节点   %s (Transform %s)' % (pname, parent_tr))
    print('新实例   PrefabInstance &%d   strippedTr &%d   strippedGO &%d'
          % (inst_fid, tr_fid, go_fid))
    print('--set-event 目标请用 GameObject &%d' % go_fid)
    if apply:
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape',
                newline='').write(dst)
        print('已写入 %s' % scene)
    else:
        print('（dry-run，未写盘；加 --apply 生效）')


if __name__ == '__main__':
    main()
