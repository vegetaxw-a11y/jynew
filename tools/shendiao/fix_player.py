#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复主角：把 MOD 的 Player.prefab 换成官方 Player.prefab（内嵌 BuildSource 的 Zhujue）。

背景
----
    Assets/Mods/shendiao/Prefabs/Player.prefab 内嵌的是 Taoliuyi.prefab，
    它依赖 Assets/Mods/shendiao/ModelsResource/陶六一/TaoLiuYi.fbx|.mat。
    这个目录没有被纳入 shendiao_mod 这个 AssetBundle，导出后 mesh 丢失，
    SkinnedMeshRenderer 没有网格 -> 主角在游戏里是"空气"（但能走动、能触发剧情）。

    官方 Assets/Prefabs/Player.prefab 内嵌 Assets/BuildSource/ModelCharacters/Player/Zhujue.prefab，
    它的 fbx / mat 都在 base_assets 里（所有 MOD 共享），因此一定可加载。
    官方 JYX2 MOD 的地图（如 08_dalunsi）就是用这个 prefab 当主角。

做法
----
    1. 用官方 Player.prefab 的 YAML 覆盖 MOD 的 Player.prefab 内容，
       但保留 MOD 自己的 .meta（guid 不变，场景引用不需要改）。
    2. 两个 prefab 内部 fileID 不同，场景里 PrefabInstance 的 m_Modifications
       的 target 必须重映射，否则位置/名字等覆盖项会失效（主角会被丢到 (0,0,0)）。
       这里按"文档在文件里的出现顺序"自动配对生成映射表。

用法
----
    python tools/shendiao/fix_player.py --dry
    python tools/shendiao/fix_player.py --apply
"""
import io
import os
import re
import shutil
import sys

MOD_PLAYER = "jyx2/Assets/Mods/shendiao/Prefabs/Player.prefab"
OFFICIAL_PLAYER = "jyx2/Assets/Prefabs/Player.prefab"
MOD_PLAYER_GUID = "3865cb9c075a411d920aee4d5c7d0149"
SCENES = ["00_mochuanlinju", "01_moqiaoshanzhuang", "02_wanzhushuyuan"]
MAPS = "jyx2/Assets/Mods/shendiao/Maps/GameMaps"

DOC_RE = re.compile(r"--- !u!(\d+) &(-?\d+)( stripped)?\r?\n")


def read(path):
    with io.open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


def split_docs(text):
    """-> (header, [(class_id, file_id, stripped, raw_block)])"""
    hits = list(DOC_RE.finditer(text))
    header = text[: hits[0].start()] if hits else text
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        out.append((m.group(1), m.group(2), bool(m.group(3)), text[m.start():end]))
    return header, out


def build_map(old_docs, new_docs):
    """按 (class_id, 是否stripped) 分组、组内按出现顺序配对，生成 fileID 映射"""
    def keyed(docs):
        d = {}
        for cls, fid, stripped, _raw in docs:
            d.setdefault((cls, stripped), []).append(fid)
        return d

    old_k, new_k = keyed(old_docs), keyed(new_docs)
    mapping = {}
    for k, old_ids in old_k.items():
        new_ids = new_k.get(k, [])
        if len(new_ids) != len(old_ids):
            print("  [warn] class %s stripped=%s 数量不同: 旧 %d / 新 %d，按较短的配对"
                  % (k[0], k[1], len(old_ids), len(new_ids)))
        for a, b in zip(old_ids, new_ids):
            mapping[a] = b
    return mapping


MOD_RE = re.compile(
    r"    - target: \{fileID: (-?\d+), guid: " + MOD_PLAYER_GUID + r",\s*type: 3\}\r?\n"
    r"      propertyPath: (.*?)\r?\n"
    r"      value: (.*?)\r?\n"
    r"      objectReference: (\{[^}]*\})\r?\n"
)


def patch_scene(path, mapping, dry):
    """重写场景里 Player 实例的 m_Modifications target fileID

    Unity 写 YAML 时会把 target 行折成两行：
        - target: {fileID: 123, guid: xxx,
            type: 3}
    所以必须用带 \s* 的整条 modification 正则来匹配。
    """
    text = read(path)
    header, docs = split_docs(text)

    changed = dropped = 0
    out = []
    for cls, fid, stripped, raw in docs:
        if cls == "1001" and MOD_PLAYER_GUID in raw:
            def repl(m):
                nonlocal changed, dropped
                old = m.group(1)
                if old not in mapping:
                    dropped += 1
                    return ""
                changed += 1
                return ("    - target: {fileID: %s, guid: %s, type: 3}\n"
                        "      propertyPath: %s\n"
                        "      value: %s\n"
                        "      objectReference: %s\n") % (
                    mapping[old], MOD_PLAYER_GUID,
                    m.group(2), m.group(3), m.group(4))

            raw = MOD_RE.sub(repl, raw)
        out.append(raw)

    result = header + "".join(out)
    if dry:
        print("  [dry] %s: 重映射 %d 条，删掉 %d 条失效 target" % (path, changed, dropped))
    else:
        write(path, result)
        print("  [ok] %s: 重映射 %d 条，删掉 %d 条失效 target" % (path, changed, dropped))
    return changed, dropped


def clean_stripped_mods(path, stripped_ids, dry):
    """删掉指向 stripped（子 prefab 内部）对象的 modification。

    这类 override 很危险：例如 m_IsActive=0 命中子 prefab 的根，会把整只模型关掉。
    场景对 prefab 实例真正需要的覆盖只有 root GameObject（名字）和 root Transform
    （位置/旋转/缩放），其余一律清掉最安全。
    """
    text = read(path)
    header, docs = split_docs(text)

    removed = 0
    out = []
    for cls, fid, stripped, raw in docs:
        if cls == "1001" and MOD_PLAYER_GUID in raw:
            def repl(m):
                nonlocal removed
                if m.group(1) in stripped_ids:
                    removed += 1
                    return ""
                return m.group(0)

            raw = MOD_RE.sub(repl, raw)
        out.append(raw)

    result = header + "".join(out)
    if removed:
        if dry:
            print("  [dry] %s: 清理 %d 条指向子 prefab 的 override" % (path, removed))
        else:
            write(path, result)
            print("  [ok] %s: 清理 %d 条指向子 prefab 的 override" % (path, removed))
    return removed


def main():
    dry = "--apply" not in sys.argv

    old_text = read(MOD_PLAYER)
    new_text = read(OFFICIAL_PLAYER)
    _, old_docs = split_docs(old_text)
    _, new_docs = split_docs(new_text)

    print("== 配对 fileID（旧 MOD Player.prefab -> 官方 Player.prefab）")
    mapping = build_map(old_docs, new_docs)
    for a, b in mapping.items():
        print("   %-20s -> %s" % (a, b))

    if dry:
        print("\n== [dry] 不写文件。加 --apply 落盘。")
    else:
        shutil.copyfile(MOD_PLAYER, MOD_PLAYER + ".bak")
        write(MOD_PLAYER, new_text)
        print("\n[ok] 已用官方 Player.prefab 内容覆盖 %s（旧文件备份为 .bak，.meta 未动）" % MOD_PLAYER)

    # 新 prefab 里所有 stripped 对象（内嵌子 prefab 的节点）都不允许被场景 override
    stripped_ids = set(fid for _c, fid, st, _r in new_docs if st)

    print("\n== 修正场景 Player 实例的 m_Modifications")
    for scene in SCENES:
        path = os.path.join(MAPS, scene + ".unity")
        patch_scene(path, mapping, dry)
        clean_stripped_mods(path, stripped_ids, dry)

    return 0


if __name__ == "__main__":
    sys.exit(main())
