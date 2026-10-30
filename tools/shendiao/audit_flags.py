# -*- coding: utf-8 -*-
"""审计 MOD 剧情脚本的 flag 图，找「静态检查发现不了」的断链。

三类问题（按严重度排序）：

1. 只读不写   —— 某个分支守卫读 XXX，但全 MOD 没有任何地方写它。
                  结果：那段剧情**永远不会触发**（如果是门禁，就是永久卡关）。
2. 只写不读   —— 设了 XXX 却没人读。通常是改名/删剧情后留下的死 flag，
                  也可能是"埋了伏笔没回收"。
3. 同名不同义 —— 同一个 flag 在多个脚本里被写不同的值（0/1/2），
                  容易把"进度标记"和"计数器"混用。

用法:
    python tools/shendiao/audit_flags.py
产物:
    Logs/_flags.txt
"""
import io
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
LUA_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
OUT = os.path.join(REPO, 'Logs', '_flags.txt')

# SetFlagInt / GetFlagInt / SetFlagString / GetFlagString / SetFlagBool / GetFlagBool
SET_RE = re.compile(r'SetFlag(?:Int|String|Bool)\s*\(\s*["\']([^"\']+)["\']\s*(?:,\s*([^)]*))?\)')
GET_RE = re.compile(r'GetFlag(?:Int|String|Bool)\s*\(\s*["\']([^"\']+)["\']')
# scene_api.SetInt / GetInt 之类
SET2_RE = re.compile(r'(?:scene_api|Scene)\s*[.:]\s*Set(?:Int|String|Bool)\s*\(\s*["\']([^"\']+)["\']\s*(?:,\s*([^)]*))?\)')
GET2_RE = re.compile(r'(?:scene_api|Scene)\s*[.:]\s*Get(?:Int|String|Bool)\s*\(\s*["\']([^"\']+)["\']')


def rel(p):
    return os.path.relpath(p, REPO).replace('\\', '/')


def main():
    sets = defaultdict(set)      # flag -> {(file, value)}
    gets = defaultdict(set)      # flag -> {file}
    order = []                   # 保持首次出现顺序
    files = 0

    for name in sorted(os.listdir(LUA_DIR)):
        if not name.endswith('.lua'):
            continue
        p = os.path.join(LUA_DIR, name)
        try:
            text = io.open(p, encoding='utf-8', errors='replace').read()
        except (IOError, OSError):
            continue
        files += 1
        # 去掉行注释，避免把注释里的示例当成真代码
        lines = []
        for line in text.split('\n'):
            idx = line.find('--')
            lines.append(line[:idx] if idx >= 0 else line)
        code = '\n'.join(lines)

        for m in list(SET_RE.finditer(code)) + list(SET2_RE.finditer(code)):
            flag = m.group(1)
            val = (m.group(2) or '').strip() or '?'
            sets[flag].add((name, val))
            if flag not in order:
                order.append(flag)
        for m in list(GET_RE.finditer(code)) + list(GET2_RE.finditer(code)):
            flag = m.group(1)
            gets[flag].add(name)
            if flag not in order:
                order.append(flag)

    only_read = [f for f in order if f in gets and f not in sets]
    only_write = [f for f in order if f in sets and f not in gets]

    out = []
    out.append('脚本 %d 个 / 出现 flag %d 个' % (files, len(order)))
    out.append('  只读不写（剧情永不触发）: %d' % len(only_read))
    out.append('  只写不读（死 flag / 伏笔未回收）: %d' % len(only_write))
    out.append('')

    out.append('== 一、只读不写（最严重：这些分支永远是假的）==')
    for f in sorted(only_read):
        out.append('  %-24s  读于: %s' % (f, ', '.join(sorted(gets[f]))))
    if not only_read:
        out.append('  （无）')
    out.append('')

    out.append('== 二、只写不读（设了没人用）==')
    for f in sorted(only_write):
        vals = sorted({v for (_n, v) in sets[f]})
        out.append('  %-24s  写于: %s   值=%s' % (
            f, ', '.join(sorted({n for (n, _v) in sets[f]})), ','.join(vals)))
    if not only_write:
        out.append('  （无）')
    out.append('')

    out.append('== 三、同名多处写入且值不一致 ==')
    multi = 0
    for f in order:
        if f not in sets:
            continue
        vals = {v for (_n, v) in sets[f]}
        if len(vals) > 1:
            multi += 1
            detail = ', '.join('%s=%s' % (n, v) for (n, v) in sorted(sets[f]))
            out.append('  %-24s  %s' % (f, detail))
    if multi == 0:
        out.append('  （无）')
    out.append('')

    out.append('== 四、全量 flag 清单（按首次出现排序）==')
    for f in order:
        w = ','.join(sorted({n for (n, _v) in sets.get(f, set())})) or '-'
        r = ','.join(sorted(gets.get(f, set()))) or '-'
        out.append('  %-24s 写[%s] 读[%s]' % (f, w, r))

    with io.open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('written %s (%d flags, %d read-only, %d write-only)'
          % (OUT, len(order), len(only_read), len(only_write)))
    return 1 if only_read else 0


if __name__ == '__main__':
    sys.exit(main())
