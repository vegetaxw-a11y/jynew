# -*- coding: utf-8 -*-
"""把 JYX2 剧情 Lua 解析成「节点图」，供 Web 剧情编辑器展示与局部修改。

为什么不写完整的 Lua 解析器：shendiao 的剧情脚本是一套**受限方言**，
167 个脚本里用到的构造只有这些（`tools/storyeditor/survey_lua.py` 统计）：

    Talk / ShowMessage / ShowYesOrNoSelectPanel / 各种动作调用
    if <cond> then goto L end;                  ← 单行条件跳转，29 个文件
    if <cond> then ... [elseif ...] [else] end   ← 多行块，73 个文件，最深 4 层
    ::label:: / goto label                      ← 分段，29 个文件有 label
    do return end;                              ← 惯例收尾，164 个文件
    local x = ...                               ← 只有 5 个文件（都是 expr/hotfix/balance）

所以本模块做「行级 + 块级」解析：先去掉注释，再按 if/elseif/else/end 递归，
其余一律当一个语句。解析结果是一张有向图：

    start / label  → 每段入口
    talk           → Talk(...) 一句对白（带说话人、表情、头像 id）
    choice         → ShowYesOrNoSelectPanel（玩家选项，分支 = 是/否）
    condition      → 其它 if（分支 = 条件成立 / 否则）
    action         → 有副作用的调用（旗标 / 物品 / 战斗 / 武功 / 镜头 / 场景 NPC…）
    code           → 其余代码（local / 赋值 / 不认识的调用）
    end            → do return end / return

图里同时保留每个节点的源文件行号与原始行（`line` / `raw`），
`story_edit.py` 靠这两样做「只改这一行」的安全回写。
"""
from __future__ import annotations

import re


# --------------------------------------------------------------------------- #
# 词法：去注释（字符串感知）
# --------------------------------------------------------------------------- #

def strip_comment(line: str) -> str:
    """去掉 `--` 行注释，但不碰字符串里的 `--`。"""
    out = []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c in '"\'':
            j = i + 1
            while j < n:
                if line[j] == '\\':
                    j += 2
                    continue
                if line[j] == c:
                    break
                j += 1
            out.append(line[i:j + 1])
            i = j + 1
            continue
        if line.startswith('--', i):
            break
        out.append(c)
        i += 1
    return ''.join(out)


def split_top(text: str, sep: str = ','):
    """按顶层分隔符切分，照顾 [[..]] / "..." / {...} / (...) 的嵌套。"""
    out, buf, depth = [], [], 0
    i, n = 0, len(text)
    while i < n:
        if text.startswith('[[', i):
            j = text.find(']]', i + 2)
            j = n if j < 0 else j + 2
            buf.append(text[i:j])
            i = j
            continue
        c = text[i]
        if c in '"\'':
            j = i + 1
            while j < n:
                if text[j] == '\\':
                    j += 2
                    continue
                if text[j] == c:
                    break
                j += 1
            buf.append(text[i:j + 1])
            i = j + 1
            continue
        if c in '{(':
            depth += 1
        elif c in '})':
            depth -= 1
        if c == sep and depth == 0:
            out.append(''.join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    tail = ''.join(buf)
    if tail.strip():
        out.append(tail)
    return [x.strip() for x in out]


def lua_literal(v: str):
    """Lua 字面量 -> Python 值；不认识的原样返回字符串。"""
    v = v.strip()
    if not v:
        return ''
    if v.startswith('[[') and v.endswith(']]'):
        return v[2:-2]
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1]
    if v == 'nil':
        return None
    if v == 'true':
        return True
    if v == 'false':
        return False
    if re.fullmatch(r'-?\d+', v):
        return int(v)
    if re.fullmatch(r'-?\d*\.\d+', v):
        return float(v)
    return v


def split_call(code: str):
    """`Name(args);` -> (name, args_text)；不是调用返回 None。"""
    m = re.match(r'^([A-Za-z_][\w.:]*)\s*\(', code)
    if not m:
        return None
    name = m.group(1)
    start = m.end() - 1                     # 指向 '('
    depth, i, n = 0, start, len(code)
    while i < n:
        c = code[i]
        if c in '"\'':
            j = i + 1
            while j < n:
                if code[j] == '\\':
                    j += 2
                    continue
                if code[j] == c:
                    break
                j += 1
            i = j + 1
            continue
        if code.startswith('[[', i):
            j = code.find(']]', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return name, code[start + 1:i]
        i += 1
    return name, code[start + 1:]           # 括号没配平：交给 lint 报，这里尽力而为


def parse_args(text: str):
    return split_top(text) if text.strip() else []


# --------------------------------------------------------------------------- #
# 语法：语句树
# --------------------------------------------------------------------------- #

SINGLE_IF_RE = re.compile(r'^if\b(.*?)\bthen\b(.*)\bend\s*;?\s*$', re.S)


class _Parser:
    def __init__(self, raw_lines):
        self.raw = raw_lines
        self.code = [strip_comment(x) for x in raw_lines]
        self.i = 0

    # -- 语句块 ---------------------------------------------------------
    def parse_block(self):
        out = []
        while self.i < len(self.code):
            code = self.code[self.i].strip()
            if not code:
                self.i += 1
                continue
            if code.startswith('::'):
                out.append(self._label())
                continue
            if code.startswith('elseif') or re.match(r'^else\b', code) or re.match(r'^end\b', code):
                return out
            if re.match(r'^if\b', code):
                m = SINGLE_IF_RE.match(code)
                if m and m.group(2).strip():
                    out.append(self._single_if(m))
                else:
                    out.append(self._multi_if())
                continue
            out.append(self._simple())
        return out

    # -- 单语句 ---------------------------------------------------------
    def _label(self):
        idx = self.i
        code = self.code[idx].strip()
        self.i += 1
        m = re.match(r'^::\s*(\w+)\s*::', code)
        return {'kind': 'label', 'line': idx + 1, 'raw': self.raw[idx].rstrip('\r\n'),
                'name': m.group(1) if m else code}

    def _simple(self):
        idx = self.i
        code = self.code[idx].strip()
        raw = self.raw[idx].rstrip('\r\n')
        self.i += 1
        st = {'kind': 'code', 'line': idx + 1, 'raw': raw, 'code': code}
        m = re.match(r'^goto\s+(\w+)\s*;?$', code)
        if m:
            st.update(kind='goto', target=m.group(1))
            return st
        if re.match(r'^(do\s+)?return\b', code):
            st.update(kind='return')
            return st
        call = split_call(code)
        if call:
            st.update(kind='call', name=call[0], args=parse_args(call[1]))
        return st

    def _single_if(self, m):
        idx = self.i
        self.i += 1
        body = self._inline_body(m.group(2).strip(), idx)
        return {'kind': 'if', 'line': idx + 1, 'endLine': idx + 1,
                'raw': self.raw[idx].rstrip('\r\n'),
                'branches': [{'cond': m.group(1).strip(), 'line': idx + 1, 'body': body}]}

    def _inline_body(self, code, idx):
        """单行 if 的 body：只可能是 goto / return / 单个调用。"""
        st = {'kind': 'code', 'line': idx + 1, 'raw': self.raw[idx].rstrip('\r\n'), 'code': code}
        m = re.match(r'^goto\s+(\w+)\s*;?$', code)
        if m:
            st.update(kind='goto', target=m.group(1))
            return [st]
        if re.match(r'^(do\s+)?return\b', code):
            st.update(kind='return')
            return [st]
        call = split_call(code)
        if call:
            st.update(kind='call', name=call[0], args=parse_args(call[1]))
        return [st]

    def _multi_if(self):
        idx = self.i
        code = self.code[idx].strip()
        m = re.match(r'^if\b(.*?)\bthen\b', code)
        cond = m.group(1).strip() if m else code
        self.i += 1
        branches = [{'cond': cond, 'line': idx + 1, 'body': self.parse_block()}]
        while self.i < len(self.code):
            c = self.code[self.i].strip()
            if c.startswith('elseif'):
                mm = re.match(r'^elseif\b(.*?)\bthen\b', c)
                ln = self.i + 1
                self.i += 1
                branches.append({'cond': (mm.group(1).strip() if mm else c), 'line': ln,
                                 'body': self.parse_block()})
                continue
            if re.match(r'^else\b', c):
                ln = self.i + 1
                self.i += 1
                branches.append({'cond': None, 'line': ln, 'body': self.parse_block()})
                continue
            if re.match(r'^end\b', c):
                end_line = self.i + 1
                self.i += 1
                return {'kind': 'if', 'line': idx + 1, 'endLine': end_line,
                        'raw': self.raw[idx].rstrip('\r\n'), 'branches': branches}
            break
        return {'kind': 'if', 'line': idx + 1, 'endLine': idx + 1,
                'raw': self.raw[idx].rstrip('\r\n'), 'branches': branches}


def parse_statements(text: str):
    """Lua 文本 -> (顶层语句列表, 行数)。"""
    lines = text.split('\n')
    p = _Parser(lines)
    return p.parse_block(), len(lines)


# --------------------------------------------------------------------------- #
# 语义：条件 / 调用 的展示文本
# --------------------------------------------------------------------------- #

FLAG_GET = re.compile(r'Get(?:FlagInt|Flag|Int)\(\s*"([^"]+)"\s*\)')
YES_NO = re.compile(r'ShowYesOrNoSelectPanel\s*\(\s*"((?:[^"\\]|\\.)*)"')


def humanize_cond(cond: str) -> str:
    c = YES_NO.sub(r'「\1」', cond)
    c = FLAG_GET.sub(r'旗标「\1」', c)
    c = c.replace('==', ' = ').replace('~=', ' ≠ ').replace('>=', ' ≥ ').replace('<=', ' ≤ ')
    c = re.sub(r'\band\b', '且', c)
    c = re.sub(r'\bor\b', '或', c)
    c = re.sub(r'\bnot\b', '非', c)
    c = re.sub(r'\s+', ' ', c)
    return c.strip()


# 调用 -> (分组, 中文标题)
CALL_INFO = {
    'SetFlagInt': ('flag', '设置旗标'), 'SetFlag': ('flag', '设置旗标'),
    'SetFlagStr': ('flag', '设置旗标'), 'scene_api.SetInt': ('flag', '设置场景旗标'),
    'AddItem': ('item', '获得物品'), 'AddItemWithoutHint': ('item', '获得物品（静默）'),
    'UseItem': ('item', '使用物品'), 'RemoveItem': ('item', '失去物品'),
    'TryBattle': ('battle', '进入战斗'), 'AskBattle': ('battle', '请求战斗'),
    'TryBattleWithConfig': ('battle', '进入战斗'),
    'LearnMagic2': ('skill', '习得武功'), 'LearnMagic': ('skill', '习得武功'),
    'ShowSceneNpc': ('npc', '场景 NPC 显隐'), 'HideSceneNpc': ('npc', '场景 NPC 显隐'),
    'jyx2_CameraFollow': ('camera', '镜头跟随'), 'jyx2_CameraFollowPlayer': ('camera', '镜头回到主角'),
    'PlayMusic': ('audio', '切换音乐'), 'PlaySound': ('audio', '播放音效'),
    'ScreenVignette': ('screen', '画面暗角'), 'LightScene': ('screen', '画面转亮'),
    'LightScence': ('screen', '画面转亮'), 'DarkScene': ('screen', '画面转暗'),
    'DarkScence': ('screen', '画面转暗'),
    'AddExp': ('stat', '属性变化'), 'AddHp': ('stat', '属性变化'),
    'AddHpWithoutHint': ('stat', '属性变化'), 'AddMp': ('stat', '属性变化'),
    'AddAttack': ('stat', '属性变化'), 'AddDefence': ('stat', '属性变化'),
    'AddSpeed': ('stat', '属性变化'), 'AddEthics': ('stat', '道德变化'),
    'AddRepute': ('stat', '声望变化'),
    'ModifyEvent': ('event', '触发器状态'), 'jyx2_ReplaceSceneObject': ('event', '场景物件替换'),
    'jyx2_FixMapObject': ('event', '场景物件摆放'), 'jyx2_Wait': ('event', '等待'),
    'ShowToast': ('toast', '浮动提示'),
    'ShowYesOrNoSelectPanel': ('choice', '玩家选项'), 'ShowSelectPanel': ('choice', '玩家选项'),
    'ShowMessageSelectPanel': ('choice', '玩家选项'),
}


def _arg(args, i):
    return lua_literal(args[i]) if len(args) > i else None


def describe_call(name: str, args, resolve) -> dict:
    """调用 -> {group, title, detail, params}（detail 尽量说人话）。"""
    group, title = CALL_INFO.get(name, ('misc', name))
    detail = ''
    params = {}

    if name in ('SetFlagInt', 'SetFlag', 'SetFlagStr', 'scene_api.SetInt'):
        flag, val = _arg(args, 0), _arg(args, 1)
        params = {'flag': flag, 'value': val}
        detail = '%s = %s' % (flag, val)
    elif name in ('AddItem', 'AddItemWithoutHint', 'UseItem', 'RemoveItem'):
        iid, num = _arg(args, 0), _arg(args, 1)
        params = {'item': iid, 'count': num}
        nm = resolve.item_name(iid) if hasattr(resolve, 'item_name') else ''
        detail = '%s%s' % (nm or ('物品 %s' % iid), ' ×%s' % num if num not in (None, 1) else '')
    elif name in ('TryBattle', 'AskBattle', 'TryBattleWithConfig'):
        bid = _arg(args, 0)
        params = {'battle': bid}
        nm = resolve.battle_name(bid) if hasattr(resolve, 'battle_name') else ''
        detail = '%s%s' % (nm or ('战斗 %s' % bid), '（%s）' % bid if nm else '')
    elif name in ('LearnMagic2', 'LearnMagic'):
        role, sid = _arg(args, 0), _arg(args, 1)
        params = {'role': role, 'skill': sid}
        nm = resolve.skill_name(sid) if hasattr(resolve, 'skill_name') else ''
        detail = '%s（角色 %s）' % (nm or ('武功 %s' % sid), role)
    elif name in ('ShowSceneNpc', 'HideSceneNpc'):
        path, show = _arg(args, 0), _arg(args, 1)
        if name == 'HideSceneNpc':
            show = False
        params = {'path': path, 'show': show}
        detail = '%s %s' % (path, '出现' if show else '隐藏')
    elif name in ('jyx2_CameraFollow',):
        params = {'path': _arg(args, 0)}
        detail = str(params['path'])
    elif name == 'PlayMusic':
        params = {'music': _arg(args, 0)}
        detail = '音乐 id %s' % params['music']
    elif name == 'jyx2_Wait':
        params = {'seconds': _arg(args, 0)}
        detail = '等待 %s 秒' % params['seconds']
    elif name == 'jyx2_FixMapObject':
        params = {'key': _arg(args, 0), 'value': _arg(args, 1)}
        detail = '%s = %s' % (params['key'], params['value'])
    elif name == 'jyx2_ReplaceSceneObject':
        params = {'scene': _arg(args, 0), 'path': _arg(args, 1), 'replace': _arg(args, 2)}
        detail = '%s / %s' % (params['path'], params['replace'])
    elif name == 'ModifyEvent':
        params = {'args': list(args)}
        detail = '让触发器 / 自身进入下一状态'
    elif name in ('AddExp', 'AddHp', 'AddMp', 'AddAttack', 'AddDefence', 'AddSpeed',
                  'AddEthics', 'AddRepute', 'AddHpWithoutHint'):
        val = _arg(args, 0)
        params = {'value': val}
        detail = '%+d' % val if isinstance(val, int) else str(val)
    elif name in ('ShowYesOrNoSelectPanel', 'ShowSelectPanel', 'ShowMessageSelectPanel'):
        prompt = _arg(args, 0)
        params = {'prompt': prompt, 'options': [_arg(args, i) for i in range(1, len(args))]}
        detail = str(prompt)
    elif name == 'ShowToast':
        params = {'text': _arg(args, 0)}
        detail = str(params['text'])

    return {'group': group, 'title': title, 'detail': detail, 'params': params,
            'call': name, 'args': list(args)}


# --------------------------------------------------------------------------- #
# 建图
# --------------------------------------------------------------------------- #

def _indent(raw: str) -> str:
    return raw[:len(raw) - len(raw.lstrip())]


def _talk_node(st, resolve):
    role = _arg(st['args'], 0)
    try:
        role = int(role)
    except (TypeError, ValueError):
        role = None
    text = _arg(st['args'], 1)
    expr_raw = st['args'][2] if len(st['args']) > 2 else ''
    m = re.match(r'^EXPR(?:\.(\w+)|\[\s*[\'"]([^\'"]+)[\'"]\s*\])$', str(expr_raw).strip())
    expr = (m.group(1) or m.group(2)) if m else None
    info = resolve.talk(role, expr)
    return {'kind': 'talk', 'line': st['line'], 'raw': st['raw'], 'text': text or '',
            'role': role, 'expr': expr, 'exprRaw': expr_raw or None,
            'roleName': info.get('roleName'), 'headId': info.get('headId'),
            'exprSlot': info.get('exprSlot'), 'indent': _indent(st['raw'])}


class _PlainResolver:
    """没有 MOD 数据时的兜底：名字直接用 id。"""

    def talk(self, role, expr):
        return {'roleName': str(role), 'headId': role, 'exprSlot': None}


def build_graph(text: str, resolve=None):
    """Lua 文本 -> {'nodes','edges','segments','stats','speakers','errors','title'}"""
    resolve = resolve or _PlainResolver()
    stmts, line_count = parse_statements(text)
    nodes, edges, errors = [], [], []

    def add_node(kind, **kw):
        nid = 'n%d' % len(nodes)
        node = {'id': nid, 'kind': kind}
        node.update(kw)
        nodes.append(node)
        return node

    def add_edge(a, b, label=None, kind='flow'):
        if not a or not b:
            return
        edges.append({'from': a, 'to': b, 'label': label, 'kind': kind})

    # --- 分段：每个 label 开一段；首个 label 之前是入口段 ----------------
    segs, cur = [], None
    for st in stmts:
        if st['kind'] == 'label':
            cur = {'name': st['name'], 'line': st['line'], 'raw': st.get('raw', ''), 'stmts': []}
            segs.append(cur)
        else:
            if cur is None:
                cur = {'name': None, 'line': 1, 'raw': '', 'stmts': []}
                segs.append(cur)
            cur['stmts'].append(st)
    if not segs:
        segs = [{'name': None, 'line': 1, 'raw': '', 'stmts': []}]

    jump_targets = {}
    for seg in segs:
        if seg['name']:
            n = add_node('label', line=seg['line'], raw=seg['raw'], name=seg['name'],
                         title='::%s::' % seg['name'], indent='')
            jump_targets[seg['name']] = n['id']
        else:
            n = add_node('start', line=1, raw='', title='开始', indent='')
        seg['head'] = n['id']

    # --- 逐段连线 ------------------------------------------------------
    def walk(stmts_, from_items, first_label=None):
        cur = [(i, None) if isinstance(i, str) else i for i in from_items]
        pend = first_label

        def link(node_id):
            nonlocal cur, pend
            for fid, lbl in cur:
                add_edge(fid, node_id, pend or lbl)
            pend = None
            cur = [(node_id, None)]

        for st in list(stmts_):
            kind = st['kind']
            if kind == 'label':
                continue
            if kind == 'call' and st['name'] == 'Talk':
                link(add_node(**_talk_node(st, resolve))['id'])
                continue
            if kind == 'call' and st['name'] in ('ShowMessage', 'ShowToast'):
                n = add_node('message', line=st['line'], raw=st['raw'], group='message',
                             title='旁白提示', text=str(_arg(st['args'], 0) or ''),
                             indent=_indent(st['raw']))
                link(n['id'])
                continue
            if kind == 'if':
                conds = ' '.join(br['cond'] or '' for br in st['branches'])
                m = YES_NO.search(conds)
                if m:
                    n = add_node('choice', line=st['line'], endLine=st.get('endLine'),
                                 raw=st['raw'], prompt=m.group(1), cond=conds,
                                 indent=_indent(st['raw']), branches=len(st['branches']))
                else:
                    n = add_node('condition', line=st['line'], endLine=st.get('endLine'),
                                 raw=st['raw'], cond=conds, condText=humanize_cond(conds),
                                 indent=_indent(st['raw']), branches=len(st['branches']))
                link(n['id'])
                exits, has_else, total = [], False, len(st['branches'])
                for bi, br in enumerate(st['branches']):
                    if br['cond'] is None:
                        has_else = True
                        label = '否则'
                    elif m:
                        label = '是' if bi == 0 else ('否' if total == 2 else '选项%d' % (bi + 1))
                    else:
                        label = '条件成立' if bi == 0 else '条件%d' % (bi + 1)
                    exits.extend(walk(br['body'], [(n['id'], None)], label))
                if not has_else:
                    exits.append((n['id'], '否则'))
                cur, pend = exits, None
                continue
            if kind == 'goto':
                target = jump_targets.get(st['target'])
                if target is None:
                    errors.append({'line': st['line'],
                                   'message': 'goto %s 找不到对应 label' % st['target']})
                for fid, lbl in cur:
                    add_edge(fid, target, pend or lbl, kind='jump')
                cur, pend = [], None
                continue
            if kind == 'return':
                n = add_node('end', line=st['line'], raw=st['raw'], title='事件结束',
                             indent=_indent(st['raw']))
                link(n['id'])
                cur = []
                continue
            if kind == 'call':
                info = describe_call(st['name'], st['args'], resolve)
                n = add_node('action', line=st['line'], raw=st['raw'], indent=_indent(st['raw']),
                             **{k: info[k] for k in ('group', 'title', 'detail', 'params',
                                                     'call', 'args')})
                link(n['id'])
                continue
            n = add_node('code', line=st['line'], raw=st['raw'], code=st['code'],
                         indent=_indent(st['raw']), title='代码')
            link(n['id'])
        return cur

    for seg_i, seg in enumerate(segs):
        exits = walk(seg['stmts'], [(seg['head'], None)])
        seg['exits'] = exits
        # 段尾自然落进下一段（Lua 里一般不会；出现说明作者想要「顺序执行」）
        if exits and seg_i + 1 < len(segs):
            for nid, lbl in exits:
                add_edge(nid, segs[seg_i + 1]['head'], lbl, kind='fallthrough')

    in_deg = {}
    for e in edges:
        in_deg[e['to']] = in_deg.get(e['to'], 0) + 1
    for n in nodes:
        if in_deg.get(n['id'], 0) == 0 and n['kind'] not in ('start', 'label'):
            n['orphan'] = True

    return {'nodes': nodes, 'edges': edges,
            'segments': [{'name': s['name'], 'line': s['line'], 'head': s['head']} for s in segs],
            'stats': _stats(nodes), 'speakers': _speakers(nodes),
            'errors': errors, 'lineCount': line_count,
            'title': script_title(text) or _fallback_title(nodes)}


def _fallback_title(nodes) -> str:
    """没有头部注释的脚本（占位剧情很多），用第一句对白当标题。"""
    for n in nodes:
        if n['kind'] == 'talk' and n.get('text'):
            text = str(n['text']).strip().replace('\n', ' ')
            return text[:28] + ('…' if len(text) > 28 else '')
    return ''


GROUP_PARAM = {'flag': 'flag', 'item': 'item', 'battle': 'battle',
               'skill': 'skill', 'npc': 'path'}
STAT_LIST = {'flag': 'flags', 'item': 'items', 'battle': 'battles',
             'skill': 'skills', 'npc': 'npcs'}


def _stats(nodes):
    stats = {'talk': 0, 'action': 0, 'code': 0, 'choice': 0, 'condition': 0,
             'label': 0, 'end': 0, 'flags': [], 'items': [], 'battles': [],
             'skills': [], 'npcs': []}
    for n in nodes:
        if n['kind'] in stats:
            stats[n['kind']] += 1
        group = n.get('group')
        if group not in GROUP_PARAM:
            continue
        params = n.get('params') or {}
        val = params.get(GROUP_PARAM[group])
        bucket = stats[STAT_LIST[group]]
        if val is not None and val not in bucket:
            bucket.append(val)
    return stats


def _speakers(nodes):
    out = []
    for n in nodes:
        if n['kind'] == 'talk' and n.get('role') is not None and n['role'] not in out:
            out.append(n['role'])
    return out


def script_title(text: str) -> str:
    """第一条注释当标题（剧本头部惯例：`-- 【第一回 …】佛堂：…`）。"""
    for line in text.split('\n')[:4]:
        s = line.strip()
        if s.startswith('--') and not s.startswith('--[['):
            t = s.lstrip('-').strip()
            if t:
                return t
    return ''
