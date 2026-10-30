# -*- coding: utf-8 -*-
"""离线跑剧情脚本：用 lupa 真跑 Lua，捕捉运行时报错 + 打印对白流水。

为什么需要它：`lint_lua.py` 只查括号/字符串配平，`check_story.py` 只查表引用；
两者都发现不了「flag 分支写反」「goto 跳进死路」「某条线永远走不到」——这些
只有真跑一遍才知道。本工具把 Talk / GetFlagInt / SetFlagInt / AddItem 等等
打成桩，按顺序执行指定脚本，输出完整对白 + 结束时 flag 快照。

用法:
    # 跑指定脚本（同一个 flag 状态里顺序执行）
    python tools/shendiao/sim_lua.py 557 559 563 559 1001 1002

    # 第一回的 4 条回归线（带断言，改完第一回必须跑）
    python tools/shendiao/sim_lua.py --preset ch1

    # 选择面板一律回答「否」
    python tools/shendiao/sim_lua.py --preset ch1 --no

输出写到 Logs/_sim_out.txt（UTF-8），别直接看控制台，中文 Windows 会乱码。
"""
import io
import os
import sys

import lupa

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
LUA_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
OUT_PATH = os.path.join(REPO, 'Logs', '_sim_out.txt')

EXPR = {'calm': 1, 'angry': 2, 'smile': 3, 'think': 4, 'body': 5,
        'bodyside': 6, 'shock': 7, 'sad': 8, 'lookback': 9}


class Sim(object):
    def __init__(self, flags=None, yes=True, quiet=False, win_battle=False):
        self.rt = lupa.LuaRuntime()
        self.flags = dict(flags or {})
        self.log = []
        self.items = []
        self.yes = yes
        self.quiet = quiet
        self.win_battle = win_battle
        g = self.rt.globals()
        g.EXPR = self.rt.table_from(EXPR)
        g.GetFlagInt = lambda k: int(self.flags.get(str(k), 0))
        g.SetFlagInt = lambda k, v: self.flags.__setitem__(str(k), int(v))
        g.Talk = self._talk
        g.AddItem = lambda i, n=1: self.items.append((int(i), int(n)))
        g.ShowMessage = lambda m, *a: self._rec('【提示】', str(m))
        g.ModifyEvent = lambda *a: self._rec('【事件关闭】', '')
        g.ScreenVignette = lambda v: None
        g.ShowYesOrNoSelectPanel = self._select
        g.LearnMagic2 = lambda *a: None
        # 场景层面的指令（见 Jyx2LuaBridge）：显隐 NPC / 相机 / 过场黑幕
        g.jyx2_ReplaceSceneObject = lambda scene, path, v: self._rec(
            '【场景】', '%s -> %s' % (path, '出现' if str(v) == '1' else '隐藏'))
        # hotfix.lua 里的包装：先 Transform.Find 挖出 inactive 对象再 SetActive，
        # 再走 ReplaceSceneObject 记状态。模拟器里只记录成同一种事件。
        g.ShowSceneNpc = lambda path, on=True: self._rec(
            '【场景】', '%s -> %s' % (path, '隐藏' if (on is False or str(on) == '0') else '出现'))

        g.jyx2_CameraFollow = lambda path: self._rec('【镜头】', '对准 %s' % path)
        g.jyx2_CameraFollowPlayer = lambda: self._rec('【镜头】', '回到主角')
        g.jyx2_Wait = lambda t: None
        g.DarkScene = lambda: self._rec('【过场】', '画面转暗')
        g.LightScene = lambda: self._rec('【过场】', '画面转亮')
        g.ShowToast = lambda m: self._rec('【浮字】', str(m))
        g.AddItemWithoutHint = lambda i, n=1: self.items.append((int(i), int(n)))
        g.HaveItem = lambda i: any(k == int(i) for k, _ in self.items)
        # 战斗：默认打输（第一回坟前那场是"必败"），--win 可以切成打赢
        g.TryBattle = self._battle
        # 事件脚本里可以直接用 main.lua 里的 luaBridge 全局（CS.Jyx2.Jyx2LuaBridge）
        g.luaBridge = self.rt.table_from({
            'RestTeam': lambda: self._rec('【系统】', '全队恢复'),
        })
        self.counts = {}
        self.battles = []

    def _battle(self, battle_id):
        self.battles.append(int(battle_id))
        win = self.win_battle
        self._rec('【战斗】', 'battle %d -> %s' % (int(battle_id), '胜' if win else '败'))
        return win

    def _select(self, question):
        self._rec('【选择】', '%s -> %s' % (question, '是' if self.yes else '否'))
        return self.yes


    def _rec(self, who, text):
        self.log.append((who, text))
        if not self.quiet:
            OUT.write('[%s] %s\n' % (who, text))

    def _talk(self, *a):
        rid = a[0]
        text = a[1] if len(a) > 1 else ''
        third = a[2] if len(a) > 2 else None
        fourth = a[3] if len(a) > 3 else None
        # Talk(0, 文本, "", 2) = 旁白（无头像无姓名），见 main.lua 的 Info()
        who = '旁白' if (isinstance(third, str) and third == '' and fourth == 2) else str(rid)
        self._rec(who, text)

    def run(self, name):
        path = os.path.join(LUA_DIR, '%s.lua' % name)
        if not os.path.exists(path):
            raise SystemExit('找不到脚本 %s' % path)
        if not self.quiet:
            OUT.write('\n--- %s.lua ---\n' % name)
        before = len(self.log)
        self.rt.execute(io.open(path, encoding='utf-8').read())
        # 每场景的对白句数（不含【提示】等系统记录），用来守住"一场景 15 句内"
        talked = sum(1 for w, _ in self.log[before:] if not w.startswith('【'))
        prev = self.counts.get(name, 0)
        self.counts[name] = max(prev, talked)
        if not self.quiet:
            OUT.write('（本场 %d 句）\n' % talked)
        return self.log

    def dump_flags(self, title):
        OUT.write('\n== %s ==\n' % title)
        OUT.write('flags: %s\n' % ', '.join('%s=%d' % kv for kv in sorted(self.flags.items())))
        OUT.write('items: %s\n' % (self.items,))


def run_seq(s, spec):
    """按 '557 559 563x3 1001x2' 这种写法顺序跑脚本，xN 表示重复 N 次。"""
    for token in spec.split():
        if 'x' in token:
            name, times = token.split('x')
            times = int(times)
        else:
            name, times = token, 1
        for _ in range(times):
            s.run(name)


def scenario_ch1():
    """第一回《风月无情》四条线。任何一条跑不通都会抛错，flags 不对会断言失败。"""
    OUT.write('\n############ 主线：楔子 → 庙祝 → 坟前三人 → 李莫愁（必败战）→ 求医 → 认亲 → 夜戏 ############\n')
    s = Sim()
    run_seq(s, '557 559 563x3 559 1001x3 1002x3')
    s.dump_flags('主线')
    assert s.flags.get('第一回_楔子') == 1
    assert s.flags.get('第一回_坟地') == 1
    assert s.flags.get('第一回_李莫愁') == 1
    assert s.flags.get('第一回_中毒') == 1
    assert s.flags.get('第一回_解毒') == 1
    assert s.flags.get('第一回_完') == 1
    assert s.flags.get('序章完成') == 1
    # 坟前那场必败之战，且两根针 + 掌上一根 = 3 枚冰魄银针（道具 71，暗器）
    assert s.battles == [203], s.battles
    assert (71, 3) in s.items, s.items
    # 一场景 15 句内
    for name, limit in (('557', 6), ('559', 16), ('563', 16), ('1001', 16), ('1002', 16)):
        assert s.counts.get(name, 0) <= limit, (name, s.counts.get(name))
    for name in ('559', '1001', '1002', '563'):
        s.run(name)
    s.dump_flags('主线·收尾后的重复对话')

    OUT.write('\n############ 支线：跳过坟地，直接认亲 ############\n')
    s = Sim()
    for name in ('557', '559', '1001', '1001', '1002', '1002', '1002'):
        s.run(name)
    s.dump_flags('跳过坟地')
    assert s.flags.get('第一回_中毒') is None
    assert s.flags.get('序章完成') == 1

    OUT.write('\n############ 支线：先挖坟（564）再看碑 ############\n')
    s = Sim()
    run_seq(s, '557 564 563x3 559 559 1001x3 1002x3')
    s.dump_flags('先挖坟')
    assert s.flags.get('第一回_玉镯') == 1
    assert s.flags.get('序章完成') == 1
    # 带玉镯的支线会让 1002 多一句，也不能超过 16
    assert s.counts.get('1002', 0) <= 16, s.counts.get('1002')

    OUT.write('\n############ 支线：拒绝上岛 ############\n')
    s = Sim(yes=False)
    run_seq(s, '557 559 563x3 559 1001x3 1002x3')
    s.dump_flags('拒绝上岛')
    assert s.flags.get('第一回_拒辞') == 1
    assert s.flags.get('序章完成') == 1

    OUT.write('\n############ 回归：拿了铁枪残片（558）回问庙祝，郭靖/黄蓉 不该提前登场 ############\n')
    s = Sim()
    run_seq(s, '557 558 559 559 559')
    s.dump_flags('铁枪残片线')
    assert s.flags.get('父亲遗物') == 1
    assert s.flags.get('第一回_求医') is None
    # 559 的 label3 只在「已被指去佛堂求医」之后才补显两位客人
    early = [t for w, t in s.log
             if w == '【场景】' and '出现' in t and ('郭靖' in t or '黄蓉' in t)]
    assert not early, early

    OUT.write('\n############ 支线：坟前打赢了也一样往下走 ############\n')
    s = Sim(win_battle=True)
    run_seq(s, '557 559 563x3 559 1001x3 1002x3')
    s.dump_flags('坟前打赢')
    assert s.flags.get('第一回_中毒') == 1
    assert (71, 3) in s.items
    assert s.flags.get('序章完成') == 1
    OUT.write('\n全部断言通过。\n')



def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 1
    yes = '--no' not in argv
    for flag in ('--no', '--preset'):
        if flag in argv:
            argv = [a for a in argv if a != flag]
    preset = None
    if 'ch1' in argv:
        preset = argv.pop(argv.index('ch1'))
    OUT = io.open(OUT_PATH, 'w', encoding='utf-8')
    globals()['OUT'] = OUT
    try:
        if preset == 'ch1':
            scenario_ch1()
        else:
            s = Sim(yes=yes)
            for name in argv:
                s.run(name)
            s.dump_flags('顺序执行')
    finally:
        OUT.close()
    print('已写出 %s' % OUT_PATH)
    return 0


if __name__ == '__main__':
    sys.exit(main())
