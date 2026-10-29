"""扫所有 .unity 中某 prefab guid 的实例，输出世界坐标（含父节点名）——用于对比原版与我方摆法。"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew\jyx2\Assets'
guid = sys.argv[1].lower()
out = []


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
    return s


def blocks(text):
    return re.split(r'^--- ', text, flags=re.M)


for dirpath, dirs, files in os.walk(ROOT):
    for f in sorted(files):
        if not f.endswith('.unity'):
            continue
        fp = os.path.join(dirpath, f)
        txt = io.open(fp, encoding='utf-8', errors='replace').read()
        if guid not in txt:
            continue
        # GameObject fileID -> name
        goname = {}
        for m in re.finditer(r'^--- !u!1 &(-?\d+)\nGameObject:\n(.*?)(?=^--- |\Z)', txt, re.S | re.M):
            nm = re.search(r'^  m_Name: (.*)$', m.group(2), re.M)
            goname[m.group(1)] = unquote(nm.group(1)) if nm else '?'
        for m in re.finditer(r'^--- !u!1001 &(-?\d+)\nPrefabInstance:(.*?)(?=^--- |\Z)', txt, re.S | re.M):
            body = m.group(2)
            if guid not in body:
                continue
            vals = {}
            for pm in re.finditer(r'propertyPath: m_LocalPosition\.([xyz])\s*\n\s*value: ([-0-9.eE]+)', body):
                vals[pm.group(1)] = pm.group(2)
            nm = re.search(r'propertyPath: m_Name\s*\n\s*value: (.*)', body)
            par = re.search(r'propertyPath: m_Name\s*\n\s*value: (.*)', body)
            name = unquote(nm.group(1)) if nm else '?'
            out.append('%s  &%s  name=%s  pos=(%s, %s, %s)' % (
                os.path.relpath(fp, ROOT), m.group(1), name,
                vals.get('x', '?'), vals.get('y', '?'), vals.get('z', '?')))

io.open(os.path.join(r'c:\Games\jynew\Logs', '_inst.txt'), 'w', encoding='utf-8').write('\n'.join(out) or '(none)')
print('ok')
