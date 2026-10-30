# -*- coding: utf-8 -*-
"""第一回补人：给 武三通 / 洪凌波 建模型资源，并把三人摆进 62_pomiao.unity。

为什么要一个驱动脚本：中文名字经 PowerShell -> python.exe 的 argv 会被 cp936 破坏，
写进 .asset / 场景就是乱码。这里把 sys.argv 在进程内拼好，绕开命令行。

用法:
    python tools/shendiao/add_ch1_extra.py            # dry-run（只做模型，不写场景）
    python tools/shendiao/add_ch1_extra.py --apply    # 全部写盘

做两件事：
  ① Models/武三通.asset  ← StoryNpc/Zhuangjiahan（庄稼汉：一灯门下"农夫"的形貌）
     Models/洪凌波.asset  ← BattleNpc/Chenglingsu（素净女弟子）
  ② 场景 Level/NPC 下摆三个实例（默认坐标见 NPCS，依据 Tomb/fenbao 与三人的站位）
     柯镇恶 用的是已经存在的 Models/柯镇恶.asset（Xiexun.prefab），只需摆进场景。

注意：这些 prefab 在 Assets/BuildSource/ModelCharacters 里，属于 base_assets，
导出 MOD 要带 base：jyx2mod.py unity shendiao --with-base --force
"""
import importlib.util
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SCENE = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps',
                     '62_pomiao.unity')
BATTLENPC = os.path.join(REPO, 'jyx2', 'Assets', 'BuildSource', 'ModelCharacters',
                         'BattleNpc')
STORYNPC = os.path.join(REPO, 'jyx2', 'Assets', 'BuildSource', 'ModelCharacters',
                        'StoryNpc')

# (人物名, 模型资源引用的 prefab，相对 BuildSource/ModelCharacters)
MODELS = [
    (u'武三通', 'StoryNpc/Zhuangjiahan'),
    (u'洪凌波', 'BattleNpc/Chenglingsu'),
]

# (实例名, prefab 绝对路径, x, y, z, rot-y)
# 地面高度由 Tomb(4.95) / fenbao(5.14) 推定 y=5；坟前三人已在 (-3.8..-2.7, -12.2..-13.5)
NPCS = [
    (u'武三通', os.path.join(STORYNPC, 'Zhuangjiahan.prefab'), 1.7, 5, -15.3, 195),
    (u'洪凌波', os.path.join(BATTLENPC, 'Chenglingsu.prefab'), -4.7, 5, -11.3, 165),
    (u'柯镇恶', os.path.join(BATTLENPC, 'Xiexun.prefab'), -1.5, 5, -16.8, 15),
]


def load(name):
    path = os.path.join(REPO, 'tools', 'shendiao', name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    apply_ = '--apply' in sys.argv
    model_tool = load('add_model')
    prefab_tool = load('add_prefab')

    print('=== ① 模型资源 ===')
    for name, ref in MODELS:
        argv = ['add_model.py', name, ref]
        if apply_:
            argv.append('--force')
        saved = sys.argv
        sys.argv = argv
        try:
            model_tool.main()
        finally:
            sys.argv = saved

    print('')
    print('=== ② 场景实例 ===')
    for name, prefab, x, y, z, roty in NPCS:
        argv = ['add_prefab.py', '--scene', SCENE, '--prefab', prefab,
                '--parent', 'NPC', '--name', name,
                '--pos', '%g,%g,%g' % (x, y, z), '--rot-y', '%g' % roty]
        if apply_:
            argv.append('--apply')
        print('---- %s ----' % name)
        saved = sys.argv
        sys.argv = argv
        try:
            prefab_tool.main()
        finally:
            sys.argv = saved


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
