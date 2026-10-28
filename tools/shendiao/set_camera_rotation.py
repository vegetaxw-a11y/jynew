# -*- coding: utf-8 -*-
"""精确设置/复制某个 GameObject 的局部旋转（四元数 + 欧拉角 hint）。

用法：
    # 从 JYX2 原版场景把 CM vcam1 的旋转原样复制回来（推荐，绝对不失真）
    python tools/shendiao/set_camera_rotation.py <目标.unity> --name "CM vcam1" --copy-from <参考.unity>

    # 直接指定欧拉角（Unity 为 ZXY 顺序）
    python tools/shendiao/set_camera_rotation.py <目标.unity> --name "CM vcam1" --euler 27,180,0

默认只打印将要改的内容；加 --apply 才真正写盘。
"""
import math
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)
ROT_RE = re.compile(r'^  m_LocalRotation: \{[^}]*\}$', re.M)
HINT_RE = re.compile(r'^  m_LocalEulerAnglesHint: \{x: [^,]+, y: [^,]+, z: [^\}]+\}$', re.M)


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def iter_blocks(text):
    blocks = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(blocks):
        if m.group(3):
            continue
        start = m.end()
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        yield i, m.group(1), m.group(2), start, end


def read_rotation(text, name):
    """按 GameObject 名字读它的 Transform 旋转行。"""
    go_ids = set()
    for _, cls, fid, s, e in iter_blocks(text):
        if cls != '1':
            continue
        nm = re.search(r'^  m_Name: (.*)$', text[s:e], re.M)
        if nm and unquote(nm.group(1)) == name:
            go_ids.add(fid)
    if not go_ids:
        raise SystemExit('找不到 GameObject: %s' % name)

    for _, cls, fid, s, e in iter_blocks(text):
        if cls not in ('4', '224'):
            continue
        body = text[s:e]
        go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
        if not go or go.group(1) not in go_ids:
            continue
        rot = ROT_RE.search(body)
        hint = HINT_RE.search(body)
        if rot:
            return s + rot.start(), s + rot.end(), rot.group(0), (hint.group(0) if hint else None), s + (hint.start() if hint else -1)
    raise SystemExit('找不到 %s 的 Transform' % name)


def quat_line(q):
    return '  m_LocalRotation: {x: %.7g, y: %.7g, z: %.7g, w: %.7g}' % q


def hint_line(h):
    return '  m_LocalEulerAnglesHint: {x: %g, y: %g, z: %g}' % h


def euler_to_quat(ex, ey, ez):
    """Unity 顺序 ZXY：q = Ry * Rx * Rz。"""
    hx, hy, hz = (math.radians(v) / 2.0 for v in (ex, ey, ez))
    cx, sx = math.cos(hx), math.sin(hx)
    cy, sy = math.cos(hy), math.sin(hy)
    cz, sz = math.cos(hz), math.sin(hz)
    # Rz
    qz = (0.0, 0.0, sz, cz)   # x,y,z,w
    qx = (sx, 0.0, 0.0, cx)
    qy = (0.0, sy, 0.0, cy)

    def mul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return (aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw,
                aw * bw - ax * bx - ay * by - az * bz)

    return mul(mul(qy, qx), qz)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    target = sys.argv[1]

    def opt(flag):
        return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None

    name = opt('--name') or 'CM vcam1'
    src = opt('--copy-from')
    euler = opt('--euler')
    apply = '--apply' in sys.argv

    text = open(target, encoding='utf-8').read()
    rs, re_, old_rot, old_hint, hint_pos = read_rotation(text, name)

    if src:
        s_text = open(src, encoding='utf-8').read()
        _, _, new_rot, new_hint, _ = read_rotation(s_text, name)
        if not new_hint:
            new_hint = old_hint
    elif euler:
        vals = [float(v) for v in euler.split(',')]
        q = euler_to_quat(*vals)
        new_rot = quat_line(q)
        new_hint = hint_line(vals)
    else:
        raise SystemExit('需要 --copy-from 或 --euler')

    print('目标 : %s' % target)
    print('对象 : %s' % name)
    print('原值 : %s' % old_rot.strip())
    print('       %s' % (old_hint.strip() if old_hint else '(无 hint)'))
    print('新值 : %s' % new_rot.strip())
    print('       %s' % new_hint.strip())

    if not apply:
        print('（dry-run，加 --apply 才写盘）')
        return 0

    out = text[:rs] + new_rot + text[re_:]
    if hint_pos >= 0 and new_hint:
        # 重新定位（长度可能变了）
        out2 = out
        rs2, re2, _, old_hint2, hp2 = read_rotation(out2, name)
        if hp2 >= 0:
            out = out2[:hp2] + new_hint + out2[hp2 + len(old_hint2):]
    open(target, 'w', encoding='utf-8', newline='').write(out)
    print('[ok] 已写盘')
    return 0


if __name__ == '__main__':
    sys.exit(main())
