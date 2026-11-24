/* Sellify v5: script compartido por / (español) y /en/ (inglés).
   El CSS ya deja la página en su estado final. Aquí se añade el movimiento, y solo si
   GSAP cargó y la persona no pidió movimiento reducido. */
(function(){
  'use strict';
  var html = document.documentElement;
  var lang = html.lang === 'en' ? 'en' : 'es';
  var $ = function(s, r){ return (r || document).querySelector(s); };
  var $$ = function(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGSAP = !!(window.gsap && window.ScrollTrigger);
  var lenis = null;
  var clamp = function(v, a, b){ return v < a ? a : (v > b ? b : v); };

  /* ---------- Idioma: recuerda la elección para que la detección automática no la pise ---------- */
  $$('[data-set-lang]').forEach(function(a){
    a.addEventListener('click', function(){
      document.cookie = 'lang=' + a.getAttribute('data-set-lang') + '; path=/; max-age=31536000; SameSite=Lax';
    });
  });

  /* ---------- Formulario: abre WhatsApp Business con los datos (sin backend) ---------- */
  var T = {
    es: { intro: 'Hola Alonso, quiero agendar una auditoría.', name: 'Nombre', email: 'Email', brand: 'Marca', market: 'Vendo en', sales: 'Ventas mensuales en Amazon' },
    en: { intro: "Hi Alonso, I'd like to book an audit.", name: 'Name', email: 'Email', brand: 'Brand', market: 'Selling on', sales: 'Monthly Amazon sales' }
  }[lang];
  var form = $('#audit-form');
  if (form) {
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var d = new FormData(form);
      var msg = T.intro + '\n' +
        T.name + ': ' + (d.get('nombre') || '') + '\n' +
        T.email + ': ' + (d.get('email') || '') + '\n' +
        T.brand + ': ' + (d.get('marca') || '-') + '\n' +
        T.market + ': ' + (d.get('mercado') || '') + '\n' +
        T.sales + ': ' + (d.get('ventas') || '');
      window.open('https://wa.me/34627071754?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    });
  }

  /* ---------- Video de Tatiana: los botones solo se activan si el archivo existe ---------- */
  var dialog = $('#video-dialog');
  var video = $('#video-el');
  if (dialog && video && dialog.showModal) {
    var openVideo = function(e){
      if (e) e.preventDefault();
      dialog.showModal();
      if (lenis) lenis.stop();
      var playing = video.play();
      if (playing && playing.catch) playing.catch(function(){}); // si se cierra antes de arrancar, no es un error
    };
    var closeVideo = function(){ video.pause(); dialog.close(); };
    fetch('/assets/tatiana-testimonio.mp4', { method: 'HEAD' }).then(function(r){
      if (!r.ok) return;
      $$('[data-video-open]').forEach(function(a){
        a.hidden = false;
        a.addEventListener('click', openVideo);
      });
    }).catch(function(){});
    $('#video-close').addEventListener('click', closeVideo);
    dialog.addEventListener('click', function(e){ if (e.target === dialog) closeVideo(); });
    dialog.addEventListener('close', function(){ video.pause(); if (lenis) lenis.start(); });
  }

  /* ---------- Cinta de logos: duplica la lista hasta llenar el ancho y la pone a correr ---------- */
  $$('[data-marquee]').forEach(function(m){
    var track = $('.marquee__track', m);
    if (!track || reduce) return;
    var items = $$('li', track);
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    var one = track.scrollWidth + gap;
    if (!one) return;
    var copies = Math.max(2, Math.ceil((m.clientWidth * 2) / one) + 1);
    for (var c = 1; c < copies; c++) {
      items.forEach(function(li){
        var n = li.cloneNode(true);
        n.setAttribute('aria-hidden', 'true');
        track.appendChild(n);
      });
    }
    m.style.setProperty('--shift', one);
    m.style.setProperty('--dur', Math.round(one / 28) + 's');
    m.classList.add('is-on');
  });

  /* ---------- Asterisco de celdas en el hero ----------
     Un campo de cuadros sobre una rejilla: cada celda se enciende si cae dentro de la marca.
     Entra como ruido que se ordena, se abre alrededor del cursor y se deshace al hacer scroll. */
  (function(){
    var canvas = $('[data-mark-canvas]');
    var hero = $('[data-hero]');
    var anchor = $('[data-mark-anchor]');
    if (!canvas || !hero || !anchor || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var W = 0, H = 0, dpr = 1, P = 9, cx = 0, cy = 0, sc = 1, bg = [];
    var mouse = { x: -9999, y: -9999, tx: -9999, ty: -9999 };
    var visible = true, raf = 0, t0 = 0;
    var A = 58.5 * Math.PI / 180;
    var ORANGE = '#F58238', GRAY = '#8E9094', WHITE = '#F2F2F2';
    var hash = function(i, j){ var n = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return n - Math.floor(n); };
    var hash2 = function(i, j){ var n = Math.sin(i * 269.5 + j * 183.3) * 24634.6345; return n - Math.floor(n); };
    var outCubic = function(x){ return 1 - Math.pow(1 - x, 3); };
    var outExpo = function(x){ return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x); };
    var inOut = function(x){ return x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };

    function layout(){
      var r = hero.getBoundingClientRect();
      W = r.width; H = r.height;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      P = W < 700 ? 6 : (W < 1200 ? 8 : 9);
      var a = anchor.getBoundingClientRect();
      cx = a.left - r.left + a.width / 2;
      cy = a.top - r.top + a.height / 2;
      sc = Math.min(a.width / 600, a.height / 740);
      bg = [];
      var cols = Math.ceil(W / P), rows = Math.ceil(H / P), far = Math.max(W, H) * .6;
      for (var j = 0; j < rows; j++) {
        for (var i = 0; i < cols; i++) {
          var x = i * P, y = j * P;
          var d = Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy));
          var dens = .012 + .085 * Math.max(0, 1 - d / far);
          var h = hash(i + 11, j + 7);
          if (h < dens) bg.push(x, y, h / dens);
        }
      }
    }

    function draw(now){
      if (!t0) t0 = now;
      var t = (now - t0) / 1000;
      var ti = reduce ? 1 : clamp((t - .1) / 2.1, 0, 1);
      var resolve = outCubic(ti);
      var wipe = reduce ? 1 : inOut(clamp((t - .9) / 1.3, 0, 1));
      var hr = hero.getBoundingClientRect();
      var p = reduce ? 0 : clamp(-hr.top / (hr.height * .8), 0, 1);
      var theta = reduce ? 0 : (1 - outExpo(ti)) * -1.25 + .03 * Math.sin(t * .35) + p * .9;
      mouse.x += (mouse.tx - mouse.x) * .16;
      mouse.y += (mouse.ty - mouse.y) * .16;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      var q = P * .58, o = (P - q) / 2, k, i, j;

      // Fondo: celdas sueltas que titilan despacio
      ctx.fillStyle = WHITE;
      for (k = 0; k < bg.length; k += 3) {
        var tw = reduce ? .5 : .5 + .5 * Math.sin(t * .7 + bg[k + 2] * 40);
        ctx.globalAlpha = (.03 + .07 * tw) * resolve * (1 - p * .7);
        ctx.fillRect(bg[k] + o, bg[k + 1] + o, q, q);
      }

      // Marca
      var cs = [Math.cos(theta), Math.cos(theta + A), Math.cos(theta - A)];
      var sn = [Math.sin(theta), Math.sin(theta + A), Math.sin(theta - A)];
      var edge = P / sc, R = 150, R2 = R * R;
      var i0 = Math.max(0, Math.floor((cx - 340 * sc) / P)), i1 = Math.min(Math.ceil(W / P), Math.ceil((cx + 340 * sc) / P));
      var j0 = Math.max(0, Math.floor((cy - 400 * sc) / P)), j1 = Math.min(Math.ceil(H / P), Math.ceil((cy + 400 * sc) / P));
      var fr = Math.floor(t * 20), sp = Math.floor(t * 5);
      var lists = [[], [], []]; // gris, naranja, blanco
      for (j = j0; j < j1; j++) {
        for (i = i0; i < i1; i++) {
          var x = i * P + P / 2, y = j * P + P / 2, sx = x, sy = y, glow = 0;
          var dx = x - mouse.x, dy = y - mouse.y, d2 = dx * dx + dy * dy;
          if (d2 < R2) {
            var d = Math.sqrt(d2) || 1, f = 1 - d / R, push = f * f * 36;
            sx = x - dx / d * push; sy = y - dy / d * push; glow = f;
          }
          var u = (sx - cx) / sc + 274, v = (sy - cy) / sc + 350;
          var du = u - 274, dv = v - 258, cov = 0, base = false, c;
          for (k = 0; k < 3; k++) {
            var xr = du * cs[k] + dv * sn[k], yr = -du * sn[k] + dv * cs[k];
            c = .5 - Math.max(Math.abs(xr) - 274, Math.abs(yr) - 53.5) / edge;
            if (c > cov) cov = c;
          }
          c = .5 - Math.max(Math.abs(u - 273) - 185, Math.abs(v - 655) - 45) / edge;
          if (c > cov) { cov = c; base = true; }
          if (cov <= 0) {
            // ruido de entrada: celdas al azar que se apagan cuando la marca termina de ordenarse
            if (resolve < 1 && hash(i + fr * 7, j + fr * 3) > .965 + resolve * .035) lists[0].push(x, y, .3 * (1 - resolve));
            continue;
          }
          if (cov > 1) cov = 1;
          var h = hash(i, j), h2 = hash2(i, j);
          if (h2 > resolve * 1.08) continue;
          if (h2 < p * 1.6 - (1 - y / H) * .5) continue;
          var bx = v <= 258 ? 166 + 170 * (v + 20) / 278 : 336 - 283 * (v - 258) / 462;
          var orange = base || u < bx - (1 - wipe) * 460;
          var b = (.72 + .28 * h) * (reduce ? 1 : .93 + .07 * Math.sin(t * 1.7 + h * 31));
          var al = Math.min(1, cov * b + glow * .25);
          if (!reduce && hash(i + sp * 13, j * 7 + sp) > .9978) lists[2].push(x, y, 1);
          else lists[orange ? 1 : 0].push(x, y, al);
        }
      }
      var cols = [GRAY, ORANGE, WHITE];
      for (k = 0; k < 3; k++) {
        ctx.fillStyle = cols[k];
        var L = lists[k];
        for (i = 0; i < L.length; i += 3) {
          ctx.globalAlpha = L[i + 2];
          ctx.fillRect(L[i] - q / 2, L[i + 1] - q / 2, q, q);
        }
      }
      ctx.globalAlpha = 1;
    }

    function loop(now){
      raf = 0;
      draw(now);
      if (visible && !reduce && !document.hidden) raf = requestAnimationFrame(loop);
    }
    function kick(){ if (!raf) raf = requestAnimationFrame(loop); }

    layout();
    kick();
    if (window.ResizeObserver) new ResizeObserver(function(){ layout(); kick(); }).observe(hero);
    else window.addEventListener('resize', function(){ layout(); kick(); });
    if (window.IntersectionObserver) {
      new IntersectionObserver(function(en){ visible = en[0].isIntersecting; if (visible) kick(); }).observe(hero);
    }
    document.addEventListener('visibilitychange', function(){ if (!document.hidden) kick(); });
    if (!reduce && window.matchMedia('(pointer: fine)').matches) {
      hero.addEventListener('pointermove', function(e){
        var r = hero.getBoundingClientRect();
        mouse.tx = e.clientX - r.left; mouse.ty = e.clientY - r.top;
      });
      hero.addEventListener('pointerleave', function(){ mouse.tx = -9999; mouse.ty = -9999; });
    }
  })();

  /* ---------- Sin GSAP: la página queda en su estado final ---------- */
  if (!hasGSAP) { html.classList.add('ready'); return; }

  var gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ ignoreMobileResize: true });

  /* ---------- Scroll suave (solo con ratón o trackpad) ---------- */
  if (!reduce && window.Lenis && window.matchMedia('(pointer: fine)').matches) {
    lenis = new window.Lenis({ autoRaf: false, lerp: .11, anchors: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function(time){ lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
  var scrollToY = function(y){
    if (lenis) lenis.scrollTo(y);
    else window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
  };

  /* ---------- Encabezado: sólido al bajar, se esconde bajando y vuelve subiendo ---------- */
  var hdr = $('[data-hdr]');
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: function(self){
      var y = self.scroll();
      hdr.classList.toggle('is-solid', y > 24);
      hdr.classList.toggle('is-hidden', self.direction === 1 && y > 480);
    }
  });

  /* ---------- Movimiento reducido: solo lo funcional ---------- */
  var hero = $('[data-hero]'), dock = $('[data-dock]'), audit = $('[data-audit]');
  var makeDock = function(){
    if (!dock || !hero || !audit) return;
    ScrollTrigger.create({ trigger: hero, start: 'bottom 55%', endTrigger: audit, end: 'top 75%', toggleClass: { targets: dock, className: 'is-on' } });
  };
  if (reduce) { html.classList.add('ready'); makeDock(); return; }

  /* ---------- Utilidades de animación ---------- */
  var fmt = function(el, v){
    var dec = +el.getAttribute('data-dec') || 0;
    return (el.getAttribute('data-pre') || '') + v.toFixed(dec) + (el.getAttribute('data-suf') || '');
  };
  var count = function(tl, el, pos, dur){
    var o = { v: 0 }, n = parseFloat(el.getAttribute('data-n'));
    tl.fromTo(o, { v: 0 }, { v: n, duration: dur, ease: 'power1.out', onUpdate: function(){ el.textContent = fmt(el, o.v); } }, pos);
  };
  var splitWords = function(el){
    var walk = function(node){
      Array.prototype.slice.call(node.childNodes).forEach(function(ch){
        if (ch.nodeType === 3) {
          var frag = document.createDocumentFragment();
          ch.textContent.split(/(\s+)/).forEach(function(part){
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var s = document.createElement('span');
            s.className = 'w'; s.textContent = part;
            frag.appendChild(s);
          });
          node.replaceChild(frag, ch);
        } else if (ch.nodeType === 1) walk(ch);
      });
    };
    walk(el);
    return $$('.w', el);
  };

  /* Figura de cada caso: devuelve una línea de tiempo que va del estado vacío al final */
  var figTl = function(el){
    var tl = gsap.timeline({ defaults: { ease: 'none' } });
    var fig = $('[data-fig]', el);
    var kind = fig ? fig.getAttribute('data-fig') : '';
    if (kind === 'chart') {
      var clip = $('[data-chart-clip]', fig), last = $('[data-chart-last]', fig), o = { v: 441 };
      tl.fromTo(clip, { attr: { width: 0 } }, { attr: { width: 640 }, duration: 1 }, 0);
      $$('[data-dot]', fig).forEach(function(dot){
        var x = parseFloat(dot.getAttribute('cx'));
        tl.fromTo(dot, { scale: 0 }, { scale: 1, duration: .1, ease: 'back.out(3)' }, Math.max(0, x / 640 - .02));
      });
      tl.fromTo($('[data-chart-first]', fig), { autoAlpha: 0 }, { autoAlpha: 1, duration: .1 }, .06);
      tl.fromTo(last, { autoAlpha: 0 }, { autoAlpha: 1, duration: .1 }, .5);
      tl.fromTo(o, { v: 441 }, { v: 30546, duration: .46, ease: 'power1.in', onUpdate: function(){
        last.textContent = '$' + Math.round(o.v).toLocaleString('en-US');
      } }, .5);
    } else if (fig) {
      tl.fromTo($('.tile', fig), { autoAlpha: 0, scale: .94 }, { autoAlpha: 1, scale: 1, duration: .3, ease: 'power2.out' }, 0);
      $$('[data-n]', fig).forEach(function(n, i){ count(tl, n, .1 + i * .15, .7); });
      $$('[data-bar]', fig).forEach(function(b, i){
        tl.fromTo(b, { scaleX: 0 }, { scaleX: 1, duration: .6, ease: 'power2.out' }, .2 + i * .2);
      });
      $$('[data-step]', fig).forEach(function(s, i){
        tl.fromTo(s, { autoAlpha: .22 }, { autoAlpha: 1, duration: .2 }, .15 + i * .3);
      });
      tl.to({}, { duration: .01 }, 1);
    }
    return tl;
  };

  /* ---------- Hero: única secuencia de entrada ---------- */
  var lines = $$('.hero [data-line]'), ins = $$('.hero [data-in]');
  gsap.set(lines, { yPercent: 112, opacity: 1 });
  gsap.set(ins, { autoAlpha: 0, y: 18 });
  html.classList.add('ready');
  gsap.timeline({ delay: .15 })
    .to(lines, { yPercent: 0, duration: 1.15, ease: 'expo.out', stagger: .12 }, 0)
    .to(ins, { autoAlpha: 1, y: 0, duration: .8, ease: 'power3.out', stagger: .09 }, .45);

  /* ---------- Todo lo que depende del tamaño de pantalla ---------- */
  var mm = gsap.matchMedia();
  mm.add({ wide: '(min-width: 1001px) and (min-height: 600px)', narrow: '(max-width: 1000px), (max-height: 599px)' }, function(ctx){
    var wide = ctx.conditions.wide;
    var undo = [function(){ html.classList.remove('pin-on'); }];
    // En pantallas bajas, la barra de agenda y el encabezado se apartan mientras una sección está fija (ver site.css)
    var onPin = function(self){ html.classList.toggle('pin-on', self.isActive); };

    // 1. Frase que se enciende palabra por palabra
    $$('[data-words]').forEach(function(el){
      var words = el._words || (el._words = splitWords(el));
      gsap.fromTo(words, { opacity: .14 }, { opacity: 1, ease: 'none', stagger: .1,
        scrollTrigger: { trigger: el, start: 'top 85%', end: 'bottom 55%', scrub: .3 } });
    });

    // 2. Los $100
    (function(){
      var sec = $('[data-pl]');
      if (!sec) return;
      var num = $('[data-pl-num]', sec), state = $('[data-pl-state]', sec), big = $('.pl__big', sec);
      var segs = $$('[data-pl-seg]', sec), rows = $$('[data-pl-row]', sec);
      var keep = $('[data-pl-keep]', sec), goal = $('[data-pl-goal]', sec), foot = $('[data-pl-foot]', sec);
      var o = { v: 100 }, left = 100, END = 6.4;
      var paint = function(){
        num.textContent = Math.round(o.v);
        var now = tl.time();
        state.textContent = state.getAttribute(now >= END ? 'data-b' : (now > .55 ? 'data-m' : 'data-a'));
      };
      var tl = gsap.timeline({ defaults: { ease: 'power2.out' }, onUpdate: function(){ paint(); } });
      tl.fromTo(segs, { backgroundColor: '#ACBBD2' }, { backgroundColor: '#ACBBD2', duration: .01 }, 0)
        .fromTo(keep, { backgroundColor: '#ACBBD2' }, { backgroundColor: '#ACBBD2', duration: .01 }, 0)
        .fromTo(big, { color: '#F2F2F2' }, { color: '#F2F2F2', duration: .01 }, 0)
        .fromTo(rows, { opacity: .28 }, { opacity: .28, duration: .01 }, 0)
        .fromTo(goal, { autoAlpha: 0, scaleX: 0 }, { autoAlpha: 0, scaleX: 0, duration: .01 }, 0)
        .fromTo(foot, { autoAlpha: 0, y: 16 }, { autoAlpha: 0, y: 16, duration: .01 }, 0);
      rows.forEach(function(row, i){
        var at = .5 + i;
        left -= parseFloat(row.getAttribute('data-amt'));
        tl.to(row, { opacity: 1, duration: .3 }, at)
          .to(segs[i], { backgroundColor: '#34363B', duration: .5 }, at)
          .to(o, { v: left, duration: .65 }, at);
      });
      tl.to(keep, { backgroundColor: '#F58238', duration: .4 }, END)
        .to(big, { color: '#F58238', duration: .4 }, END)
        .to(goal, { autoAlpha: 1, scaleX: 1, duration: .5 }, END + .4)
        .to(foot, { autoAlpha: 1, y: 0, duration: .5 }, END + .5)
        .to({}, { duration: .5 });
      paint();
      undo.push(function(){ num.textContent = '9'; state.textContent = state.getAttribute('data-b'); sec.classList.remove('is-pinned'); });
      if (wide) {
        sec.classList.add('is-pinned');
        ScrollTrigger.create({ animation: tl, trigger: sec, start: 'top top', end: '+=230%', pin: true, scrub: .5, anticipatePin: 1, onToggle: onPin });
      } else {
        tl.pause();
        ScrollTrigger.create({ trigger: $('.pl__rows', sec), start: 'top 88%', once: true, onEnter: function(){ tl.timeScale(1.5).play(); } });
      }
    })();

    // 3. Cifras de la agencia
    (function(){
      var box = $('[data-stats]');
      if (!box) return;
      var tl = gsap.timeline({ scrollTrigger: { trigger: box, start: 'top 82%', once: true } });
      $$('[data-n]', box).forEach(function(n, i){ count(tl, n, i * .12, 1.3); });
    })();

    // 4. Visor de casos
    (function(){
      var viewer = $('[data-viewer]');
      if (!viewer) return;
      var frame = $('.viewer__frame', viewer), items = $$('[data-case]', viewer), tabs = $$('[data-tab]', viewer);
      var counter = $('[data-viewer-count]', viewer), n = items.length, active = -1;
      if (!wide) {
        items.forEach(function(el){
          var tl = figTl(el).pause();
          ScrollTrigger.create({ trigger: $('[data-fig]', el), start: 'top 80%', once: true, onEnter: function(){ tl.duration(1.7).play(); } });
        });
        return;
      }
      viewer.classList.add('is-pinned');
      undo.push(function(){
        viewer.classList.remove('is-pinned');
        tabs.forEach(function(t, i){ t.setAttribute('aria-selected', i === 0 ? 'true' : 'false'); });
      });
      var setActive = function(i){
        if (i === active) return;
        active = i;
        tabs.forEach(function(t, k){ t.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
        counter.textContent = (i + 1) + ' / ' + n;
      };
      // El primer caso se dibuja mientras el visor entra en pantalla
      var first = figTl(items[0]);
      ScrollTrigger.create({ animation: first, trigger: frame, start: 'top 82%', end: 'center center', scrub: .5 });
      // Los demás se abren con el visor fijo
      var tl = gsap.timeline({ defaults: { ease: 'none' } });
      gsap.set(items.slice(1), { autoAlpha: 0 });
      items.forEach(function(el, i){
        if (!i) return;
        var at = i - .3;
        tl.to(items[i - 1], { autoAlpha: 0, duration: .1 }, at)
          .fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: .1 }, at + .1)
          .add(figTl(el).duration(.5), at + .15);
      });
      tl.to({}, { duration: .01 }, n - .01);
      var st = ScrollTrigger.create({
        animation: tl, trigger: frame, start: 'center center', end: '+=' + (n * 80) + '%', pin: true, scrub: .5, anticipatePin: 1,
        onToggle: onPin,
        onUpdate: function(self){ setActive(clamp(Math.floor(self.progress * n + .3), 0, n - 1)); }
      });
      setActive(0);
      var onTab = function(e){
        var i = +e.currentTarget.getAttribute('data-tab');
        var time = i ? i + .3 : .05;
        scrollToY(st.start + (st.end - st.start) * (time / n));
      };
      tabs.forEach(function(t){ t.addEventListener('click', onTab); });
      undo.push(function(){ tabs.forEach(function(t){ t.removeEventListener('click', onTab); }); });
    })();

    // 5. Pasos: la línea naranja avanza de izquierda a derecha
    (function(){
      var box = $('[data-steps]');
      if (!box) return;
      gsap.fromTo($$('li', box), { '--p': 0 }, { '--p': 1, duration: 1, ease: 'power2.out', stagger: .28,
        scrollTrigger: { trigger: box, start: 'top 78%', once: true } });
    })();

    // 6. Dashboard: la línea de ventas se dibuja
    (function(){
      var line = $('[data-dash-line]');
      if (!line) return;
      gsap.fromTo(line, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.8, ease: 'power2.inOut',
        scrollTrigger: { trigger: line, start: 'top 85%', once: true } });
    })();

    // 7. Barra fija de agenda
    makeDock();

    return function(){ undo.forEach(function(fn){ fn(); }); };
  });

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ ScrollTrigger.refresh(); });
  window.addEventListener('load', function(){ ScrollTrigger.refresh(); });
})();
