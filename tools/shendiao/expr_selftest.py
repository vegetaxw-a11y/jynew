# -*- coding: utf-8 -*-
"""不开游戏就验证 Lua/expr.lua 的表情路由逻辑（用 lupa 真跑一遍）。

为什么要有它：表情系统靠"改 id + 热更新还原 id"，一旦写错，
在游戏里的表现是"头像空白/玩家跑到左边/旁白多出头像"，很难定位。
这里把 `CS` / `util` / `Talk` 全桩掉，只验证三件事：
  1. 带表情 -> 传的是虚拟 id（9000000 + 角色id*10 + 槽位）
  2. 不带表情 / 没生成图 -> 原样透传真实 id（不会变空白）
  3. 老的四参用法 Talk(id, text, talkName, type)（main.lua 的 Info 就是它）参数不被吞
  4. ChangePosition 补丁把虚拟 id 还原成真实 id，且默认 ShowName 补成 true

用法:
    python tools/shendiao/expr_selftest.py
"""
import os
import sys

LUA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', '..', 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua', 'expr.lua')

STUB = r"""
CALLS = {}
HOTFIX = nil
POS = nil

-- main.lua 里的 Talk 是 util.async_to_sync(luaBridge.Talk)；这里桩一个同步版本，
-- 并且模拟 C# 内部"先 ChangePosition 再加载头像"的顺序（自检逻辑依赖这个顺序）
function Talk(a, b, c, d)
    CALLS[#CALLS + 1] = {a, b, c, d}
    if HOTFIX then HOTFIX(MKSELF(), a) end
end

util = {
    hotfix_ex = function(cs, field, fn)
        assert(field == 'ChangePosition', '补丁目标应只有 ChangePosition，实际 ' .. tostring(field))
        HOTFIX = fn
    end,
}

CS = {
    ChatUIPanel = {
        ChangePosition = function(self, id, showName)
            POS = {id, showName}
        end,
    },
}

function MKSELF() return CS.ChatUIPanel end
"""


def check(tag, want, got):
    ok = want == got
    print('%-42s %s  want=%r got=%r' % (tag, 'OK  ' if ok else 'FAIL', want, got))
    return ok


def main():
    import lupa
    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(STUB)
    src = open(os.path.abspath(LUA), encoding='utf-8').read()
    rt.execute(src)

    ok = True
    g = rt.globals()

    def last():
        """最后一次 Talk 的四个入参（缺的补 None）"""
        t = g.CALLS[len(g.CALLS)]
        return [t[i] for i in (1, 2, 3, 4)]

    def pos():
        t = g.POS
        return [t[1], t[2]]

    # 1) 带表情：玩家 0 -> 9000008（槽位 8 = 悲），这个组合已生成图
    rt.execute('Talk(0, "甲", EXPR.sad)')
    ok &= check('表情路线 Talk(0, ..., EXPR.sad)', [9000008, '甲', None, None], last())
    # 中文键也行（小龙女 22 + 沉思 4 = 9000224，已生成）
    rt.execute('Talk(22, "乙", EXPR["沉思"])')
    ok &= check('中文键 Talk(22, ..., EXPR["沉思"])', [9000224, '乙', None, None], last())

    # 2) 不带表情：原样透传
    rt.execute('Talk(0, "丙")')
    ok &= check('无表情 Talk(0, "丙")', [0, '丙', None, None], last())

    # 2b) 表情合法但没生成图（小龙女 22 没有"怒"的台词/图）-> 退回默认头像
    rt.execute('Talk(22, "丁", EXPR.angry)')
    ok &= check('缺图时回退 Talk(22, ..., EXPR.angry)', [22, '丁', None, None], last())

    # 2c) 槽位 1（平静）等于默认头像，不该走虚拟 id
    rt.execute('Talk(22, "戊", EXPR.calm)')
    ok &= check('平静 Talk(22, ..., EXPR.calm)', [22, '戊', None, None], last())

    # 3) 老的四参用法（main.lua 的 Info -> Talk(0, msg, "", 2)）
    rt.execute('Talk(0, "己", "", 2)')
    ok &= check('四参 Talk(0, msg, "", 2)', [0, '己', '', 2], last())

    # 4) ChangePosition 补丁：虚拟 id -> 真实 id，ShowName 缺省补 true
    rt.execute('HOTFIX(MKSELF(), 9000222)')
    ok &= check('补丁还原 9000222 -> 22 (showName 缺省)', [22, True], pos())
    rt.execute('HOTFIX(MKSELF(), 9000004, false)')
    ok &= check('补丁还原 9000004 -> 0 (showName=false)', [0, False], pos())
    rt.execute('HOTFIX(MKSELF(), 22, true)')
    ok &= check('补丁不动真实 id 22', [22, True], pos())

    print('')
    print('全部通过' if ok else '有失败项')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
