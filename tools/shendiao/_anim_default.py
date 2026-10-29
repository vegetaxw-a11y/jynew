"""查 AnimatorController 的默认 state 与 state 列表。用法: python _anim_default.py <controller_guid>"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew\jyx2\Assets'
guid = sys.argv[1].lower()
out = []

# 1. guid -> controller path
target = None
for dirpath, dirs, files in os.walk(ROOT):
    for f in files:
        if f.endswith('.controller.meta'):
            fp = os.path.join(dirpath, f)
            head = io.open(fp, encoding='utf-8', errors='replace').read(300)
            if guid in head:
                target = fp[:-5]
                break
    if target:
        break

if not target:
    out.append('(找不到 controller) ' + guid)
else:
    out.append('controller: ' + os.path.relpath(target, ROOT))
    t = io.open(target, encoding='utf-8', errors='replace').read()
    out.append('大小 %.1f KB' % (len(t) / 1024.0))
    # state 名字
    names = re.findall(r'^  m_Name: (.*)$', t, re.M)
    out.append('state/对象名: ' + ', '.join(names[:40]))
    # 默认 state（AnimatorStateMachine 里的 m_DefaultState）
    for m in re.finditer(r'--- !u!1107 &(-?\d+)\nAnimatorStateMachine:(.*?)(?=\n--- |\Z)', t, re.S):
        body = m.group(2)
        d = re.search(r'm_DefaultState: \{fileID: (-?\d+)\}', body)
        out.append('StateMachine &%s defaultState fileID=%s' % (m.group(1), d.group(1) if d else '?'))
    # 每个 State 的 m_Name + m_Motion
    for m in re.finditer(r'--- !u!1102 &(-?\d+)\nAnimatorState:(.*?)(?=\n--- |\Z)', t, re.S):
        fid, body = m.group(1), m.group(2)
        nm = re.search(r'^  m_Name: (.*)$', body, re.M)
        mo = re.search(r'm_Motion: \{fileID: (-?\d+), guid: ([0-9a-f]+)', body)
        out.append('  State &%s name=%s motion=%s' % (fid, nm.group(1) if nm else '?', mo.group(2) if mo else '-'))

io.open(os.path.join(r'c:\Games\jynew\Logs', '_anim.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
