"""按 GUID 反查资源文件（扫 .meta）。用法: python _guid_find.py <guid> [guid...]"""
import io
import os
import sys

ROOT = r'c:\Games\jynew\jyx2\Assets'
targets = set(g.lower() for g in sys.argv[1:])
out = []

for dirpath, dirs, files in os.walk(ROOT):
    for f in files:
        if not f.endswith('.meta'):
            continue
        fp = os.path.join(dirpath, f)
        try:
            head = io.open(fp, encoding='utf-8', errors='replace').read(400)
        except Exception:
            continue
        for line in head.splitlines():
            if line.startswith('guid:'):
                g = line.split(':', 1)[1].strip().lower()
                if g in targets:
                    out.append('%s  ->  %s' % (g, os.path.relpath(fp[:-5], ROOT)))
                break

io.open(os.path.join(r'c:\Games\jynew\Logs', '_guid_find.txt'), 'w', encoding='utf-8').write('\n'.join(out) or '(none)')
print('ok')
