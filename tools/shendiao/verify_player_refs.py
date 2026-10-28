#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""校验场景里 Player 预制体实例的引用是否全部有效。

检查项
------
    1. PrefabInstance.m_Modifications 的 target fileID 必须存在于 Player.prefab
    2. stripped 文档的 m_CorrespondingSourceObject 必须存在于 Player.prefab
    3. 属性名与目标对象类型要匹配（m_Name -> GameObject，位置/旋转 -> Transform）

用法
----
    python tools/shendiao/verify_player_refs.py
"""
import io
import os
import re
import sys

MOD_PLAYER = "jyx2/Assets/Mods/shendiao/Prefabs/Player.prefab"
MAPS = "jyx2/Assets/Mods/shendiao/Maps/GameMaps"
SCENES = ["00_mochuanlinju", "01_moqiaoshanzhuang", "02_wanzhushuyuan", "1000_daditu"]

MOD_RE = re.compile(
    r"    - target: \{fileID: (-?\d+), guid: ([0-9a-f]+),\s*type: (\d+)\}\r?\n"
    r"      propertyPath: (.*?)\r?\n"
    r"      value: (.*?)\r?\n"
    r"      objectReference: (\{[^}]*\})\r?\n"
)

# propertyPath -> 期望的 YAML class id
EXPECTED_CLASS = {
    "m_Name": "1",
    "m_IsActive": "1",
    "m_TagString": "1",
    "m_Layer": "1",
}


def read(path):
    with io.open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def doc_classes(text):
    """fileID -> class id"""
    return {m.group(2): m.group(1)
            for m in re.finditer(r"(?m)^--- !u!(\d+) &(-?\d+)", text)}


def main():
    prefab = read(MOD_PLAYER)
    guid = re.search(r"guid: ([0-9a-f]+)", read(MOD_PLAYER + ".meta")).group(1)
    cls = doc_classes(prefab)
    ids = set(cls) | set(re.findall(r"fileID: (-?\d+)", prefab))

    print("Player.prefab guid = %s, 文档 %d 个" % (guid, len(cls)))

    bad_total = 0
    for scene in SCENES:
        path = os.path.join(MAPS, scene + ".unity")
        if not os.path.exists(path):
            print("\n== %s 不存在，跳过" % scene)
            continue
        text = read(path)
        print("\n== %s" % scene)

        n_mod = n_bad = 0
        wrong_cls = []
        for block in re.split(r"(?m)^--- !u!", text):
            if not block.startswith("1001 &") or guid not in block:
                continue
            for fid, g, _t, prop, value, _ref in MOD_RE.findall(block):
                if g != guid:
                    continue
                n_mod += 1
                if fid not in ids:
                    n_bad += 1
                    print("   [失效] %s -> fileID %s" % (prop, fid))
                    continue
                want = EXPECTED_CLASS.get(prop)
                if want is None and "." in prop:
                    want = "4"  # m_LocalPosition.x 等 Transform 属性
                if want and cls.get(fid) != want:
                    wrong_cls.append((prop, fid, cls.get(fid), want))
        print("   m_Modifications 指向本 prefab 共 %d 条，失效 %d 条" % (n_mod, n_bad))

        n_src = n_src_bad = 0
        for m in re.finditer(
                r"m_CorrespondingSourceObject: \{fileID: (-?\d+), guid: " + guid + r",", text):
            n_src += 1
            if m.group(1) not in ids:
                n_src_bad += 1
                print("   [失效] m_CorrespondingSourceObject -> fileID %s" % m.group(1))
        print("   m_CorrespondingSourceObject 共 %d 条，失效 %d 条" % (n_src, n_src_bad))

        for prop, fid, got, want in wrong_cls:
            print("   [类型不符] %s -> fileID %s 是 class %s，期望 %s" % (prop, fid, got, want))

        bad_total += n_bad + n_src_bad + len(wrong_cls)

    print("\n结果：%s" % ("全部有效" if bad_total == 0 else "发现 %d 个问题" % bad_total))
    return 0 if bad_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
