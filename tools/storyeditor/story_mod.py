# -*- coding: utf-8 -*-
"""MOD 数据层：给 Web 剧情编辑器提供配置表 / 场景事件 / 剧本清单。

数据来源（全部在 MOD 目录内，**只读**，不碰游戏本体）：

    Configs/Lua/<表名>Config.lua    excel2lua 生成物，本模块只解析成 {id: {字段: 值}}
    Maps/GameMaps/*.unity           只捞 m_InteractiveEventId / m_EnterEventId / m_UseItemEventId
    Lua/*.lua                       剧本，文件名 = 事件 id
    BuildSource/head/*.png          对话头像，文件名 = 说话人 id（含 9000000 系列表情虚拟 id）
    ModSetting.asset                MOD 名 / 主角名（主角 id 0 在对话里的显示名）

改名 / 改文本等写操作在 story_edit.py；本模块只负责"读"。
"""
from __future__ import annotations

import io
import os
import re

import story_lua

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEFAULT_MOD_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao')
GLOBAL_HEAD_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'BuildSource', 'head')

# ModSetting.PreloadedLua 里的库脚本，不是剧情
LIB_SCRIPTS = ('hotfix', 'expr', 'balance')
EXPR_BASE = 9000000
EXPR_STEP = 10

# .unity 是 YAML 文本，用字节正则扫比逐行 decode 快得多
EVENT_RE = re.compile(rb'm_(?:Interactive|Enter|UseItem)EventId: (-?\d+)')


def read_text(path: str) -> str:
    # newline='' 关键：13 个剧本是 CRLF，通用换行模式会把 \r 吃掉，回写时整份变成 LF
    return io.open(path, encoding='utf-8', errors='replace', newline='').read()


def repo_root(mod_dir: str) -> str:
    """从 MOD 目录反推仓库根（<repo>/jyx2/Assets/Mods/<id>）。

    容器里代码在 /app、仓库挂在 /repo，只有按 MOD 目录反推才找得到 tools/shendiao。
    """
    parts = os.path.abspath(mod_dir).split(os.sep)
    if 'jyx2' in parts:
        idx = parts.index('jyx2')
        if idx > 0:
            return os.sep.join(parts[:idx])
    return REPO


def parse_rows(path: str):
    """Configs/Lua/<表名>Config.lua -> (fieldIdx, [行列表])。"""
    if not os.path.exists(path):
        return {}, []
    text = read_text(path)
    idx = {}
    for m in re.finditer(r'^fieldIdx\.(\w+)\s*=\s*(\d+)\s*$', text, re.M):
        idx[m.group(1)] = int(m.group(2))
    rows = []
    start = text.find('local data = {')
    if start < 0:
        return idx, rows
    for line in text[start:].split('\n'):
        s = line.strip()
        if s.endswith(','):
            s = s[:-1].rstrip()
        if not (s.startswith('{') and s.endswith('}')):
            continue
        body = s[1:-1]
        if not body.strip():
            continue
        rows.append([story_lua.lua_literal(v) for v in story_lua.split_top(body)])
    return idx, rows


def unity_str(raw: str) -> str:
    """Unity YAML 里的字符串：去掉引号并把 \\uXXXX 还原成中文。"""
    s = raw.strip().strip('"')
    return re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)


class ModData:
    """一个 MOD 的只读视图。构造一次，`events()` / `event_graph()` 反复调用。"""

    def __init__(self, mod_dir: str = None):
        self.mod_dir = os.path.abspath(mod_dir or DEFAULT_MOD_DIR)
        self.lua_dir = os.path.join(self.mod_dir, 'Lua')
        self.cfg_dir = os.path.join(self.mod_dir, 'Configs', 'Lua')
        self.head_dirs = [os.path.join(self.mod_dir, 'BuildSource', 'head'), GLOBAL_HEAD_DIR]
        self._summary_cache = {}
        self.reload()

    # ------------------------------------------------------------------ 加载
    def reload(self):
        self.characters = self._load_table('CharacterConfig')
        self.items = self._load_table('ItemConfig')
        self.skills = self._load_table('SkillConfig')
        self.battles = self._load_table('BattleConfig')
        self.maps = self._load_table('MapConfig')
        self.expr_keys = self._load_exprs()
        self.mod_setting = self._load_mod_setting()
        self.scene_events = self._scan_scenes()

    def _load_table(self, name: str):
        idx, rows = parse_rows(os.path.join(self.cfg_dir, name + '.lua'))
        out = {}
        for row in rows:
            rec = {}
            for field, pos in idx.items():
                rec[field] = row[pos - 1] if len(row) >= pos else None
            rid = rec.get('Id')
            if isinstance(rid, int):
                out.setdefault(rid, rec)
        return out

    def _load_mod_setting(self):
        info = {'modName': os.path.basename(self.mod_dir), 'playerName': '主角',
                'luaPattern': '{0}'}
        path = os.path.join(self.mod_dir, 'ModSetting.asset')
        if os.path.exists(path):
            text = read_text(path)
            for key, field in (('ModName', 'modName'), ('PlayerName', 'playerName'),
                               ('LuaFilePatten', 'luaPattern')):
                m = re.search(r'^\s*' + key + r':\s*(.+)$', text, re.M)
                if m:
                    info[field] = unity_str(m.group(1))
        return info

    def _load_exprs(self):
        """Lua/expr.lua 的 EXPR 表：表情名 -> 九宫格槽位号。"""
        out = {}
        path = os.path.join(self.lua_dir, 'expr.lua')
        if os.path.exists(path):
            text = read_text(path)
            m = re.search(r'^EXPR\s*=\s*\{(.*?)^\}', text, re.S | re.M)
            if m:
                for mm in re.finditer(r"(\w+|\[\s*['\"][^'\"]+['\"]\s*\])\s*=\s*(\d+)", m.group(1)):
                    key = mm.group(1).strip()
                    if key.startswith('['):
                        key = key.strip('[]').strip().strip('\'"')
                    out.setdefault(key, int(mm.group(2)))
        if not out:
            out = {'calm': 1, 'angry': 2, 'smile': 3, 'think': 4, 'body': 5,
                   'bodyside': 6, 'shock': 7, 'sad': 8, 'lookback': 9}
        return out

    def _scan_scenes(self):
        """事件 id -> [{'scene': '62_pomiao', 'map': '破庙'}]（剧情列表按场景分组用）。"""
        scene_map = {}
        for mid in sorted(self.maps):
            rec = self.maps[mid]
            sc = rec.get('MapScene')
            if isinstance(sc, str) and sc and sc not in scene_map:
                scene_map[sc] = rec.get('Name') or sc
        index = {}
        folder = os.path.join(self.mod_dir, 'Maps', 'GameMaps')
        if not os.path.isdir(folder):
            return index
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith('.unity'):
                continue
            stem = fn[:-6]
            with open(os.path.join(folder, fn), 'rb') as fp:
                ids = {int(x) for x in EVENT_RE.findall(fp.read())}
            ids.discard(-1)
            for eid in ids:
                index.setdefault(str(eid), []).append({'scene': stem,
                                                       'map': scene_map.get(stem, stem)})
        return index

    # ------------------------------------------------------------------ 名字
    def char_name(self, cid):
        if cid == 0:
            return self.mod_setting.get('playerName') or '主角'
        rec = self.characters.get(cid) if isinstance(cid, int) else None
        return (rec or {}).get('Name') or ('角色 %s' % cid)

    def item_name(self, iid):
        rec = self.items.get(iid) if isinstance(iid, int) else None
        return (rec or {}).get('Name') or ''

    def skill_name(self, sid):
        rec = self.skills.get(sid) if isinstance(sid, int) else None
        return (rec or {}).get('Name') or ''

    def battle_name(self, bid):
        rec = self.battles.get(bid) if isinstance(bid, int) else None
        return (rec or {}).get('Name') or ''

    def map_name(self, mid):
        rec = self.maps.get(mid) if isinstance(mid, int) else None
        return (rec or {}).get('Name') or ''

    def head_path(self, head_id):
        if not isinstance(head_id, int):
            return None
        for folder in self.head_dirs:
            path = os.path.join(folder, '%d.png' % head_id)
            if os.path.exists(path):
                return path
        return None

    def head_id(self, role, expr):
        """Talk 实际用的头像：有表情图就用 9000000+id*10+槽位，否则用默认头像。"""
        if not isinstance(role, int):
            return None
        slot = self.expr_keys.get(expr) if expr else None
        if slot and slot > 1:
            vid = EXPR_BASE + role * EXPR_STEP + slot
            if self.head_path(vid):
                return vid
        return role

    def talk(self, role, expr):
        """story_lua.build_graph 的回调：把人物 id / 表情名翻成人话。"""
        slot = self.expr_keys.get(expr) if expr else None
        return {'roleName': self.char_name(role), 'headId': self.head_id(role, expr),
                'exprSlot': slot or None}

    # ------------------------------------------------------------------ 剧本
    def event_ids(self):
        if not os.path.isdir(self.lua_dir):
            return []
        ids = []
        for fn in os.listdir(self.lua_dir):
            stem = fn[:-4] if fn.endswith('.lua') else ''
            if not stem.isdigit() or stem in LIB_SCRIPTS:
                continue
            ids.append(stem)
        return sorted(ids, key=int)

    def script_path(self, eid: str):
        return os.path.join(self.lua_dir, '%s.lua' % eid)

    def read_script(self, eid: str):
        path = self.script_path(eid)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        return read_text(path)

    def event_graph(self, eid: str):
        path = self.script_path(eid)
        text = self.read_script(eid)
        st = os.stat(path)
        graph = story_lua.build_graph(text, self)
        graph.update({'event': eid, 'file': os.path.basename(path),
                      'mtime': int(st.st_mtime), 'size': st.st_size, 'source': text,
                      'maps': self.scene_events.get(eid, []),
                      'speakerNames': [self.char_name(r) for r in graph['speakers']]})
        stats = graph['stats']
        stats['itemNames'] = [self.item_name(i) or ('#%s' % i) for i in stats['items']]
        stats['battleNames'] = [self.battle_name(b) or ('#%s' % b) for b in stats['battles']]
        stats['skillNames'] = [self.skill_name(s) or ('#%s' % s) for s in stats['skills']]
        return graph

    def events(self):
        """全部剧情的摘要列表（按文件 mtime 缓存，改完脚本刷新即可看到）。"""
        out = []
        for eid in self.event_ids():
            path = self.script_path(eid)
            try:
                st = os.stat(path)
            except OSError:
                continue
            key = (int(st.st_mtime), st.st_size)
            cached = self._summary_cache.get(eid)
            if cached and cached['key'] == key:
                out.append(cached['data'])
                continue
            text = read_text(path)
            graph = story_lua.build_graph(text, self)
            stats = graph['stats']
            data = {
                'id': eid,
                'title': graph['title'],
                'talks': stats['talk'],
                'choices': stats['choice'],
                'flags': stats['flags'],
                'items': stats['items'],
                'battles': stats['battles'],
                'npcs': stats['npcs'],
                'speakers': [{'id': r, 'name': self.char_name(r),
                              'headId': self.head_id(r, None)} for r in graph['speakers']],
                'maps': self.scene_events.get(eid, []),
                'search': _search_text(graph),
                'mtime': key[0],
            }
            self._summary_cache[eid] = {'key': key, 'data': data}
            out.append(data)
        return out

    def meta(self):
        return {
            'modId': os.path.basename(self.mod_dir),
            'modName': self.mod_setting.get('modName'),
            'playerName': self.mod_setting.get('playerName'),
            'luaPattern': self.mod_setting.get('luaPattern'),
            'modDir': self.mod_dir,
            'counts': {'events': len(self.event_ids()), 'characters': len(self.characters),
                       'items': len(self.items), 'skills': len(self.skills),
                       'battles': len(self.battles), 'maps': len(self.maps)},
            'characters': [{'id': cid, 'name': self.char_name(cid),
                            'level': (self.characters[cid] or {}).get('Level'),
                            'sex': (self.characters[cid] or {}).get('Sexual'),
                            'headId': self.head_id(cid, None)}
                           for cid in sorted(self.characters)],
            'exprs': [{'key': k, 'slot': v}
                      for k, v in sorted(self.expr_keys.items(), key=lambda kv: kv[1])],
            'maps': [{'id': mid, 'name': m.get('Name'), 'scene': m.get('MapScene')}
                     for mid, m in sorted(self.maps.items())],
        }


def _search_text(graph) -> str:
    """给前端做全文过滤：把所有对白 / 旗标拼起来（截断，够用就行）。"""
    parts = []
    for n in graph['nodes']:
        if n['kind'] in ('talk', 'message'):
            parts.append(str(n.get('text') or ''))
        elif n.get('group') == 'flag' and (n.get('params') or {}).get('flag'):
            parts.append('旗标 ' + str(n['params']['flag']))
    return '\n'.join(parts)[:6000]
