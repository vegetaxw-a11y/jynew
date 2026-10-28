import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "..", "..", "jyx2")
SC = os.path.join(BASE, "Assets", "Mods", "shendiao", "Maps", "GameMaps", "00_mochuanlinju.unity")

# 常见 Unity 类 id -> 名字
CLS = {
    "1": "GameObject",
    "4": "Transform",
    "114": "MonoBehaviour",
    "135": "SphereCollider",
    "136": "CapsuleCollider",
    "65": "BoxCollider",
    "64": "MeshCollider",
    "54": "Rigidbody",
    "108": "Light",
    "20": "Camera",
    "33": "MeshFilter",
    "23": "MeshRenderer",
    "137": "SkinnedMeshRenderer",
    "1001": "PrefabInstance",
    "195": "NavMeshAgent",
}


def read(p):
    with io.open(p, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


text = read(SC)
docs = {}
for d in re.split(r"(?m)^--- !u!", text):
    head = d.split("\n", 1)[0].strip()
    m = re.match(r"^(\d+) &(-?\d+)", head)
    if m:
        docs[m.group(2)] = (m.group(1), d)


def name_of(fid):
    if fid not in docs:
        return "<missing %s>" % fid
    cls, d = docs[fid]
    if cls == "1":
        nm = re.search(r"(?m)^  m_Name: (.*)$", d)
        return nm.group(1).strip() if nm else "?"
    if cls == "114":
        g = re.search(r"m_Script: \{fileID: \d+, guid: ([0-9a-f]+)", d)
        return "MonoBehaviour(guid=%s)" % (g.group(1) if g else "?")
    return CLS.get(cls, "class" + cls)


# 找 Leave 的 GameObject
leave_go = None
for fid, (cls, d) in docs.items():
    if cls == "1" and re.search(r"(?m)^  m_Name: Leave\s*$", d):
        leave_go = fid
        comps = re.findall(r"component: \{fileID: (-?\d+)\}", d)
        pos = re.search(r"(?m)^  m_TagString: (.*)$", d)
        print("=== Leave GameObject fileID=%s tag=%s" % (leave_go, pos.group(1) if pos else "?"))
        for c in comps:
            print("    component %-14s -> %s" % (c, name_of(c)))
        for c in comps:
            if docs.get(c, ("", ""))[0] == "114":
                print("    --- 114 详细 (%s) ---" % c)
                for line in docs[c][1].splitlines():
                    if "m_Script" in line or "Name" in line or "Command" in line or "Text" in line:
                        print("      ", line.strip())
        break

# Player 与 Level 层级
print("\n=== 检查 Level/Player")
for fid, (cls, d) in docs.items():
    if cls == "1001":
        if re.search(r"propertyPath: m_Name\s*\n\s*value: Player\s*$", d, re.M):
            par = re.search(r"m_TransformParent: \{fileID: (-?\d+)\}", d)
            print("  Player PrefabInstance fileID=%s  m_TransformParent=%s" % (fid, par.group(1) if par else "?"))
            pv = re.search(r"m_TransformParent: \{fileID: (-?\d+)\}", d)
            if pv:
                pfid = pv.group(1)
                if pfid in docs:
                    c2, d2 = docs[pfid]
                    go = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", d2)
                    print("    父 Transform=%s -> GameObject=%s" % (pfid, name_of(go.group(1)) if go else "?"))
