# -*- coding: utf-8 -*-
"""给剧本里的 Talk(id, "台词") 自动补第三个参数 —— 表情。

背景（见 docs/shendiao-context.md 第十一节「对话表情系统」）：
  * 对话头像文件是 Assets/BuildSource/head/<id>.png，一个角色只有一张脸；
  * Lua/expr.lua 把 Talk 包了一层：第三个参数是表情时改传"表情虚拟 id"，
    同一角色就能按情绪换头像；
  * 1123 句台词逐句手标不现实，所以这里按台词里的语气词/标点做一次粗分类：
    只标"认得准"的，没把握的一律不动（照旧用默认头像）。

判定顺序（先命中先用）：悲 -> 怒 -> 笑 -> 惊 -> 沉思

用法:
  python tools/shendiao/tag_expr.py --stats              # 只看统计，不写盘
  python tools/shendiao/tag_expr.py --apply              # 写回剧本
  python tools/shendiao/tag_expr.py --apply --only 210,1001
"""
import io
import os
import re
import sys
import collections

ROOT = r'c:\Games\jynew'
MOD_LUA = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
REPORT = os.path.join(ROOT, 'Logs', '_tag_expr.txt')

# 表情名 -> 九宫格槽位号（与 gen_sheets.SLOTS / Lua 的 EXPR 表必须一致）
SLOTS = collections.OrderedDict([
    ('angry', 2), ('smile', 3), ('think', 4), ('shock', 7), ('sad', 8),
])

# 语气词表：只放"出现即基本能确定情绪"的词，宁缺毋滥
RULES = [
    ('sad', ('泪', '哭', '呜咽', '悲', '诀别', '永别', '死别', '孤零零', '可怜',
             '心如死灰', '对不起', '叹息', '惭愧', '命苦', '罢了')),
    ('angry', ('怒', '喝道', '厉声', '住口', '放肆', '可恶', '岂有此理', '走着瞧',
               '别挡道', '滚', '混蛋', '叛徒', '小贼', '凭什么', '找死',
               '不自量力', '狂妄', '咬牙', '呸')),
    ('smile', ('笑', '哈哈', '嘻嘻', '莞尔', '有趣', '好玩', '妙极')),
    ('shock', ('大惊', '惊', '骇', '愕', '怔', '一愣', '不可能', '竟然',
               '怎么可能', '怎么会')),
    ('think', ('沉吟', '沉默', '心想', '难道', '或许', '想来', '究竟', '到底')),
]

# 全角括号包起来的"内心独白/场景旁观"（本剧本的主角视角写法）要不要给"沉思"？
# 这类台词占全部 1123 句的四成多，全给沉思会显得重复；想要更保守就置 False 再跑一遍。
THINK_FOR_PAREN = True

# Talk(id, "字面量")                     —— 还没标表情
CALL2 = re.compile(r'\bTalk\(\s*(\d+)\s*,\s*("(?:[^"\\\n]|\\.)*")\s*\)')
# Talk(id, "字面量", EXPR.xxx)           —— 已标表情（幂等：不再重复处理）
CALL3 = re.compile(r'\bTalk\(\s*(\d+)\s*,\s*("(?:[^"\\\n]|\\.)*")\s*,\s*EXPR\.([A-Za-z]+)\s*\)')
COLOR = re.compile(r'</?color[^>]*>')
_ESC = {'n': '\n', 't': '\t', '"': '"', '\\': '\\', "'": "'"}


def lua_unquote(lit):
    """把 Lua 双引号字面量还原成普通字符串（只处理脚本里真会出现的转义）。"""
    body = lit[1:-1]
    out = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            nxt = body[i + 1]
            out.append(_ESC.get(nxt, '\\' + nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def classify(text):
    """按台词判一个表情名；判不出来返回 None（保持默认头像）。

    顺序有讲究：先认"全角括号的旁白/内心独白"。
    旁白里出现的"笑/哭/怒"是**别人**的表情（如"（他们笑着走开了。）"），
    拿来套在说话人脸上会全是错的，所以这类统一按"沉默旁观"给沉思。
    """
    plain = COLOR.sub('', text)
    if THINK_FOR_PAREN and plain.lstrip().startswith('（'):
        return 'think'
    for name, words in RULES:
        for w in words:
            if w in plain:
                return name
    return None


def lua_files(only=None):
    out = []
    for f in sorted(os.listdir(MOD_LUA)):
        if not f.endswith('.lua') or f in ('hotfix.lua', 'expr.lua'):
            continue
        if only is not None and f[:-4] not in only:
            continue
        out.append(os.path.join(MOD_LUA, f))
    return out


def scan(path):
    """返回 (已标表情列表, 待处理列表)：[(match, roleId, 台词, 表情), ...]"""
    text = io.open(path, encoding='utf-8').read()
    tagged = [(m, int(m.group(1)), lua_unquote(m.group(2)), m.group(3))
              for m in CALL3.finditer(text)]
    todo = []
    for m in CALL2.finditer(text):
        role_id = int(m.group(1))
        line = lua_unquote(m.group(2))
        expr = classify(line)
        if expr:
            todo.append((m, role_id, line, expr))
    return tagged, todo


def retag(path, todo):
    """把 Talk(id, "…") 改成 Talk(id, "…", EXPR.xxx)，返回改动条数。"""
    text = io.open(path, encoding='utf-8').read()
    hits = 0

    def _sub(m):
        nonlocal hits
        line = lua_unquote(m.group(2))
        expr = classify(line)
        if not expr:
            return m.group(0)
        hits += 1
        return 'Talk(%s, %s, EXPR.%s)' % (m.group(1), m.group(2), expr)

    new = CALL2.sub(_sub, text)
    if hits:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(new)
    return hits


def used_combos():
    """剧本里实际用到的 (角色id, 槽位号)，供 gen_expr_heads.py 决定要生成哪些图。"""
    used = set()
    for path in lua_files():
        text = io.open(path, encoding='utf-8').read()
        for m in CALL3.finditer(text):
            slot = SLOTS.get(m.group(3))
            if slot:
                used.add((int(m.group(1)), slot))
    return used


def main():
    argv = sys.argv[1:]
    apply_ = '--apply' in argv
    only = None
    if '--only' in argv:
        only = set(x.strip() for x in argv[argv.index('--only') + 1].split(',') if x.strip())

    total2 = total3 = 0
    by_expr = collections.Counter()       # 已标在剧本里的
    plan_expr = collections.Counter()     # 本次会标的（写盘后就是 by_expr 的一部分）
    by_char = collections.Counter()
    lines = []
    changed = 0

    for path in lua_files(only):
        name = os.path.basename(path)
        text = io.open(path, encoding='utf-8').read()
        tagged, todo = scan(path)
        total3 += len(tagged)
        total2 += len(CALL2.findall(text))
        for _m, role_id, _line, expr in tagged:
            by_expr[expr] += 1
            by_char[role_id] += 1
        if not todo:
            continue
        for _m, role_id, _line, expr in todo:
            plan_expr[expr] += 1
        lines.append('%s: 可标 %d 句（已标 %d 句）' % (name, len(todo), len(tagged)))
        for _m, role_id, line, expr in todo:
            lines.append('    %-6s id=%-4d %-6s %s' % ('', role_id, expr, line[:40]))
        if apply_:
            n = retag(path, todo)
            if n:
                changed += 1
                for _m, role_id, _line, expr in todo:
                    by_expr[expr] += 1
                    by_char[role_id] += 1
            lines.append('    -> 已写入 %d 句' % n)

    head = [
        '模式: %s' % ('apply' if apply_ else 'stats（未写盘）'),
        'Talk 总数 %d 句；已标表情 %d 句；本次可标 %d 句；改动文件 %d 个'
        % (total2 + total3, total3, sum(plan_expr.values()), changed),
        '本次可标（按表情）: ' + (', '.join('%s=%d' % (k, v) for k, v in plan_expr.most_common()) or '-'),
        '已在剧本里（按表情）: ' + (', '.join('%s=%d' % (k, v) for k, v in by_expr.most_common()) or '-'),
        '已在剧本里（按角色）: ' + (', '.join('%s=%d' % (k, v) for k, v in by_char.most_common()) or '-'),
        '',
    ]
    io.open(REPORT, 'w', encoding='utf-8', newline='\n').write('\n'.join(head + lines))
    print('report -> %s  (changed files: %d)' % (REPORT, changed))


if __name__ == '__main__':
    main()
