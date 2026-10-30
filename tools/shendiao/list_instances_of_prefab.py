# -*- coding: utf-8 -*-
"""按源 prefab 查场景实例：名字 / 局部坐标 / 朝向(yaw) / 缩放。

场景里的 prefab 实例只留 stripped 子块，真正的位置朝向都在 PrefabInstance 的
m_Modifications 覆盖里。摆 NPC 时最常问的两个问题——
「原版场景里这个人站在多高」「原版给他多少度」——用这个脚本对着原版地图取基准，
比自己猜地面高度靠谱。

用法:
    python tools/shendiao/list_instances_of_prefab.py <scene.unity> --guid e258f6bf50035b54888fd864fd4996c5
    python tools/shendiao/list_instances_of_prefab.py <scene.unity> --name Guojing
    python tools/shendiao/list_instances_of_prefab.py <scene.unity> --guid <g> --all-scenes
--all-scenes 会扫描整个 Assets 下所有 .unity（慢，但一次就能找出"原版都把这个
prefab 摆在哪、多高"）。
"""
import io
import math
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(REPO, 'jyx2', 'Assets')

INST_RE = re.compile(r'^--- !u!1001 &(-?\d+)\nPrefabInstance:\n(.*?)(?=^--- |\Z)', re.S | re.M)
SRC_RE = re.compile(r'm_SourcePrefab: \{fileID: 100100000, guid: ([0-9a-f]{32})')
MOD_RE = re.compile(r'propertyPath: (\S+)\n      value: (.*)')


def yaw_from_quat(qy, qw):
    return round(math.degrees(2.0 * math.atan2(qy, qw)), 1)


def scan(scene, guids):
    text = io.open(scene, encoding='utf-8', errors='replace').read()
    rows = []
    for m in INST_RE.finditer(text):
        body = m.group(2)
        s = SRC_RE.search(body)
        if not s or s.group(1) not in guids:
            continue
        d = dict(MOD_RE.findall(body))
        try:
            qy, qw = float(d.get('m_LocalRotation.y', 0)), float(d.get('m_LocalRotation.w', 1))
        except ValueError:
            qy, qw = 0.0, 1.0
        rows.append({
            'scene': os.path.relpath(scene, REPO),
            'inst': m.group(1),
            'guid': s.group(1),
            'name': d.get('m_Name', '<无>').strip('"'),
            'pos': (d.get('m_LocalPosition.x', '?'), d.get('m_LocalPosition.y', '?'),
                    d.get('m_LocalPosition.z', '?')),
            'yaw': yaw_from_quat(qy, qw),
            'scale': d.get('m_LocalScale.x', '1'),
        })
    return rows


def main():
    argv = sys.argv[1:]
    if not argv:
        sys.stderr.write(__doc__.strip() + '\n')
        raise SystemExit(2)

    def opt(k, d=None):
        return argv[argv.index('--' + k) + 1] if '--' + k in argv else d

    guids = set()
    if opt('guid'):
        guids.add(opt('guid'))
    name = opt('name')

    if '--all-scenes' in argv:
        scenes = []
        for d, _, fs in os.walk(ASSETS):
            for f in fs:
                if f.endswith('.unity'):
                    scenes.append(os.path.join(d, f))
    else:
        scenes = [argv[0]]

    rows = []
    for sc in scenes:
        rows.extend(scan(sc, guids))

    if name:
        rows = [r for r in rows if name.lower() in r['name'].lower()]

    print('%d 个实例' % len(rows))
    print('%-46s %-12s %-30s %-8s %s'
          % ('场景', '名字', '(x, y, z)', 'yaw', 'scale'))
    print('-' * 110)
    for r in rows:
        print('%-46s %-12s %-30s %-8s %s'
              % (r['scene'][-44:], r['name'], '(%s, %s, %s)' % r['pos'], r['yaw'], r['scale']))


if __name__ == '__main__':
    main()
