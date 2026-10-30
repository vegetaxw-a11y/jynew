# -*- coding: utf-8 -*-
"""把"一张图"的 Canvas 实例（Prefabs/CgTaohuadao.prefab）摆进 62_pomiao.unity。

路径约定：实例挂在 Level 下、名字叫 去桃花岛，所以 Lua 里就是
    ShowSceneNpc("去桃花岛", true)      -- GameObject.Find("Level/去桃花岛")
图片本身是 BuildSource/cg/taohuadao.png（tools/shendiao/gen_scene_pic.py 生成）。

用法:
    python tools/shendiao/add_cg_node.py            # dry-run
    python tools/shendiao/add_cg_node.py --apply
"""
import importlib.util
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SCENE = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps',
                     '62_pomiao.unity')
PREFAB = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Prefabs',
                      'CgTaohuadao.prefab')


def load(name):
    path = os.path.join(REPO, 'tools', 'shendiao', name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    apply_ = '--apply' in sys.argv
    tool = load('add_prefab')
    argv = ['add_prefab.py', '--scene', SCENE, '--prefab', PREFAB,
            '--parent', 'Level', '--name', u'去桃花岛', '--pos', '0,0,0', '--rot-y', '0']
    if apply_:
        argv.append('--apply')
    saved = sys.argv
    sys.argv = argv
    try:
        tool.main()
    finally:
        sys.argv = saved


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
