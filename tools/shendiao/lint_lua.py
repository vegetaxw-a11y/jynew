# -*- coding: utf-8 -*-
"""轻量 Lua 语法体检：块关键字配平 + 字符串/注释状态 + 常见笔误。

工程里没有 lua/luac 可执行文件，`jyx2mod.py check` 也只查 Configs/Lua 的 7 个
配置文件（它们是生成物），**剧情脚本 Lua/*.lua 完全没人校验**。手写剧情时少一个
`end`、中文引号打成半角，Unity 那边只会在运行时静默报 nil，很难定位。

本工具不做完整语法分析，只做能覆盖 95% 手误的检查：
  1. 块关键字配平（if/for/while/function/do … end，含 repeat-until）
  2. 字符串是否闭合（"..." 和 [[...]]），注释 -- 与 --[[ ]]
  3. 括号是否配平
  4. 中文全角括号/引号混入代码
  5. Talk 的头像 id 是否在人物表里、TryBattle 的战斗 id 是否在战斗表里

用法:
    python tools/shendiao/lint_lua.py                 # 检查全部 Lua/*.lua
    python tools/shendiao/lint_lua.py 902.lua 442.lua # 只查指定文件
    python tools/shendiao/lint_lua.py --battle        # 额外核对 TryBattle 的战斗 Id
"""
import glob
import io
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LUA_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
CFG = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Configs', 'Lua')
FULLWIDTH = '（）：，；“”‘’！？'
KW_RE = re.compile(r'\b(if|elseif|else|then|for|while|function|do|end|'
                   r'repeat|until)\b')



def strip_code(text):
    """去掉字符串和注释，返回 (纯代码, 问题列表)。"""
    out, probs = [], []
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == '\n':
            line += 1
            out.append(c)
            i += 1
            continue
        if text.startswith('--[[', i):
            j = text.find(']]', i + 4)
            if j < 0:
                probs.append((line, '长注释 --[[ 未闭合'))
                break
            nl = text.count('\n', i, j)
            line += nl
            out.append('\n' * nl)
            i = j + 2
            continue
        if text.startswith('--', i):
            j = text.find('\n', i)
            i = n if j < 0 else j
            continue
        if c in '"\'':
            j = i + 1
            while j < n:
                if text[j] == '\\':
                    j += 2
                    continue
                if text[j] == c or text[j] == '\n':
                    break
                j += 1
            if j >= n or text[j] != c:
                probs.append((line, '字符串 %s 未闭合' % c))
                i = j
                continue
            line += text.count('\n', i, j + 1)
            out.append('""')
            i = j + 1
            continue
        if text.startswith('[[', i):
            j = text.find(']]', i + 2)
            if j < 0:
                probs.append((line, '长字符串 [[ 未闭合'))
                break
            line += text.count('\n', i, j + 1)
            out.append('""')
            i = j + 2
            continue
        out.append(c)
        i += 1
    return ''.join(out), probs


def check_balance(code, probs):
    stack = []
    for lineno, raw in enumerate(code.split('\n'), 1):
        suppress_do = False          # for/while 头部自带的 do 不另开一层块
        for m in KW_RE.finditer(raw):
            kw = m.group(1)
            if kw in ('for', 'while'):
                stack.append((kw, lineno))
                suppress_do = True
            elif kw == 'do':
                if suppress_do:
                    suppress_do = False
                else:
                    stack.append((kw, lineno))
            elif kw in ('if', 'function', 'repeat'):
                stack.append((kw, lineno))
            elif kw == 'end':
                if not stack:
                    probs.append((lineno, '多出一个 end'))
                else:
                    stack.pop()
            elif kw == 'until':
                if stack and stack[-1][0] == 'repeat':
                    stack.pop()
    for kw, lineno in stack:
        probs.append((lineno, '%s 没有配对的 end/until' % kw))
    depth = code.count('(') - code.count(')')
    if depth:
        probs.append((len(code.split('\n')), '括号不配平（差 %d）' % depth))


def check_fullwidth(code, probs):
    for lineno, raw in enumerate(code.split('\n'), 1):
        for ch in FULLWIDTH:
            if ch in raw:
                probs.append((lineno, '代码里出现全角字符「%s」' % ch))
                break


def cfg_ids(fname, pat=r'^\{(\d+),'):
    p = os.path.join(CFG, fname)
    if not os.path.exists(p):
        return set()
    txt = io.open(p, encoding='utf-8', errors='replace').read()
    return {int(v) for v in re.findall(pat, txt, re.M)}


EXPR_BASE = 9000000        # 对话表情的虚拟头像 id 基址，见 Lua/expr.lua
EXPR_STEP = 10


def real_char_id(cid):
    """把"表情虚拟 id"（9000000 + 角色id*10 + 槽位）还原成真实角色 id。"""
    if EXPR_BASE < cid < EXPR_BASE + 1000 * EXPR_STEP:
        return (cid - EXPR_BASE) // EXPR_STEP
    return cid


def lint(path, ids=None, bids=None):
    text = io.open(path, encoding='utf-8', errors='surrogateescape').read()
    code, probs = strip_code(text)
    check_balance(code, probs)
    check_fullwidth(code, probs)
    for lineno, raw in enumerate(text.split('\n'), 1):
        if ids is not None:
            for m in re.finditer(r'\bTalk\(\s*(-?\d+)', raw):
                cid = int(m.group(1))
                real = real_char_id(cid)
                if real > 0 and real not in ids:
                    probs.append((lineno, 'Talk 的人物 Id %d 不在人物表里' % cid))
        if bids is not None:
            for m in re.finditer(r'\bTryBattle\(\s*(\d+)\s*\)', raw):
                bid = int(m.group(1))
                if bid not in bids:
                    probs.append((lineno, 'TryBattle 的战斗 Id %d 不在战斗表里' % bid))
    return probs


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    ids = cfg_ids('CharacterConfig.lua')
    bids = cfg_ids('BattleConfig.lua') if '--battle' in sys.argv else None

    files = ([os.path.join(LUA_DIR, a) for a in argv] if argv
             else sorted(glob.glob(os.path.join(LUA_DIR, '*.lua'))))

    total = 0
    bad = 0
    for f in files:
        if not os.path.exists(f):
            print('!! 找不到 %s' % f)
            total += 1
            continue
        probs = lint(f, ids, bids)
        if probs:
            bad += 1
            total += len(probs)
            print('%-12s %d 个问题' % (os.path.basename(f), len(probs)))
            for lineno, msg in probs:
                print('    line %-4d %s' % (lineno, msg))
    print()
    print('检查 %d 个脚本，有问题 %d 个，问题共 %d 条' % (len(files), bad, total))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
