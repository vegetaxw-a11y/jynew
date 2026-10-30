"""给所有 LearnMagic2 补一本对应秘籍，让学会的武功可以继续升级。

原理：JYX2 里武功升级靠"经书"（ItemConfig.ItemType == 2），
用书才走 role.LearnMagic 的升级分支；只调 LearnMagic2 只能拿到 1 级。

映射从 ItemConfig 读：ItemType == 2 且 Skill == <skillId> 的那一行就是它的秘籍。

用法：
    python tools/shendiao/_add_books.py            # 只看
    python tools/shendiao/_add_books.py --apply
"""
import glob
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
LUADIR = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
ITEM = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Configs', 'Lua', 'ItemConfig.lua')

ROW = re.compile(r'^\{(\d+),\[\[(.*?)\]\],\[\[(.*?)\]\],(-?\d+),(-?\d+),(\d+),', re.M)
LEARN = re.compile(r'^(\s*)LearnMagic2\(\s*(\d+)\s*,\s*(\d+)\s*,[^)]*\)\s*;?\s*$', re.M)


def books():
    """skillId -> (itemId, itemName)"""
    t = io.open(ITEM, encoding='utf-8', errors='replace').read()
    out = {}
    for m in ROW.finditer(t):
        iid, name, _desc, skill, _equip, itype = m.groups()
        if itype == '2' and int(skill) >= 0:
            out.setdefault(int(skill), (int(iid), name))
    return out


def main():
    apply = '--apply' in sys.argv
    bmap = books()
    total = 0
    for fp in sorted(glob.glob(os.path.join(LUADIR, '*.lua'))):
        src = io.open(fp, encoding='utf-8').read()
        hits = []
        added = []

        def repl(m):
            indent, role, skill = m.group(1), int(m.group(2)), int(m.group(3))
            if skill not in bmap:
                hits.append((skill, None, None))
                return m.group(0)
            iid, iname = bmap[skill]
            hits.append((skill, iid, iname))
            line = m.group(0).rstrip()
            # 幂等：紧跟着的 3 行里已经有这本书就不再补
            tail = src[m.end():m.end() + 160]
            if re.search(r'AddItem\(\s*%d\s*,' % iid, tail):
                return m.group(0)
            added.append(iid)
            return line + '\n%sAddItem(%d, 1);' % (indent, iid)

        new = LEARN.sub(repl, src)
        if hits:
            print('%s' % os.path.basename(fp))
            for skill, iid, iname in hits:
                if iid is None:
                    print('    skill %d -> 没有对应秘籍（跳过）' % skill)
                else:
                    print('    skill %-4d -> 物品 %-4d %s' % (skill, iid, iname))
            if added and apply and new != src:
                io.open(fp, 'w', encoding='utf-8', newline='\n').write(new)
                total += 1
                print('    已补 %d 本' % len(added))
    print('\n%s %d 个文件' % ('已改写' if apply else '待改写', total))
    return 0


if __name__ == '__main__':
    sys.exit(main())
