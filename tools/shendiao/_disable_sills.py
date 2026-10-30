"""禁用/habilitates 场景里"贴地薄板"型的 NavMeshObstacle（门槛、台阶）。

原理：这些 NavMeshObstacle 的 m_Extents.y 只有 0.04~0.10 米，躺在门口/台阶上。
它们以非 carving 模式（m_Carve: 0）存在，Unity 会把 NavMeshAgent 的目标点
整个推出障碍盒的 XZ 范围 —— 于是一道 4 厘米高的门槛变成一堵看不见的墙。

这类障碍只该"看起来有"，不该挡人，所以直接 m_Enabled: 0。
墙体阻挡靠的是烘焙进 NavMesh 的静态几何，不依赖 NavMeshObstacle。

用法：
    python tools/shendiao/_disable_sills.py <场景...>            # 只看
    python tools/shendiao/_disable_sills.py <场景...> --apply    # 落盘
    python tools/shendiao/_disable_sills.py --all               # MOD 全部场景

判定：m_Extents.y < --max-y（默认 0.35）且 m_Shape == 1（Box）。
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
MAPDIR = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps')


def targets():
    if '--all' in sys.argv:
        return sorted(os.path.join(MAPDIR, f) for f in os.listdir(MAPDIR) if f.endswith('.unity'))
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = []
    for a in args:
        out.append(a if os.path.isabs(a) else os.path.join(ROOT, a))
    return out


def max_y():
    if '--max-y' in sys.argv:
        return float(sys.argv[sys.argv.index('--max-y') + 1])
    return 0.35


def process(fp, apply):
    t = io.open(fp, encoding='utf-8', errors='replace').read()
    hits = []

    def repl(m):
        blk = m.group(0)
        if not blk.startswith('--- !u!208 '):
            return blk
        shape = re.search(r'm_Shape: (\d)', blk)
        ext = re.search(r'm_Extents: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', blk)
        en = re.search(r'm_Enabled: (\d)', blk)
        if not (shape and ext and en):
            return blk
        if shape.group(1) != '1':
            return blk
        if en.group(1) == '0':
            return blk
        if float(ext.group(2)) >= max_y():
            return blk
        hits.append((float(ext.group(1)), float(ext.group(2)), float(ext.group(3))))
        return blk.replace('m_Enabled: 1', 'm_Enabled: 0', 1)

    new = re.sub(r'(?ms)^--- !u!\d+ &-?\d+\n.*?(?=^--- !u!|\Z)', repl, t)
    if hits and apply and new != t:
        io.open(fp, 'w', encoding='utf-8', newline='\n').write(new)
    return hits


def main():
    apply = '--apply' in sys.argv
    total = 0
    for fp in targets():
        if not os.path.exists(fp):
            print('跳过（不存在）: %s' % fp)
            continue
        hits = process(fp, apply)
        if hits:
            total += len(hits)
            print('%s%s：%d 处' % (os.path.basename(fp), ' [已禁用]' if apply else ' [待禁用]', len(hits)))
            for x, y, z in hits:
                print('    extents=(%.2f, %.3f, %.2f)' % (x, y, z))
    print('\n合计 %d 处%s' % (total, '' if apply else '（干跑，加 --apply 落盘）'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
