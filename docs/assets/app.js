/* Audit the experts — landing page interactions. Vanilla JS, no dependencies. */
(function () {
  'use strict';
  var doc = document.documentElement; doc.classList.remove('no-js');
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var COL = { missing_meta_description: '#6cb6ff', missing_canonical: '#b69cff', missing_h1: '#ffd166', multiple_h1: '#f78fb3',
    pages_content_img_no_alt: '#5ee3a1', broken_urls: '#ff7b7b', redirecting_internal_urls: '#ff9f43' };
  var SITECOL = ['#5ee3a1', '#6cb6ff', '#f5b942', '#ff9f43', '#b69cff', '#ff7b7b', '#ffd166', '#f78fb3', '#7fd6e8', '#c8e27a'];
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) { if (k === 'style') e.style.cssText = attrs[k]; else e.setAttribute(k, attrs[k]); } if (parent) parent.appendChild(e); return e; }
  function fmt(n) { return Number(n).toLocaleString('en-US'); }
  function onVisible(node, fn, margin) {
    if (!node) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io.disconnect(); fn(); } }); }, { rootMargin: margin || '0px 0px -12% 0px' });
    io.observe(node);
  }
  function chip(b, color, label) { var d = document.createElement('i'); d.style.background = color; b.appendChild(d); b.appendChild(document.createTextNode(label)); }
  /* tooltip */
  var tip = document.getElementById('tip');
  function showTip(html, ev) { tip.innerHTML = html; tip.classList.add('on'); moveTip(ev); }
  function moveTip(ev) { var x = ev.clientX + 14, y = ev.clientY + 14, w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > innerWidth - 8) x = ev.clientX - w - 14; if (y + h > innerHeight - 8) y = ev.clientY - h - 14; tip.style.left = x + 'px'; tip.style.top = y + 'px'; }
  function hideTip() { tip.classList.remove('on'); }
  function bindTip(node, fn) {
    node.addEventListener('mousemove', function (ev) { var h = fn(ev.target); if (h) showTip(h, ev); else hideTip(); });
    node.addEventListener('mouseleave', hideTip);
    node.addEventListener('focusin', function (ev) { var h = fn(ev.target); if (h) { var r = ev.target.getBoundingClientRect(); showTip(h, { clientX: r.right, clientY: r.top }); } });
    node.addEventListener('focusout', hideTip);
  }
  /* reveal on scroll */
  var rev = document.querySelectorAll('.reveal');
  if (RM || !('IntersectionObserver' in window)) rev.forEach(function (n) { n.classList.add('in'); });
  else { var rio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    rev.forEach(function (n) { rio.observe(n); }); }
  /* count-up */
  document.querySelectorAll('[data-count]').forEach(function (n) {
    var to = +n.getAttribute('data-count'); if (RM) { n.textContent = fmt(to); return; }
    n.textContent = '0';
    onVisible(n, function () { var t0 = performance.now(), d = 1400 + Math.min(to, 3000) / 3;
      (function step(t) { var p = Math.min(1, (t - t0) / d), e = 1 - Math.pow(1 - p, 3); n.textContent = fmt(Math.round(to * e)); if (p < 1) requestAnimationFrame(step); })(t0); }, '0px');
  });
  /* videos: play only while visible; never autoplay for reduced motion */
  document.querySelectorAll('video[data-lazy]').forEach(function (v) {
    if (RM) { v.removeAttribute('autoplay'); v.pause(); v.controls = true; return; }
    if (!('IntersectionObserver' in window)) return;
    new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () { v.controls = true; }); } else v.pause(); }); }, { threshold: .25 }).observe(v);
  });
  /* sortable table */
  var table = document.getElementById('sites-table');
  if (table) table.querySelectorAll('th[data-k]').forEach(function (th, ci) {
    var b = th.querySelector('button'); if (!b) return;
    b.addEventListener('click', function () {
      var dir = th.getAttribute('aria-sort') === 'descending' ? 'ascending' : 'descending';
      table.querySelectorAll('th').forEach(function (o) { o.removeAttribute('aria-sort'); }); th.setAttribute('aria-sort', dir);
      var idx = Array.prototype.indexOf.call(th.parentNode.children, th), tb = table.tBodies[0];
      var rows = Array.prototype.slice.call(tb.rows); var num = th.getAttribute('data-k') !== 'site';
      rows.sort(function (a, c) { var x = a.cells[idx].getAttribute('data-v') || a.cells[idx].textContent, y = c.cells[idx].getAttribute('data-v') || c.cells[idx].textContent;
        var r = num ? (parseFloat(x) - parseFloat(y)) : x.localeCompare(y); return dir === 'ascending' ? r : -r; });
      rows.forEach(function (r) { tb.appendChild(r); });
      var live = document.getElementById('sort-status'); if (live) live.textContent = 'Sorted by ' + b.textContent + ', ' + dir + '.';
    });
  });
  if (!window.fetch) return;
  fetch('data/study.json').then(function (r) { return r.json(); }).then(init).catch(function () {});

  function init(D) {
    var S = D.sites, ISS = D.issues;
    crawlCanvas(S); healthGrid(S); stacked(S, ISS); heat(S, ISS); race(S);
  }
  /* hero: every crawled page is a dot that lights up in crawl order */
  function crawlCanvas(S) {
    var c = document.getElementById('crawl'); if (!c || RM) return; var ctx = c.getContext('2d');
    var cells = []; var maxLen = 0; S.forEach(function (s) { maxLen = Math.max(maxLen, s.grid.length); });
    for (var j = 0; j < maxLen; j++) S.forEach(function (s) { if (j < s.grid.length) cells.push(s.grid[j]); });
    var dpr = Math.min(2, window.devicePixelRatio || 1), W, H, cols, size, pos = [];
    function layout() { W = c.clientWidth; H = c.clientHeight; c.width = W * dpr; c.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      size = Math.max(7, Math.sqrt((W * H) / cells.length) * 0.98); cols = Math.ceil(W / size); pos = [];
      var order = cells.map(function (_, i) { return i; });
      for (var i = 0; i < cells.length; i++) pos.push([(i % cols) * size + size / 2, Math.floor(i / cols) * size + size / 2]); }
    layout(); var color = { '0': '#2f8a5f', '1': '#b08a35', '2': '#d39a3a', '3': '#f5b942', 'B': '#ff7b7b' };
    var t0 = null, DUR = 4200, drawn = 0;
    ctx.fillStyle = '#16231d'; pos.forEach(function (p) { ctx.beginPath(); ctx.arc(p[0], p[1], size * .18, 0, 6.283); ctx.fill(); });
    function frame(t) { if (t0 === null) t0 = t; var p = Math.min(1, (t - t0) / DUR), n = Math.floor(cells.length * p);
      for (var i = drawn; i < n; i++) { ctx.fillStyle = color[cells[i]]; ctx.beginPath(); ctx.arc(pos[i][0], pos[i][1], size * (cells[i] === 'B' ? .42 : .3), 0, 6.283); ctx.fill(); }
      drawn = n; if (p < 1) requestAnimationFrame(frame); }
    requestAnimationFrame(frame);
  }
  /* per-site strip of pages, each cell = one page */
  function healthGrid(S) {
    var root = document.getElementById('hg'); if (!root) return; root.innerHTML = '';
    S.forEach(function (s) {
      var row = document.createElement('div'); row.className = 'hg-row';
      var nm = document.createElement('div'); nm.className = 'name'; nm.textContent = s.site; row.appendChild(nm);
      var cells = document.createElement('div'); cells.className = 'hg-cells'; cells.setAttribute('role', 'img');
      var clean = s.grid.split('').filter(function (c) { return c === '0'; }).length;
      cells.setAttribute('aria-label', s.site + ': ' + s.grid.length + ' pages, ' + clean + ' with no counted gap');
      var frag = document.createDocumentFragment();
      for (var j = 0; j < 300; j++) { var i = document.createElement('i'); if (j < s.grid.length) { i.className = 'c' + s.grid[j]; i.setAttribute('data-j', j); i.setAttribute('data-s', s.site); i.setAttribute('data-c', s.grid[j]); if (!RM) i.style.transitionDelay = (j * 4) + 'ms'; } else i.style.visibility = 'hidden'; frag.appendChild(i); }
      cells.appendChild(frag); row.appendChild(cells);
      var n = document.createElement('div'); n.className = 'n'; n.textContent = Math.round(100 * clean / s.grid.length) + '%'; n.title = 'pages with no counted gap'; row.appendChild(n);
      root.appendChild(row);
      if (RM) cells.classList.add('lit'); else onVisible(cells, function () { cells.classList.add('lit'); });
    });
    bindTip(root, function (t) { var c = t.getAttribute && t.getAttribute('data-c'); if (c == null) return '';
      var what = c === 'B' ? '<b class="bad">broken URL (404)</b>' : (c === '0' ? 'no counted gap' : c + ' counted gap' + (c === '1' ? '' : 's'));
      return '<b>' + t.getAttribute('data-s') + '</b><br>page ' + (+t.getAttribute('data-j') + 1) + ' in crawl order<br>' + what; });
  }
  /* stacked bars, issue toggles, animated resort */
  function stacked(S, ISS) {
    var host = document.getElementById('stacked'), tg = document.getElementById('stacked-toggles'); if (!host) return;
    var on = {}; ISS.forEach(function (i) { on[i.key] = true; });
    ISS.forEach(function (i) { var b = document.createElement('button'); b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', 'true');
      chip(b, COL[i.key], i.label); b.addEventListener('click', function () { on[i.key] = !on[i.key]; b.setAttribute('aria-pressed', on[i.key]); draw(); }); tg.appendChild(b); });
    var W = 900, rowH = 40, top = 10, left = 190, H = top + S.length * rowH + 34;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img', 'aria-labelledby': 'stacked-title' }, host);
    el('title', { id: 'stacked-title' }, svg).textContent = 'Counted issues per 100 pages, stacked by issue type, for each site';
    var axis = el('g', {}, svg), rows = {};
    S.forEach(function (s) { var g = el('g', { class: 'row', style: 'transition:transform .8s cubic-bezier(.2,.8,.2,1)' }, svg);
      var t = el('text', { x: left - 12, y: rowH / 2 + 5, 'text-anchor': 'end', 'font-size': 14 }, g); t.textContent = s.site;
      var segs = {}; ISS.forEach(function (i) { segs[i.key] = el('rect', { class: 'bar', y: 8, height: rowH - 16, rx: 3, x: left, width: 0, fill: COL[i.key], tabindex: 0, 'data-s': s.site, 'data-k': i.key }, g); });
      var v = el('text', { y: rowH / 2 + 5, 'font-size': 13, class: 'muted', x: left + 6 }, g); rows[s.site] = { g: g, segs: segs, v: v, s: s }; });
    function draw() {
      var tot = S.map(function (s) { var t = 0; ISS.forEach(function (i) { if (on[i.key]) t += s.counts[i.key]; }); return { s: s, t: t * 100 / s.pages }; });
      var max = Math.max(10, Math.max.apply(null, tot.map(function (x) { return x.t; }))); var scale = (W - left - 90) / max;
      tot.sort(function (a, b) { return b.t - a.t; });
      tot.forEach(function (x, r) { var R = rows[x.s.site]; R.g.style.transform = 'translateY(' + (top + r * rowH) + 'px)'; var cx = left;
        ISS.forEach(function (i) { var w = on[i.key] ? x.s.counts[i.key] * 100 / x.s.pages * scale : 0; R.segs[i.key].setAttribute('x', cx); R.segs[i.key].setAttribute('width', w); cx += w; });
        R.v.setAttribute('x', cx + 8); R.v.textContent = x.t.toFixed(1); });
      while (axis.firstChild) axis.removeChild(axis.firstChild);
      var step = max > 60 ? 20 : (max > 25 ? 10 : 5);
      for (var k = 0; k <= max; k += step) { var X = left + k * scale; el('line', { x1: X, x2: X, y1: top, y2: top + S.length * rowH, stroke: '#24332b' }, axis);
        var tt = el('text', { x: X, y: H - 8, 'text-anchor': 'middle', 'font-size': 12, class: 'muted' }, axis); tt.textContent = k; }
    }
    if (RM) draw(); else { draw0(); onVisible(host, draw); }
    function draw0() { S.forEach(function (s, r) { rows[s.site].g.style.transform = 'translateY(' + (top + r * rowH) + 'px)'; }); }
    var lab = {}; ISS.forEach(function (i) { lab[i.key] = i.label; });
    bindTip(host, function (t) { var k = t.getAttribute && t.getAttribute('data-k'); if (!k) return ''; var s = rows[t.getAttribute('data-s')].s;
      return '<b>' + s.site + '</b><br>' + lab[k] + ': <b>' + s.counts[k] + '</b> of ' + s.pages + ' pages (' + (s.counts[k] * 100 / s.pages).toFixed(1) + ' per 100)'; });
  }
  /* sites x issues heatmap */
  function heat(S, ISS) {
    var host = document.getElementById('heat'); if (!host) return;
    var cw = 96, ch = 36, left = 190, top = 70, W = left + ISS.length * cw + 10, H = top + S.length * ch + 10;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img', 'aria-labelledby': 'heat-title' }, host);
    el('title', { id: 'heat-title' }, svg).textContent = 'Heatmap: share of each site\'s pages affected by each issue type';
    var short = { missing_meta_description: 'No meta', missing_canonical: 'No canonical', missing_h1: 'No H1', multiple_h1: '2+ H1', pages_content_img_no_alt: 'Img no alt', broken_urls: 'Broken', redirecting_internal_urls: 'Redirects' };
    ISS.forEach(function (i, c) { var t = el('text', { x: left + c * cw + cw / 2, y: top - 14, 'text-anchor': 'middle', 'font-size': 13, class: 'muted' }, svg); t.textContent = short[i.key]; });
    S.forEach(function (s, r) { var t = el('text', { x: left - 12, y: top + r * ch + ch / 2 + 5, 'text-anchor': 'end', 'font-size': 14 }, svg); t.textContent = s.site;
      ISS.forEach(function (i, c) { var n = s.counts[i.key], p = n * 100 / s.pages, a = n === 0 ? 0 : Math.min(1, .18 + Math.sqrt(p / 100) * .9);
        var g = el('g', {}, svg);
        el('rect', { class: 'cell', x: left + c * cw + 2, y: top + r * ch + 2, width: cw - 4, height: ch - 4, rx: 5, fill: n === 0 ? '#16221c' : COL[i.key], 'fill-opacity': n === 0 ? 1 : a, tabindex: 0, 'data-s': s.site, 'data-k': i.key, 'data-n': n, style: RM ? '' : 'opacity:0;transition:opacity .5s ease ' + ((r + c) * 45) + 'ms' }, g);
        var tx = el('text', { x: left + c * cw + cw / 2, y: top + r * ch + ch / 2 + 5, 'text-anchor': 'middle', 'font-size': 13, 'pointer-events': 'none', fill: a > .6 ? '#0b1410' : '#eaf2ec' }, g); tx.textContent = n === 0 ? '·' : n; }); });
    if (!RM) onVisible(host, function () { host.querySelectorAll('.cell').forEach(function (c) { c.style.opacity = 1; }); });
    var lab = {}; ISS.forEach(function (i) { lab[i.key] = i.label; }); var by = {}; S.forEach(function (s) { by[s.site] = s; });
    bindTip(host, function (t) { var k = t.getAttribute && t.getAttribute('data-k'); if (!k) return ''; var s = by[t.getAttribute('data-s')], n = +t.getAttribute('data-n');
      return '<b>' + s.site + '</b><br>' + lab[k] + ': <b>' + n + '</b> (' + (n * 100 / s.pages).toFixed(1) + '% of ' + s.pages + ' pages)'; });
  }
  /* cumulative issues as the crawl progresses, per-site toggle */
  function race(S) {
    var host = document.getElementById('race'), tg = document.getElementById('race-toggles'); if (!host) return;
    var W = 900, H = 380, L = 54, R = 150, T = 16, B = 40, maxY = 0; S.forEach(function (s) { s.race.forEach(function (p) { maxY = Math.max(maxY, p[1]); }); });
    maxY = Math.ceil(maxY / 50) * 50; var sx = function (x) { return L + x / 300 * (W - L - R); }, sy = function (y) { return T + (1 - y / maxY) * (H - T - B); };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%', role: 'img', 'aria-labelledby': 'race-title' }, host);
    el('title', { id: 'race-title' }, svg).textContent = 'Cumulative counted issues as each crawl progressed, by site';
    for (var y = 0; y <= maxY; y += 50) { el('line', { x1: L, x2: W - R, y1: sy(y), y2: sy(y), stroke: '#24332b' }, svg); var t = el('text', { x: L - 8, y: sy(y) + 4, 'text-anchor': 'end', 'font-size': 12, class: 'muted' }, svg); t.textContent = y; }
    for (var x = 0; x <= 300; x += 50) { var tx = el('text', { x: sx(x), y: H - 14, 'text-anchor': 'middle', 'font-size': 12, class: 'muted' }, svg); tx.textContent = x; }
    var xl = el('text', { x: (L + W - R) / 2, y: H - 4, 'text-anchor': 'middle', 'font-size': 12, class: 'muted' }, svg); xl.textContent = 'pages crawled →';
    var lines = {};
    var ends = S.map(function (s, i) { return { s: s, i: i, y: s.race[s.race.length - 1][1] }; }).sort(function (a, b) { return b.y - a.y; });
    var lastY = -99, labY = {}; ends.forEach(function (e) { var yy = sy(e.y) + 4; if (yy - lastY < 15) yy = lastY + 15; labY[e.s.site] = yy; lastY = yy; });
    S.forEach(function (s, i) { var d = s.race.map(function (p, k) { return (k ? 'L' : 'M') + sx(p[0]).toFixed(1) + ' ' + sy(p[1]).toFixed(1); }).join(' ');
      var g = el('g', { style: 'transition:opacity .3s' }, svg);
      var path = el('path', { d: d, fill: 'none', stroke: SITECOL[i], 'stroke-width': 2.5, 'stroke-linejoin': 'round' }, g);
      var e = s.race[s.race.length - 1]; el('circle', { cx: sx(e[0]), cy: sy(e[1]), r: 4, fill: SITECOL[i] }, g);
      var lt = el('text', { x: W - R + 8, y: labY[s.site], 'font-size': 12.5, fill: SITECOL[i] }, g); lt.textContent = s.site.replace('.com', '').replace('searchenginejournal', 'SEJ') + ' ' + e[1];
      var hit = el('path', { d: d, fill: 'none', stroke: 'transparent', 'stroke-width': 14, tabindex: 0, 'data-s': s.site, 'data-v': e[1], 'data-p': e[0] }, g);
      lines[s.site] = { g: g, path: path };
      var b = document.createElement('button'); b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', 'true'); chip(b, SITECOL[i], s.site);
      b.addEventListener('click', function () { var o = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', o); g.style.opacity = o ? 1 : .06; }); tg.appendChild(b); });
    if (!RM) { Object.keys(lines).forEach(function (k) { var p = lines[k].path, len = p.getTotalLength(); p.style.strokeDasharray = len; p.style.strokeDashoffset = len; });
      onVisible(host, function () { Object.keys(lines).forEach(function (k) { var p = lines[k].path; p.style.transition = 'stroke-dashoffset 2.6s ease-out'; p.style.strokeDashoffset = 0; }); }); }
    bindTip(host, function (t) { var s = t.getAttribute && t.getAttribute('data-s'); if (!s) return ''; return '<b>' + s + '</b><br>' + t.getAttribute('data-v') + ' counted issues across ' + t.getAttribute('data-p') + ' pages'; });
  }
})();
