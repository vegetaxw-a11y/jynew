"""补回被 _set_grind.py 早期版本丢掉的 .unity 文件头（%YAML 1.1 / %TAG !u!）。"""
import io
import sys

HEAD = '%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n'

for path in sys.argv[1:]:
    t = io.open(path, encoding='utf-8', newline='').read()
    if t.startswith('%YAML'):
        print('已有文件头: %s' % path)
        continue
    io.open(path, 'w', encoding='utf-8', newline='').write(HEAD + t)
    print('已补文件头: %s' % path)
