import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "..", "..", "jyx2", "Assets", "Mods")

FILES = {
    "shendiao": os.path.join(BASE, "shendiao", "Maps", "GameMaps", "1000_daditu.unity"),
    "JYX2": os.path.join(BASE, "JYX2", "Maps", "GameMaps", "1000_daditu.unity"),
    "SAMPLE": os.path.join(BASE, "SAMPLE", "Maps", "GameMaps", "1000_daditu.unity"),
}

INTEREST = [
    "Player",
    "LevelMasterBooster",
    "Level",
    "Triggers",
    "Dynamic",
    "CameraGroup",
    "CM vcam1",
    "Main Camera",
    "Boat",
    "UI",
]


def read(p):
    with io.open(p, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


def unesc(s):
    # Unity YAML 双引号字符串里的 \uXXXX / \n 等转义
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
        try:
            return s.encode("utf-8", "backslashreplace").decode("unicode_escape")
        except Exception:
            return s
    return s


def stats(path):
    t = read(path)
    docs = re.findall(r"(?m)^--- !u!(\d+) &", t)
    names = [unesc(m.group(1).strip()) for m in re.finditer(r"(?m)^  m_Name: (.*)$", t)]
    return t, docs, names


def main():
    info = {}
    for tag, p in FILES.items():
        if not os.path.exists(p):
            print("%-9s 缺失 %s" % (tag, p))
            continue
        t, docs, names = stats(p)
        info[tag] = (t, docs, names)
        print(
            "%-9s size=%-9d docs=%-5d GameObjects=%d"
            % (tag, len(t.encode("utf-8", "surrogateescape")), len(docs), len(names))
        )

    print("\n=== 关键对象是否存在")
    for tag, (t, docs, names) in info.items():
        ns = set(names)
        row = []
        for k in INTEREST:
            row.append("%s=%s" % (k, "Y" if k in ns else "N"))
        print("  %-9s %s" % (tag, "  ".join(row)))

    print("\n=== Triggers 子对象数量 / Player 路径")
    for tag, (t, docs, names) in info.items():
        cnt = 0
        m = re.search(r"m_Name: Player", t)
        print("  %-9s 含 m_Name: Player = %s" % (tag, "Y" if m else "N"))


if __name__ == "__main__":
    main()
