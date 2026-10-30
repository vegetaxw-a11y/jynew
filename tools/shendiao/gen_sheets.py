# -*- coding: utf-8 -*-
"""生成"人物设定图"（九宫格：多情绪表情 + 正面/侧面 + 全身/半身），再切成 512 头像。

为什么这么做（承接 gen_heads.py）：
  * 一次调用只画一张头像时，人物的情绪/姿态信息完全丢失，改表情得重新调。
  * 九宫格里九格画的是同一个人，服装发色神情变化成体系，天然就是"角色设定表"。
  * 游戏立绘只要 512x512 的正方形头像，所以把九宫格按 3x3 等分切开，
    第一格（正面·平静）写进 MOD 的 BuildSource/head/<id>.png 当主头像，
    其余八格留在 Export/heads_sheet/cells/ 备用（以后做表情系统直接用）。

九格内容（固定顺序，方便程序裁切后对应）：
    1 正面·平静      2 正面·含怒      3 正面·微笑
    4 侧面·沉思      5 全身·正面      6 全身·侧面
    7 惊愕           8 悲恸/决绝      9 背身回望

用法:
  $env:TURBO_KEY = 'sk-...'
  python tools/shendiao/gen_sheets.py --list
  python tools/shendiao/gen_sheets.py --only 0 --apply        # 只做杨过（少年）
  python tools/shendiao/gen_sheets.py --apply                 # 全部
  python tools/shendiao/gen_sheets.py --only 0 --apply --force # 覆盖已存在的主头像
"""
import glob
import io
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G  # noqa: E402  （复用 ROSTER / gen_one / to_512 / meta_for）
import gen_cards as CG  # noqa: E402  （复用 STYLE_BODY：两套产物同一画风）

SHEET_DIR = os.path.join(G.ROOT, 'Export', 'heads_sheet')
CELL_DIR = os.path.join(SHEET_DIR, 'cells')
LOG = os.path.join(G.ROOT, 'Logs', '_sheets_gen.log')

SLOTS = [
    ('正面·平静', '正视前方，神情平静，眉眼自然放松'),
    ('正面·含怒', '正视前方，眉头紧锁、双眼锐利含怒，下颌收紧'),
    ('正面·微笑', '正视前方，微微一笑，眼中带着温度'),
    ('侧面·沉思', '四分之三侧脸，目光望向画面一侧，眉间若有所思'),
    ('全身·正面', '正面全身站立，双手自然垂放或轻扶衣襟，露出完整的衣袍与靴履'),
    ('全身·侧面', '侧面全身，身体侧向一边、迈步或持兵器，衣袂带风'),
    ('惊愕', '半身，双眼睁大、嘴唇微张，满脸愕然'),
    ('悲恸·决绝', '半身，眼圈泛红、紧紧抿唇，神情悲愤而决绝'),
    ('背身回望', '半身，身体背向画面、只回头露出侧脸，眼神意味深长'),
]

SHEET_STYLE = (
    '画面要求：这是一张把同一个角色画九遍的九宫格拼图。正方形画面，画面被整齐地均分为 '
    '3 行 3 列共 9 个等大的方格，从左到右、从上到下依次排列；'
    '方格之间留出均匀的留白，绝对不要画网格线、分隔边框；'
    '每一个方格里只画这一个角色的一个完整形象，人物完整地落在格内、不被裁切；'
    '九格的画风、脸型五官、发型发色、服装配色必须完全一致，是同一个人。'
    # ↓ 画风段直接复用设定卡那套"精致"描述，保证两套产物同一画风
    + CG.STYLE_BODY
    + '纯白或极浅灰白背景，背景不画任何景物与纹样；'
    '南宋时期的服饰与发式，符合金庸《神雕侠侣》原著的人物设定。'
)

# 实测坑：只要把九格写成"第1格：正面·平静 —— …"这种图例格式，模型就会在画面里
# 烧上 "Frontal·Calm" / "Full Body·Side" 这类英文字幕（小龙女那张就是这么毁的）。
# 所以：① 描述改成纯句子、不给"名称：描述"的结构；② 末尾再硬性禁一次文字。
NO_TEXT = (
    '这是纯图像输出，画面里绝对不许出现任何文字：不要中文、不要英文字母、不要拼音、'
    '不要"Frontal·Calm"这类说明性字幕或标签、不要数字、不要水印与 logo。'
    '每个方格内只有人物和纯色背景，除此之外什么都没有。'
)

_CN = '一二三四五六七八九'


def build_prompt(label, desc):
    rows = []
    for i, (_name, how) in enumerate(SLOTS):
        rows.append('第%s个方格画的是：%s。' % (_CN[i], how))
    return (
        '请画一张中国武侠人物的九宫格拼图。\n'
        '人物是%s。\n%s\n\n'
        '%s\n\n'
        '%s\n\n'
        '%s\n\n%s'
        % (label, desc, NO_TEXT, '\n'.join(rows), SHEET_STYLE, NO_TEXT)
    )



def ensure_meta(dst_png, cid):
    """写 .meta：已存在且非空就一个字都不动（guid 和导入设置沿用原样，最安全）。

    只有缺文件或文件为空时才从同目录模板复制一份并换 guid。
    顺序坑：必须"先取模板文本、再 open('w')"，否则 open('w') 先把目标截断，
    模板恰好又是它自己时读回来就是空字符串。
    """
    mp = dst_png + '.meta'
    if os.path.isfile(mp) and os.path.getsize(mp) > 0:
        return False
    txt = G.meta_for(cid)
    io.open(mp, 'w', encoding='utf-8', newline='\n').write(txt)
    return True


def avatar_crop(png_bytes, inset=0.02, keep=0.86):
    """从九宫格第 1 格（正面·平静）取"上半 keep 比例的正方形"当游戏头像。

    为什么不是直接取整格：
      ① 头像只需要脸，整格塞进去脸会偏小；
      ② 模型偶尔会在格子底部烧一行字幕（实测小龙女那张写了 "Frontal·Calm"），
         取上半部分能把这行字整块切掉。
    """
    from PIL import Image
    sheet = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    w, h = sheet.size
    cw, ch = w / 3.0, h / 3.0
    dx, dy = cw * inset, ch * inset
    side = (ch - 2 * dy) * keep
    x0 = (cw - side) / 2.0
    im = sheet.crop((int(x0), int(dy), int(x0 + side), int(dy + side)))
    im = im.convert('RGBA').resize((G.FINAL, G.FINAL), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def split_cells(png_bytes, inset=0.02):
    """把九宫格切成 9 张 512x512 RGBA，返回 [(slot_name, bytes, Image), ...]。

    inset: 每格四边各内缩的比例。AI 即使被要求"不画网格线"，仍常在格与格的
    交界处留下细黑线，贴边裁切会把线带进成品，所以默认内缩 2%。
    """
    from PIL import Image
    sheet = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    w, h = sheet.size
    cw, ch = w / 3.0, h / 3.0
    dx, dy = cw * inset, ch * inset
    out = []
    for idx, (name, _how) in enumerate(SLOTS):
        r, c = divmod(idx, 3)
        box = (int(c * cw + dx), int(r * ch + dy),
               int((c + 1) * cw - dx), int((r + 1) * ch - dy))
        cell = sheet.crop(box).convert('RGBA')
        cell = cell.resize((G.FINAL, G.FINAL), Image.LANCZOS)
        buf = io.BytesIO()
        cell.save(buf, 'PNG', optimize=True)
        out.append((name, buf.getvalue(), cell))
    return out, sheet.size


def write_cells(fname, cells):
    """落地九格切片，返回写入的文件数。"""
    n = 0
    for i, (_name, cell_png, _im) in enumerate(cells, 1):
        io.open(os.path.join(CELL_DIR, '%s_%d.png' % (fname, i)), 'wb').write(cell_png)
        n += 1
    return n


def resplit_all(apply_, force):
    """只重切已经生成过的设定图，不调用接口（省钱）。"""
    from PIL import Image  # noqa: F401
    if not os.path.isdir(SHEET_DIR):
        G.log('还没有任何设定图：%s' % SHEET_DIR)
        return
    sheets = [f for f in sorted(os.listdir(SHEET_DIR))
              if f.endswith('_sheet.png') or '_sheet_' in f and f.endswith('.png')]
    if not sheets:
        G.log('还没有任何设定图：%s' % SHEET_DIR)
        return
    by_name = {r[1]: r for r in G.ROSTER}
    for f in sheets:
        fname = f.split('_sheet')[0]
        row = by_name.get(fname)
        if row is None:
            G.log('-- 跳过 %s（ROSTER 里没有这个文件名）' % f)
            continue
        cid, _fn, label, _d = row
        raw = io.open(os.path.join(SHEET_DIR, f), 'rb').read()
        cells, size = split_cells(raw)
        write_cells(fname, cells)
        msg = 'RESPLIT %-18s %dx%d -> 九格' % (label, size[0], size[1])
        dst_png = os.path.join(G.HEAD_DIR, '%s.png' % fname)
        if fname.endswith('_adult'):
            msg += '  (变体，不入 MOD)'
        elif apply_ and (force or not os.path.isfile(dst_png)):
            io.open(dst_png, 'wb').write(avatar_crop(raw))
            ensure_meta(dst_png, cid)
            msg += '  -> %s.png + .meta（第 1 格上半部）' % fname
        G.log(msg)



def make_contact(thumb=200, cols=6):
    """把各角色第 1 格（正面·平静）拼成一张总览图，方便一眼看全套画风是否统一。"""
    from PIL import Image, ImageDraw
    items = []
    for cid, fname, _label, _d in G.ROSTER:
        p = os.path.join(CELL_DIR, '%s_1.png' % fname)
        if os.path.isfile(p):
            items.append((fname, Image.open(p).convert('RGB')))
    if not items:
        G.log('还没有切片，先跑生成或 --resplit')
        return
    rows = (len(items) + cols - 1) // cols
    pad, cap = 6, 16
    W = cols * (thumb + pad) + pad
    H = rows * (thumb + cap + pad) + pad
    canvas = Image.new('RGB', (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(canvas)
    for i, (fname, im) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (thumb + pad)
        y = pad + r * (thumb + cap + pad)
        canvas.paste(im.resize((thumb, thumb), Image.LANCZOS), (x, y))
        dr.rectangle([x - 1, y - 1, x + thumb, y + thumb], outline=(200, 200, 200))
        dr.text((x + 2, y + thumb + 2), fname, fill=(90, 90, 90))
    out = os.path.join(SHEET_DIR, '_contact.png')
    canvas.save(out, 'PNG', optimize=True)
    G.log('总览图：%s（%d 人，%dx%d）' % (out, len(items), W, H))


def main():
    argv = sys.argv[1:]
    apply_ = '--apply' in argv
    force = '--force' in argv
    size = argv[argv.index('--size') + 1] if '--size' in argv else G.IMAGE_SIZE
    model = argv[argv.index('--model') + 1] if '--model' in argv else G.MODEL
    only = None
    if '--only' in argv:
        only = set(x.strip() for x in argv[argv.index('--only') + 1].split(',') if x.strip())

    if '--list' in argv:
        for cid, fname, label, _d in G.ROSTER:
            G.log('%3d  %-8s %s' % (cid, fname, label))
        return

    if '--resplit' in argv:
        resplit_all(apply_, force)
        return

    if '--contact' in argv:
        make_contact()
        return

    todo = [r for r in G.ROSTER
            if only is None or r[1] in only or str(r[0]) in only]
    if not todo:
        sys.exit('没有匹配到人物，检查 --only')

    key = G.api_key()
    os.makedirs(CELL_DIR, exist_ok=True)
    with io.open(LOG, 'a', encoding='utf-8') as fh:
        fh.write('\n==== %s  九宫格 %d 张（%s, %s, %s）\n' % (
            time.strftime('%Y-%m-%d %H:%M:%S'), len(todo),
            'apply' if apply_ else 'dry', model, size))

    ok = fail = skip = 0
    for cid, fname, label, desc in todo:
        dst_png = os.path.join(G.HEAD_DIR, '%s.png' % fname)
        t0 = time.time()
        try:
            # 已有设定图就复用它（重切即可，不再花钱调接口）；--force 才会重新出图
            olds = sorted(glob.glob(os.path.join(SHEET_DIR, '%s_sheet*.png' % fname)))
            if olds and not force:
                raw = io.open(olds[-1], 'rb').read()
                src = 'REUSE ' + os.path.basename(olds[-1])
                reused = True
            else:
                raw = G.gen_one(key, build_prompt(label, desc), image_size=size, model=model)
                sheet_path = os.path.join(SHEET_DIR, '%s_sheet.png' % fname)
                if os.path.isfile(sheet_path):
                    sheet_path = os.path.join(SHEET_DIR, '%s_sheet_%s.png'
                                              % (fname, time.strftime('%m%d_%H%M%S')))
                io.open(sheet_path, 'wb').write(raw)
                src = os.path.basename(sheet_path)
                reused = False
            cells, sheet_size = split_cells(raw)
            write_cells(fname, cells)
            msg = ('%s %-18s 设定图 %dx%d  %5.1fKB  %3.0fs  九格已切'
                   % ('OK  ' if not reused else 'CACH', label,
                      sheet_size[0], sheet_size[1], len(raw) / 1024.0, time.time() - t0))
            if fname.endswith('_adult'):
                msg += '  (变体，不入 MOD)'
            elif apply_:
                io.open(dst_png, 'wb').write(avatar_crop(raw))        # 第 1 格上半部（切掉格底字幕、脸更大）
                ensure_meta(dst_png, cid)
                msg += '  -> %s.png + .meta（用第 1 格上半部）' % fname
            else:
                msg += '  (预演，未写入 MOD)'
            G.log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '  sheet=' + src + '\n')
            ok += 1
        except Exception as e:  # noqa: BLE001
            msg = 'FAIL %-18s %s' % (label, e)
            G.log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '\n')
            fail += 1

    G.log('')
    G.log('完成：成功 %d，失败 %d，跳过 %d' % (ok, fail, skip))
    G.log('设定图：%s' % SHEET_DIR)
    G.log('九格切片：%s' % CELL_DIR)


if __name__ == '__main__':
    main()
