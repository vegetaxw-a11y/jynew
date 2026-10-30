"""列出场景里所有 NavMeshObstacle（!u!208）：启用状态、尺寸、carve、所属物体名。"""
import io
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)


def main():
    path = sys.argv[1]
    text = io.open(path, encoding='utf-8', errors='replace').read()
    ms = list(BLOCK_RE.finditer(text))
    names = {}
    for i, m in enumerate(ms):
        if m.group(1) != '1':
            continue
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end]
        n = re.search(r'^  m_Name: (.*)$', body, re.M)
        names[m.group(2)] = n.group(1).rstrip() if n else ''
    for i, m in enumerate(ms):
        if m.group(1) != '208':
            continue
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end]
        go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', body)
        en = re.search(r'm_Enabled: (\d)', body)
        ez = re.search(r'm_Extents: \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+)\}', body)
        cv = re.search(r'm_Carve: (\d)', body)
        print('#%s  name=%r  enabled=%s carve=%s extents=%s' % (
            m.group(2), names.get(go.group(1) if go else '', '?'),
            en.group(1) if en else '?', cv.group(1) if cv else '?',
            ez.groups() if ez else '?'))


if __name__ == '__main__':
    main()
