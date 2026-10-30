# -*- coding: utf-8 -*-
"""统计 shendiao 剧本 Lua 用到的语法构造 —— 决定 `story_lua.py` 解析器的覆盖面。

    python tools/storyeditor/survey_lua.py

改剧情写法（比如开始用 while / for / 局部函数）前跑一次：
如果某个构造从 0 变成有，说明解析器可能要补。
"""
import io
import os
import re
import sys

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                   'jyx2', 'Assets', 'Mods', 'shendiao')
LUA = os.path.join(MOD, 'Lua')

PATTERNS = {
    'if_then_goto': r'^\s*if\s+.*\bthen\s*goto\s+\w+\s*;?\s*end\s*;?\s*$',
    'if_then_end_multiline': r'^\s*if\s+.*\bthen\s*$',
    'elseif': r'^\s*elseif\b',
    'else': r'^\s*else\s*$',
    'end': r'^\s*end\s*;?\s*$',
    'label': r'^\s*::\w+::',
    'goto': r'^\s*goto\s+\w+',
    'do_return': r'^\s*do\s+return\s+end',
    'return': r'^\s*return\b',
    'while': r'^\s*while\b',
    'for': r'^\s*for\b',
    'function': r'^\s*(local\s+)?function\b',
    'local': r'^\s*local\b',
    'assign': r'^\s*[A-Za-z_][\w.]*\s*=\s*[^=]',
    'yes_no': r'ShowYesOrNoSelectPanel',
    'select_panel': r'ShowSelectPanel\(',
    'message_select': r'ShowMessageSelectPanel',
    'talk_expr': r'Talk\(\s*-?\d+\s*,\s*"[^"]*"\s*,\s*EXPR\.',
    'talk_long': r'Talk\(\s*-?\d+\s*,\s*\[\[',
    'talk_multi_space': r'Talk\(\s*-?\d+\s*,\s*"[^"]*"\s*\)\s*--',
}

stats = {k: set() for k in PATTERNS}
files = sorted(f for f in os.listdir(LUA) if f.endswith('.lua'))
maxdepth = 0
for f in files:
    text = io.open(os.path.join(LUA, f), encoding='utf-8', errors='replace').read()
    depth = 0
    for line in text.split('\n'):
        for k, pat in PATTERNS.items():
            if re.search(pat, line):
                stats[k].add(f)
        stripped = line.strip()
        if re.match(r'^(if|for|while|function)\b', stripped) and not re.search(r'\bthen\s*\S+.*\bend\b', stripped):
            depth += 1
            maxdepth = max(maxdepth, depth)
        if re.match(r'^end\b', stripped):
            depth = max(0, depth - 1)

print('files: %d   max nesting depth: %d' % (len(files), maxdepth))
for k in PATTERNS:
    s = sorted(stats[k])
    print('%-24s %3d  %s' % (k, len(s), ', '.join(s[:8]) + (' ...' if len(s) > 8 else '')))
