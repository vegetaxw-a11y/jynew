/* 剧情节点图渲染器（原生 SVG，无依赖）
 * 分层布局 + 贝塞尔连线 + 平移缩放 + 节点拖动；数据全部来自后端 /api/event/<id>。
 */
(function () {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const NODE_W = 236;
  const COL_GAP = 300;
  const ROW_GAP = 24;
  const HEAD_H = 22;
  const LINE_H = 17;
  const PAD = 9;

  function el(name, attrs) {
    const node = document.createElementNS(NS, name);
    if (attrs) Object.keys(attrs).forEach(k => node.setAttribute(k, attrs[k]));
    return node;
  }

  function charWidth(ch) {
    return /[\u2e80-\u9fff\uff00-\uffef\u3000-\u303f]/.test(ch) ? 12.6 : 6.9;
  }

  function wrapText(text, maxWidth, maxLines) {
    const out = [];
    let line = '';
    let width = 0;
    for (const ch of String(text == null ? '' : text)) {
      if (ch === '\n') { out.push(line); line = ''; width = 0; continue; }
      const w = charWidth(ch);
      if (width + w > maxWidth && line) {
        out.push(line);
        line = '';
        width = 0;
        if (out.length >= maxLines) break;
      }
      line += ch;
      width += w;
    }
    if (line && out.length < maxLines) out.push(line);
    if (out.length > maxLines) {
      out.length = maxLines;
      out[maxLines - 1] = out[maxLines - 1].slice(0, -1) + '…';
    }
    return out;
  }

  /* 每种节点画什么：{title, lines[]} */
  function nodeContent(n) {
    switch (n.kind) {
      case 'start':
        return { title: '开始', lines: ['事件入口'] };
      case 'label':
        return { title: n.title || '::label::', lines: ['跳转目标'] };
      case 'talk':
        return { title: n.roleName || ('角色 ' + n.role),
                 lines: wrapText(n.text, NODE_W - 2 * PAD, 3) };
      case 'message':
        return { title: '旁白提示', lines: wrapText(n.text, NODE_W - 2 * PAD, 3) };
      case 'choice':
        return { title: '玩家选项',
                 lines: wrapText('「' + (n.prompt || '') + '」', NODE_W - 2 * PAD, 2) };
      case 'condition':
        return { title: '条件', lines: wrapText(n.condText || n.cond, NODE_W - 2 * PAD, 2) };
      case 'action':
        return { title: n.title || n.call,
                 lines: wrapText(n.detail || n.call, NODE_W - 2 * PAD, 2) };
      case 'end':
        return { title: '事件结束', lines: [String(n.raw || 'do return end').trim()] };
      default:
        return { title: n.title || '代码', lines: wrapText(n.code || n.raw, NODE_W - 2 * PAD, 2) };
    }
  }

  function nodeHeight(content) {
    return HEAD_H + PAD + Math.max(1, content.lines.length) * LINE_H + PAD;
  }

  class StoryGraph {
    constructor(svg, opts) {
      this.svg = svg;
      this.opts = opts || {};
      this.onSelect = this.opts.onSelect || function () {};
      this.nodes = [];
      this.edges = [];
      this.byId = {};
      this.pos = {};
      this.size = {};
      this.view = { x: 0, y: 0, k: 1 };
      this.selId = null;
      this.key = '';
      this._drag = null;
      this._pan = null;

      const defs = el('defs');
      const marker = el('marker', {
        id: 'arrow', viewBox: '0 0 10 10', refX: '9', refY: '5',
        markerWidth: '7', markerHeight: '7', orient: 'auto-start-reverse'
      });
      marker.appendChild(el('path', { d: 'M0,0 L10,5 L0,10 z', fill: '#4d5b72' }));
      defs.appendChild(marker);
      svg.appendChild(defs);

      this.world = el('g', { class: 'world' });
      this.edgeLayer = el('g', { class: 'edges' });
      this.nodeLayer = el('g', { class: 'nodes' });
      this.world.appendChild(this.edgeLayer);
      this.world.appendChild(this.nodeLayer);
      svg.appendChild(this.world);

      this._bind();
      this.applyView();
    }

    /* ------------------------------------------------------------ 视图 */
    applyView() {
      const v = this.view;
      this.world.setAttribute('transform',
        'translate(' + v.x + ',' + v.y + ') scale(' + v.k + ')');
    }

    screenToWorld(px, py) {
      const r = this.svg.getBoundingClientRect();
      return {
        x: (px - r.left - this.view.x) / this.view.k,
        y: (py - r.top - this.view.y) / this.view.k
      };
    }

    bbox() {
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      this.nodes.forEach(n => {
        const p = this.pos[n.id], s = this.size[n.id];
        minX = Math.min(minX, p.x); minY = Math.min(minY, p.y);
        maxX = Math.max(maxX, p.x + s.w); maxY = Math.max(maxY, p.y + s.h);
      });
      return { minX, minY, maxX, maxY };
    }

    fit(minK) {
      if (!this.nodes.length) return;
      const b = this.bbox();
      const rect = this.svg.getBoundingClientRect();
      const pad = 40;
      const kFit = Math.min(
        (rect.width - pad * 2) / Math.max(1, b.maxX - b.minX),
        (rect.height - pad * 2) / Math.max(1, b.maxY - b.minY));
      const k = Math.min(1.1, Math.max(minK || 0.16, kFit));
      this.view.k = k;
      this.view.x = pad - b.minX * k;                       // 左对齐：起点一眼可见
      const centered = (rect.height - (b.maxY - b.minY) * k) / 2 - b.minY * k;
      this.view.y = Math.max(pad - b.minY * k, centered);   // 竖向居中，但不越界
      this.applyView();
    }

    zoom(factor, cx, cy) {
      const rect = this.svg.getBoundingClientRect();
      const px = (cx === undefined ? rect.width / 2 : cx - rect.left);
      const py = (cy === undefined ? rect.height / 2 : cy - rect.top);
      const k = Math.min(2.2, Math.max(0.12, this.view.k * factor));
      const ratio = k / this.view.k;
      this.view.x = px - (px - this.view.x) * ratio;
      this.view.y = py - (py - this.view.y) * ratio;
      this.view.k = k;
      this.applyView();
    }

    focusNode(id) {
      const p = this.pos[id];
      if (!p) return;
      const s = this.size[id];
      const rect = this.svg.getBoundingClientRect();
      const k = Math.max(this.view.k, 0.9);
      this.view.k = k;
      this.view.x = rect.width / 2 - (p.x + s.w / 2) * k;
      this.view.y = rect.height / 2 - (p.y + s.h / 2) * k;
      this.applyView();
      this.select(id);
    }

    select(id) {
      this.selId = id;
      this.nodeLayer.querySelectorAll('.node').forEach(g => {
        g.classList.toggle('sel', g.getAttribute('data-id') === id);
      });
      if (this.byId[id]) this.onSelect(this.byId[id]);
    }

    /* ------------------------------------------------------------ 交互 */
    _bind() {
      const svg = this.svg;
      svg.addEventListener('wheel', ev => {
        ev.preventDefault();
        this.zoom(ev.deltaY < 0 ? 1.12 : 1 / 1.12, ev.clientX, ev.clientY);
      }, { passive: false });

      svg.addEventListener('pointerdown', ev => {
        const hit = ev.target.closest && ev.target.closest('.node');
        if (hit) {
          const id = hit.getAttribute('data-id');
          this.select(id);
          const start = this.screenToWorld(ev.clientX, ev.clientY);
          const p = this.pos[id];
          this._drag = { id, dx: p.x - start.x, dy: p.y - start.y, moved: false };
          svg.setPointerCapture(ev.pointerId);
          return;
        }
        this._pan = { x: ev.clientX, y: ev.clientY, vx: this.view.x, vy: this.view.y };
        svg.classList.add('panning');
        svg.setPointerCapture(ev.pointerId);
      });

      svg.addEventListener('pointermove', ev => {
        if (this._drag) {
          const w = this.screenToWorld(ev.clientX, ev.clientY);
          const p = this.pos[this._drag.id];
          p.x = w.x + this._drag.dx;
          p.y = w.y + this._drag.dy;
          this._drag.moved = true;
          this.placeNode(this._drag.id);
          this.drawEdges();
          return;
        }
        if (this._pan) {
          this.view.x = this._pan.vx + (ev.clientX - this._pan.x);
          this.view.y = this._pan.vy + (ev.clientY - this._pan.y);
          this.applyView();
        }
      });

      const end = () => {
        if (this._drag && this._drag.moved) this.savePositions();
        this._drag = null;
        this._pan = null;
        svg.classList.remove('panning');
      };
      svg.addEventListener('pointerup', end);
      svg.addEventListener('pointercancel', end);
      svg.addEventListener('dblclick', ev => {
        const hit = ev.target.closest && ev.target.closest('.node');
        if (hit) this.focusNode(hit.getAttribute('data-id'));
        else this.fit();
      });
    }

    /* ------------------------------------------------------------ 数据 */
    setData(graph) {
      this.graph = graph;
      this.nodes = graph.nodes || [];
      this.edges = graph.edges || [];
      this.byId = {};
      this.size = {};
      this.selId = null;
      // 位置按事件号存（不带 mtime）：改一句台词不会把手工摆的位置清掉
      this.key = 'storyeditor:pos:' + graph.event;
      this.nodes.forEach(n => {
        n._content = nodeContent(n);
        this.byId[n.id] = n;
        this.size[n.id] = { w: NODE_W, h: nodeHeight(n._content) };
      });
      this.nodeLayer.innerHTML = '';
      this.edgeLayer.innerHTML = '';
      this.pos = {};
      if (!this._loadPositions()) this.layout();
      this.render();
      this.fit();               // 先给全貌（结构一眼看完），双击节点可放大到可读尺寸
    }

    /* 分层布局：沿边做最长路径定列，列内按源码行号排 */
    layout() {
      const rank = {};
      const maxRank = Math.min(60, this.nodes.length);
      this.nodes.forEach(n => { rank[n.id] = 0; });
      for (let pass = 0; pass < maxRank; pass++) {
        let changed = false;
        this.edges.forEach(e => {
          if (!(e.from in rank) || !(e.to in rank)) return;
          if (rank[e.from] >= maxRank) return;          // 环路：别再往前推
          const want = rank[e.from] + 1;
          if (rank[e.to] < want && want <= maxRank) {
            rank[e.to] = want;
            changed = true;
          }
        });
        if (!changed) break;
      }
      const columns = {};
      this.nodes.forEach((n, i) => {
        const r = rank[n.id] || 0;
        (columns[r] = columns[r] || []).push({ n, i });
      });
      const heights = {};
      Object.keys(columns).forEach(r => {
        columns[r].sort((a, b) => (a.n.line || 0) - (b.n.line || 0) || a.i - b.i);
        heights[r] = columns[r].reduce((sum, it) => sum + this.size[it.n.id].h + ROW_GAP, 0);
      });
      const tallest = Math.max.apply(null, Object.keys(heights).map(r => heights[r]));
      Object.keys(columns).forEach(r => {
        let y = (tallest - heights[r]) / 2;          // 每列竖向居中，短列不贴顶
        columns[r].forEach(item => {
          this.pos[item.n.id] = { x: Number(r) * COL_GAP, y };
          y += this.size[item.n.id].h + ROW_GAP;
        });
      });
      this._savedByUser = false;
    }

    _loadPositions() {
      if (!this.key) return false;
      try {
        const raw = window.localStorage.getItem(this.key);
        if (!raw) return false;
        const saved = JSON.parse(raw);
        const ids = Object.keys(saved);
        if (ids.length !== this.nodes.length) return false;
        if (!this.nodes.every(n => saved[n.id])) return false;
        this.pos = saved;
        this._savedByUser = true;
        return true;
      } catch (err) {
        return false;
      }
    }

    savePositions() {
      if (!this.key) return;
      try {
        window.localStorage.setItem(this.key, JSON.stringify(this.pos));
      } catch (err) { /* 隐私模式就算了 */ }
    }

    resetLayout() {
      this.layout();
      this.render();
      this.fit();
    }

    /* ------------------------------------------------------------ 绘制 */
    render() {
      this.nodeLayer.innerHTML = '';
      this.nodes.forEach(n => {
        const g = el('g', { class: 'node k-' + n.kind + (n.orphan ? ' orphan' : ''),
                            'data-id': n.id });
        const s = this.size[n.id];
        const accent = {
          start: '#2f9e57', label: '#2f9e9e', talk: '#2f6df6', choice: '#9257e8',
          condition: '#c8871f', action: '#a45cf0', message: '#3d7d8c',
          end: '#c8503f', code: '#46536b'
        }[n.kind] || '#46536b';

        g.appendChild(el('rect', { class: 'box', x: 0, y: 0, width: s.w, height: s.h, rx: 10 }));
        g.appendChild(el('rect', { x: 0, y: 8, width: 4, height: Math.max(10, s.h - 16),
                                   rx: 2, fill: accent }));

        let tx = PAD + 6;
        if (n.kind === 'talk' && n.headId != null) {
          const href = '/api/head/' + n.headId + '.png';
          const img = el('image', { x: PAD, y: 3, width: 16, height: 16,
                                    preserveAspectRatio: 'xMidYMid slice', href: href });
          img.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', href);
          g.appendChild(img);
          tx += 20;
        }

        let title = n._content.title;
        if (n.kind === 'talk' && n.expr) title += ' · ' + n.expr;
        const titleText = el('text', { class: 'title', x: tx, y: 16 });
        titleText.textContent = title;
        g.appendChild(titleText);

        if (n.line) {
          const ln = el('text', { class: 'line-no', x: s.w - PAD, y: 16,
                                  'text-anchor': 'end' });
          ln.textContent = 'L' + n.line;
          g.appendChild(ln);
        }

        n._content.lines.forEach((line, i) => {
          const t = el('text', {
            class: (n.kind === 'talk' || n.kind === 'message') ? 'body' : 'detail',
            x: PAD + 6, y: HEAD_H + PAD + 11 + i * LINE_H
          });
          t.textContent = line;
          g.appendChild(t);
        });

        this.nodeLayer.appendChild(g);
        this.placeNode(n.id);
      });
      this.drawEdges();
    }

    placeNode(id) {
      const g = this.nodeLayer.querySelector('[data-id="' + id + '"]');
      const p = this.pos[id];
      if (g && p) g.setAttribute('transform', 'translate(' + p.x + ',' + p.y + ')');
    }

    drawEdges() {
      this.edgeLayer.innerHTML = '';
      this.edges.forEach(e => {
        const sp = this.pos[e.from], ss = this.size[e.from];
        const tp = this.pos[e.to], ts = this.size[e.to];
        if (!sp || !ss || !tp || !ts) return;

        const forward = tp.x >= sp.x + ss.w - 4;
        let x1, y1, x2, y2;
        if (forward) {
          x1 = sp.x + ss.w; y1 = sp.y + ss.h / 2;
          x2 = tp.x; y2 = tp.y + ts.h / 2;
        } else {
          x1 = sp.x; y1 = sp.y + ss.h / 2;
          x2 = tp.x + ts.w; y2 = tp.y + ts.h / 2;
        }
        const dir = forward ? 1 : -1;
        const dx = Math.max(40, Math.min(180, Math.abs(x2 - x1) * 0.55)) * dir;
        const path = el('path', {
          class: 'edge ' + (e.kind || 'flow'),
          d: 'M' + x1 + ',' + y1 + ' C' + (x1 + dx) + ',' + y1 + ' '
             + (x2 - dx) + ',' + y2 + ' ' + x2 + ',' + y2,
          'marker-end': 'url(#arrow)'
        });
        this.edgeLayer.appendChild(path);

        if (e.label) {
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2;
          const w = String(e.label).length * 11 + 8;
          this.edgeLayer.appendChild(el('rect', {
            class: 'edge-label-bg', x: mx - w / 2, y: my - 8, width: w, height: 14, rx: 7
          }));
          const t = el('text', { class: 'edge-label', x: mx, y: my + 2,
                                 'text-anchor': 'middle' });
          t.textContent = e.label;
          this.edgeLayer.appendChild(t);
        }
      });
    }
  }

  window.StoryGraph = StoryGraph;
  window.StoryGraph.util = { wrapText, nodeContent, nodeHeight };
}());
