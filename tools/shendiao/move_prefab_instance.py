# -*- coding: utf-8 -*-
"""修改场景里某个 prefab 实例的位置 / 旋转（改的是 PrefabInstance 的 m_Modifications）。

prefab 实例的坐标不在 Transform 块里（那是 stripped 的），而在
PrefabInstance(!u!1001) 的 m_Modifications 中 `m_LocalPosition.x/y/z`。
本工具按「实例名」定位并改写这三个值。

用法:
    python tools/shendiao/move_prefab_instance.py \\
        --scene <scene.unity> --name 老庙祝 --pos -2.5,5.0,13.5 [--rot-y 180] [--apply]
默认 dry-run。
"""
import io
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from list_prefab_instances import split_blocks, parse_scene, MOD_RE  # noqa: E402


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
    name = opt['name']
    pos = [v.strip() for v in opt['pos'].split(',')] if opt.get('pos') else None
    rot_y = opt.get('rot-y')
    apply = opt.get('apply', False)

    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    by_fid = {b['fid']: b for b in blocks}
    instances, _, _ = parse_scene(text)

    hits = [i for i in instances if i['name'] == name]
    if opt.get('parent'):
        hits = [i for i in hits if i['parent_name'] == opt['parent']]
    if not hits:
        raise SystemExit('找不到名为 %s 的 prefab 实例' % name)
    if len(hits) > 1:
        print('!! 有 %d 个同名实例，全部修改' % len(hits))

    edits = []
    for inst in hits:
        b = by_fid[inst['fid']]
        body = b['body']
        old_name = inst['name']
        if pos:
            for axis, val in zip('xyz', pos):
                body, n = re.subn(
                    r'(propertyPath: m_LocalPosition\.%s\n\s+value: )[-0-9.eE+]+' % axis,
                    lambda m, v=val: m.group(1) + v, body, count=1)
                if n == 0:
                    print('  !! %s 没有 m_LocalPosition.%s 覆盖项，无法改' % (old_name, axis))
        if rot_y:
            qy = math.sin(math.radians(float(rot_y)) / 2.0)
            qw = math.cos(math.radians(float(rot_y)) / 2.0)
            body = re.sub(r'(propertyPath: m_LocalRotation\.y\n\s+value: )[-0-9.eE+]+',
                          lambda m: m.group(1) + '%.6f' % qy, body, count=1)
            body = re.sub(r'(propertyPath: m_LocalRotation\.w\n\s+value: )[-0-9.eE+]+',
                          lambda m: m.group(1) + '%.6f' % qw, body, count=1)
            body = re.sub(r'(propertyPath: m_LocalEulerAnglesHint\.y\n\s+value: )[-0-9.eE+]+',
                          lambda m: m.group(1) + '%g' % float(rot_y), body, count=1)
        hdr_len = (b['end'] - b['start']) - len(b['body'])
        edits.append((b['start'] + hdr_len, b['end'], body))
        print('  实例 %s (&%s) 父=%s  pos=%s rotY=%s'
              % (old_name, inst['fid'], inst['parent_name'], pos or '(不变)', rot_y or '(不变)'))

    new_text = text
    for start, end, content in sorted(edits, key=lambda e: -e[0]):
        new_text = new_text[:start] + content + new_text[end:]

    print()
    print('文件 %d -> %d 字节' % (len(text), len(new_text)))
    if apply:
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(new_text)
        print('已写入 %s' % scene)
    else:
        print('（dry-run，未写盘；加 --apply 生效）')


if __name__ == '__main__':
    main()
