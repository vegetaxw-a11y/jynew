import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(ROOT, "..", "..", "jyx2", "Assets", "Mods", "shendiao")
DADITU = os.path.join(MOD, "Maps", "GameMaps", "1000_daditu.unity")


def read(p):
    with io.open(p, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


def parse(text):
    go_by_tr = {}
    tr_by_go = {}
    name_by_go = {}
    father_by_tr = {}
    pos_by_tr = {}

    for d in re.split(r"(?m)^--- !u!", text):
        head = d.split("\n", 1)[0].strip()
        m = re.match(r"^(\d+) &(-?\d+)", head)
        if not m:
            continue
        cls, fid = m.group(1), m.group(2)

        if cls == "1":
            nm = re.search(r"(?m)^  m_Name: (.*)$", d)
            name_by_go[fid] = nm.group(1).strip() if nm else "<none>"
        elif cls in ("4", "224"):
            go = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", d)
            fa = re.search(r"m_Father: \{fileID: (-?\d+)\}", d)
            p = re.search(
                r"m_LocalPosition: \{x: ([-\d.eE]+), y: ([-\d.eE]+), z: ([-\d.eE]+)\}", d
            )
            if go:
                go_by_tr[fid] = go.group(1)
                tr_by_go[go.group(1)] = fid
            if fa:
                father_by_tr[fid] = fa.group(1)
            if p:
                pos_by_tr[fid] = tuple(float(v) for v in p.groups())
    return go_by_tr, tr_by_go, name_by_go, father_by_tr, pos_by_tr


def main():
    go_by_tr, tr_by_go, name_by_go, father_by_tr, pos_by_tr = parse(read(DADITU))

    def kids(tr):
        return [t for t, f in father_by_tr.items() if f == tr]

    # Level 节点
    level_tr = None
    trig_tr = None
    for go, nm in name_by_go.items():
        if nm.strip('"') == "Level":
            level_tr = tr_by_go.get(go)
        elif nm.strip('"') == "Triggers":
            trig_tr = tr_by_go.get(go)

    print("=== Level tr =", level_tr, " Triggers tr =", trig_tr)
    print("=== Level 下的子对象：")
    for k in kids(level_tr):
        print("   ", name_by_go.get(go_by_tr.get(k), "?"))

    print("\n=== Level/Triggers 子对象：%d 个" % len(kids(trig_tr)))
    trig_names = set()
    for k in kids(trig_tr):
        nm = name_by_go.get(go_by_tr.get(k), "?").strip('"')
        trig_names.add(nm)
        print("   %-30s pos=%s" % (nm, pos_by_tr.get(k)))

    print("\n=== 场景表 Name 是否都能在 Triggers 下找到")
    import openpyxl

    wb = openpyxl.load_workbook(os.path.join(MOD, "Configs", "场景.xlsx"), data_only=True)
    ws = wb["main"]
    for r in list(ws.iter_rows(values_only=True))[4:]:
        if not r or r[0] is None:
            continue
        print(
            "   id=%-5s %-16s scene=%-24s %s"
            % (r[0], r[1], r[2], "OK" if str(r[1]).strip() in trig_names else "**缺失**")
        )


if __name__ == "__main__":
    main()
