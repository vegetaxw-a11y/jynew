# -*- coding: utf-8 -*-
"""神雕侠侣 · 剧情编辑器（本地 Web 服务，只用 Python 标准库）。

启动：
    python tools/storyeditor/serve.py                 # http://127.0.0.1:8777
    python tools/storyeditor/serve.py --port 9000 --mod <MOD目录>

为什么不用 FastAPI/Flask：这个工具要能在**没装 pip 包**的机器和 Docker 里都秒起，
只用 `http.server` 就够了；前端是零构建的原生 JS + SVG，也不需要 npm。

REST：
    GET  /api/meta                   MOD 概览（人物 / 表情 / 场景 / 统计）
    GET  /api/events                 全部剧情摘要（左侧列表 + 搜索用）
    GET  /api/event/<id>?source=1    单个事件的节点图（含源码）
    GET  /api/head/<id>.png          对话头像（含 9000000 系列表情虚拟 id）
    POST /api/refresh                重新读配置表 / 场景
    POST /api/event/<id>/line        改一句对白（行级回写 + 自检）
    POST /api/event/<id>/source      整份保存源码
    POST /api/validate               跑 lint_lua + check_story
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import story_edit
import story_mod

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, 'static')
MOD = None


class Handler(BaseHTTPRequestHandler):
    server_version = 'StoryEditor/1.0'
    protocol_version = 'HTTP/1.1'

    # ------------------------------------------------------------ 基础设施
    def log_message(self, fmt, *args):
        sys.stderr.write('[storyeditor] %s\n' % (fmt % args))

    def _send(self, status, body: bytes, ctype: str):
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._send(status, body, 'application/json; charset=utf-8')

    def _error(self, message, status=400):
        self._json({'ok': False, 'error': message}, status)

    def _body(self):
        length = int(self.headers.get('Content-Length') or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode('utf-8-sig'))     # 容忍 BOM（PowerShell 写出来的会带）
        except ValueError:
            raise story_edit.EditError('请求体不是合法 JSON', 400)

    # ------------------------------------------------------------ 路由
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        try:
            if path.startswith('/api/'):
                return self._api_get(path, urllib.parse.parse_qs(parsed.query))
            return self._static(path)
        except story_edit.EditError as exc:
            return self._error(str(exc), exc.status)
        except FileNotFoundError:
            return self._error('没有这个文件', 404)
        except Exception as exc:                       # pragma: no cover
            traceback.print_exc()
            return self._error('服务器内部错误：%s' % exc, 500)

    do_HEAD = do_GET

    def do_POST(self):
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        try:
            return self._api_post(path, self._body())
        except story_edit.EditError as exc:
            return self._error(str(exc), exc.status)
        except Exception as exc:                       # pragma: no cover
            traceback.print_exc()
            return self._error('服务器内部错误：%s' % exc, 500)

    def _api_get(self, path: str, query):
        if path == '/api/meta':
            return self._json(MOD.meta())
        if path == '/api/events':
            return self._json({'events': MOD.events()})
        if path.startswith('/api/event/'):
            eid = path[len('/api/event/'):].strip('/')
            graph = MOD.event_graph(eid)
            if not query.get('source'):
                graph.pop('source', None)
            return self._json(graph)
        if path.startswith('/api/head/'):
            name = os.path.basename(path[len('/api/head/'):])
            head_id = name.split('.')[0]
            if not head_id.isdigit():
                raise story_edit.EditError('头像 id 必须是数字', 400)
            png = MOD.head_path(int(head_id))
            if not png:
                raise story_edit.EditError('没有 %s 的头像图' % head_id, 404)
            with open(png, 'rb') as fp:
                return self._send(200, fp.read(), 'image/png')
        return self._error('未知接口 %s' % path, 404)

    def _api_post(self, path: str, body):
        if path == '/api/refresh':
            MOD.reload()
            return self._json({'ok': True, 'counts': MOD.meta()['counts']})
        if path == '/api/validate':
            return self._json({'ok': True, 'results': story_edit.validate(MOD)})
        if path.startswith('/api/event/'):
            rest = path[len('/api/event/'):].strip('/')
            eid, _, action = rest.partition('/')
            if action == 'line':
                return self._json(story_edit.edit_line(MOD, eid, body))
            if action == 'source':
                return self._json(story_edit.save_source(MOD, eid, body.get('text') or '',
                                                         body.get('mtime')))
        return self._error('未知接口 %s' % path, 404)

    def _static(self, path: str):
        if path in ('/', ''):
            path = '/index.html'
        if path == '/favicon.ico':
            return self._send(200, b'', 'image/x-icon')
        rel = os.path.normpath(path.lstrip('/')).replace('\\', '/')
        if rel.startswith('..') or os.path.isabs(rel):
            return self._error('非法路径', 403)
        full = os.path.join(STATIC_DIR, rel)
        if not os.path.isfile(full):
            return self._error('没有这个文件：%s' % rel, 404)
        ctype = mimetypes.guess_type(full)[0] or 'application/octet-stream'
        if ctype.startswith('text/') or ctype in ('application/javascript', 'image/svg+xml'):
            ctype += '; charset=utf-8'
        with open(full, 'rb') as fp:
            return self._send(200, fp.read(), ctype)


def main(argv=None):
    global MOD
    ap = argparse.ArgumentParser(description='神雕侠侣 · 剧情编辑器')
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8777)
    ap.add_argument('--mod', default=None, help='MOD 目录（默认 shendiao）')
    args = ap.parse_args(argv)

    MOD = story_mod.ModData(args.mod)
    meta = MOD.meta()
    print('MOD  : %s (%s)' % (meta['modName'], meta['modId']))
    print('目录 : %s' % meta['modDir'])
    print('统计 : %s' % meta['counts'])
    print('服务 : http://%s:%d' % (args.host, args.port))
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
    finally:
        httpd.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())