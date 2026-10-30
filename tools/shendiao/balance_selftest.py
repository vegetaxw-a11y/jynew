# -*- coding: utf-8 -*-
"""balance.lua 数值自测：用 lupa 加载 MOD 的平衡层，模拟 1v1 互砍，输出回合数。

为什么要有这个：平衡改动的验收标准是「常见战斗 5~8 回合结束、不被秒杀」，
靠肉眼进游戏试太慢，这里把 AdjustDamage 单独跑一遍就能看出曲线。

用法:
    python tools/shendiao/balance_selftest.py
"""
import io
import os
import sys

import lupa

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BALANCE = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua', 'balance.lua')

# 配表真值（Mods/shendiao/Configs/Lua/CharacterConfig.lua）
# 字段顺序: Id 性别 Level MaxHp MaxMp Attack Defence HpInc MpInc
ROLES = {
    '杨过':   dict(Id=0,  Level=13, MaxHp=300, MaxMp=110, Attack=74, Defence=60, HpInc=3, MpInc=3),
    '郭芙':   dict(Id=41, Level=14, MaxHp=230, MaxMp=290, Attack=77, Defence=60, HpInc=3, MpInc=3),
    '欧阳锋': dict(Id=40, Level=31, MaxHp=885, MaxMp=900, Attack=79, Defence=70, HpInc=3, MpInc=3),
    '武敦儒': dict(Id=42, Level=10, MaxHp=180, MaxMp=80,  Attack=58, Defence=40, HpInc=3, MpInc=3),
    '野狼':   dict(Id=140, Level=5, MaxHp=90,  MaxMp=20,  Attack=40, Defence=20, HpInc=2, MpInc=2),
}

# 原引擎公式的简化版（DamagеCaculator.lua:171-220），只用来产出"原始伤害"
def raw_damage(a, b):
    attack = (a['Attack'] * 3 + 10) // 2
    defence = b['Defence']
    v = (attack - defence * 3) * 2 // 3
    if v <= 0:
        v = attack // 10
    if v <= 0:
        return 0
    return v + 10 // 15


def load_balance():
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    with io.open(BALANCE, encoding='utf-8') as f:
        src = f.read()
    lua.execute(src)
    mod = lua.globals().SHENDIAO_BALANCE
    if mod is None:
        raise SystemExit('balance.lua 没有导出 SHENDIAO_BALANCE')
    return lua, mod


def make_role(lua, name):
    t = lua.table()
    for k, v in ROLES[name].items():
        t[k] = v
    t['Name'] = name
    t['Hp'] = ROLES[name]['MaxHp']
    return t


def duel(lua, mod, name_a, name_b, max_rounds=60):
    a = make_role(lua, name_a)
    b = make_role(lua, name_b)
    rounds = 0
    while a['Hp'] > 0 and b['Hp'] > 0 and rounds < max_rounds:
        rounds += 1
        d1 = mod.AdjustDamage(a, b, raw_damage(ROLES[name_a], ROLES[name_b]))
        b['Hp'] = b['Hp'] - d1
        if b['Hp'] <= 0:
            return rounds, name_a, d1
        d2 = mod.AdjustDamage(b, a, raw_damage(ROLES[name_b], ROLES[name_a]))
        a['Hp'] = a['Hp'] - d2
    winner = name_a if b['Hp'] <= 0 else (name_b if a['Hp'] <= 0 else '超时')
    return rounds, winner, 0


def main():
    lua, mod = load_balance()
    cases = [
        ('杨过', '野狼'),
        ('杨过', '武敦儒'),
        ('杨过', '郭芙'),
        ('杨过', '欧阳锋'),
    ]
    print('%-6s vs %-6s  %-16s %s' % ('我方', '敌方', '结果', '回合数'))
    print('-' * 52)
    bad = 0
    for a, b in cases:
        rounds, winner, _ = duel(lua, mod, a, b)
        flag = ''
        if rounds > 12:
            flag = '  <-- 偏拖沓'
            bad += 1
        print('%-6s vs %-6s  %-16s %d%s' % (a, b, winner, rounds, flag))

    print()
    # 血量地板：13 级却只有 40 血的杨过应被补到 184
    t = lua.table()
    t['Name'] = '残血杨过'
    t['Level'] = 13
    t['MaxHp'] = 40
    t['Hp'] = 40
    t['MaxMp'] = 10
    t['Mp'] = 10
    t['HpInc'] = 3
    t['MpInc'] = 3
    mod.FixStats(t)
    print('FixStats: MaxHp %d / Hp %d / MaxMp %d / Mp %d' % (t['MaxHp'], t['Hp'], t['MaxMp'], t['Mp']))
    ok1 = t['MaxHp'] == 40 + 12 * 6 and t['Hp'] == t['MaxHp'] and t['MaxMp'] == 20 + 12 * 3
    # 配表本来就够的角色不应被改
    t2 = make_role(lua, '杨过')
    before = t2['MaxHp']
    mod.FixStats(t2)
    ok2 = t2['MaxHp'] == before
    print('FixStats 只补不降: %s' % ('OK' if ok2 else 'FAIL'))
    print('FixStats 地板生效: %s' % ('OK' if ok1 else 'FAIL'))
    if not (ok1 and ok2) or bad:
        raise SystemExit('FAILED')


if __name__ == '__main__':
    main()
