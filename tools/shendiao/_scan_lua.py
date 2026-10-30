"""在 MOD 的 Lua 里按正则搜索，结果写 Logs/_lua_grep.txt（UTF-8），再读文件。

用法：
    python tools/shendiao/_scan_lua.py "LearnMagic2"
    python tools/shendiao/_scan_lua.py "AddItem\\(35"
"""
import glob
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
LOG = os.path.join(ROOT, 'Logs', '_lua_grep.txt')


def main():
    if len(sys.argv) < 2:
        print('用法: python tools/shendiao/_scan_lua.py <正则>')
        return 1
    pat = re.compile(sys.argv[1])
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua', '*.lua'))):
        for i, line in enumerate(io.open(f, encoding='utf-8', errors='replace'), 1):
            if pat.search(line):
                out.append('%s:%d: %s' % (os.path.basename(f), i, line.strip()))
    io.open(LOG, 'w', encoding='utf-8').write('\n'.join(out) or '(无匹配)')
    print('命中 %d 条 -> Logs/_lua_grep.txt' % len(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
