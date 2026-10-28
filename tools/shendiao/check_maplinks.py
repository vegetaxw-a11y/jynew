# -*- coding: utf-8 -*-
"""校验 场景.xlsx -> MapConfig.lua 与各场景 Level/Triggers 的传送链路是否闭合。

检查项：
  1) 每个地图配置的 MapScene 是否有对应 .unity
  2) 场景内是否真的有 Level/Triggers/<Leave 之类> 触发器
  3) TransportToMap 指向大地图(1000)时，大地图里是否存在与「地图 Name」同名的触发器
     （LevelMaster 用 para.triggerName = curMap.Name 来找落点）
  4) 大地图里的每个触发器，是否都能对上一个地图 Name（避免死触发器）

用法：python tools/shendiao/check_maplinks.py
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inspect_worldmap import Scene, load_scene  # noqa: E402

ROW = re.compile(r'^\{(?P<id>-?\d+),\[\[(?P<name>.*?)\]\],\[\[(?P<scene>.*?)\]\],\[\[(?P<trans>.*?)\]\],')


def parse_maps(path):
    maps = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            m = ROW.match(line.strip())
            if m:
                maps.append(m.groupdict())
    return maps


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    mod = os.path.join(root, 'jyx2', 'Assets', 'Mods', 'shendiao')
    maps = parse_maps(os.path.join(mod, 'Configs', 'Lua', 'MapConfig.lua'))
    scene_dir = os.path.join(mod, 'Maps', 'GameMaps')

    triggers = {}
    for mp in maps:
        p = os.path.join(scene_dir, mp['scene'] + '.unity')
        if not os.path.exists(p):
            triggers[int(mp['id'])] = None
            continue
        sc = Scene(p, load_scene(p))
        node = sc.find_tr_by_name('Triggers')
        triggers[int(mp['id'])] = [sc.tr_name(c) for c in sc.children_of(node)] if node else None

    by_name = {}
    for mp in maps:
        by_name[mp['name']] = mp

    problems = []
    print('%-6s %-16s %-22s %-22s %s' % ('id', 'Name', '场景', 'TransportToMap', '检测'))
    print('-' * 110)
    for mp in maps:
        mid = int(mp['id'])
        trs = triggers[mid]
        notes = []
        if trs is None:
            notes.append('缺少场景文件或 Level/Triggers')
            problems.append('%s: 场景/Triggers 缺失' % mp['name'])
        else:
            targets = [t for t in mp['trans'].split(',') if t and ':' in t]
            for t in targets:
                tname, tid = t.split(':', 1)
                if tname not in trs:
                    notes.append('缺少触发器 %s' % tname)
                    problems.append('%s: 找不到触发器 %s' % (mp['name'], tname))
            if '1000' in [t.split(':', 1)[1] for t in targets] and '1000' != str(mid):
                if mp['name'] not in (triggers.get(1000) or []):
                    notes.append('大地图无同名落点')
                    problems.append('%s: 大地图缺少同名触发器「%s」' % (mp['name'], mp['name']))
        print('%-6s %-16s %-22s %-22s %s' % (mid, mp['name'], mp['scene'], mp['trans'],
                                             '; '.join(notes) if notes else 'OK'))

    print('')
    print('== 大地图触发器反向核对（%d 个）' % len(triggers.get(1000) or []))
    for t in triggers.get(1000) or []:
        mp = by_name.get(t)
        if mp is None:
            print('   [X] %-18s 没有任何地图配置用这个名字（死触发器）' % t)
            problems.append('大地图死触发器: %s' % t)
        elif '1000' not in mp['trans']:
            print('   [!] %-18s 对应地图 %s 的 TransportToMap 未指回大地图' % (t, mp['scene']))
        else:
            print('   [OK] %-18s -> %s' % (t, mp['scene']))

    print('')
    print('== 结论：%s' % ('全部闭合' if not problems else '%d 处问题' % len(problems)))
    for p in problems:
        print('   - ' + p)


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    main()
