#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重排 MOD 场景里的 NPC：换 prefab、改名字、摆位置。

背景：jyx2mod new 出来的场景是从 SAMPLE 复制的，里面站着的是 SAMPLE 的角色
（莫穿林、四蛇儿…），而且不少实例的 y 坐标停在 0，而场景地面在 y=5，
结果 NPC 全被"埋"在地板下面，看起来像庙里没人。

用法：
    python tools/shendiao/set_npc.py --dry     # 只看会改成什么
    python tools/shendiao/set_npc.py --apply   # 落盘

摆位是幂等的：每次运行都会先清空 Level/NPC 下的所有子物体，再按 LAYOUT 重建。
"""
import io
import math
import os
import re
import sys

MOD = "shendiao"
ROOT = "jyx2/Assets/Mods/%s" % MOD
PREFABS = os.path.join(ROOT, "Prefabs")
MAPS = os.path.join(ROOT, "Maps/GameMaps")
# 共享角色模型池（随游戏本体发布，所有 MOD 都能引用）
SHARED = "jyx2/Assets/BuildSource/ModelCharacters"
NPC_LAYER = 16

# 场景 -> [(显示名, prefab 引用, (x, y, z), yaw 角度)]
# prefab 引用有两种写法：
#   "Guojing"             -> Mods/shendiao/Prefabs/Guojing.prefab
#   "BattleNpc/Guojing"   -> Assets/BuildSource/ModelCharacters/BattleNpc/Guojing.prefab
# 每个角色都用独立 prefab，不做一人多角共用。
# y 必须跟场景地面一致：00 的地面在 5.0，01/02 沿用 SAMPLE 原实例的高度。
LAYOUT = {
    "00_mochuanlinju": [
        ("庙祝", "StoryNpc/Maitanghululaotou", (0.5, 5.0, 2.0), 0),
        ("郭靖", "BattleNpc/Guojing", (-1.8, 5.0, 4.2), 20),
        ("黄蓉", "BattleNpc/Huangrong", (2.6, 5.0, 3.6), 340),
    ],
    "01_moqiaoshanzhuang": [
        ("郭靖", "BattleNpc/Guojing", (26.56, 0.1, 0.42), 0),
        ("赵志敬", "BattleNpc/QuanzhenDizi", (12.8, 0.09, 26.58), 90),
        ("鹿清笃", "BattleNpc/QuanzhenDizi 1", (15.34, 0.06, 9.12), 90),
        ("丘处机", "BattleNpc/Qiuchuji", (15.34, 0.06, 8.13), 90),
    ],
    "02_wanzhushuyuan": [
        ("孙婆婆", "StoryNpc/Laotaitai", (18.88, 0.21, -5.05), 0),
        ("小龙女", "BattleNpc/xiaolongnv", (0.584, 0.24, 10.43), 90),
        ("李莫愁", "BattleNpc/Miejue", (11.2, 0.2, 38.13), 0),
    ],
}


def read(path):
    with io.open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


DOC_RE = re.compile(r"--- !u!(\d+) &(-?\d+)( stripped)?\r?\n")


def split_docs(text):
    """-> (header, [(class_id, file_id, stripped, raw_block)])"""
    hits = list(DOC_RE.finditer(text))
    header = text[:hits[0].start()] if hits else text
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        out.append((m.group(1), m.group(2), bool(m.group(3)), text[m.start():end]))
    return header, out


def load_prefab(ref):
    """读 prefab 的 guid / root Transform / root GameObject / 所有 GameObject id"""
    if "/" in ref:
        path = os.path.join(SHARED, ref.replace("/", os.sep) + ".prefab")
    else:
        path = os.path.join(PREFABS, ref + ".prefab")
    if not os.path.exists(path):
        raise RuntimeError("找不到 prefab: %s" % path)
    guid = re.search(r"guid: ([0-9a-f]{32})", read(path + ".meta")).group(1)
    _, docs = split_docs(read(path))


    root_tf = None
    for cls, fid, stripped, raw in docs:
        if cls == "4" and not stripped and re.search(r"m_Father: \{fileID: 0\}", raw):
            root_tf = fid
            break
    if root_tf is None:
        raise RuntimeError("%s 找不到 root Transform" % ref)

    root_go, go_ids = None, []
    for cls, fid, stripped, raw in docs:
        if cls == "4" and fid == root_tf:
            root_go = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", raw).group(1)
        if cls == "1" and not stripped:
            # 只要 root 子树下的；prefab 里除 root 外都是它的子孙，直接全收
            go_ids.append(fid)
    return {"name": ref, "guid": guid, "root_tf": root_tf,
            "root_go": root_go, "go_ids": go_ids}

def fmt(v):
    """Unity 的浮点写法：去掉多余的 .0，保留有效位"""
    if v == int(v):
        return str(int(v))
    return ("%.6f" % v).rstrip("0").rstrip(".")


def build_npc_blocks(inst_id, tf_id, parent_tf, npc, pf):
    name, pos, yaw = npc
    rad = math.radians(yaw) * 0.5
    qy, qw = math.sin(rad), math.cos(rad)

    mods = [(pf["root_go"], "m_Name", name)]
    for ax, v in zip("xyz", pos):
        mods.append((pf["root_tf"], "m_LocalPosition." + ax, fmt(v)))
    for ax, v in (("x", 0), ("y", qy), ("z", 0), ("w", qw)):
        mods.append((pf["root_tf"], "m_LocalRotation." + ax, fmt(v)))
    for ax in "xyz":
        mods.append((pf["root_tf"], "m_LocalScale." + ax, "1"))
    # 整个 prefab 的所有 GameObject 都要进 NPC 层，否则摄像机 culling mask 直接剔除
    for gid in pf["go_ids"]:
        mods.append((gid, "m_Layer", str(NPC_LAYER)))

    lines = [
        "--- !u!1001 &%s" % inst_id,
        "PrefabInstance:",
        "  m_ObjectHideFlags: 0",
        "  serializedVersion: 2",
        "  m_Modification:",
        "    m_TransformParent: {fileID: %s}" % parent_tf,
        "    m_Modifications:",
    ]
    for target, prop, val in mods:
        lines += [
            "    - target: {fileID: %s, guid: %s, type: 3}" % (target, pf["guid"]),
            "      propertyPath: " + prop,
            "      value: " + val,
            "      objectReference: {fileID: 0}",
        ]
    lines += [
        "    m_RemovedComponents: []",
        "  m_SourcePrefab: {fileID: 100100000, guid: %s, type: 3}" % pf["guid"],
        "--- !u!4 &%s stripped" % tf_id,
        "Transform:",
        "  m_CorrespondingSourceObject: {fileID: %s, guid: %s, type: 3}" % (pf["root_tf"], pf["guid"]),
        "  m_PrefabInstance: {fileID: %s}" % inst_id,
        "  m_PrefabAsset: {fileID: 0}",
    ]
    return "\n".join(lines) + "\n"


def find_npc_transform(docs):
    """Level/NPC 的 Transform id"""
    gn, tf_go, father = {}, {}, {}
    for cls, fid, stripped, raw in docs:
        if cls == "1" and not stripped:
            m = re.search(r"^  m_Name: (.*)$", raw, re.M)
            if m:
                gn[fid] = m.group(1).strip()
        elif cls == "4":
            m = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", raw)
            if m:
                tf_go[fid] = m.group(1)
            m = re.search(r"m_Father: \{fileID: (-?\d+)\}", raw)
            father[fid] = m.group(1) if m else "0"

    for tid, gid in tf_go.items():
        if gn.get(gid) != "NPC":
            continue
        p, hop = father.get(tid, "0"), 0
        while p != "0" and hop < 5:
            if gn.get(tf_go.get(p, ""), "") == "Level":
                return tid
            p, hop = father.get(p, "0"), hop + 1
    raise RuntimeError("找不到 Level/NPC")


def collect_removals(docs, npc_tf):
    """要删掉的文档：NPC 下所有子物体及其组件 / 实例"""
    by_id = {}
    for cls, fid, stripped, raw in docs:
        by_id[(cls, fid)] = raw

    npc_raw = by_id[("4", npc_tf)]
    # m_Children 在 m_Father 之前
    kids = re.findall(r"- \{fileID: (-?\d+)\}", npc_raw.split("m_Father")[0])

    drop = set()
    for kid in kids:
        raw = by_id.get(("4", kid), "")
        if not raw:
            continue
        inst = re.search(r"m_PrefabInstance: \{fileID: (-?\d+)\}", raw)
        if inst and inst.group(1) != "0":
            drop.add(("4", kid))
            drop.add(("1001", inst.group(1)))
            continue
        # 普通 GameObject：自己 + 组件 + 子孙
        gid = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", raw)
        stack = [kid]
        while stack:
            cur = stack.pop()
            if ("4", cur) in drop:
                continue
            drop.add(("4", cur))
            craw = by_id.get(("4", cur), "")
            for sub in re.findall(r"- \{fileID: (-?\d+)\}", craw.split("m_Father")[0]):
                stack.append(sub)
        if gid:
            drop.add(("1", gid.group(1)))
            for (cls, fid), r in by_id.items():
                if re.search(r"m_GameObject: \{fileID: %s\}" % gid.group(1), r):
                    drop.add((cls, fid))
    return drop, kids


def replace_children(raw, kids, eol="\n"):
    """把 Transform 的 m_Children 换成给定列表"""
    lines = raw.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("m_Children:"):
            out.append("  m_Children:" if kids else "  m_Children: []")
            for k in kids:
                out.append("  - {fileID: %s}" % k)
            i += 1
            while i < len(lines) and lines[i].strip().startswith("- {fileID:"):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return ("\n".join(out)).replace("\n", eol)


def rebuild_scene(scene, npcs, dry):
    path = os.path.join(MAPS, scene + ".unity")
    text = read(path)
    eol = "\r\n" if "\r\n" in text else "\n"
    header, docs = split_docs(text)
    npc_tf = find_npc_transform(docs)
    drop, old_kids = collect_removals(docs, npc_tf)

    # 被删实例的 stripped GameObject / 其它组件也要一起删
    inst_ids = [fid for (cls, fid) in drop if cls == "1001"]
    for cls, fid, _s, raw in docs:
        if any(re.search(r"m_PrefabInstance: \{fileID: %s\}" % i, raw) for i in inst_ids):
            drop.add((cls, fid))

    used = [int(fid) for _c, fid, _s, _r in docs if fid.lstrip("-").isdigit()]
    next_id = max(used) + 1

    new_blocks, new_kids = [], []
    for name, ref, pos, yaw in npcs:
        pf = load_prefab(ref)
        inst, tf = str(next_id), str(next_id + 1)
        next_id += 2
        new_blocks.append(build_npc_blocks(inst, tf, npc_tf, (name, pos, yaw), pf).replace("\n", eol))
        new_kids.append(tf)
        print("  + %-6s %-32s pos=%-22s yaw=%s  (%d 个 GameObject 进 NPC 层)"
              % (name, ref, pos, yaw, len(pf["go_ids"])))
    print("  - 清掉 %d 个旧实例（%d 条子物体）" % (len(inst_ids), len(old_kids)))

    out = []
    for cls, fid, _s, raw in docs:
        if (cls, fid) in drop:
            continue
        if cls == "4" and fid == npc_tf:
            raw = replace_children(raw, new_kids, eol)
        out.append(raw)
    result = header + "".join(out) + "".join(new_blocks)

    if dry:
        print("  [dry] %s 会重写（%d -> %d 字节）" % (scene, len(text), len(result)))
    else:
        write(path, result)
        print("  [ok] 已写入 %s" % scene)


def main():
    dry = "--apply" not in sys.argv
    for scene, npcs in LAYOUT.items():
        print("== %s" % scene)
        rebuild_scene(scene, npcs, dry)


if __name__ == "__main__":
    main()

