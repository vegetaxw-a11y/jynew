# -*- coding: utf-8 -*-
"""剧情编辑器自测：不启动服务器就能验证「解析 + 回写」的正确性。

    python tools/storyeditor/selftest_story.py

检查项：
  1. 解析 shendiao 全部剧本：不抛异常、边不悬空、Talk 数量与源码一致、goto 有 label
  2. 回写保真：只改目标行，缩进 / 结尾分号 / 行尾注释 / 行尾 CRLF 全部保留
  3. 幂等：把改过的行改回原样，文件必须与原文件逐字节一致
  4. 整份源码保存：语法坏掉时拒绝落盘
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import story_edit      # noqa: E402
import story_lua       # noqa: E402
import story_mod       # noqa: E402

FAILED = []


def check(cond, message):
    if cond:
        print('  [ok]   %s' % message)
    else:
        print('  [FAIL] %s' % message)
        FAILED.append(message)


def test_parse_all(mod):
    print('\n== 1. 解析全部剧本 ==')
    total_nodes = total_edges = 0
    bad = []
    for eid in mod.event_ids():
        graph = mod.event_graph(eid)
        ids = {n['id'] for n in graph['nodes']}
        total_nodes += len(graph['nodes'])
        total_edges += len(graph['edges'])
        for edge in graph['edges']:
            if edge['from'] not in ids or edge['to'] not in ids:
                bad.append('%s 边悬空 %s->%s' % (eid, edge['from'], edge['to']))
        for err in graph['errors']:
            bad.append('%s:%s %s' % (eid, err['line'], err['message']))
        src_talks = graph['source'].count('Talk(')
        node_talks = sum(1 for n in graph['nodes'] if n['kind'] == 'talk')
        if src_talks != node_talks:
            bad.append('%s Talk 数不符 %d/%d' % (eid, node_talks, src_talks))
        if not graph['nodes']:
            bad.append('%s 解析出 0 个节点' % eid)
    print('  剧本 %d 个 / 节点 %d / 边 %d' % (len(mod.event_ids()), total_nodes, total_edges))
    check(not bad, '全部剧本解析干净%s' % ('' if not bad else
                                         '（%d 条问题：%s）' % (len(bad), bad[:3])))


def make_temp_mod(mod, names):
    """拷一份最小 MOD（配置表 + 指定剧本）到临时目录，随便改不会伤到真文件。"""
    tmp = tempfile.mkdtemp(prefix='storyeditor_')
    os.makedirs(os.path.join(tmp, 'Lua'))
    shutil.copytree(mod.cfg_dir, os.path.join(tmp, 'Configs', 'Lua'))
    for name in names:
        shutil.copy2(os.path.join(mod.lua_dir, name), os.path.join(tmp, 'Lua', name))
    return tmp


def test_roundtrip(mod):
    print('\n== 2. 回写保真（LF / CRLF / 缩进 / 分号）==')
    tmp = make_temp_mod(mod, ['2.lua', '1001.lua'])
    tmod = story_mod.ModData(tmp)
    try:
        _roundtrip_one(tmod, '2.lua', 3)
        _roundtrip_one(tmod, '1001.lua', 17)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _roundtrip_one(mod, name, line_no):
    path = os.path.join(mod.lua_dir, name)
    original = io.open(path, encoding='utf-8', newline='').read()
    crlf = '\r\n' in original
    lines = original.split('\n')
    raw = lines[line_no - 1].rstrip('\r')

    graph = story_lua.build_graph(original, mod)
    node = next(n for n in graph['nodes'] if n.get('line') == line_no and n['kind'] == 'talk')
    check(node['raw'] == raw, '%s:%d 解析出的 raw 与文件一致' % (name, line_no))

    new_text = '（自测）这一行被改过。'
    story_edit.edit_line(mod, name[:-4], {
        'line': line_no, 'expect': raw, 'kind': 'talk',
        'role': node['role'], 'expr': None, 'text': new_text,
    })
    after = io.open(path, encoding='utf-8', newline='').read()
    after_lines = after.split('\n')
    check(after_lines[line_no - 1].rstrip('\r').endswith('Talk(%s, "%s")'
          % (node['role'], new_text)),
          '%s:%d 只改了 Talk 调用体' % (name, line_no))
    check(len(after_lines) == len(lines), '%s 行数没变' % name)
    changed = [i for i, (a, b) in enumerate(zip(lines, after_lines), 1) if a != b]
    check(changed == [line_no], '%s 只有第 %d 行变了（实际 %s）' % (name, line_no, changed))
    if crlf:
        check(after.count('\r\n') == original.count('\r\n'), '%s 保留了 CRLF 行尾' % name)

    issues = story_edit.lint_file(path, mod)
    check(not issues, '%s 改完 lint 无问题%s' % (name, '' if not issues else '（%s）' % issues[:2]))

    new_raw = after_lines[line_no - 1].rstrip('\r')
    story_edit.edit_line(mod, name[:-4], {
        'line': line_no, 'expect': new_raw, 'kind': 'talk',
        'role': node['role'], 'expr': node['expr'], 'text': node['text'],
    })
    restored = io.open(path, encoding='utf-8', newline='').read()
    check(restored == original, '%s 改回原词后逐字节还原' % name)


def test_guard(mod):
    print('\n== 3. 护栏 ==')
    tmp = make_temp_mod(mod, ['2.lua'])
    tmod = story_mod.ModData(tmp)
    try:
        path = os.path.join(tmod.lua_dir, '2.lua')
        before = io.open(path, encoding='utf-8', newline='').read()
        line3 = before.split('\n')[2].rstrip('\r')
        try:
            story_edit.edit_line(tmod, '2', {'line': 3, 'expect': '错的原文',
                                             'kind': 'talk', 'role': 0, 'text': 'x'})
            check(False, '原文对不上时应该拒绝写入')
        except story_edit.EditError as exc:
            check(exc.status == 409, '原文对不上时返回 409')
        try:
            story_edit.edit_line(tmod, '2', {'line': 3, 'kind': 'talk', 'role': 9999,
                                             'text': 'x', 'expect': line3})
            check(False, '人物 Id 不存在时应该拒绝')
        except story_edit.EditError:
            check(True, '人物 Id 不在表里时拒绝写入')
        try:
            story_edit.save_source(tmod, '2', 'if x then\nTalk(0, "x")\n')
            check(False, '语法错误（缺 end）应该拒绝落盘')
        except story_edit.EditError:
            check(True, '语法体检不过时拒绝落盘')
        check(io.open(path, encoding='utf-8', newline='').read() == before,
              '被拒绝的写入没有改动文件')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print('仓库: %s' % story_mod.REPO)
    mod = story_mod.ModData()
    meta = mod.meta()
    print('MOD : %s（%s）' % (meta['modName'], meta['modId']))
    print('统计: %s' % meta['counts'])
    test_parse_all(mod)
    test_roundtrip(mod)
    test_guard(mod)

    print('\n== 结果 ==')
    if FAILED:
        print('失败 %d 项：' % len(FAILED))
        for f in FAILED:
            print('  - %s' % f)
        return 1
    print('全部通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
