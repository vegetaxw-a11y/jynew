"""把场景里空闲的 GameEvent 宿主改成"走过即遇敌"的练级区，或克隆一个新宿主。

导入的 JYX2 场景里常有一批三个事件 ID 全是 -1 的空宿主（原本挂装饰物交互，搬走
剧情后就没用了）。它们的位置是原作者摆的、一定可达，正适合当练级遇敌区：

    m_InteractiveEventId: -1   ->  不弹"交互"按钮
    m_EnterEventId:     3001   ->  玩家踩进去直接开战

用法:
    # 用已有空宿主（推荐：位置不用猜）
    python tools/shendiao/_set_grind.py --scene <scene.unity> --host 6 --event 3001

    # 场景里没有空宿主时，从 --clone 指定的宿主复制一个到 --pos
    python tools/shendiao/_set_grind.py --scene <scene.unity> --clone 2 \
        --pos -15,0.5,-9 --event 3006

默认 dry-run，加 --apply 落盘。

宿主必须落在 m_Layer 20（GameEvent），本项目 Jyx2Player 只按这一层做 OverlapSphere。
若原本是实体 BoxCollider，会被强制改成 m_IsTrigger: 1，否则既挡路又不触发
OnTriggerEnter。
"""
import io
import re
import sys

GAME_EVENT_GUID = '28456c42ed689d9458276be4c9851804'
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)
GOID_RE = re.compile(r'm_GameObject: \{fileID: (-?\d+)\}')


def split_blocks(text):
    ms = list(BLOCK_RE.finditer(text))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append({'cls': m.group(1), 'fid': m.group(2), 'stripped': bool(m.group(3)),
                    'hdr': m.group(0), 'body': text[m.end():end]})
    return out


def rebuild(blocks, prefix=''):
    # 首块之前还有 `%YAML 1.1` / `%TAG !u! ...` 两行文件头，丢了 Unity 解析不了
    return prefix + ''.join(b['hdr'] + b['body'] for b in blocks)


def opt_of(argv, key, default=None):
    return argv[argv.index(key) + 1] if key in argv else default


def find_hosts(blocks):
    gos = {}
    for b in blocks:
        if b['cls'] == '1':
            m = re.search(r'^  m_Name: (.*)$', b['body'], re.M)
            gos[b['fid']] = (m.group(1).rstrip() if m else '')

    def comp_of(go_fid, cls):
        for b in blocks:
            if b['cls'] != cls:
                continue
            m = GOID_RE.search(b['body'])
            if m and m.group(1) == go_fid:
                return b
        return None

    hosts = []
    for b in blocks:
        if b['cls'] != '114' or GAME_EVENT_GUID not in b['body']:
            continue
        m = GOID_RE.search(b['body'])
        if not m:
            continue
        go = m.group(1)
        # GameObject 块里没有 m_GameObject 字段，只能按 fileID 直接取
        go_block = next((x for x in blocks if x['cls'] == '1' and x['fid'] == go), None)
        hosts.append({'name': gos.get(go, '?'), 'go': go_block,
                      'trans': comp_of(go, '4') or comp_of(go, '224'),
                      'mono': b, 'col': comp_of(go, '65')})
    return hosts


def free_hosts(hosts):
    return [h for h in hosts
            if h['mono']['body'].count(': -1') >= 3]



def set_enter(host, event_id):
    body = host['mono']['body']
    body = re.sub(r'^  m_InteractiveEventId: \S+', '  m_InteractiveEventId: -1',
                  body, count=1, flags=re.M)
    if re.search(r'^  m_EnterEventId: \S+', body, flags=re.M):
        body = re.sub(r'^  m_EnterEventId: \S+', '  m_EnterEventId: %s' % event_id,
                      body, count=1, flags=re.M)
    else:
        body = body.rstrip('\n') + '\n  m_EnterEventId: %s\n' % event_id
    host['mono']['body'] = body


def make_trigger(host):
    """BoxCollider 强制成 4x3x4 的触发体；没有就返回 False。"""
    if host['col'] is None:
        return False
    b = host['col']
    b['body'] = re.sub(r'^  m_IsTrigger: \d', '  m_IsTrigger: 1', b['body'], count=1, flags=re.M)
    b['body'] = re.sub(r'^  m_Enabled: \d', '  m_Enabled: 1', b['body'], count=1, flags=re.M)
    b['body'] = re.sub(r'^  m_Size: \{[^}]*\}', '  m_Size: {x: 4, y: 3, z: 4}',
                       b['body'], count=1, flags=re.M)
    b['body'] = re.sub(r'^  m_Center: \{[^}]*\}', '  m_Center: {x: 0, y: 1.5, z: 0}',
                       b['body'], count=1, flags=re.M)
    return True


def clone_host(blocks, src, pos, event_id, base):
    tr, go = src['trans'], src['go']
    if tr is None or go is None:
        raise SystemExit('模板宿主缺 Transform/GameObject，无法克隆')
    ids = {'go': base, 'trans': base + 1, 'mono': base + 2, 'col': base + 3}

    gb = go['body']
    comps = '  m_Component:\n  - component: {fileID: %d}\n' % ids['trans']
    if src['col']:
        comps += '  - component: {fileID: %d}\n' % ids['col']
    comps += '  - component: {fileID: %d}\n' % ids['mono']
    gb = re.sub(r'(?ms)^  m_Component:\n(?:  - component: \{[^}]*\}\n)+', comps, gb)
    gb = re.sub(r'^  m_Name: .*$', '  m_Name: 练级', gb, count=1, flags=re.M)
    gb = re.sub(r'^  m_Layer: \d', '  m_Layer: 20', gb, count=1, flags=re.M)

    tb = tr['body']
    tb = re.sub(r'^  m_GameObject: \{[^}]*\}', '  m_GameObject: {fileID: %d}' % ids['go'],
                tb, count=1, flags=re.M)
    tb = re.sub(r'^  m_LocalPosition: \{[^}]*\}',
                '  m_LocalPosition: {x: %s, y: %s, z: %s}' % tuple(pos), tb, count=1, flags=re.M)
    tb = re.sub(r'(?ms)^  m_Children:\n(?:  - \{[^}]*\}\n)*', '  m_Children: []\n', tb)
    father = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', tb, re.M).group(1)

    mb = src['mono']['body']
    mb = re.sub(r'^  m_GameObject: \{[^}]*\}', '  m_GameObject: {fileID: %d}' % ids['go'],
                mb, count=1, flags=re.M)
    mb = re.sub(r'(?ms)^  m_EventTargets:\n(?:  - \{[^}]*\}\n)*',
                '  m_EventTargets:\n  - {fileID: %d}\n' % ids['go'], mb)
    mb = re.sub(r'^  m_InteractiveEventId: \S+', '  m_InteractiveEventId: -1',
                mb, count=1, flags=re.M)
    mb = re.sub(r'^  m_EnterEventId: \S+', '  m_EnterEventId: %s' % event_id,
                mb, count=1, flags=re.M)

    new = [{'hdr': '--- !u!1 &%d\n' % ids['go'], 'body': gb},
           {'hdr': '--- !u!4 &%d\n' % ids['trans'], 'body': tb},
           {'hdr': '--- !u!114 &%d\n' % ids['mono'], 'body': mb}]
    if src['col']:
        cb = src['col']['body']
        cb = re.sub(r'^  m_GameObject: \{[^}]*\}', '  m_GameObject: {fileID: %d}' % ids['go'],
                    cb, count=1, flags=re.M)
        cb = re.sub(r'^  m_IsTrigger: \d', '  m_IsTrigger: 1', cb, count=1, flags=re.M)
        cb = re.sub(r'^  m_Size: \{[^}]*\}', '  m_Size: {x: 4, y: 3, z: 4}', cb, count=1, flags=re.M)
        cb = re.sub(r'^  m_Center: \{[^}]*\}', '  m_Center: {x: 0, y: 1.5, z: 0}', cb, count=1, flags=re.M)
        new.append({'hdr': '--- !u!65 &%d\n' % ids['col'], 'body': cb})
    return new, father, ids['trans']


def add_child(blocks, father_fid, trans_fid):
    for b in blocks:
        if b['fid'] != father_fid or b['cls'] not in ('4', '224'):
            continue
        if '  m_Children: []' in b['body']:
            b['body'] = b['body'].replace('  m_Children: []',
                                          '  m_Children:\n  - {fileID: %d}' % trans_fid, 1)
        else:
            b['body'] = re.sub(r'^(  m_Children:\n)', r'\1  - {fileID: %d}\n' % trans_fid,
                               b['body'], count=1, flags=re.M)
        return True
    return False


def main():
    argv = sys.argv[1:]
    apply = '--apply' in argv
    scene = opt_of(argv, '--scene')
    event_id = opt_of(argv, '--event')
    if not scene or not event_id:
        print(__doc__)
        return 1
    text = io.open(scene, encoding='utf-8', errors='replace').read()
    blocks = split_blocks(text)
    prefix = text[:text.index(blocks[0]['hdr'])] if blocks else ''
    hosts = find_hosts(blocks)
    if not hosts:
        print('场景里没有 GameEvent 宿主')
        return 1

    want = opt_of(argv, '--host')
    if want is not None:
        cand = [h for h in hosts if h['name'].strip() == want.strip()]
        if not cand:
            print('找不到宿主 %r；现有: %s'
                  % (want, ', '.join('%s(交互%s 经过%s)' % (
                      h['name'],
                      re.search(r'm_InteractiveEventId: (\S+)', h['mono']['body']).group(1),
                      re.search(r'm_EnterEventId: (\S+)', h['mono']['body']).group(1))
                      for h in hosts)))
            return 1
        h = cand[0]
        pos = re.search(r'm_LocalPosition: \{[^}]*\}', h['trans']['body']).group(0) if h['trans'] else '?'
        set_enter(h, event_id)
        ok = make_trigger(h)
        print('宿主 %r  %s' % (h['name'], pos))
        print('  交互=-1  经过=%s  collider=%s' % (event_id, '4x3x4 trigger' if ok else '缺失(走不进)'))
    else:
        src_name = opt_of(argv, '--clone')
        pos = (opt_of(argv, '--pos') or '').split(',')
        if src_name is None or len(pos) != 3:
            print('需要 --host <名>，或 --clone <名> --pos x,y,z')
            return 1
        cand = [h for h in hosts if h['name'].strip() == src_name.strip()]
        if not cand:
            print('找不到模板宿主 %r；现有: %s'
                  % (src_name, ', '.join(h['name'] for h in hosts)))
            return 1
        used = set(b['fid'] for b in blocks)
        base = 2151000000
        while any(str(base + k) in used for k in range(4)):
            base += 10
        new, father, trans_fid = clone_host(blocks, cand[0], pos, event_id, base)
        if not add_child(blocks, father, trans_fid):
            print('警告：父节点 &%s 不在本场景（可能是 prefab 内），新节点会成为孤儿' % father)
        blocks.extend(new)
        print('克隆 %r -> 练级 &%d @%s  经过事件=%s' % (src_name, base, opt_of(argv, '--pos'), event_id))

    if apply:
        io.open(scene, 'w', encoding='utf-8', newline='\n').write(rebuild(blocks, prefix))
        print('已写入 %s' % scene)
    else:
        print('（干跑，加 --apply 落盘）')
    return 0


if __name__ == '__main__':
    sys.exit(main())

