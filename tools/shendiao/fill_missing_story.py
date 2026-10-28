# -*- coding: utf-8 -*-
"""为场景里已挂 GameEvent 但没有对应 Lua 脚本的事件，生成「占位」剧情。

为什么必须补：`LuaManager.LoadLua` 返回 null 时，`LuaExecutor.Execute` 虽然已经
加了 null 检查、不会把全局事件锁焊死，但**这一个**滑块点下去毫无反应 ——
玩家只会觉得「游戏坏了」。补一个占位脚本即可让反馈恢复正常。
（详见 docs/jyx2-mod-guide.md 的「事件流水线」一节。）

用法:
    python tools/shendiao/fill_missing_story.py            # dry-run，只列清单
    python tools/shendiao/fill_missing_story.py --apply    # 真正写文件
    python tools/shendiao/fill_missing_story.py --apply --text "（此处暂无可叙之事。）"
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao')
LUA = os.path.join(MOD, 'Lua')
MAP = os.path.join(MOD, 'Maps', 'GameMaps')

TEMPLATE = '''Talk(0, "{}")
do return end;
'''


def main():
    argv = sys.argv[1:]
    apply = '--apply' in argv
    text = '（此处暂无可叙之事。）'
    if '--text' in argv:
        text = argv[argv.index('--text') + 1]

    have = {f[:-4] for f in os.listdir(LUA) if f.endswith('.lua')}
    created = 0
    for fn in sorted(os.listdir(MAP)):
        if not fn.endswith('.unity'):
            continue
        scene = io.open(os.path.join(MAP, fn), encoding='utf-8', errors='surrogateescape').read()
        ids = set(re.findall(r'm_(?:Interactive|UseItem|Enter)EventId: (-?\d+)', scene)) - {'-1'}
        lost = sorted(ids - have, key=int)
        if not lost:
            continue
        print('%s -> %s' % (fn, ', '.join(lost)))
        for eid in lost:
            path = os.path.join(LUA, '%s.lua' % eid)
            if apply:
                io.open(path, 'w', encoding='utf-8', newline='').write(TEMPLATE.format(text))
                created += 1
            have.add(eid)

    print()
    if apply:
        print('新建 %d 个占位脚本' % created)
    else:
        print('（dry-run，未写文件；加 --apply 生效）')


if __name__ == '__main__':
    main()
