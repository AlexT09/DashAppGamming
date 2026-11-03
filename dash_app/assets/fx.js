/* fx.js — Animaciones del dashboard (Dash carga solo todo lo que hay en assets/).
   1. KPIs que cuentan hasta su valor cuando cambian.
   2. Indicador del menú que se desliza a la página activa.
   3. Fondo con símbolos △ ○ ✕ □ flotando muy tenues.
   Solo cambia texto y clases; no toca los datos ni los callbacks. */
(function () {
  var root = document.documentElement;
  root.classList.add('fx');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── 1. KPIs que cuentan ─────────────────────────────────────
  // Acepta "23,151", "$7.99", "62.1%", "1.2M". Otros textos ("—", "PS4") no se animan.
  var NUM = /^([$€£¥]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(%|[KMB])?$/;
  function parse(text) {
    var m = NUM.exec((text || '').trim());
    if (!m) return null;
    return {
      pre: m[1], suf: m[4] || '', dec: m[3] ? m[3].length - 1 : 0, comma: m[2].indexOf(',') > -1,
      value: parseFloat(m[2].replace(/,/g, '') + (m[3] || '')),
    };
  }
  function format(v, f) {
    var s = f.comma || v >= 10000
      ? v.toLocaleString('en-US', { minimumFractionDigits: f.dec, maximumFractionDigits: f.dec })
      : v.toFixed(f.dec);
    return f.pre + s + f.suf;
  }
  // Solo se cambia el nodeValue del texto que creó React, así Dash puede seguir actualizándolo.
  function animate(el, target) {
    var node = el.firstChild;
    if (!node || node.nodeType !== 3) return;
    var to = parse(target);
    if (!to || reduce) { el._fxShown = target; return; }
    var prev = parse(el._fxShown);
    var from = prev ? prev.value : 0;
    el._fxShown = target;
    if (from === to.value) return;
    var dur = prev ? 700 : 1100, t0 = performance.now(), id = (el._fxId || 0) + 1;
    el._fxId = id;
    (function step(now) {
      if (el._fxId !== id) return;
      var p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      var text = p < 1 ? format(from + (to.value - from) * e, to) : target;
      el._fxWrote = text;
      node.nodeValue = text;
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }
  function scanKpis(scope) {
    var list = scope.querySelectorAll ? scope.querySelectorAll('.kpi-value') : [];
    for (var i = 0; i < list.length; i++) {
      var el = list[i], text = el.textContent;
      if (text !== el._fxWrote && text !== el._fxShown) animate(el, text);
    }
  }

  // ── 2. Indicador deslizante del menú ────────────────────────
  var pill = null;
  function movePill() {
    var side = document.querySelector('.sidebar');
    var active = side && side.querySelector('.nav-item.active');
    if (!side || !active) return;
    if (!pill) {
      pill = document.createElement('span');
      pill.className = 'fx-nav-pill';
      side.appendChild(pill);
      root.classList.add('fx-pill');
    }
    pill.style.transform = 'translateY(' + active.offsetTop + 'px)';
    pill.style.height = active.offsetHeight + 'px';
  }
  window.addEventListener('resize', movePill);

  // Dash dibuja la app después de cargar: se observan los cambios del DOM.
  new MutationObserver(function (muts) {
    var nav = false;
    for (var i = 0; i < muts.length; i++) {
      var m = muts[i];
      if (m.type === 'attributes') { if (m.target.classList.contains('nav-item')) nav = true; continue; }
      var t = m.target.nodeType === 3 ? m.target.parentNode : m.target;
      if (!t || (t.closest && t.closest('.js-plotly-plot'))) continue;  // ignora cambios internos de Plotly
      if (t.closest && t.closest('.kpi-grid')) scanKpis(t.closest('.kpi-grid'));
      else if (m.addedNodes.length) { scanKpis(t); nav = true; }
    }
    if (nav) movePill();
  }).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['class'] });

  // ── 3. Fondo con símbolos flotando ──────────────────────────
  if (reduce) return;
  var cv = document.createElement('canvas');
  cv.id = 'fx-bg';
  cv.setAttribute('aria-hidden', 'true');
  document.body.insertBefore(cv, document.body.firstChild);
  var ctx = cv.getContext('2d'), W = 0, H = 0, shapes = [];
  var tint = ['0,170,255', '167,139,250', '0,112,209', '127,211,247'];
  function resize() {
    var r = window.devicePixelRatio || 1;
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W * r; cv.height = H * r; ctx.setTransform(r, 0, 0, r, 0, 0);
    var n = Math.round(W * H / 42000) + 8;
    shapes = [];
    for (var i = 0; i < n; i++) shapes.push({
      x: Math.random() * W, y: Math.random() * H, s: 8 + Math.random() * 16, k: i % 4,
      vy: -(0.08 + Math.random() * 0.22), vx: (Math.random() - .5) * .12,
      a: Math.random() * Math.PI, va: (Math.random() - .5) * .006, o: .05 + Math.random() * .1,
    });
  }
  function frame() {
    if (!document.hidden) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < shapes.length; i++) {
        var p = shapes[i], s = p.s;
        p.x += p.vx; p.y += p.vy; p.a += p.va;
        if (p.y < -30) { p.y = H + 30; p.x = Math.random() * W; }
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a);
        ctx.strokeStyle = 'rgba(' + tint[p.k] + ',' + p.o + ')'; ctx.lineWidth = 1.6; ctx.beginPath();
        if (p.k === 0) { ctx.moveTo(0, -s); ctx.lineTo(s * .87, s * .5); ctx.lineTo(-s * .87, s * .5); ctx.closePath(); }
        else if (p.k === 1) ctx.arc(0, 0, s * .8, 0, Math.PI * 2);
        else if (p.k === 2) { ctx.moveTo(-s * .7, -s * .7); ctx.lineTo(s * .7, s * .7); ctx.moveTo(s * .7, -s * .7); ctx.lineTo(-s * .7, s * .7); }
        else ctx.rect(-s * .7, -s * .7, s * 1.4, s * 1.4);
        ctx.stroke(); ctx.restore();
      }
    }
    requestAnimationFrame(frame);
  }
  window.addEventListener('resize', resize);
  resize();
  frame();
})();
