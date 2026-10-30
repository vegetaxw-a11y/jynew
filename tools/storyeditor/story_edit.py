# -*- coding: utf-8 -*-
"""剧本回写：只改「被点中的那一行」，改完立刻自检。

设计原则（很重要，剧本是手写的，不能整份重排）：

1. **行级替换**，不做格式化。原行的缩进、结尾分号、行尾 `-- 注释` 全部保留，
   只重写 `Talk(...)` / `ShowMessage(...)` 的调用体。
2. **乐观锁**：前端把「当前行的原文」一起发过来（`expect`），
   服务端比对不上就 409，避免在别人改过的文件上盲写。
3. **改前备份**，改后立刻跑 `story_lua` 重新解析 + `lint_lua` 语法体检，
   有问题返回给界面（文件已经写下去了，界面提示"去 git checkout 回滚"）。
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import time

import story_lua
import story_mod

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SHENDIAO_TOOLS = os.path.join(REPO, 'tools', 'shendiao')


def tools_dir(mod_dir: str = None) -> str:
    """tools/shendiao 的真实位置（容器里要靠 MOD 目录反推仓库根）。"""
    if mod_dir:
        cand = os.path.join(story_mod.repo_root(mod_dir), 'tools', 'shendiao')
        if os.path.isdir(cand):
            return cand
    return SHENDIAO_TOOLS


class EditError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


# --------------------------------------------------------------------------- #
# 文本 <-> Lua 字面量
# --------------------------------------------------------------------------- #

def lua_quote(text: str) -> str:
    """Python 文本 -> Lua 双引号字面量。"""
    body = text.replace('\\', '\\\\').replace('"', '\\"')
    return '"%s"' % body


def split_trailing_comment(raw: str):
    """把一行切成 (代码部分, 行尾注释部分)。注释部分原样保留。"""
    code = story_lua.strip_comment(raw)
    return code, raw[len(code):]


def build_talk_line(indent: str, role: int, text: str, expr, semicolon: bool,
                    comment: str) -> str:
    args = '%d, %s' % (role, lua_quote(text))
    if expr:
        args += ', EXPR.%s' % expr
    return '%sTalk(%s)%s%s' % (indent, args, ';' if semicolon else '', comment)


def build_message_line(indent: str, text: str, semicolon: bool, comment: str) -> str:
    return '%sShowMessage(%s)%s%s' % (indent, lua_quote(text), ';' if semicolon else '', comment)


# --------------------------------------------------------------------------- #
# 文件读写
# --------------------------------------------------------------------------- #

def _backup_dir(mod_dir: str) -> str:
    folder = os.path.join(HERE, '.backups')     # tools/storyeditor/.backups（已 gitignore）
    os.makedirs(folder, exist_ok=True)
    return folder


def backup_file(mod_dir: str, path: str):
    folder = _backup_dir(mod_dir)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(folder, '%s.%s.lua' % (os.path.basename(path)[:-4], stamp))
    try:
        shutil.copy2(path, dest)
    except OSError:
        return None
    # 只留最近 200 份，避免越攒越多
    files = sorted(os.listdir(folder))
    for fn in files[:-200]:
        try:
            os.remove(os.path.join(folder, fn))
        except OSError:
            pass
    return dest


def atomic_write(path: str, text: str):
    tmp = path + '.storyeditor.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as fp:
        fp.write(text)
    os.replace(tmp, path)


def read_lines(path: str):
    """读成 (行列表, 原文本)。newline='' 必须留：否则 CRLF 文件会被通用换行模式吃掉 \\r。"""
    text = io.open(path, encoding='utf-8', newline='').read()
    return text.split('\n'), text


def replace_line(path: str, line_no: int, new_code: str, expect: str = None):
    """替换第 line_no 行（1 起）为 new_code，保留该行原有的 \\r。"""
    lines, _ = read_lines(path)
    if line_no < 1 or line_no > len(lines):
        raise EditError('行号 %d 超出文件范围（共 %d 行）' % (line_no, len(lines)), 400)
    idx = line_no - 1
    orig = lines[idx]
    cr = orig.endswith('\r')
    cur = orig[:-1] if cr else orig
    if expect is not None and cur.strip() != expect.strip():
        raise EditError('第 %d 行已被改动，请刷新后再试。\n当前：%s\n期望：%s'
                        % (line_no, cur.strip(), expect.strip()), 409)
    lines[idx] = new_code + ('\r' if cr else '')
    return '\n'.join(lines)


# --------------------------------------------------------------------------- #
# 体检
# --------------------------------------------------------------------------- #

def lint_file(path: str, mod=None):
    """用 tools/shendiao/lint_lua.py 的规则体检一个文件（跑不动就返回空）。"""
    tool_dir = tools_dir(mod.mod_dir if mod is not None else None)
    if os.path.isdir(tool_dir) and tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)
    try:
        import lint_lua            # noqa: WPS433
    except Exception:              # pragma: no cover - 环境缺工具时降级
        return []
    ids = set(mod.characters) if mod is not None else None
    bids = set(mod.battles) if mod is not None else None
    try:
        return [{'line': ln, 'message': msg} for ln, msg in lint_lua.lint(path, ids, bids)]
    except Exception as exc:       # pragma: no cover
        return [{'line': 0, 'message': 'lint 执行失败：%s' % exc}]


def graph_errors(text: str):
    graph = story_lua.build_graph(text)
    return graph['errors']


# --------------------------------------------------------------------------- #
# 对外操作
# --------------------------------------------------------------------------- #

def edit_line(mod, eid: str, payload: dict):
    """改一行：目前支持 talk（说话人/表情/文本）与 message（旁白文本）。

    payload = {
      'line': 17,                         # 1 起
      'expect': '原行原文',                # 乐观锁
      'kind': 'talk' | 'message',
      'role': 11, 'expr': 'think', 'text': '...'
    }
    """
    path = mod.script_path(eid)
    if not os.path.exists(path):
        raise EditError('事件 %s 没有对应脚本' % eid, 404)

    line_no = int(payload.get('line') or 0)
    expect = payload.get('expect')
    kind = payload.get('kind') or 'talk'
    text = payload.get('text')
    if text is None:
        raise EditError('缺少 text', 400)

    lines, _ = read_lines(path)
    if line_no < 1 or line_no > len(lines):
        raise EditError('行号 %d 超出文件范围（共 %d 行）' % (line_no, len(lines)), 400)
    orig = lines[line_no - 1].rstrip('\r')
    code, comment = split_trailing_comment(orig)
    indent = code[:len(code) - len(code.lstrip())]
    semicolon = code.rstrip().endswith(';')

    if kind == 'talk':
        role = payload.get('role')
        if role is None:
            raise EditError('缺少 role', 400)
        role = int(role)
        if role not in mod.characters:
            raise EditError('人物 Id %d 不在人物表里（游戏里会让事件卡死）' % role, 400)
        expr = payload.get('expr') or None
        if expr and expr not in mod.expr_keys:
            raise EditError('表情 %s 不在 expr.lua 的 EXPR 表里' % expr, 400)
        if not text.strip():
            raise EditError('对白不能为空', 400)
        new_code = build_talk_line(indent, role, text, expr, semicolon, comment)
    elif kind == 'message':
        new_code = build_message_line(indent, text, semicolon, comment)
    else:
        raise EditError('kind 只支持 talk / message', 400)

    new_text = replace_line(path, line_no, new_code, expect)
    if new_text == io.open(path, encoding='utf-8', newline='').read():
        return {'ok': True, 'changed': False, 'line': line_no, 'new': new_code,
                'issues': [], 'graphErrors': []}

    backup = backup_file(mod.mod_dir, path)
    atomic_write(path, new_text)

    issues = lint_file(path, mod)
    gerrs = graph_errors(new_text)
    return {'ok': True, 'changed': True, 'line': line_no, 'new': new_code,
            'issues': issues, 'graphErrors': gerrs, 'backup': os.path.basename(backup or '')}


def quick_syntax_problems(text: str, mod=None):
    """用 lint_lua 的块配平规则做一次快速语法体检（环境没工具就跳过）。"""
    tool_dir = tools_dir(mod.mod_dir if mod is not None else None)
    if os.path.isdir(tool_dir) and tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)
    try:
        import lint_lua            # noqa: WPS433
    except Exception:              # pragma: no cover
        return []
    code, probs = lint_lua.strip_code(text)
    lint_lua.check_balance(code, probs)
    return probs


def save_source(mod, eid: str, text: str, expect_mtime: int = None):
    """整份保存源码（给「源码」页签用）。先静态校验，有明显语法错就不落盘。"""
    path = mod.script_path(eid)
    if not os.path.exists(path):
        raise EditError('事件 %s 没有对应脚本' % eid, 404)
    if expect_mtime and int(expect_mtime) != int(os.stat(path).st_mtime):
        raise EditError('文件已被外部修改，请刷新后再保存', 409)

    probs = quick_syntax_problems(text, mod)
    if probs:
        raise EditError('语法体检没过：' + '；'.join('第 %d 行 %s' % p for p in probs[:5]), 400)

    # 浏览器 textarea 会把行尾统一成 \n，这里按原文件的风格还原，避免整份 CRLF->LF
    original = io.open(path, encoding='utf-8', newline='').read()
    if '\r\n' in original and '\r' not in text:
        text = text.replace('\n', '\r\n')

    backup_file(mod.mod_dir, path)
    atomic_write(path, text)
    return {'ok': True, 'issues': lint_file(path, mod), 'graphErrors': graph_errors(text)}


def validate(mod):
    """跑 tools/shendiao 的两个门禁，返回它们的输出（界面上的「校验」按钮）。"""
    import subprocess
    tool_dir = tools_dir(mod.mod_dir)
    root = story_mod.repo_root(mod.mod_dir)
    results = {}
    for name in ('lint_lua.py', 'check_story.py'):
        script = os.path.join(tool_dir, name)
        if not os.path.exists(script):
            results[name] = {'ok': False, 'output': '找不到 %s' % script}
            continue
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        proc = subprocess.run([sys.executable, script], capture_output=True, timeout=180,
                              env=env, cwd=root)
        out = (proc.stdout or b'').decode('utf-8', 'replace')
        err = (proc.stderr or b'').decode('utf-8', 'replace')
        results[name] = {'ok': proc.returncode == 0, 'output': (out + err).strip()}
    return results
