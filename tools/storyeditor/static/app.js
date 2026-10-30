/* 剧情编辑器主逻辑：左侧列表 / 中间节点图 / 右侧详情与改词 */
(function () {
  'use strict';

  const $ = sel => document.querySelector(sel);
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const state = { meta: null, events: [], graph: null, node: null, filter: '', view: 'graph' };
  let graphApp = null;

  /* ---------------------------------------------------------------- 工具 */
  async function api(path, opts) {
    const res = await fetch(path, Object.assign({ headers: { 'Content-Type': 'application/json' } },
      opts || {}));
    let data;
    try {
      data = await res.json();
    } catch (err) {
      throw new Error('服务返回的不是 JSON（HTTP ' + res.status + '）');
    }
    if (!res.ok || data.ok === false) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
  }

  let toastTimer = null;
  function toast(msg, kind) {
    const box = $('#toast');
    box.textContent = msg;
    box.className = kind || '';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { box.className = 'hidden'; }, kind === 'err' ? 6000 : 3200);
  }

  function headUrl(id) {
    return id == null ? '' : '/api/head/' + id + '.png';
  }

  /* ---------------------------------------------------------------- 入口（在哪张图 / 怎么触发） */
  function entryKind(kind) {
    const list = (state.meta && state.meta.entryKinds) || [];
    return list.find(k => k.kind === kind) || { kind: kind, label: kind, hint: '' };
  }

  function kindLabel(kind) {
    return entryKind(kind).label;
  }

  function fmtPos(pos) {
    if (!pos) return '';
    return '(' + pos.map(v => Math.round(Number(v) * 10) / 10).join(', ') + ')';
  }

  // 一个入口一行：交互 · Level/Triggers/5 · (0.8, 5.5, -6.0)
  function entryText(t, withMap) {
    const parts = [];
    if (withMap && t.map) parts.push(t.map);
    parts.push(kindLabel(t.kind));
    if (t.kind === 'leave') {
      if (t.char) parts.push('「' + t.char + '」');
    } else if (t.object) {
      parts.push(t.object);
    }
    if (t.pos) parts.push(fmtPos(t.pos));
    return parts.join(' · ');
  }

  function entryChipHTML(t, withMap) {
    const info = entryKind(t.kind);
    const unreg = t.registered === false && t.scene;
    const tip = info.hint + (unreg ? '\n⚠ 这张图没在 MapConfig 登记，玩家正常玩进不去' : '');
    return '<span class="entry-chip ' + t.kind + (unreg ? ' unreg' : '') +
      '" title="' + esc(tip) + '">' + (unreg ? '⚠ ' : '') +
      esc(entryText(t, withMap)) + '</span>';
  }

  function noEntryHTML() {
    return '<span class="entry-chip warn" title="地图里没有 GameEvent 指向它：可能只是被别的事件/' +
      '控制台临时调用，也可能已经废弃">⚠ 没有任何入口，玩家正常玩进不来</span>';
  }

  function renderEntryBar(g) {
    const bar = $('#entryBar');
    const trs = (g && g.triggers) || [];
    bar.classList.remove('hidden');
    const list = $('#entryList');
    if (!trs.length) {
      $('#entryMap').textContent = '未挂接';
      $('#entryScene').textContent = '';
      $('#entryHint').textContent = '';
      list.innerHTML = noEntryHTML();
      return;
    }
    const maps = [];
    const scenes = [];
    trs.forEach(t => {
      if (t.map && maps.indexOf(t.map) < 0) maps.push(t.map);
      if (t.scene && scenes.indexOf(t.scene) < 0) scenes.push(t.scene);
    });
    const sceneTrs = trs.filter(t => t.scene);
    const allUnreg = sceneTrs.length > 0 && !sceneTrs.some(t => t.registered);
    const mapText = maps.length > 2
      ? maps.slice(0, 2).join(' / ') + ' 等 ' + maps.length + ' 张图'
      : maps.join(' / ');
    $('#entryMap').textContent = (maps.length ? mapText : '不在任何地图里') +
      (allUnreg ? '（MapConfig 未登记）' : '');
    $('#entryScene').textContent = (scenes.length ? '场景 ' + scenes.join('、') : '') +
      (trs[0].mapId != null ? ' · 地图 id ' + trs[0].mapId : '');
    const kinds = [];
    trs.forEach(t => { if (kinds.indexOf(t.kind) < 0) kinds.push(t.kind); });
    $('#entryHint').textContent = '共 ' + trs.length + ' 处入口：' +
      kinds.map(kindLabel).join(' / ') + '（悬停看触发方式）';
    // 多张图时每条都带地图名，免得不知道是哪张图的触发点
    const withMap = maps.length > 1;
    list.innerHTML = trs.map(t => entryChipHTML(t, withMap)).join('');
    if (allUnreg) {
      list.innerHTML += '<span class="entry-chip warn" title="MapConfig.lua 里没有这张图，' +
        '游戏不会加载它；要启用得先在地图表里登记，再在大地图加落点">⚠ 这几张图都没在 ' +
        'MapConfig 登记，玩家进不去</span>';
    }
  }

  // 列表分组用：优先「已登记的地图」，其次离队剧情，最后「没挂接」
  function primaryGroup(e) {
    const trs = (e.triggers || []).filter(t => t.scene);
    const t = trs.find(x => x.registered) || trs[0];
    if (t) return t.map;
    if ((e.triggers || []).some(x => x.kind === 'leave')) return '侠客离队剧情';
    return '未挂接任何入口';
  }

  const GROUP_ORDER = { '未挂接任何入口': 2, '侠客离队剧情': 1 };

  /* ---------------------------------------------------------------- 列表 */
  function renderSidebar() {
    const list = $('#eventList');
    const q = state.filter.trim().toLowerCase();
    const events = state.events.filter(e => {
      if (!q) return true;
      if (e.id.indexOf(q) >= 0) return true;
      if ((e.title || '').toLowerCase().indexOf(q) >= 0) return true;
      if (e.speakers.some(s => (s.name || '').toLowerCase().indexOf(q) >= 0)) return true;
      return (e.search || '').toLowerCase().indexOf(q) >= 0;
    });

    $('#eventCount').textContent = events.length + ' / ' + state.events.length;

    const groups = new Map();
    events.forEach(e => {
      const where = primaryGroup(e);
      if (!groups.has(where)) groups.set(where, []);
      groups.get(where).push(e);
    });

    const frag = document.createDocumentFragment();
    const names = Array.from(groups.keys()).sort((a, b) => {
      const oa = GROUP_ORDER[a] == null ? 0 : GROUP_ORDER[a];
      const ob = GROUP_ORDER[b] == null ? 0 : GROUP_ORDER[b];
      if (oa !== ob) return oa - ob;
      return a.localeCompare(b, 'zh-Hans-CN');
    });
    names.forEach(where => {
      const grp = groups.get(where);
      const allUnreg = grp.every(e => {
        const st = (e.triggers || []).filter(t => t.scene);
        return st.length > 0 && !st.some(t => t.registered);
      });
      const head = document.createElement('div');
      head.className = 'group-title';
      head.innerHTML = esc(where) + ' <span class="muted">' + grp.length + ' 条</span>' +
        (allUnreg ? ' <span class="chip entry-none" title="MapConfig 里没登记这张图，' +
          '玩家正常玩进不去">未登记</span>' : '');
      frag.appendChild(head);
      grp.forEach(e => frag.appendChild(eventRow(e)));
    });
    list.innerHTML = '';
    list.appendChild(frag);
    if (state.graph) markActive(state.graph.event);
  }

  function eventRow(e) {
    const li = document.createElement('li');
    li.dataset.id = e.id;
    const chips = [];
    const kinds = e.kinds || [];
    if (!kinds.length) chips.push('<span class="chip entry-none">无入口</span>');
    else kinds.forEach(k => chips.push('<span class="chip entry-' + k + '">' +
      esc(kindLabel(k)) + '</span>'));
    if ((e.scenes || []).length > 1) {
      chips.push('<span class="chip">' + e.scenes.length + ' 张图</span>');
    }
    const sceneTrs = (e.triggers || []).filter(t => t.scene);
    if (sceneTrs.length && !sceneTrs.some(t => t.registered)) {
      chips.push('<span class="chip entry-none" title="MapConfig 里没登记，玩家进不去">图未登记</span>');
    }
    if (e.choices) chips.push('<span class="chip choice">选项 ' + e.choices + '</span>');
    if (e.flags.length) chips.push('<span class="chip flag">旗标 ' + e.flags.length + '</span>');
    if (e.battles.length) chips.push('<span class="chip battle">战斗 ' + e.battles.length + '</span>');
    const where = primaryGroup(e);
    li.title = where + ' · ' + ((e.triggers || []).map(t => entryText(t, false)).join('；') ||
      '没有任何入口');
    li.innerHTML =
      '<div class="ev-top"><span class="ev-id">' + esc(e.id) + '</span>' +
      '<span class="ev-title">' + esc(e.title || '(无标题)') + '</span></div>' +
      '<div class="ev-meta"><span class="avatars">' +
      e.speakers.slice(0, 4).map(s =>
        '<img src="' + headUrl(s.headId) + '" title="' + esc(s.name) + '">').join('') +
      '</span><span>' + e.talks + ' 句</span>' + chips.join('') + '</div>';
    li.addEventListener('click', () => openEvent(e.id));
    return li;
  }

  function markActive(id) {
    document.querySelectorAll('#eventList li').forEach(li => {
      li.classList.toggle('active', li.dataset.id === id);
    });
  }

  /* ---------------------------------------------------------------- 打开事件 */
  async function openEvent(id, keepLine) {
    try {
      const graph = await api('/api/event/' + id + '?source=1');
      state.graph = graph;
      state.node = null;
      $('#graphTitle').textContent = '#' + id + ' · ' + (graph.title || graph.file) +
        '（' + graph.stats.talk + ' 句）';
      renderEntryBar(graph);
      graphApp.setData(graph);
      markActive(id);
      try { history.replaceState(null, '', '#' + id); } catch (err) { /* file:// 下会抛 */ }
      if (state.view === 'timeline') renderTimeline();
      if (keepLine) {
        const node = graph.nodes.find(n => n.line === keepLine);
        if (node) {
          graphApp.focusNode(node.id);
          return;
        }
      }
      renderInspector(null);
    } catch (err) {
      toast('打开 #' + id + ' 失败：' + err.message, 'err');
    }
  }

  /* ---------------------------------------------------------------- 视图切换 */
  function setView(view) {
    state.view = view;
    try { window.localStorage.setItem('storyeditor:view', view); } catch (err) { /* 忽略 */ }
    document.querySelectorAll('#viewToggle button').forEach(b => {
      b.classList.toggle('on', b.dataset.view === view);
    });
    $('#canvasWrap').classList.toggle('hidden', view !== 'graph');
    $('#timeline').classList.toggle('hidden', view !== 'timeline');
    // 只对节点图有意义的按钮，在台词表里藏起来
    const graphOnly = ['layout', 'fit', 'zoomIn', 'zoomOut', 'start'];
    document.querySelectorAll('#graphToolbar button[data-act]').forEach(b => {
      if (graphOnly.indexOf(b.dataset.act) >= 0) b.classList.toggle('hidden', view !== 'graph');
    });
    if (view === 'timeline') renderTimeline();
    else if (state.graph) graphApp.applyView();
  }

  function renderTimeline() {
    const box = $('#timeline');
    const g = state.graph;
    if (!g) {
      box.innerHTML = '<div class="tl-empty">还没有选中剧情</div>';
      return;
    }
    const nodes = g.nodes.slice().sort((a, b) => (a.line || 0) - (b.line || 0));
    const frag = document.createDocumentFragment();
    nodes.forEach(n => {
      if (n.kind === 'start') {
        frag.appendChild(markRow(n));
      } else if (n.kind === 'label') {
        const sep = document.createElement('div');
        sep.className = 'tl-sep';
        sep.textContent = '::' + n.name + '::  跳转目标（第 ' + n.line + ' 行）';
        sep.addEventListener('click', () => pickNode(n));
        frag.appendChild(sep);
      } else if (n.kind === 'talk') {
        frag.appendChild(talkRow(n));
      } else {
        frag.appendChild(markRow(n));
      }
    });
    box.innerHTML = '';
    box.appendChild(frag);
    highlightTimeline();
  }

  function talkRow(n) {
    const row = document.createElement('div');
    row.className = 'tl-row';
    row.dataset.line = n.line;
    row.innerHTML = '<img src="' + headUrl(n.headId) + '">' +
      '<div class="tl-who">' + esc(n.roleName) +
      '<small>' + (n.expr ? esc(n.expr) : '') + '</small></div>' +
      '<div class="tl-text">' + esc(n.text) + '</div>' +
      '<div class="tl-line">L' + n.line + '</div>';
    row.addEventListener('click', () => pickNode(n));
    return row;
  }

  function markRow(n) {
    const row = document.createElement('div');
    row.className = 'tl-mark ' + n.kind;
    row.dataset.line = n.line || 0;
    let text;
    if (n.kind === 'start') {
      const trs = (state.graph && state.graph.triggers) || [];
      text = '<b>开始</b> ' + (trs.length
        ? '入口：' + esc(entryText(trs[0], true)) +
          (trs.length > 1 ? ' 等 ' + trs.length + ' 处' : '')
        : '入口：地图里没有挂这条剧情');
    } else if (n.kind === 'condition') {
      text = '<b>条件</b> ' + esc(n.condText || n.cond);
    } else if (n.kind === 'choice') {
      text = '<b>玩家选项</b> 「' + esc(n.prompt) + '」';
    } else if (n.kind === 'message') {
      text = '<b>旁白</b> ' + esc(n.text);
    } else if (n.kind === 'end') {
      text = '<b>事件结束</b> ' + esc(n.raw || '');
    } else if (n.kind === 'code') {
      text = '<b>代码</b> ' + esc(n.code || n.raw);
    } else {
      text = '<b>' + esc(n.title || '') + '</b> ' + esc(n.detail || '');
    }
    row.innerHTML = text + ' <span class="tl-line">' + (n.line ? 'L' + n.line : '') + '</span>';
    row.addEventListener('click', () => pickNode(n));
    return row;
  }

  function pickNode(n) {
    renderInspector(n);
    highlightTimeline();
    if (state.view === 'graph' && graphApp.byId[n.id]) graphApp.focusNode(n.id);
  }

  function highlightTimeline() {
    const line = state.node ? state.node.line : null;
    document.querySelectorAll('#timeline .tl-row, #timeline .tl-mark').forEach(el => {
      el.classList.toggle('sel', Number(el.dataset.line) === line);
    });
  }

  /* ---------------------------------------------------------------- 概览 */
  function triggerSectionHTML(g) {
    const trs = g.triggers || [];
    const hinted = [];
    const rows = ['<div class="section-title">触发入口（在哪张图、怎么进）</div>'];
    if (!trs.length) {
      rows.push('<div class="err">地图里没有任何 GameEvent 指向这条剧情：玩家正常玩进不来。' +
        '可能是被别的事件动态 <code>ModifyEvent</code> 挂上、控制台手动跑，或者已经废弃。</div>');
      return rows.join('');
    }
    trs.forEach(t => {
      const info = entryKind(t.kind);
      let where;
      if (t.kind === 'leave') {
        where = '侠客「' + esc(t.char || '?') + '」离队时播（人物表 LeaveStoryId）';
      } else {
        where = esc(t.map || '?') + (t.scene ? '（' + esc(t.scene) + '）' : '') +
          ' · <b>' + esc(t.object || '?') + '</b>' + (t.pos ? ' @' + esc(fmtPos(t.pos)) : '') +
          (t.registered === false ? ' <span class="err">（MapConfig 未登记，玩家进不去）</span>' : '');
      }
      rows.push('<div class="entry-row"><span class="chip entry-' + t.kind + '">' +
        esc(info.label) + '</span><span>' + where + '</span></div>');
      if (info.hint && hinted.indexOf(t.kind) < 0) {
        hinted.push(t.kind);
        rows.push('<div class="note">' + esc(info.hint) + '</div>');
      }
    });
    return rows.join('');
  }

  function summaryHTML() {
    const g = state.graph;
    if (!g) return '<div class="empty">还没有选中剧情</div>';
    const s = g.stats;
    const rows = [];
    rows.push(triggerSectionHTML(g));
    rows.push('<div class="section-title">这条剧情</div>');
    const maps = [];
    (g.triggers || []).forEach(t => {
      if (t.map && maps.indexOf(t.map) < 0) maps.push(t.map);
    });
    rows.push('<div class="kv">文件 <b>' + esc(g.file) + '</b> · ' + g.lineCount + ' 行 · ' +
      (maps.length ? esc(maps.join('、')) : '未挂地图') + '</div>');
    rows.push('<div class="kv">节点：对白 <b>' + s.talk + '</b> / 动作 <b>' + s.action +
      '</b> / 条件 <b>' + s.condition + '</b> / 选项 <b>' + s.choice + '</b> / 跳转点 <b>' +
      s.label + '</b> / 结束 <b>' + s.end + '</b></div>');
    if (s.flags.length) {
      rows.push('<div class="section-title">会写到的旗标</div><div class="tags">' +
        s.flags.map(f => '<span class="chip flag">' + esc(f) + '</span>').join('') + '</div>');
    }
    if (s.items.length) {
      rows.push('<div class="section-title">物品</div><div class="tags">' +
        (s.itemNames || s.items).map(t => '<span class="chip">' + esc(t) + '</span>').join('') +
        '</div>');
    }
    if (s.battles.length) {
      rows.push('<div class="section-title">战斗</div><div class="tags">' +
        (s.battleNames || s.battles).map(t => '<span class="chip battle">' + esc(t) +
          '</span>').join('') + '</div>');
    }
    if (s.skills && s.skills.length) {
      rows.push('<div class="section-title">武功</div><div class="tags">' +
        (s.skillNames || s.skills).map(t => '<span class="chip">' + esc(t) + '</span>').join('') +
        '</div>');
    }
    if (s.npcs.length) {
      rows.push('<div class="section-title">场景 NPC 显隐</div><div class="kv">' +
        s.npcs.map(n => esc(n)).join('<br>') + '</div>');
    }
    if (g.errors && g.errors.length) {
      rows.push('<div class="section-title">解析告警</div><div class="err">' +
        g.errors.map(e => '第 ' + e.line + ' 行：' + esc(e.message)).join('<br>') + '</div>');
    }
    rows.push('<div class="section-title">说话人</div><div class="kv">' +
      g.speakers.map((r, i) => esc(g.speakerNames[i]) + '（' + r + '）').join('、') + '</div>');
    rows.push('<hr class="sep"><div class="note">点画布上的节点看详情；对白节点可以直接改词、' +
      '换说话人、换表情。</div>');
    return rows.join('');
  }

  /* ---------------------------------------------------------------- 详情 */
  function renderInspector(node) {
    const box = $('#inspector');
    state.node = node;
    highlightTimeline();
    if (!node) {
      box.innerHTML = '<div class="section-title">本幕概览</div>' + summaryHTML();
      return;
    }
    if (node.kind === 'talk') {
      box.innerHTML = talkHTML(node);
      bindLine(node, 'talk');
      return;
    }
    if (node.kind === 'message') {
      box.innerHTML = messageHTML(node);
      bindLine(node, 'message');
      return;
    }
    box.innerHTML = readonlyHTML(node);
  }

  function talkHTML(n) {
    const chars = state.meta.characters.map(c =>
      '<option value="' + c.id + '"' + (c.id === n.role ? ' selected' : '') + '>' +
      esc(c.name) + '（' + c.id + '）</option>').join('');
    const exprs = ['<option value="">（默认头像）</option>'].concat(
      state.meta.exprs.filter(e => /^[a-z]+$/.test(e.key)).map(e =>
        '<option value="' + e.key + '"' + (e.key === n.expr ? ' selected' : '') + '>' +
        e.key + ' · 槽位 ' + e.slot + '</option>')).join('');
    const len = String(n.text || '').length;
    return '' +
      '<div class="insp-head"><img id="edHead" src="' + headUrl(n.headId) + '">' +
      '<div><div class="who">' + esc(n.roleName) + '</div>' +
      '<div class="sub">人物 id ' + n.role + ' · 第 ' + n.line + ' 行' +
      (n.expr ? ' · 表情 ' + esc(n.expr) : '') + '</div></div></div>' +
      '<div class="field"><label>说话人</label><select id="edRole">' + chars + '</select></div>' +
      '<div class="field"><label>表情（Talk 的第三个参数 EXPR.x）</label>' +
      '<select id="edExpr">' + exprs + '</select></div>' +
      '<div class="field"><label>台词（Ctrl+Enter 保存）</label>' +
      '<textarea id="edText">' + esc(n.text) + '</textarea></div>' +
      '<div class="note' + (len > 156 ? ' warn' : '') + '">' + len + ' 字' +
      (len > 156 ? ' · 超过 156 字游戏会按标点强制分段，富文本标签可能被切断' : '') + '</div>' +
      '<div class="actions"><button class="primary" id="edSave">保存这一句</button>' +
      '<button class="ghost" id="edRevert">还原</button></div>' +
      '<div class="section-title">源码</div><div class="raw">' + esc(n.raw) + '</div>';
  }

  function messageHTML(n) {
    const len = String(n.text || '').length;
    return '' +
      '<div class="insp-head"><div><div class="who">旁白 / 系统提示</div>' +
      '<div class="sub">第 ' + n.line + ' 行 · ShowMessage</div></div></div>' +
      '<div class="field"><label>文本（Ctrl+Enter 保存）</label>' +
      '<textarea id="edText">' + esc(n.text) + '</textarea></div>' +
      '<div class="note' + (len > 156 ? ' warn' : '') + '">' + len + ' 字</div>' +
      '<div class="actions"><button class="primary" id="edSave">保存这一句</button>' +
      '<button class="ghost" id="edRevert">还原</button></div>' +
      '<div class="section-title">源码</div><div class="raw">' + esc(n.raw) + '</div>';
  }

  function readonlyHTML(n) {
    const names = { start: '开始', label: '跳转目标', choice: '玩家选项', condition: '条件',
                    action: '动作', end: '事件结束', code: '代码' };
    let extra = '';
    if (n.params && Object.keys(n.params).length) {
      extra = '<div class="section-title">参数</div>' + Object.keys(n.params).map(k => {
        let v = n.params[k];
        if (Array.isArray(v)) v = v.join(', ');
        if (v && typeof v === 'object') v = JSON.stringify(v);
        return '<div class="kv">' + esc(k) + '：<b>' + esc(v) + '</b></div>';
      }).join('');
    }
    return '' +
      '<div class="section-title">' + (names[n.kind] || n.kind) + '</div>' +
      '<div class="kv"><b>' + esc(n.title || '') + '</b>' +
      (n.detail ? ' · ' + esc(n.detail) : '') + '</div>' +
      (n.condText ? '<div class="section-title">条件</div><div class="kv">' +
        esc(n.condText) + '</div>' : '') +
      (n.prompt ? '<div class="section-title">选项文字</div><div class="kv">' +
        esc(n.prompt) + '</div>' : '') +
      extra +
      '<div class="section-title">源码（第 ' + (n.line || '?') + ' 行）</div>' +
      '<div class="raw">' + esc(n.raw || '') + '</div>' +
      '<div class="note">这类节点暂时只读：改它会动到分支结构，留到下一版。</div>';
  }

  /* ---------------------------------------------------------------- 改词 */
  function bindLine(node, kind) {
    const roleSel = $('#edRole');
    if (roleSel) {
      roleSel.addEventListener('change', () => {
        const img = $('#edHead');
        if (img) img.src = '/api/head/' + Number(roleSel.value) + '.png';
      });
    }
    const ta = $('#edText');
    ta.addEventListener('keydown', ev => {
      if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') {
        ev.preventDefault();
        saveLine(node, kind);
      }
    });
    $('#edSave').addEventListener('click', () => saveLine(node, kind));
    $('#edRevert').addEventListener('click', () => renderInspector(node));
  }

  function prettyIssues(res) {
    const lines = [];
    (res.issues || []).forEach(it => lines.push('lint 第 ' + it.line + ' 行：' + it.message));
    (res.graphErrors || []).forEach(it => lines.push('图 第 ' + it.line + ' 行：' + it.message));
    return lines.join('\n') || '（没有提示）';
  }

  async function saveLine(node, kind) {
    const payload = { line: node.line, expect: node.raw, kind };
    if (kind === 'talk') {
      payload.role = Number($('#edRole').value);
      payload.expr = $('#edExpr').value || null;
    }
    payload.text = $('#edText').value;

    try {
      const res = await api('/api/event/' + state.graph.event + '/line',
        { method: 'POST', body: JSON.stringify(payload) });
      if (!res.changed) {
        toast('内容和原来一样，没有写盘');
        return;
      }
      const bad = (res.issues || []).length + (res.graphErrors || []).length;
      toast('已写回第 ' + res.line + ' 行' +
        (bad ? '，但有 ' + bad + ' 条自检提示' : '，语法自检通过'), bad ? 'err' : 'ok');
      if (bad) showModal('保存后的自检提示', prettyIssues(res));
      await openEvent(state.graph.event, res.line);
      await reloadEvents();
    } catch (err) {
      toast('保存失败：' + err.message, 'err');
    }
  }

  /* ---------------------------------------------------------------- 工具栏 */
  function bindToolbar() {
    document.querySelectorAll('#graphToolbar button[data-act]').forEach(btn => {
      btn.addEventListener('click', () => {
        const act = btn.dataset.act;
        if (act === 'layout') graphApp.resetLayout();
        else if (act === 'fit') graphApp.fit();
        else if (act === 'zoomIn') graphApp.zoom(1.2);
        else if (act === 'zoomOut') graphApp.zoom(1 / 1.2);
        else if (act === 'start') {
          const first = state.graph && state.graph.nodes.find(n => n.kind === 'start');
          if (first) graphApp.focusNode(first.id);
        } else if (act === 'json') exportJSON();
        else if (act === 'source') openSource();
      });
    });
  }

  function exportJSON() {
    if (!state.graph) return;
    const copy = Object.assign({}, state.graph);
    delete copy.source;
    const blob = new Blob([JSON.stringify(copy, null, 1)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'story_' + state.graph.event + '.json';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  function showModal(title, content) {
    $('#modalTitle').textContent = title;
    const body = $('#modalBody');
    body.innerHTML = '';
    if (typeof content === 'string') {
      body.style.whiteSpace = 'pre-wrap';
      body.textContent = content;
    } else {
      body.style.whiteSpace = 'normal';
      body.appendChild(content);
    }
    $('#modal').classList.remove('hidden');
  }

  /* ---------------------------------------------------------------- 源码 / 校验 / 刷新 */
  function openSource() {
    if (!state.graph) return;
    const wrap = document.createElement('div');
    const ta = document.createElement('textarea');
    ta.value = state.graph.source || '';
    ta.spellcheck = false;
    ta.style.minHeight = '46vh';
    ta.style.fontFamily = 'ui-monospace, Consolas, monospace';
    ta.style.fontSize = '12px';

    const bar = document.createElement('div');
    bar.className = 'actions';
    const save = document.createElement('button');
    save.className = 'primary';
    save.textContent = '保存整份源码';
    const note = document.createElement('span');
    note.className = 'note';
    note.textContent = '保存前会做块配平体检；改完记得跑一次「校验剧本」。';
    bar.appendChild(save);
    bar.appendChild(note);

    wrap.appendChild(ta);
    wrap.appendChild(bar);
    showModal('源码 · ' + state.graph.file + '（' + state.graph.lineCount + ' 行）', wrap);

    save.addEventListener('click', async () => {
      save.disabled = true;
      try {
        await api('/api/event/' + state.graph.event + '/source', {
          method: 'POST',
          body: JSON.stringify({ text: ta.value, mtime: state.graph.mtime })
        });
        toast('源码已保存', 'ok');
        $('#modal').classList.add('hidden');
        await openEvent(state.graph.event);
        await reloadEvents();
      } catch (err) {
        toast('保存失败：' + err.message, 'err');
      } finally {
        save.disabled = false;
      }
    });
  }

  async function runValidate() {
    toast('正在跑 lint_lua.py + check_story.py …');
    try {
      const res = await api('/api/validate', { method: 'POST' });
      const parts = Object.keys(res.results).map(k => {
        const r = res.results[k];
        return '== ' + k + (r.ok ? '   [ok]' : '   [失败]') + ' ==\n' + r.output;
      });
      showModal('剧本校验', parts.join('\n\n'));
    } catch (err) {
      toast('校验失败：' + err.message, 'err');
    }
  }

  async function refresh() {
    try {
      await api('/api/refresh', { method: 'POST' });
      await loadMeta();
      await reloadEvents();
      toast('已重读配置表与场景索引', 'ok');
    } catch (err) {
      toast('刷新失败：' + err.message, 'err');
    }
  }

  /* ---------------------------------------------------------------- 启动 */
  function updateBrand() {
    const m = state.meta;
    const c = m.counts;
    $('#modName').textContent = (m.modName || m.modId) + ' · ' + c.events + ' 条剧情 / ' +
      c.characters + ' 人物 / ' + c.items + ' 物品 / ' + c.maps + ' 场景 · 主角「' +
      m.playerName + '」';
  }

  async function loadMeta() {
    state.meta = await api('/api/meta');
    updateBrand();
  }

  async function reloadEvents() {
    const res = await api('/api/events');
    state.events = res.events;
    renderSidebar();
  }

  async function init() {
    graphApp = new window.StoryGraph($('#canvas'), { onSelect: renderInspector });
    bindToolbar();
    document.querySelectorAll('#viewToggle button').forEach(btn => {
      btn.addEventListener('click', () => setView(btn.dataset.view));
    });
    $('#search').addEventListener('input', ev => {
      state.filter = ev.target.value;
      renderSidebar();
    });
    $('#btnRefresh').addEventListener('click', refresh);
    $('#btnValidate').addEventListener('click', runValidate);
    $('#modalClose').addEventListener('click', () => $('#modal').classList.add('hidden'));
    $('#modal').addEventListener('click', ev => {
      if (ev.target.id === 'modal') $('#modal').classList.add('hidden');
    });
    window.addEventListener('resize', () => { if (graphApp) graphApp.applyView(); });

    try {
      await loadMeta();
      await reloadEvents();
    } catch (err) {
      toast('连接后端失败：' + err.message, 'err');
      return;
    }
    const first = state.events.find(e => e.talks > 0) || state.events[0];
    let savedView = 'timeline';
    try { savedView = window.localStorage.getItem('storyeditor:view') || 'timeline'; } catch (err) { /* 忽略 */ }
    setView(savedView);
    const want = decodeURIComponent((location.hash || '').replace('#', '').trim());
    const parts = want.split('/');
    if (parts[1] === 'graph' || parts[1] === 'timeline') setView(parts[1]);
    const pick = state.events.find(e => e.id === parts[0]) || first;
    if (pick) await openEvent(pick.id);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());



