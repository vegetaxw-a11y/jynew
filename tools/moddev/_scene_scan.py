"""一次性工具：扫描 MOD 场景里的交互事件点 / NPC / 传送点，用于剧情编排。

用法：python tools/moddev/_scene_scan.py <MOD_ID> [场景名...]
"""
from __future__ import annotations

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODS_DIR = os.path.join(ROOT, "jyx2", "Assets", "Mods")


def script_guids():
    """把 Assets 下所有 .cs.meta 的 guid 映射成文件名，用来识别 MonoBehaviour 类型"""
    result = {}
    assets = os.path.join(ROOT, "jyx2", "Assets")
    for dirpath, _dirs, files in os.walk(assets):
        for name in files:
            if name.endswith(".cs.meta"):
                text = io.open(os.path.join(dirpath, name), encoding="utf-8", errors="replace").read()
                m = re.search(r"^guid: ([0-9a-fA-F]{32})", text, re.M)
                if m:
                    result[m.group(1)] = name[:-8]
    return result


def parse_docs(text):
    docs = {}
    for m in re.finditer(r"^--- !u!(\d+) &(-?\d+).*?\n(.*?)(?=^--- |\Z)", text, re.M | re.S):
        docs.setdefault(m.group(1), {})[m.group(2)] = m.group(3)
    return docs


def decode_name(raw):
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    return raw.encode().decode("unicode_escape") if "\\u" in raw else raw


def scan(path, guids):
    text = io.open(path, encoding="utf-8", errors="replace").read()
    docs = parse_docs(text)

    go_name = {}
    for gid, body in docs.get("1", {}).items():
        m = re.search(r"^  m_Name: (.*)$", body, re.M)
        go_name[gid] = decode_name(m.group(1)) if m else "?"

    tf_go, tf_father, go_tf = {}, {}, {}
    for tid, body in docs.get("4", {}).items():
        m = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", body)
        if m:
            tf_go[tid] = m.group(1)
            go_tf[m.group(1)] = tid
        m = re.search(r"m_Father: \{fileID: (-?\d+)\}", body)
        tf_father[tid] = m.group(1) if m else "0"

    def path_of(go_id):
        tf = go_tf.get(go_id)
        parts = []
        while tf and tf != "0":
            gid = tf_go.get(tf)
            if gid:
                parts.append(go_name.get(gid, "?"))
            tf = tf_father.get(tf, "0")
        return "/".join(reversed(parts))

    events, npcs = [], []
    for _mid, body in docs.get("114", {}).items():
        m = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", body)
        if not m:
            continue
        go_id = m.group(1)
        sm = re.search(r"m_Script: \{fileID: \d+, guid: ([0-9a-fA-F]{32})", body)
        kind = guids.get(sm.group(1), sm.group(1)[:8]) if sm else "?"
        p = path_of(go_id)
        if kind == "GameEvent":
            def gv(key):
                mm = re.search(r"^  %s: (\S+)$" % key, body, re.M)
                return mm.group(1) if mm else "?"
            events.append((p, gv("m_InteractiveEventId"), gv("m_EnterEventId"), gv("m_UseItemEventId")))
        elif kind == "MapTeleportor":
            tm = re.search(r"^  TransportTriggerName: (.*)$", body, re.M)
            events.append((p, "TELEPORT->" + (decode_name(tm.group(1)) if tm else ""), "-", "-"))
        elif kind == "MapChest":
            events.append((p, "CHEST", "-", "-"))

    # NPC 通常是 PrefabInstance 实例，它在场景里的子物体是 stripped 文档、没有
    # m_Name，靠遍历 m_Name 会全部漏掉。改成顺着 Level/NPC 的 m_Children 找，
    # 拿不到名字就回落到 prefab 资源名。
    npc_tf = None
    for tid, body in docs.get("4", {}).items():
        gid = tf_go.get(tid)
        if gid and go_name.get(gid) == "NPC" and path_of(gid).endswith("Level/NPC"):
            npc_tf = tid
            break

    def prefab_name_of(go_id: str) -> str:
        body = docs.get("1", {}).get(go_id, "")
        m = re.search(r"m_PrefabInstance: \{fileID: (-?\d+)\}", body)
        if not m:
            return "?"
        inst = docs.get("1001", {}).get(m.group(1), "")
        m = re.search(r"m_SourcePrefab: .*guid: ([0-9a-fA-F]{32})", inst)
        return "prefab:" + (m.group(1)[:8] if m else "?")

    def prefab_of_transform(tid: str) -> str:
        """stripped Transform 没有 m_GameObject 字段，只能顺着 PrefabInstance 找源资源"""
        body = docs.get("4", {}).get(tid, "")
        m = re.search(r"m_PrefabInstance: \{fileID: (-?\d+)\}", body)
        if not m:
            return "?"
        inst = docs.get("1001", {}).get(m.group(1), "")
        m = re.search(r"m_SourcePrefab: .*guid: ([0-9a-fA-F]{32})", inst)
        return "prefab:" + (m.group(1)[:8] if m else "?")

    if npc_tf:
        children = re.findall(r"- \{fileID: (-?\d+)\}", docs["4"][npc_tf].split("m_Father")[0])
        for child in children:
            gid = tf_go.get(child)
            name = go_name.get(gid) if gid else None
            npcs.append(name if name and name != "?" else prefab_of_transform(child))

    return events, npcs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    mod_id = sys.argv[1]
    maps_dir = os.path.join(MODS_DIR, mod_id, "Maps", "GameMaps")
    guids = script_guids()
    wanted = sys.argv[2:]
    for name in sorted(os.listdir(maps_dir)):
        if not name.endswith(".unity"):
            continue
        scene = name[:-6]
        if wanted and scene not in wanted:
            continue
        events, npcs = scan(os.path.join(maps_dir, name), guids)
        print(f"\n=== {scene} ===")
        print("  NPC:", ", ".join(sorted(set(n.split('/')[-1] for n in npcs))) or "-")
        for p, i, e, u in events:
            print(f"  事件 {p:<45} 交互={i:<8} 进入={e:<6} 用物={u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
