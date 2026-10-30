# -*- coding: utf-8 -*-
"""往 62_pomiao.unity 的 Level/NPC 下加坟前那三个模型（李莫愁 / 程英 / 陆无双）。

为什么不直接命令行调 add_prefab.py：中文名字经 PowerShell -> python.exe 的 argv
会被 cp936 破坏，写进场景就成了乱码。这里把 sys.argv 在进程内拼好，绕开命令行。

用法:
    python tools/shendiao/add_grave_npcs.py            # dry-run，只打印
    python tools/shendiao/add_grave_npcs.py --apply    # 写盘

注意：这三个 prefab 在 Assets/BuildSource/ModelCharacters 里，属于 base_assets，
导出 MOD 时要带 base（jyx2mod.py unity shendiao --with-base --force）。
"""
import importlib.util
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SCENE = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps', '62_pomiao.unity')
BATTLENPC = os.path.join(REPO, 'jyx2', 'Assets', 'BuildSource', 'ModelCharacters', 'BattleNpc')

NPCS = [
    # (名字, prefab, x, y, z, rot-y)  坐标依据：Tomb (1.21, 4.95, -13.41) / mubei (-1.86, 6.03, -13.18)
    (u'李莫愁', 'Miejue.prefab', -3.8, 5, -12.2, 150),
    (u'程英', 'Chengying.prefab', -5.0, 5, -12.9, 100),
    (u'陆无双', 'Azi.prefab', -2.7, 5, -13.5, 190),
]


def load_tool():
    path = os.path.join(REPO, 'tools', 'shendiao', 'add_prefab.py')
    spec = importlib.util.spec_from_file_location('add_prefab', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    apply = '--apply' in sys.argv
    tool = load_tool()
    for name, prefab, x, y, z, roty in NPCS:
        sys.argv = [
            'add_prefab.py',
            '--scene', SCENE,
            '--prefab', os.path.join(BATTLENPC, prefab),
            '--parent', 'NPC',
            '--name', name,
            '--pos', '%g,%g,%g' % (x, y, z),
            '--rot-y', '%g' % roty,
        ]
        if apply:
            sys.argv.append('--apply')
        print('==== %s ====' % name)
        tool.main()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
