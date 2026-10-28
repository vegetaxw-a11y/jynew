# -*- coding: utf-8 -*-
"""往 .unity 场景里添加一个 prefab 实例（NPC / 摆件）。

做法：从模板场景里拷一份现成的 PrefabInstance 块（含 stripped 子块），
换掉场景级 fileID、父节点、位置、名字，再挂到目标父 Transform 的 m_Children 上。

用法:
    python tools/shendiao/add_scene_npc.py \
        --scene  jyx2/Assets/Mods/shendiao/Maps/GameMaps/62_pomiao.unity \
        --template-scene jyx2/Assets/Mods/SAMPLE/Maps/GameMaps/05_yilinlou.unity \
        --prefab-guid 26a0a52bdd44cbb459d07b604f9725b1 \
        --parent NPC --name 老庙祝 --pos -2.5,5.5,13.5 --rot-y 180 --apply
默认 dry-run，加 --apply 才写盘。
"""
import io
import math
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append((m.group(1), m.group(2), m.group(3) or '',
                    m.group(0), text[m.end():end]))
    return out


def find_transform_of_go(blocks, go_fid):
    for cls, fid, st, hdr, body in blocks:
        if cls in ('4', '224') and 'm_GameObject: {fileID: %s}' % go_fid in body:
            return fid, body
    return None, None


def parse_args(argv):
    opt = {}
    i = 0
    while i < len(argv):
        if argv[i].startswith('--'):
            k = argv[i][2:]
            if k == 'apply':
                opt[k] = True
                i += 1
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def main():
    opt = parse_args(sys.argv[1:])
    scene = opt['scene']
    tmpl = opt['template-scene']
    guid = opt['prefab-guid']
    parent_name = opt.get('parent', 'NPC')
    name = opt.get('name', 'NPC')
    pos = [float(v) for v in opt.get('pos', '0,0,0').split(',')]
    rot_y = float(opt.get('rot-y', '0'))
    apply = opt.get('apply', False)

    dst_text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    src_text = io.open(tmpl, encoding='utf-8', errors='surrogateescape').read()
    dst_blocks = split_blocks(dst_text)
    src_blocks = split_blocks(src_text)

    inst_fid = None
    for cls, fid, st, hdr, body in src_blocks:
        if cls == '1001' and ('m_SourcePrefab: {fileID: 100100000, guid: %s' % guid) in body:
            inst_fid = fid
            break
    if inst_fid is None:
        raise SystemExit('模板场景里找不到 guid=%s 的 PrefabInstance' % guid)

    picked = [b for b in src_blocks
              if b[1] == inst_fid or ('m_PrefabInstance: {fileID: %s}' % inst_fid) in b[4]]
    print('模板实例 &%s 共 %d 块: %s'
          % (inst_fid, len(picked), ', '.join('%s/%s' % (c, f) for c, f, _, _, _ in picked)))

    parent_tr = None
    for cls, fid, st, hdr, body in dst_blocks:
        if cls == '1' and not st:
            m = re.search(r'^  m_Name: (?:"(.*)"|(.*))$', body, re.M)
            if m and (m.group(1) or m.group(2)) == parent_name:
                parent_tr, _ = find_transform_of_go(dst_blocks, fid)
                break
    if parent_tr is None:
        raise SystemExit('目标场景里找不到父节点: %s' % parent_name)
    print('目标父节点 %s -> Transform %s' % (parent_name, parent_tr))

    used = {int(b[1]) for b in dst_blocks}
    base = max(used) + 1
    remap = {b[1]: str(base + n) for n, b in enumerate(picked)}
    print('fileID 映射: %s' % remap)

    out_chunks = []
    root_tr_new = None
    for cls, fid, st, hdr, body in picked:
        nb = body
        for old, new in remap.items():
            nb = re.sub(r'fileID: %s\b' % old, 'fileID: %s' % new, nb)
        nb = re.sub(r'm_TransformParent: \{fileID: -?\d+\}',
                    'm_TransformParent: {fileID: %s}' % parent_tr, nb, count=1)
        for axis, val in zip('xyz', pos):
            nb = re.sub(r'(propertyPath: m_LocalPosition\.%s\n\s+value: )[-\d.eE+]+' % axis,
                        lambda m: m.group(1) + ('%g' % val), nb)
        nb = re.sub(r'(propertyPath: m_Name\n\s+value: ).*',
                    lambda m: m.group(1) + '"%s"' % name, nb)
        nb = re.sub(r'(propertyPath: m_RootOrder\n\s+value: )\d+',
                    lambda m: m.group(1) + '0', nb)
        if rot_y:
            qy = math.sin(math.radians(rot_y) / 2.0)
            qw = math.cos(math.radians(rot_y) / 2.0)
            nb = re.sub(r'(propertyPath: m_LocalRotation\.y\n\s+value: )[-\d.eE+]+',
                        lambda m: m.group(1) + '%.6f' % qy, nb)
            nb = re.sub(r'(propertyPath: m_LocalRotation\.w\n\s+value: )[-\d.eE+]+',
                        lambda m: m.group(1) + '%.6f' % qw, nb)
            nb = re.sub(r'(propertyPath: m_LocalEulerAnglesHint\.y\n\s+value: )[-\d.eE+]+',
                        lambda m: m.group(1) + '%g' % rot_y, nb)
        out_chunks.append('--- !u!%s &%s%s\n' % (cls, remap[fid], st) + nb)
        if cls == '4':
            root_tr_new = remap[fid]

    if root_tr_new is None:
        raise SystemExit('模板里没有 stripped Transform 块')

    patched = False
    for cls, fid, st, hdr, body in dst_blocks:
        if fid == parent_tr:
            start = dst_text.index(hdr) + len(hdr)
            m = re.search(r'^  m_Children:\n((?:  - \{fileID: -?\d+\}\n)*)', body, re.M)
            if not m:
                raise SystemExit('父节点没有 m_Children 列表')
            body2 = body[:m.end()] + '  - {fileID: %s}\n' % root_tr_new + body[m.end():]
            dst_text = dst_text[:start] + body2 + dst_text[start + len(body):]
            patched = True
            break
    if not patched:
        raise SystemExit('未能 patch 父节点 m_Children')

    dst_text = dst_text.rstrip('\n') + '\n\n' + '\n'.join(out_chunks).strip('\n') + '\n'

    print()
    print('新实例 Name=%s pos=%s rotY=%g parent=%s(root tr %s)'
          % (name, pos, rot_y, parent_name, root_tr_new))
    if apply:
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(dst_text)
        print('已写入 %s' % scene)
    else:
        print('（dry-run，未写盘；加 --apply 生效）')


if __name__ == '__main__':
    main()
