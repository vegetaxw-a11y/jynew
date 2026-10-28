import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "..", "..", "jyx2", "Assets", "Mods")
TARGET = os.path.join(BASE, "shendiao", "Maps", "GameMaps", "1000_daditu.unity")


def read(p):
    with io.open(p, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


def unesc(s):
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        inner = s[1:-1]
        try:
            return inner.encode("utf-8", "backslashreplace").decode("unicode_escape")
        except Exception:
            return inner
    return s


def main():
    text = read(TARGET)

    go_name = {}
    go_comps = {}
    go_layer = {}
    tr_pos = {}
    tr_parent = {}
    tr_of_go = {}

    for d in re.split(r"(?m)^--- !u!", text):
        head = d.split("\n", 1)[0].strip()
        m = re.match(r"^(\d+) &(-?\d+)", head)
        if not m:
            continue
        cls, fid = m.group(1), m.group(2)

        if cls == "1":
            nm = re.search(r"(?m)^  m_Name: (.*)$", d)
            go_name[fid] = unesc(nm.group(1).strip()) if nm else ""
            go_comps[fid] = re.findall(r"component: \{fileID: (-?\d+)\}", d)
            lay = re.search(r"m_Layer: (-?\d+)", d)
            go_layer[fid] = int(lay.group(1)) if lay else -1
        elif cls == "4":
            go = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", d)
            fa = re.search(r"m_Father: \{fileID: (-?\d+)\}", d)
            p = re.search(
                r"m_LocalPosition: \{x: ([-\d.eE]+), y: ([-\d.eE]+), z: ([-\d.eE]+)\}", d
            )
            if go:
                tr_of_go[go.group(1)] = fid
            if fa:
                tr_parent[fid] = fa.group(1)
            if p:
                tr_pos[fid] = tuple(round(float(v), 2) for v in p.groups())

    # 建立 Transform -> GameObject 反查
    tr_go = {v: k for k, v in tr_of_go.items()}

    # Triggers 的 transform
    trig_tr = None
    for go, nm in go_name.items():
        if nm == "Triggers":
            trig_tr = tr_of_go.get(go)
    trig_children = set(
        t for t, fa in tr_parent.items() if fa == trig_tr
    )

    print("=== 全部 GameObject 名（unesc），标记是否在 Level/Triggers 下")
    for go, nm in sorted(go_name.items(), key=lambda x: x[1]):
        tr = tr_of_go.get(go)
        inTrig = "TRIG" if tr in trig_children else "    "
        if nm and any(k in nm for k in ("_", "嘉兴", "Trig", "Player", "Level", "Dynamic")):
            print(
                "  %s layer=%-3s %-28s pos=%s comps=%s"
                % (inTrig, go_layer.get(go), nm, tr_pos.get(tr), len(go_comps.get(go, [])))
            )

    print("\n=== Triggers 下的对象（落点）")
    for go, nm in go_name.items():
        if tr_of_go.get(go) in trig_children:
            print("  %-28s pos=%s" % (nm, tr_pos.get(tr_of_go.get(go))))


if __name__ == "__main__":
    main()
