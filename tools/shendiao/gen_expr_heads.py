# -*- coding: utf-8 -*-
"""把九宫格里的"表情格"裁成对话头像，写进 MOD —— 表情系统的图片侧。

为什么要虚拟 id（见 docs/shendiao-context.md 第十一节）：
  * 游戏只按 Assets/BuildSource/head/<id>.png 取头像，文件名 == 说话人 id；
  * 所以"角色 + 表情"必须换一个 id 才能换图：exprId = 9000000 + 角色id*10 + 槽位；
  * 槽位号与 gen_sheets.py 的九宫格一致：
        1 平静  2 怒  3 笑  4 沉思  5 全身正面  6 全身侧面  7 惊  8 悲恸  9 回身
    槽位 1 用默认头像 <角色id>.png，这里不重复出图。

本脚本一次做四件事：
  1. Export/heads_sheet/cells/<fname>_<slot>.png -> BuildSource/head/<exprId>.png（512 RGBA）
     .meta 从同角色默认头像复制、只换 guid（导入设置 / AB 标记必须一致）
  2. 把已有表情 id 回填进 Lua/expr.lua 的 HAVE_IDS 段（剧本写了没图的会自动退回默认头像）
  3. 在 ModSetting.asset 的 StoryIdNameFixes 里登记这些虚拟 id 的姓名
     （兜底：万一 ChangePosition 热更新没生效，也不会因为查不到名字崩掉）
  4. --check 体检：剧本引用的表情是否都有图、尺寸/meta/清单是否对得上

用法:
  python tools/shendiao/gen_expr_heads.py --list        # 能生成哪些（不写盘）
  python tools/shendiao/gen_expr_heads.py --apply       # 全量出图并回填清单
  python tools/shendiao/gen_expr_heads.py --apply --used-only   # 只出剧本用到的
  python tools/shendiao/gen_expr_heads.py --apply --only 0,22 --size 384
  python tools/shendiao/gen_expr_heads.py --check       # 体检
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G          # noqa: E402 （ROSTER / FINAL / HEAD_DIR / meta_for）
import tag_expr as T           # noqa: E402 （SLOTS / used_combos）

MOD = G.MOD
EXPR_BASE = 9000000
EXPR_STEP = 10
SHEET_DIR = os.path.join(G.ROOT, 'Export', 'heads_sheet')
CELL_DIR = os.path.join(SHEET_DIR, 'cells')
EXPR_LUA = os.path.join(MOD, 'Lua', 'expr.lua')
MOD_SETTING = os.path.join(MOD, 'ModSetting.asset')
CHAR_XLSX = os.path.join(MOD, 'Configs', '人物.xlsx')
REPORT = os.path.join(G.ROOT, 'Logs', '_expr_heads.txt')

HAVE_OPEN = 'local HAVE_IDS = {'
HAVE_CLOSE = '}'
NAME_FIX_KEY = '  StoryIdNameFixes:'
PRELOAD_KEY = '  PreloadedLua:'


def slot_name(slot):
    for k, v in T.SLOTS.items():
        if v == slot:
            return k
    return str(slot)


def expr_id(role_id, slot):
    return EXPR_BASE + role_id * EXPR_STEP + slot


def roster_main():
    """[(角色id, 文件名, 标签)]，跳过 _adult 这类只做设定图不入 MOD 的变体。"""
    out = []
    for cid, fname, label, _desc in G.ROSTER:
        if fname.endswith('_adult'):
            continue
        out.append((cid, fname, label))
    return out


def cell_path(fname, slot):
    return os.path.join(CELL_DIR, '%s_%d.png' % (fname, slot))


def crop_head(path, size=G.FINAL, keep=0.86):
    """取格子"上半 86% 的正方形"当头像。

    为什么不是整格：格子常在下沿烧一行字幕/水印，取上半能整块切掉；
    同时脸更大，塞进 450x450 的对话框正合适（和 gen_sheets.avatar_crop 同比例）。
    """
    from PIL import Image
    im = Image.open(path).convert('RGB')
    w, h = im.size
    side = int(h * keep)
    x0 = (w - side) // 2
    im = im.crop((x0, 0, x0 + side, side)).convert('RGBA')
    if size and im.size != (size, size):
        im = im.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def targets(only=None, used_only=False, slots=None):
    """[(角色id, 文件名, 标签, 槽位, 格子路径, 虚拟id)]"""
    used = T.used_combos() if used_only else None
    out = []
    for cid, fname, label in roster_main():
        if only is not None and fname not in only and str(cid) not in only:
            continue
        for name, slot in T.SLOTS.items():
            if slots and slot not in slots:
                continue
            if used is not None and (cid, slot) not in used:
                continue
            p = cell_path(fname, slot)
            if not os.path.isfile(p):
                continue
            out.append((cid, fname, label, slot, p, expr_id(cid, slot)))
    return out


# ---------------------------------------------------------------- 清单回填
def write_have_ids(ids):
    """把可用表情 id 回填进 expr.lua 的 HAVE_IDS 段。"""
    text = io.open(EXPR_LUA, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.replace('\r\n', '\n').split('\n')
    try:
        i = next(i for i, ln in enumerate(lines) if ln.strip() == HAVE_OPEN)
    except StopIteration:
        raise RuntimeError('expr.lua 里找不到 "%s" 段' % HAVE_OPEN)
    j = i
    while not lines[j].strip().startswith(HAVE_CLOSE):
        j += 1
    body = []
    row = []
    for k, v in enumerate(sorted(ids), 1):
        row.append(str(v))
        if k % 6 == 0:
            body.append('    ' + ', '.join(row) + ',')
            row = []
    if row:
        body.append('    ' + ', '.join(row) + ',')
    new = lines[:i] + [HAVE_OPEN] + body + lines[j:]
    io.open(EXPR_LUA, 'w', encoding='utf-8', newline=nl).write('\n'.join(new))
    return len(ids)


def _read_asset():
    raw = io.open(MOD_SETTING, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    return raw.replace('\r\n', '\n'), nl


def _yaml_str(s):
    out = []
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ord(ch) < 0x20:
            out.append(' ')
        elif ord(ch) > 0x7e:
            out.append('\\u%04X' % ord(ch))
        else:
            out.append(ch)
    return '"' + ''.join(out) + '"'


def _match_key(line, key):
    """匹配 '  Key:' 这一行；兼容 Unity 把空列表写成 '  Key: []' 的写法。"""
    s = line.rstrip()
    return s == key or s == key + ' []'


def _patch_list(lines, key, values):
    """把 key 下面那段列表整体替换成 values（其余行不动）。"""
    idx = next((i for i, ln in enumerate(lines) if _match_key(ln, key)), None)
    if idx is None:
        raise RuntimeError('ModSetting.asset 里找不到 %r' % key)
    end = idx + 1
    if lines[idx].rstrip() != key:           # 本行就带 []，是单行空列表
        end = idx + 1
    elif end < len(lines) and lines[end].strip() == '[]':
        end += 1
    else:
        while end < len(lines) and lines[end].startswith('  - '):
            end += 1
    if not values:
        block = [key + ' []']
    else:
        block = [key] + ['  - ' + v if not v.startswith(' ') else v for v in values]
    return lines[:idx] + block + lines[end:]


def console_names():
    """人物.xlsx 的 (Id -> 姓名)，给虚拟 id 兜底起名用。"""
    import openpyxl
    wb = openpyxl.load_workbook(CHAR_XLSX, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    out = {}
    for r in rows[4:]:                       # 前 4 行是表头 / 类型 / 字段名
        if r and isinstance(r[0], (int, float)) and r[3]:
            out[int(r[0])] = str(r[3]).strip()
    return out


def patch_mod_setting(ids_by_owner):
    """ids_by_owner: {虚拟id: 角色id}；登记名 + 保证 PreloadedLua 里有 expr。"""
    names = console_names()
    text, nl = _read_asset()
    lines = text.split('\n')

    fixes = []
    for vid in sorted(ids_by_owner):
        # 注意层级：_patch_list 只会给第一行加 "  - "，所以这里第一行不带短横，
        # 第二行必须自带 4 个空格（Unity 的 YAML 里 Name 跟 Id 同级、缩进在列表项下）
        fixes.append('Id: %d' % vid)
        fixes.append('    Name: %s' % _yaml_str(names.get(ids_by_owner[vid], '')))
    lines = _patch_list(lines, NAME_FIX_KEY, fixes)

    idx = next((i for i, ln in enumerate(lines) if _match_key(ln, PRELOAD_KEY)), None)
    if idx is None:
        raise RuntimeError('ModSetting.asset 里找不到 PreloadedLua')
    end = idx + 1
    while end < len(lines) and lines[end].startswith('  - '):
        end += 1
    cur = [ln.strip()[2:].strip() for ln in lines[idx + 1:end]]
    if 'expr' not in cur:
        cur.append('expr')
    lines = _patch_list(lines, PRELOAD_KEY, cur)



    io.open(MOD_SETTING, 'w', encoding='utf-8', newline=nl).write('\n'.join(lines))
    return len(fixes) // 2, cur


# ---------------------------------------------------------------- 体检
def check():
    from PIL import Image
    bad = []
    used = T.used_combos()
    need = set()
    for cid, fname, _label in roster_main():
        for _name, slot in T.SLOTS.items():
            need.add((cid, slot))

    for cid, slot in sorted(used):
        p = os.path.join(G.HEAD_DIR, '%d.png' % expr_id(cid, slot))
        if not os.path.isfile(p):
            bad.append('缺图（剧本已引用）: 角色 %d 槽位 %d -> %d.png'
                       % (cid, slot, expr_id(cid, slot)))
            continue
        im = Image.open(p)
        if im.size != (G.FINAL, G.FINAL) or im.mode != 'RGBA':
            bad.append('尺寸/通道不对: %d.png %s %s' % (expr_id(cid, slot), im.size, im.mode))
        mp = p + '.meta'
        if not os.path.isfile(mp) or os.path.getsize(mp) == 0:
            bad.append('缺 .meta: %d.png' % expr_id(cid, slot))
        elif 'assetBundleName: shendiao_mod' not in io.open(mp, encoding='utf-8').read():
            bad.append('.meta 没挂 AB: %d.png' % expr_id(cid, slot))

    disk = set()
    for cid, slot in need:
        if os.path.isfile(os.path.join(G.HEAD_DIR, '%d.png' % expr_id(cid, slot))):
            disk.add(expr_id(cid, slot))
    lua = io.open(EXPR_LUA, encoding='utf-8').read()
    m = re.search(r'local HAVE_IDS = \{(.*?)\n\}', lua, re.S)
    have = set(int(x) for x in re.findall(r'\d+', m.group(1))) if m else set()
    if have != disk:
        bad.append('expr.lua 的 HAVE_IDS 与磁盘不一致：多 %s / 少 %s'
                   % (sorted(have - disk)[:5], sorted(disk - have)[:5]))

    setting = io.open(MOD_SETTING, encoding='utf-8').read()
    if '  - expr' not in setting:
        bad.append('ModSetting.asset 的 PreloadedLua 里没有 expr')
    miss = [v for v in sorted(disk) if ('- Id: %d' % v) not in setting]
    if miss:
        bad.append('ModSetting.asset 缺 %d 条 StoryIdNameFixes（例 %s）' % (len(miss), miss[:3]))

    # YAML 层级体检：写成 "- - Id:" 或 Name 缩进不足时，Unity 会整块读不出来
    # （表现是名字回退成 "某角色"、PreloadedLua 变空），所以这里逐行对齐检查
    lines = setting.split('\n')
    start = next((i for i, ln in enumerate(lines) if _match_key(ln, NAME_FIX_KEY)), None)
    if start is None:
        bad.append('ModSetting.asset 里找不到 StoryIdNameFixes')
    else:
        j = start + 1
        while j + 1 < len(lines) and lines[j].startswith('  - '):
            if not lines[j].startswith('  - Id: '):
                bad.append('StoryIdNameFixes 第 %d 行应是 "  - Id: N"，实际 %r'
                           % (j + 1, lines[j][:40]))
            elif not lines[j + 1].startswith('    Name: '):
                bad.append('StoryIdNameFixes 第 %d 行应是 4 空格缩进的 "    Name: …"，实际 %r'
                           % (j + 2, lines[j + 1][:40]))
            j += 2

    out = ['剧本引用到的"角色+表情": %d 组；磁盘上的表情头像: %d 张' % (len(used), len(disk)),
           '体检: ' + ('通过' if not bad else '%d 个问题' % len(bad))]
    out.extend('  ! ' + b for b in bad)
    return '\n'.join(out), len(bad)


def main():
    argv = sys.argv[1:]
    apply_ = '--apply' in argv
    used_only = '--used-only' in argv
    size = int(argv[argv.index('--size') + 1]) if '--size' in argv else G.FINAL
    only = None
    if '--only' in argv:
        only = set(x.strip() for x in argv[argv.index('--only') + 1].split(',') if x.strip())
    slots = None
    if '--slots' in argv:
        slots = set(int(x) for x in argv[argv.index('--slots') + 1].split(',') if x.strip())

    if '--check' in argv:
        msg, n = check()
        io.open(REPORT, 'w', encoding='utf-8', newline='\n').write(msg + '\n')
        print('check -> %s (problems: %d)' % (REPORT, n))
        return 0 if n == 0 else 1

    todo = targets(only, used_only, slots)
    if '--list' in argv:
        lines = ['%-4s %-8s %-6s %-10s %s' % ('id', 'fname', 'label', 'expr', 'cell')]
        for cid, fname, label, slot, p, vid in todo:
            lines.append('%-4d %-8s %-6s %-10s %s' % (cid, fname, label, slot_name(slot),
                                                      os.path.basename(p)))
        io.open(REPORT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
        print('list -> %s (%d items)' % (REPORT, len(todo)))
        return 0

    if not apply_:
        print('dry-run: %d images would be written (add --apply)' % len(todo))
        for cid, fname, label, slot, _p, vid in todo[:5]:
            print('  %s slot=%d -> %d.png' % (fname, slot, vid))
        return 0

    os.makedirs(G.HEAD_DIR, exist_ok=True)
    ids = {}
    ok = 0
    for cid, fname, label, slot, p, vid in todo:
        dst = os.path.join(G.HEAD_DIR, '%d.png' % vid)
        io.open(dst, 'wb').write(crop_head(p, size))
        mp = dst + '.meta'
        if not os.path.isfile(mp) or os.path.getsize(mp) == 0:
            io.open(mp, 'w', encoding='utf-8', newline='\n').write(G.meta_for(cid))
        ids[vid] = cid
        ok += 1

    # 磁盘上已有的表情头像也算"可用"（局部重建时不会把清单清空）
    for cid, fname, _label in roster_main():
        for _name, slot in T.SLOTS.items():
            vid = expr_id(cid, slot)
            if os.path.isfile(os.path.join(G.HEAD_DIR, '%d.png' % vid)):
                ids[vid] = cid

    n_have = write_have_ids(list(ids))
    n_fix, preload = patch_mod_setting(ids)

    msg = ['生成 %d 张表情头像（%dpx）' % (ok, size),
           'BuildSource/head 下的表情头像共 %d 张，已回填 expr.lua' % n_have,
           'ModSetting.asset: StoryIdNameFixes %d 条，PreloadedLua = %s' % (n_fix, preload)]
    io.open(REPORT, 'w', encoding='utf-8', newline='\n').write('\n'.join(msg) + '\n')
    print('done: %d images, %d name fixes, preload=%s' % (ok, n_fix, ','.join(preload)))
    print('report -> %s' % REPORT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
