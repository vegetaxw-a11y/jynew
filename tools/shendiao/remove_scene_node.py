# -*- coding: utf-8 -*-
"""从 .unity 场景里删除 prefab 实例（连带 stripped 子块 + 父节点 m_Children 引用）。

移植别人做的场景时，原版剧情 NPC / 摆件会残留在地图里，必须清干净。
本脚本按「实例名 + 父节点」定位，把 PrefabInstance(!u!1001) 块和它所有 stripped 块
一并删掉，并从父 Transform 的 m_Children 里摘掉根 Transform。

用法:
    # 先看一眼有哪些（dry-run 默认）
    python tools/shendiao/remove_scene_node.py --scene <scene.unity> --name azi --parent NPC
    # 按 instanceID 删
    python tools/shendiao/remove_scene_node.py --scene <scene.unity> --instance 1207982057 --apply
    # 一次删多个名字（逗号分隔）
    python tools/shendiao/remove_scene_node.py --scene <scene.unity> \\
        --name "azi,youtanzhi,星宿弟子5" --parent NPC --apply
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from list_prefab_instances import split_blocks, parse_scene  # noqa: E402

REF_RE = re.compile(r'fileID: (-?\d+)')


def parse_args(argv):
    opt = {}
    i = 0
    while i < len(argv):
        if argv[i].startswith('--'):
            k = argv[i][2:]
            if k == 'apply':
                opt[k] = True
                i += 1
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def main():
    opt = parse_args(sys.argv[1:])
    scene = opt['scene']
    names = [n.strip() for n in opt.get('name', '').split(',') if n.strip()]
    inst_ids = [n.strip() for n in opt.get('instance', '').split(',') if n.strip()]
    parent_filter = opt.get('parent')
    apply = opt.get('apply', False)

    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    instances, _, _ = parse_scene(text)

    targets = []
    for inst in instances:
        if inst_ids and inst['fid'] in inst_ids:
            targets.append(inst)
        elif names and inst['name'] in names:
            if parent_filter and inst['parent_name'] != parent_filter:
                continue
            targets.append(inst)

    if not targets:
        raise SystemExit('没找到匹配的 prefab 实例（name=%s instance=%s parent=%s）'
                         % (names, inst_ids, parent_filter))

    # 收集要删的块 fid
    doomed = set()
    children_patch = {}   # parent_tr_fid -> [要摘掉的子 tr fid]
    for inst in targets:
        doomed.add(inst['fid'])
        for sid in inst['stripped']:
            doomed.add(sid)
        print('删除实例: %-12s %-24s &%s  父=%s  stripped=%d 块'
              % (inst['parent_name'], inst['name'] or '<无名>', inst['fid'],
                 inst['parent_name'], len(inst['stripped'])))
        if inst['parent_tr'] and inst['root_tr']:
            children_patch.setdefault(inst['parent_tr'], []).append(inst['root_tr'])

    # 组件块（!u!114 / 208 / 54 ...）不是 stripped，却用 m_GameObject 指向被删的
    # GameObject —— 必须跟着删，否则留下"无主组件"，Unity 导入会报 missing。
    go_of = {}
    for b in blocks:
        m = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', b['body'], re.M)
        if m:
            go_of[b['fid']] = m.group(1)
    for _ in range(20):
        added = False
        for fid, gofid in go_of.items():
            if fid not in doomed and gofid in doomed:
                doomed.add(fid)
                added = True
        if not added:
            break
    extra = len(doomed)
    for inst in targets:
        extra -= 1 + len(inst['stripped'])
    if extra > 0:
        print('连带删除 %d 个挂在被删 GameObject 上的组件块' % extra)

    # 安全检查：被删的 fileID 是否还被别的块引用（m_Children 摘链不算）
    patch_refs = set()
    for v in children_patch.values():
        patch_refs |= set(v)
    dangling = []
    for b in blocks:
        if b['fid'] in doomed:
            continue
        for ref in set(REF_RE.findall(b['body'])):
            if ref in doomed and ref not in patch_refs:
                dangling.append((b['cls'], b['fid'], ref))
    if dangling:
        print()
        print('!! 警告：仍有 %d 处外部引用指向将被删除的块（删了会变 missing）：' % len(dangling))
        for cls, fid, ref in dangling[:10]:
            print('   !u!%s &%s -> fileID %s' % (cls, fid, ref))

    # 只切除目标块的文本区间 + patch 父块 m_Children，其余字节原样保留
    by_fid = {b['fid']: b for b in blocks}
    edits = []   # (start, end, new_content)

    for tr_fid, drop in children_patch.items():
        b = by_fid.get(tr_fid)
        if b is None:
            # 父 Transform 不在场景里（prefab 内部/悬挂引用），无需摘链
            continue
        hdr_len = (b['end'] - b['start']) - len(b['body'])
        kept = []
        for ln in b['body'].split('\n'):
            m = re.match(r'^  - \{fileID: (-?\d+)\}$', ln)
            if m and m.group(1) in drop:
                continue
            kept.append(ln)
        edits.append((b['start'] + hdr_len, b['end'], '\n'.join(kept)))

    for b in blocks:
        if b['fid'] in doomed:
            edits.append((b['start'], b['end'], ''))

    new_text = text
    for start, end, content in sorted(edits, key=lambda e: -e[0]):
        new_text = new_text[:start] + content + new_text[end:]

    print()
    print('删除 %d 个实例，共 %d 块；文件 %d -> %d 字节'
          % (len(targets), len(doomed), len(text), len(new_text)))
    if apply:
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(new_text)
        print('已写入 %s' % scene)
    else:
        print('（dry-run，未写盘；加 --apply 生效）')


if __name__ == '__main__':
    main()
