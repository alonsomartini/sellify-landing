"""Genera index.html (ES) y en/index.html (EN) de sellify.us v5 desde una sola plantilla.
Uso: python3 build.py <raiz_del_repo>"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()
LEAD_ENDPOINT = ""
CAL = "https://calendar.app.google/2jLD97aqcqJvhxJu5"

# Ventas mensuales en Amazon (Sellerboard). Cifras aprobadas por Alonso para publicarse.
SERIES = {
    "tatiana": dict(data=[441, 1259, 10570, 6567, 5681, 14564, 12329, 16858, 30546], maxv=32000,
                    grid=(0, 10000, 20000, 30000), years=("2024", "2025"), first=(2, -14)),
    "steepy": dict(data=[2816, 8156, 14147, 13038, 10681, 11865, 19387, 14277, 18639, 18956, 17238, 20201], maxv=22000,
                   grid=(0, 10000, 20000), years=("2024", ""), first=(14, 6)),
}

MARK = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <clipPath id="sx-clip"><polygon points="-20,-20 166,-20 336,258 53,720 -20,720"></polygon></clipPath>
    <g id="sx-bars">
      <rect x="0" y="204.5" width="548" height="107" rx="12"></rect>
      <rect x="3" y="204.5" width="542" height="107" rx="12" transform="rotate(58.5 274 258)"></rect>
      <rect x="3" y="204.5" width="542" height="107" rx="12" transform="rotate(-58.5 274 258)"></rect>
    </g>
    <g id="sx-mark">
      <use href="#sx-bars" fill="#999B9E"></use>
      <use href="#sx-bars" fill="#F58238" clip-path="url(#sx-clip)"></use>
      <rect x="88" y="610" width="370" height="90" rx="4" fill="#F58238"></rect>
    </g>
  </defs>
</svg>"""

LD = ('{"@context":"https://schema.org","@type":"Organization","name":"Sellify Agency","legalName":"Cortafuegos LLC",'
      '"url":"https://www.sellify.us/","logo":"https://www.sellify.us/assets/apple-touch-icon.png",'
      '"email":"alonso@sellify-agency.com","telephone":"+1-786-824-7458","founder":{"@type":"Person","name":"Alonso Martini"},'
      '"areaServed":["US","ES","DE"],"knowsLanguage":["es","en"]}')

# Evita el destello del estado final antes de la animación de entrada. Si el script no carga, se muestra todo a los 2.5 s.
HEAD_JS = ("<script>(function(d){d.className+=' js';setTimeout(function(){d.className+=' ready'},2500)})"
           "(document.documentElement)</script>")


def amz(code, w=640):
    """Foto de producto servida por el optimizador de Vercel, con respaldo directo a Amazon."""
    url = "https://m.media-amazon.com/images/I/" + code
    enc = url.replace(":", "%3A").replace("/", "%2F").replace("+", "%2B")
    return (f"onerror=\"this.onerror=null;this.src='{url}'\" "
            f"src=\"/_vercel/image?url={enc}&amp;w={w}&amp;q=80\"")


def mark(w, h):
    return f'<svg width="{w}" height="{h}" viewBox="0 -4 548 708" aria-hidden="true"><use href="#sx-mark"></use></svg>'


def chart(c):
    """Gráfica de líneas de ventas mensuales. Se revela de izquierda a derecha con un clip."""
    key = c["series"]; sr = SERIES[key]; data = sr["data"]
    L, R, T, B, MAXV = 52, 612, 34, 268, sr["maxv"]
    n = len(data)
    xs = [L + i * (R - L) / (n - 1) for i in range(n)]
    ys = [B - v / MAXV * (B - T) for v in data]
    money = lambda v: "$" + format(v, ",")
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"M{xs[0]:.1f},{B} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys)) + f" L{xs[-1]:.1f},{B} Z"
    grid = ""
    for v in sr["grid"]:
        y = B - v / MAXV * (B - T)
        lab = "$0" if v == 0 else f"${v // 1000}K"
        grid += (f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" class="chart__grid"></line>'
                 f'<text x="{L - 10}" y="{y + 4:.1f}" text-anchor="end" class="chart__tick">{lab}</text>')
    months = ""
    for i, m in enumerate(c["months"]):
        months += f'<text x="{xs[i]:.1f}" y="{B + 24}" text-anchor="middle" class="chart__tick">{m}</text>'
    years = f'<text x="{xs[0]:.1f}" y="{B + 42}" text-anchor="middle" class="chart__year">{sr["years"][0]}</text>'
    if sr["years"][1]:
        years += f'<text x="{xs[-1]:.1f}" y="{B + 42}" text-anchor="middle" class="chart__year">{sr["years"][1]}</text>'
    dots = ""
    for i, (x, y) in enumerate(zip(xs, ys)):
        cls = "chart__dot chart__dot--end" if i == n - 1 else "chart__dot"
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if i == n - 1 else 4}" class="{cls}" data-dot></circle>'
    fx, fy = sr["first"]
    return f"""<svg class="chart" viewBox="0 0 640 320" role="img" aria-label="{c['aria']}">
            <defs>
              <linearGradient id="chart-fill-{key}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F58238" stop-opacity=".30"></stop><stop offset="1" stop-color="#F58238" stop-opacity="0"></stop></linearGradient>
              <clipPath id="chart-clip-{key}"><rect x="0" y="0" width="640" height="320" data-chart-clip></rect></clipPath>
            </defs>
            {grid}
            {months}
            {years}
            <g clip-path="url(#chart-clip-{key})">
              <path d="{area}" fill="url(#chart-fill-{key})"></path>
              <polyline points="{pts}" class="chart__line"></polyline>
            </g>
            {dots}
            <text x="{xs[0] + fx:.1f}" y="{ys[0] + fy:.1f}" text-anchor="start" class="chart__val" data-chart-first>{money(data[0])}</text>
            <text x="{xs[-1]:.1f}" y="{ys[-1] - 16:.1f}" text-anchor="end" class="chart__val chart__val--end" data-chart-last data-from="{data[0]}" data-to="{data[-1]}">{money(data[-1])}</text>
          </svg>"""


def case_fig(i, c, t):
    if c["fig"] == "chart":
        return f"""<figure class="case__fig case__fig--chart" data-fig="chart">
          <figcaption class="cap">{c['cap']}</figcaption>
          {chart(c)}
          <p class="case__src">{c['src']}</p>
        </figure>"""
    photo = f'<div class="tile"><img {amz(c["img"])} alt="{c["alt"]}" width="640" height="640" loading="lazy"></div>'
    if c["fig"] == "stats":
        stats = "".join(
            f'<div class="big"><b><span data-n="{s["n"]}" data-pre="{s["pre"]}" data-suf="%">{s["pre"]}{s["n"]}%</span></b><span>{s["label"]}</span></div>'
            for s in c["stats"])
        body = f'<div class="bigs">{stats}</div>'
    elif c["fig"] == "bars":
        s = c["stats"][0]
        body = f"""<div class="bigs">
              <div class="big"><b><span data-n="{s['n']}" data-pre="{s['pre']}" data-suf="%">{s['pre']}{s['n']}%</span></b><span>{s['label']}</span></div>
              <div class="yoy" aria-hidden="true">
                <div class="yoy__row"><span>{c['yoy'][0]}</span><i style="--w:54.05%" data-bar></i><em>100</em></div>
                <div class="yoy__row yoy__row--now"><span>{c['yoy'][1]}</span><i style="--w:100%" data-bar></i><em>185</em></div>
              </div>
              <p class="case__src">{c['src']}</p>
            </div>"""
    else:
        steps = "".join(f'<li data-step><span></span>{s}</li>' for s in c["steps"])
        body = f'<ol class="launch">{steps}</ol>'
    return f"""<figure class="case__fig case__fig--photo" data-fig="{c['fig']}">
          <figcaption class="cap">{c['cap']}</figcaption>
          <div class="case__media">{photo}{body}</div>
        </figure>"""


def cases(t):
    tabs, panels = "", ""
    for i, c in enumerate(t["cases"]):
        sel = "true" if i == 0 else "false"
        tabs += (f'<button type="button" class="tab" role="tab" id="tab-{i}" aria-controls="case-{i}" aria-selected="{sel}" data-tab="{i}">'
                 f'<b>{c["brand"]}</b><span>{c["cat"]}</span></button>')
        note = f'<p class="case__note">{c["note"]}</p>' if c.get("note") else ""
        video = ""
        if c.get("video"):
            video = (f'<button type="button" class="play" data-video-open hidden>'
                     f'<img src="/assets/tatiana-thumb.webp" width="128" height="128" alt="" loading="lazy">'
                     f'<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M7.5 5.5v9l7-4.5z" fill="currentColor"></path></svg>'
                     f'<span>{c["video"]}</span></button>')
        panels += f"""
      <article class="case" id="case-{i}" role="tabpanel" aria-labelledby="tab-{i}" data-case="{i}">
        <div class="case__copy">
          <p class="case__brand"><img src="/assets/logos/{c['logo']}" width="{c['lw']}" height="{c['lh']}" alt="{c['brand']}" loading="lazy"><span>{c['meta']}</span></p>
          <h3 class="case__result">{c['result']}</h3>
          {note}
          <blockquote class="case__quote"><p>{c['quote']}</p><footer><b>{c['who']}</b>, {c['role']}</footer></blockquote>
          {video}
        </div>
        {case_fig(i, c, t)}
      </article>"""
    return tabs, panels


def page(t):
    a = t["a"]
    tabs, panels = cases(t)
    lang_toggle = (
        f'<span aria-current="true">ES</span><a href="/en/" hreflang="en" lang="en" data-set-lang="en" aria-label="English">EN</a>'
        if t["lang"] == "es" else
        f'<a href="/" hreflang="es" lang="es" data-set-lang="es" aria-label="Español">ES</a><span aria-current="true">EN</span>')
    pl_rows = "".join(
        f'<li data-pl-row data-amt="{amt}"><span>{label}</span><b>−${amt}</b></li>' for label, amt in t["pl_rows"])
    segs, to = "", 100
    for i, (_, amt) in enumerate(t["pl_rows"]):
        segs += f'<i class="pl__seg" style="left:{to - amt}%;width:{amt}%" data-pl-seg></i>'
        to -= amt
    problems = "".join(f"<li>{h}</li>" for h in t["problems"])
    rows = "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in t["rows"])
    stats = "".join(
        f'<div><dt><span data-n="{n}" data-dec="{dec}" data-pre="{pre}" data-suf="{suf}">{pre}{n}{suf}</span></dt><dd>{dd}</dd></div>'
        for n, dec, pre, suf, dd in t["stats"])
    steps = "".join(f'<li><span class="steps__n" aria-hidden="true">{i + 1}</span><h3>{h}</h3><p>{p}</p></li>'
                    for i, (h, p) in enumerate(t["steps"]))
    direct = f"""<a class="btn btn--ghost" href="{t['pdf']}" target="_blank" rel="noopener">{t['band_cta']}</a>"""
    if LEAD_ENDPOINT:
        hero_link = f"""<a href="#checklist" class="link">{t['hero_link']}</a>"""
        band_action = f"""<form class="lead" id="lead-form" data-lead data-endpoint="{LEAD_ENDPOINT}" data-pdf="{t['pdf']}" data-subject="{t['lead_subject']}">
      <label class="lead__label" for="lead-email">{t['lead_label']}</label>
      <div class="lead__row">
        <input id="lead-email" name="email" type="email" autocomplete="email" inputmode="email" placeholder="{t['lead_ph']}" required>
        <button type="submit" class="btn btn--ghost">{t['band_cta']}</button>
      </div>
      <input class="lead__trap" type="text" name="empresa" tabindex="-1" autocomplete="off" aria-hidden="true">
      <p class="lead__note">{t['lead_note']}</p>
      <p class="lead__done" role="status" hidden>{t['lead_done']} <a href="{t['pdf']}" target="_blank" rel="noopener">{t['lead_open']}</a></p>
    </form>
    <noscript>{direct}</noscript>"""
    else:
        hero_link = f"""<a href="{t['pdf']}" class="link" target="_blank" rel="noopener">{t['hero_link']}</a>"""
        band_action = direct
    terms = "".join(f"<div><dt>{h}</dt><dd>{p}</dd></div>" for h, p in t["terms"])
    dash_list = "".join(f"<li>{x}</li>" for x in t["dash_list"])
    KM = ' class="kpi--margin"'
    WARN = ' class="warn"'
    kpis = "".join(f'<div{KM if i == 1 else ""}><p>{k}</p><strong>{v}</strong><small>{d}</small></div>'
                   for i, (k, v, d) in enumerate(t["kpis"]))
    th = "".join(f"<th>{x}</th>" for x in t["dash_th"])
    trs = "".join(
        f'<tr><td>{p}</td><td>{s}</td><td>{ac}</td><td{WARN if i == 2 else ""}>{cv}</td></tr>'
        for i, (p, s, ac, cv) in enumerate(t["dash_rows"]))
    founder_p = "".join(f"<p>{p}</p>" for p in t["founder_p"])
    faq = "".join(f"<details><summary>{q}<span aria-hidden=\"true\"></span></summary><p>{r}</p></details>" for q, r in t["faq"])
    audit_list = "".join(f"<li>{x}</li>" for x in t["audit_list"])
    opt_m = "".join(f"<option>{x}</option>" for x in t["f_market_opts"])
    opt_s = "".join(f"<option>{x}</option>" for x in t["f_sales_opts"])
    logos = """<li><img src="/assets/logos/bullpadel.webp" width="125" height="26" alt="Bullpadel USA"></li>
          <li><img src="/assets/logos/tatiana-irizar.webp" width="105" height="38" alt="Tatiana Irizar"></li>
          <li><img src="/assets/logos/zusset.webp" width="92" height="22" alt="Zusset"></li>
          <li><img src="/assets/logos/steepy.webp" width="120" height="18" alt="Steepy"></li>
          <li><img src="/assets/logos/khoul.webp" width="113" height="22" alt="Khoul"></li>
          <li><img src="/assets/logos/valentina-gordon.webp" width="129" height="32" alt="Valentina Gordon"></li>
          <li><img src="/assets/logos/psychodelic.webp" width="45" height="46" alt="Psychodelic"></li>
          <li class="marquee__lock"><img src="/assets/logos/perinola-hg.webp" width="11" height="38" alt=""><span class="marquee__name">PERINOLA HG</span></li>
          <li><img src="/assets/logos/dosis-tea.webp" width="121" height="22" alt="Dösis Tea"></li>
          <li><img src="/assets/logos/bb-belen-berbel.webp" width="39" height="34" alt="BB by Belén Berbel"></li>
          <li><img src="/assets/logos/gran-turismo.webp" width="114" height="26" alt="Gran Turismo"></li>"""
    nav = "".join(f'<a href="#{href}">{label}</a>' for href, label in t["nav"])
    foot_nav = "".join(f'<a href="#{href}">{label}</a>' for href, label in t["foot_nav"])

    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
<link rel="canonical" href="{t['url']}">
<link rel="alternate" hreflang="es" href="https://www.sellify.us/">
<link rel="alternate" hreflang="en" href="https://www.sellify.us/en/">
<link rel="alternate" hreflang="x-default" href="https://www.sellify.us/">
<meta name="theme-color" content="#0F0F10">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{t['url']}">
<meta property="og:title" content="{t['og_title']}">
<meta property="og:description" content="{t['og_desc']}">
<meta property="og:image" content="{t['og_image']}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{t['og_locale']}">
<meta property="og:locale:alternate" content="{t['og_locale_alt']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/hanken-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">
{LD}
</script>
{HEAD_JS}
<link rel="stylesheet" href="/site.css">
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
<a class="skip" href="#{a['top']}">{t['skip']}</a>

<header class="hdr" data-hdr>
  <div class="wrap hdr__in">
    <a href="#{a['top']}" class="brand" aria-label="{t['brand_aria']}">{mark(20, 26)}<span class="brand__word">SELLIFY</span></a>
    <nav class="nav" aria-label="{t['nav_aria']}">{nav}</nav>
    <div class="hdr__end">
      <div class="lang" role="group" aria-label="{t['lang_aria']}">{lang_toggle}</div>
      <a href="{CAL}" class="btn btn--sm" target="_blank" rel="noopener"><span class="btn__long">{t['cta']}</span><span class="btn__short">{t['cta_short']}</span></a>
    </div>
  </div>
</header>

{MARK}

<main id="{a['top']}">

<section class="hero" data-hero>
  <canvas class="hero__canvas" data-mark-canvas aria-hidden="true"></canvas>
  <div class="wrap hero__in">
    <div class="hero__copy">
      <p class="status" data-in><span class="status__dot" aria-hidden="true"></span>{t['status']}</p>
      <h1 class="hero__h1"><span class="ln"><span data-line>{t['h1_a']}</span></span> <span class="ln"><span data-line><em>{t['h1_b']}</em></span></span></h1>
      <p class="hero__sub" data-in>{t['hero_sub']}</p>
      <div class="hero__actions" data-in>
        <a href="{CAL}" class="btn" target="_blank" rel="noopener">{t['cta']}</a>
        {hero_link}
      </div>
      <a class="proof" href="#{a['cases']}" data-video-open data-in>
        <span class="proof__thumb"><img src="/assets/tatiana-thumb.webp" width="128" height="128" alt=""><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#F2F2F2"/><path d="M8 6v8l6-4z" fill="#1A1A1A"/></svg></span>
        <span><b>{t['proof_b']}</b>{t['proof_who']} <span class="proof__cta">{t['proof_cta']}</span></span>
      </a>
    </div>
    <div class="hero__art" data-mark-anchor aria-hidden="true"></div>
  </div>
</section>

<section class="logos" aria-label="{t['logos_aria']}">
  <div class="wrap">
    <div class="logos__box">
      <p class="cap">{t['logos_label']}</p>
      <div class="marquee" data-marquee>
        <ul class="marquee__track">
          {logos}
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="{a['problem']}" class="say">
  <div class="wrap">
    <h2 class="say__h" data-words>{t['say_h']}</h2>
    <p class="say__p" data-words>{t['say_p']}</p>
  </div>
</section>

<section class="pl" data-pl aria-labelledby="pl-title">
  <div class="wrap pl__in">
    <div class="pl__left">
      <p class="cap">{t['pl_cap']}</p>
      <h3 class="pl__title" id="pl-title">{t['pl_title']}</h3>
      <p class="pl__big"><span class="pl__cur">$</span><span data-pl-num>9</span></p>
      <p class="pl__state"><span data-pl-state data-a="{t['pl_state_a']}" data-m="{t['pl_state_m']}" data-b="{t['pl_state_b']}">{t['pl_state_b']}</span></p>
    </div>
    <div class="pl__right">
      <div class="pl__track" aria-hidden="true">
        <i class="pl__keep" data-pl-keep></i>
        {segs}
        <span class="pl__goal" data-pl-goal><span>{t['pl_goal']}</span></span>
      </div>
      <ol class="pl__rows">
        {pl_rows}
      </ol>
      <div class="pl__foot" data-pl-foot>
        <p class="pl__punch">{t['pl_punch']}</p>
        <p class="pl__note">{t['pl_note']}</p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">
    <h2 class="h3 problems__title">{t['problems_title']}</h2>
    <ul class="problems">{problems}</ul>
  </div>
</section>

<section class="band" id="checklist" aria-label="{t['band_aria']}">
  <div class="wrap band__in">
    <img class="band__img" src="{t['band_img']}" width="480" height="480" alt="{t['band_alt']}" loading="lazy">
    <div class="band__copy">
      <h2 class="h3">{t['band_h']}</h2>
      <p>{t['band_p']}</p>
    </div>
    {band_action}
  </div>
</section>

<section id="{a['margin']}" class="sec">
  <div class="wrap duo">
    <div class="duo__head">
      <h2 class="h2">{t['margin_h']}</h2>
      <p class="lead">{t['margin_p']}</p>
    </div>
    <div>
      <ul class="rows" data-rows>{rows}</ul>
      <p class="duo__note">{t['margin_note']}</p>
    </div>
  </div>
</section>

<section id="{a['cases']}" class="cases">
  <div class="wrap">
    <div class="head">
      <h2 class="h2">{t['cases_h']}</h2>
      <p class="lead">{t['cases_p']}</p>
    </div>
    <dl class="stats" data-stats>{stats}</dl>
  </div>
  <div class="viewer" data-viewer>
    <div class="wrap">
      <div class="viewer__frame">
        <div class="viewer__tabs" role="tablist" aria-label="{t['tabs_aria']}">{tabs}</div>
        <div class="viewer__body">{panels}
        </div>
        <div class="viewer__foot">
          <span class="cap" data-viewer-count>1 / {len(t['cases'])}</span>
          <span class="cap viewer__hint">{t['viewer_hint']}</span>
          <a class="cap viewer__skip" href="#{a['how']}">{t['viewer_skip']}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="{a['how']}" class="sec">
  <div class="wrap">
    <div class="head"><h2 class="h2">{t['how_h']}</h2></div>
    <ol class="steps" data-steps>{steps}</ol>
    <a href="{CAL}" class="btn" target="_blank" rel="noopener">{t['cta']}</a>
    <div class="terms">
      <h3 class="h3">{t['terms_h']}</h3>
      <dl class="terms__list">{terms}</dl>
    </div>
  </div>
</section>

<section id="{a['dash']}" class="sec sec--panel">
  <div class="wrap split">
    <div class="split__copy">
      <h2 class="h2">{t['dash_h']}</h2>
      <p class="lead">{t['dash_p']}</p>
      <ul class="rule-list">{dash_list}</ul>
    </div>
    <figure class="dash" role="img" aria-label="{t['dash_aria']}" data-dash>
      <div class="dash__ui">
        <div class="dash__bar">{mark(12, 16)}<b>SELLIFY</b><span>{t['dash_name']}</span><span class="dash__tag">{t['dash_tag']}</span></div>
        <div class="dash__main">
          <div class="kpis">{kpis}</div>
          <div>
            <p class="dash__label">{t['dash_chart']}</p>
            <svg viewBox="0 0 600 140" preserveAspectRatio="none" aria-hidden="true" class="dash__chart">
              <line x1="0" y1="139" x2="600" y2="139" stroke="#E6E7E8" stroke-width="2"></line>
              <polyline pathLength="1" points="0,96 20,92 41,98 62,88 83,90 103,84 124,86 145,80 166,83 186,76 207,79 228,72 248,75 269,70 290,74 310,66 331,69 352,62 372,64 393,58 414,61 434,54 455,57 476,49 497,52 517,45 538,48 559,40 579,43 600,36" fill="none" stroke="#F58238" stroke-width="3" stroke-linejoin="round" data-dash-line></polyline>
            </svg>
          </div>
          <table>
            <thead><tr>{th}</tr></thead>
            <tbody>{trs}</tbody>
          </table>
        </div>
      </div>
    </figure>
  </div>
</section>

<section id="{a['founder']}" class="sec">
  <div class="wrap founder">
    <figure class="founder__photo">
      <img src="/assets/alonso.webp" width="821" height="889" alt="{t['founder_alt']}" loading="lazy">
      <figcaption class="cap">{t['founder_cap']}</figcaption>
    </figure>
    <div class="founder__copy">
      <h2 class="h2">{t['founder_h']}</h2>
      {founder_p}
      <p class="founder__sign">{mark(22, 28)}<span><b>Alonso Martini</b><br>{t['founder_role']}</span></p>
    </div>
  </div>
</section>

<section id="{a['faq']}" class="sec sec--line">
  <div class="wrap duo">
    <div class="duo__head"><h2 class="h2">{t['faq_h']}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section id="{a['audit']}" class="sec sec--panel" data-audit>
  <div class="wrap audit">
    <div class="audit__copy">
      <h2 class="h2 audit__h">{t['audit_h']}</h2>
      <p class="lead">{t['audit_p']}</p>
      <ul class="rule-list">{audit_list}</ul>
      <div class="audit__book">
        <a href="{CAL}" class="btn" target="_blank" rel="noopener">{t['cta']}</a>
        <p class="audit__note">{t['audit_note']}</p>
      </div>
    </div>
    <form class="form" id="audit-form" aria-labelledby="form-title">
      <h3 class="h3 form__title" id="form-title">{t['form_h']}</h3>
      <div class="field"><label for="f-nombre">{t['f_name']}</label><input id="f-nombre" name="nombre" type="text" autocomplete="name" placeholder="{t['f_name_ph']}" required></div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" placeholder="{t['f_email_ph']}" required></div>
      <div class="field field--full"><label for="f-marca">{t['f_brand']}</label><input id="f-marca" name="marca" type="text" inputmode="url" placeholder="{t['f_brand_ph']}"></div>
      <div class="field"><label for="f-mercado">{t['f_market']}</label><select id="f-mercado" name="mercado">{opt_m}</select></div>
      <div class="field"><label for="f-ventas">{t['f_sales']}</label><select id="f-ventas" name="ventas">{opt_s}</select></div>
      <button type="submit" class="btn btn--ghost">{t['f_submit']}</button>
      <p class="form__note">{t['f_note']} <a href="tel:+17868247458">+1 786 824 7458</a>.</p>
    </form>
  </div>
</section>

</main>

<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <p>{t['foot_p']}</p>
        <a href="{CAL}" class="btn btn--sm" target="_blank" rel="noopener">{t['cta']}</a>
      </div>
      <nav class="footer__col" aria-label="{t['foot_aria']}">
        <p class="cap">{t['foot_site']}</p>
        {foot_nav}
      </nav>
      <div class="footer__col">
        <p class="cap">{t['foot_contact']}</p>
        <a href="https://wa.me/34627071754">WhatsApp +34 627 07 17 54</a><a href="tel:+17868247458">{t['foot_calls']} +1 786 824 7458</a><a href="mailto:alonso@sellify-agency.com">alonso@sellify-agency.com</a>
      </div>
    </div>
    <p class="footer__word" aria-hidden="true">{mark(96, 124)}<span>SELLIFY</span></p>
    <div class="footer__legal">
      <span>{t['foot_legal']}</span>
      {t['foot_lang']}
    </div>
  </div>
</footer>

<div class="dock" data-dock>
  <span class="dock__status"><span class="status__dot" aria-hidden="true"></span>{t['status']}</span>
  <a href="{CAL}" class="btn btn--sm" target="_blank" rel="noopener">{t['cta']}</a>
</div>

<dialog class="video-dialog" id="video-dialog" aria-label="{t['video_aria']}">
  <video id="video-el" controls playsinline preload="none" poster="/assets/tatiana-poster.webp">
    <source src="/assets/tatiana-testimonio.mp4" type="video/mp4">
  </video>
  <button type="button" id="video-close">{t['close']}</button>
</dialog>

<script defer src="/assets/vendor/gsap.min.js"></script>
<script defer src="/assets/vendor/ScrollTrigger.min.js"></script>
<script defer src="/assets/vendor/lenis.min.js"></script>
<script defer src="/site.js"></script>
</body>
</html>
"""


ES = dict(
    lang="es",
    a=dict(top="inicio", problem="problema", margin="margen", cases="casos", how="como-funciona", dash="dashboard",
           founder="fundador", faq="preguntas", audit="auditoria"),
    title="Sellify | Agencia de Amazon: vende más sin perder margen",
    desc="Muchas marcas venden más en Amazon y ganan menos. Sellify gestiona tu publicidad, contenido y operaciones con tu P&amp;L a la vista, para que crezcas sin perder margen.",
    url="https://www.sellify.us/",
    og_title="Sellify | Vende más en Amazon sin perder margen",
    og_desc="Gestionamos la publicidad, el contenido y las operaciones de tu marca en Amazon Estados Unidos y Europa, con tu P&amp;L real cada mes.",
    og_image="https://www.sellify.us/assets/og-image.png", og_locale="es_ES", og_locale_alt="en_US",
    skip="Saltar al contenido", brand_aria="Sellify, inicio", nav_aria="Principal", lang_aria="Idioma",
    nav=[("casos", "Casos"), ("como-funciona", "Cómo funciona"), ("dashboard", "Dashboard"), ("fundador", "Fundador")],
    cta="Agenda tu auditoría", cta_short="Auditoría",
    status="Aceptando marcas nuevas",
    h1_a="Vende más en Amazon", h1_b="sin perder margen.",
    hero_sub="Gestionamos la publicidad, el contenido y las operaciones de tu marca en Amazon Estados Unidos y Europa, y cada mes te mostramos cuánto ganas de verdad.",
    pdf="/assets/checklist-10-fugas-de-margen-amazon.pdf",
    hero_link="Descarga el checklist de las 10 fugas",
    proof_b="De $441 a $30.5K al mes en Amazon, en 9 meses.", proof_who="Tatiana Irizar, fundadora.", proof_cta="Ver su testimonio",
    logos_aria="Clientes", logos_label="Marcas con las que hemos trabajado",
    say_h="Vender más no debería significar ganar menos.",
    say_p="Si no sabes qué campaña o qué producto te deja dinero, cada mes en Amazon es una apuesta.",
    pl_cap="Ejemplo ilustrativo · Producto vendido con FBA en Amazon EE.UU.",
    pl_title="De cada $100 que vendes en Amazon, ¿cuánto te queda?",
    pl_state_a="La venta que Amazon te muestra", pl_state_m="Lo que va quedando", pl_state_b="Lo que te queda",
    pl_goal="Margen sano: $15",
    pl_rows=[("Costo del producto", 28), ("Comisión de Amazon", 15), ("Envío FBA", 20), ("Publicidad", 20),
             ("Devoluciones", 5), ("Almacenamiento y otros cargos", 3)],
    pl_punch="Amazon te muestra los $100. Te quedan $9, cuando un margen sano ronda los $15. Cerrar esa diferencia es nuestro trabajo.",
    pl_note="El reparto real de cada producto aparece en tu P&amp;L.",
    problems_title="Lo que más encontramos al auditar una cuenta",
    problems=["Pagas clics que no venden.", "Tu ACoS se ve bien. Tu margen, no.",
              "Tus productos no aparecen donde se compra.", "Te quedas sin stock, o te sobra."],
    band_aria="Checklist gratuito", band_img="/assets/checklist-preview-es.webp",
    band_alt="Portada del checklist 10 fugas de margen en Amazon",
    band_h="¿Todavía no estás listo para una auditoría?",
    band_p="Revisa tu cuenta tú mismo con el checklist de las 10 fugas de margen que más encontramos. Gratis, en PDF, para hacerlo en una tarde.",
    band_cta="Descargar el checklist",
    lead_label="Tu email", lead_ph="tu@marca.com", lead_subject="Nuevo lead del checklist (web en español)",
    lead_note="Usamos tu email solo para escribirte sobre tu marca en Amazon. Sin spam.",
    lead_done="Listo. Si el PDF no se abrió,", lead_open="ábrelo aquí.",
    margin_h="Margen primero.",
    margin_p="Primero tapamos las fugas, después invertimos para crecer. Así cada dólar que pones en Amazon trabaja para tu margen.",
    rows=[("Publicidad que responde a tu margen", "Campañas gestionadas contra un objetivo de rentabilidad, no solo de ventas, y optimizadas cada semana."),
          ("Listings que convierten", "Títulos, contenido A+ e imágenes que responden lo que el comprador pregunta antes de comprar."),
          ("Inventario sin sorpresas", "Forecast y envíos a FBA para no perder ranking ni pagar almacenamiento de más."),
          ("Números claros cada mes", "Tu P&amp;L real, por producto y por campaña, y lo revisamos contigo.")],
    margin_note="Publicidad (Sponsored Products, Brands y Display), listings y contenido A+, operaciones FBA y Brand Registry. También Walmart, Shopify y TikTok Shop cuando tiene sentido para tu marca.",
    cases_h="Sabemos lo que cuesta crecer en Amazon.",
    cases_p="Es frustrante ver subir las ventas sin saber si estás ganando. Llevamos más de 10 años resolviendo eso para marcas como estas.",
    stats=[("4.5", 1, "+$", "M", "en ventas generadas para clientes"), ("1", 0, "+$", "M", "en publicidad gestionada"),
           ("10", 0, "", "+ años", "vendiendo y gestionando marcas en marketplaces")],
    tabs_aria="Casos de clientes", viewer_hint="Sigue bajando para ver el siguiente caso", viewer_skip="Saltar casos",
    cases=[
        dict(brand="Tatiana Irizar", cat="Belleza", meta="Belleza, Amazon EE.UU.", logo="tatiana-irizar.webp", lw=105, lh=38,
             result="De $441 a $30.5K al mes en 9 meses.",
             quote="“Sellify llevó nuestras ventas en Amazon de $3.5K/mes a $30K/mes en 9 meses.”", who="Tatiana Irizar", role="fundadora",
             video="Ver su testimonio en video", fig="chart", series="tatiana",
             months=["may", "jun", "jul", "ago", "sep", "oct", "nov", "dic", "ene"],
             aria="Gráfica de ventas mensuales de Tatiana Irizar en Amazon: de $441 en mayo de 2024 a $30,546 en enero de 2025.",
             cap="Fig. 1 · Ventas mensuales en Amazon EE.UU., mayo 2024 a enero 2025", src="Fuente: Sellerboard, cuenta de la marca."),
        dict(brand="Bullpadel USA", cat="Pádel", meta="Pádel", logo="bullpadel.webp", lw=125, lh=26,
             result="-20% ACoS y +110% en ingresos, en 8 meses.",
             quote="“Reconstruyeron por completo nuestra estrategia de PPC.”", who="Carlos L.", role="CFO",
             fig="stats", img="515cgaxhbKL.jpg", alt="Pala de pádel Bullpadel Vertex 05", cap="Fig. 2 · Resultado en 8 meses",
             stats=[dict(n=110, pre="+", label="ingresos"), dict(n=20, pre="−", label="ACoS")]),
        dict(brand="Steepy", cat="Accesorios de oficina", meta="Accesorios de oficina", logo="steepy.webp", lw=120, lh=18,
             result="De $2.8K a $20.2K al mes en 2024.",
             quote="“El equipo de Sellify llegó con un plan claro, tomó el control de las operaciones diarias y optimizó completamente nuestros listings.”",
             who="Alberto O.", role="fundador",
             fig="chart", series="steepy",
             months=["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
             aria="Gráfica de ventas mensuales de Steepy en Amazon: de $2,816 en enero de 2024 a $20,201 en diciembre de 2024.",
             cap="Fig. 3 · Ventas mensuales en Amazon, enero a diciembre 2024", src="Fuente: Sellerboard, productos de la marca."),
        dict(brand="Zusset", cat="Pádel", meta="Pádel", logo="zusset.webp", lw=92, lh=22,
             result="De la configuración a la primera venta.",
             quote="“Sabíamos que teníamos que estar en Amazon, pero el proceso era intimidante. Alonso y su equipo gestionaron todo nuestro lanzamiento multicanal.”",
             who="Carlos G.", role="CEO y fundador",
             fig="launch", img="81eb+MPQm6L.jpg", alt="Pala de pádel Zusset Solid Pro", cap="Fig. 4 · Lanzamiento",
             steps=["Configuración de la cuenta", "Lanzamiento multicanal", "Primera venta"]),
    ],
    how_h="Empezar es simple.",
    steps=[("Agenda tu auditoría", "30 minutos para revisar tu cuenta, o tu plan para entrar a Amazon."),
           ("Recibe tu plan", "Hallazgos por escrito, ordenados por lo que más dinero te cuesta, y una propuesta clara."),
           ("Crece con tus números a la vista", "Ejecutamos el plan y cada mes revisamos contigo tu P&amp;L y los próximos pasos.")],
    terms_h="Sin letra pequeña.",
    terms=[("Sin permanencia mínima", "Te quedas porque funciona, no porque lo diga un contrato."),
           ("Cancelas con un correo", "Un correo basta para terminar el servicio."),
           ("Tu cuenta sigue siendo tuya", "Trabajamos dentro de tu cuenta de Amazon. Nunca deja de ser tuya."),
           ("Hablas con Alonso", "Tu contacto es el fundador, no un intermediario.")],
    dash_h="Tus números, siempre a la vista.",
    dash_p="Cada mes recibes un reporte con el P&amp;L de tu cuenta y lo revisamos contigo. Entre reportes, tienes un dashboard con ventas, publicidad e inventario actualizado cada día.",
    dash_list=["P&amp;L mensual contra el mes y el año anterior", "Publicidad por campaña: inversión, ACoS y ROAS", "Inventario y días de cobertura por producto"],
    dash_aria="Vista de ejemplo del dashboard de clientes de Sellify, con datos ficticios",
    dash_name="Dashboard de clientes", dash_tag="Datos de ejemplo", dash_chart="Ventas diarias, últimos 30 días",
    kpis=[("Ventas 30 días", "$52,340", "+8%"), ("Margen neto", "23.6%", "+1.8 pts"), ("ACoS", "21.4%", "-2.1 pts"), ("TACoS", "15.2%", "-1.4 pts")],
    dash_th=["Producto", "Ventas", "ACoS", "Cobertura"],
    dash_rows=[("Producto A", "$24,910", "18.2%", "41 días"), ("Producto B", "$17,480", "23.9%", "29 días"), ("Producto C", "$9,950", "26.7%", "12 días")],
    founder_alt="Alonso Martini, fundador de Sellify", founder_cap="Alonso Martini, fundador",
    founder_h="Una agencia pequeña, a propósito.", founder_role="Fundador de Sellify",
    founder_p=["Quieres que Amazon sea un canal rentable y predecible para tu marca. Para eso necesitas que la publicidad, el contenido y el inventario trabajen hacia un mismo objetivo: tu margen. El problema es que Amazon te muestra ventas, no ganancias, y es fácil terminar pagando por crecer sin saber si estás ganando.",
               "Soy Alonso Martini. Llevo más de 10 años vendiendo y gestionando marcas en marketplaces, y fundé Sellify para trabajar con pocas marcas a la vez y responder por sus resultados como si fueran míos. Detrás de cada cuenta hay un equipo dedicado de operaciones, publicidad y contenido, y yo reviso personalmente cada reporte antes de que llegue a ti. Atendemos en español e inglés."],
    faq_h="Preguntas frecuentes.",
    faq=[("¿Trabajan con marcas que todavía no venden en Amazon?", "Sí. Te ayudamos a abrir la cuenta, registrar la marca en Brand Registry y lanzar tus primeros productos."),
         ("¿Piden un mínimo de ventas?", "No. En la auditoría vemos juntos si tiene sentido trabajar con nosotros."),
         ("¿Hay permanencia mínima?", "No. Trabajas con nosotros mientras te funcione y cancelas con un correo."),
         ("¿Voy a tener acceso a mis datos?", "Sí. Tienes tu dashboard, recibes el reporte mensual y tu cuenta de Amazon sigue siendo tuya en todo momento."),
         ("¿Cuánto cuesta?", "Depende del alcance y del tamaño de la cuenta. Después de la auditoría te enviamos una propuesta con el costo exacto.")],
    audit_h="Agenda tu auditoría.", audit_p="Deja de adivinar qué te deja dinero en Amazon.",
    audit_list=["30 minutos conmigo revisando tu cuenta", "Hallazgos por escrito, ordenados por lo que más dinero te cuesta", "Una recomendación clara, trabajes o no con nosotros"],
    audit_note="30 minutos por Google Meet. Eliges el día y la hora.",
    form_h="¿Prefieres escribir primero?",
    f_name="Nombre", f_name_ph="Tu nombre", f_email_ph="tu@marca.com",
    f_brand="Link de tu marca en Amazon o tu web", f_brand_ph="amazon.com/stores/tu-marca",
    f_market="¿Dónde vendes hoy?", f_market_opts=["Amazon EE.UU.", "Amazon Europa", "Aún no en Amazon"],
    f_sales="Ventas mensuales en Amazon", f_sales_opts=["Todavía no vendo", "Menos de $10K", "$10K a $50K", "$50K a $200K", "Más de $200K"],
    f_submit="Enviar por WhatsApp", f_note="Se abre WhatsApp con tus datos listos para mandar. También puedes llamar al",
    foot_p="Agencia de Amazon para marcas que quieren crecer sin perder margen, en Estados Unidos y Europa.",
    foot_aria="Pie de página", foot_site="Sitio", foot_contact="Contacto", foot_calls="Llamadas",
    foot_nav=[("casos", "Casos"), ("como-funciona", "Cómo funciona"), ("dashboard", "Dashboard"), ("preguntas", "Preguntas")],
    foot_legal="© 2026 Sellify Agency. Operado por Cortafuegos LLC.",
    foot_lang='<a href="/en/" hreflang="en" lang="en" data-set-lang="en">English</a>',
    video_aria="Testimonio de Tatiana Irizar", close="Cerrar",
)

EN = dict(
    lang="en",
    a=dict(top="top", problem="problem", margin="margin", cases="results", how="how-it-works", dash="dashboard",
           founder="founder", faq="faq", audit="audit"),
    title="Sellify | Amazon Agency: Sell More Without Giving Up Margin",
    desc="Many brands sell more on Amazon and keep less. Sellify runs your advertising, content, and operations with your P&amp;L in plain view, so you grow without giving up margin.",
    url="https://www.sellify.us/en/",
    og_title="Sellify | Sell more on Amazon without giving up margin",
    og_desc="We run advertising, content, and operations for your brand on Amazon in the US and Europe, with your real P&amp;L every month.",
    og_image="https://www.sellify.us/assets/og-image-en.png", og_locale="en_US", og_locale_alt="es_ES",
    skip="Skip to content", brand_aria="Sellify, home", nav_aria="Main", lang_aria="Language",
    nav=[("results", "Results"), ("how-it-works", "How it works"), ("dashboard", "Dashboard"), ("founder", "Founder")],
    cta="Book your audit", cta_short="Audit",
    status="Taking on new brands",
    h1_a="Sell more on Amazon", h1_b="without giving up margin.",
    hero_sub="We run advertising, content, and operations for your brand on Amazon in the US and Europe, and every month we show you what you're really making.",
    pdf="/assets/amazon-margin-leaks-checklist.pdf",
    hero_link="Get the 10 margin leaks checklist",
    proof_b="From $441 to $30.5K a month on Amazon, in 9 months.", proof_who="Tatiana Irizar, founder.", proof_cta="Watch her testimonial",
    logos_aria="Clients", logos_label="Brands we've worked with",
    say_h="Selling more shouldn't mean making less.",
    say_p="If you can't tell which campaign or product is making you money, every month on Amazon is a gamble.",
    pl_cap="Illustrative example · Product sold through FBA on Amazon US",
    pl_title="Out of every $100 you sell on Amazon, how much do you keep?",
    pl_state_a="The sale Amazon shows you", pl_state_m="What's left so far", pl_state_b="What you keep",
    pl_goal="Healthy margin: $15",
    pl_rows=[("Product cost", 28), ("Amazon referral fee", 15), ("FBA fulfillment", 20), ("Advertising", 20),
             ("Returns", 5), ("Storage and other fees", 3)],
    pl_punch="Amazon shows you the $100. You keep $9, when a healthy margin is around $15. Closing that gap is our job.",
    pl_note="Each product's real breakdown shows up in your P&amp;L.",
    problems_title="What we find most often when we audit an account",
    problems=["You're paying for clicks that don't sell.", "Your ACoS looks fine. Your margin doesn't.",
              "Your products don't show up where people buy.", "You run out of stock, or sit on too much."],
    band_aria="Free checklist", band_img="/assets/checklist-preview-en.webp",
    band_alt="Cover of the 10 Amazon margin leaks checklist",
    band_h="Not ready for an audit yet?",
    band_p="Review your account yourself with a checklist of the 10 margin leaks we find most often. Free, as a PDF, and doable in one afternoon.",
    band_cta="Download the checklist",
    lead_label="Your email", lead_ph="you@brand.com", lead_subject="Nuevo lead del checklist (web en inglés)",
    lead_note="We only use your email to write to you about your brand on Amazon. No spam.",
    lead_done="Done. If the PDF didn't open,", lead_open="open it here.",
    margin_h="Margin first.",
    margin_p="First we plug the leaks, then we invest to grow. That way every dollar you put into Amazon works for your margin.",
    rows=[("Advertising tied to your margin", "Campaigns managed against a profitability target, not just a sales number, and optimized every week."),
          ("Listings that convert", "Titles, A+ Content, and images that answer what shoppers ask before they buy."),
          ("Inventory without surprises", "Forecasting and FBA shipments so you don't lose rank or overpay for storage."),
          ("Clear numbers every month", "Your real P&amp;L, by product and by campaign, and we walk you through it.")],
    margin_note="Advertising (Sponsored Products, Brands, and Display), listings and A+ Content, FBA operations, and Brand Registry. Also Walmart, Shopify, and TikTok Shop when it makes sense for your brand.",
    cases_h="We know what it takes to grow on Amazon.",
    cases_p="It's frustrating to watch sales go up without knowing if you're making money. We've spent more than 10 years solving that for brands like these.",
    stats=[("4.5", 1, "+$", "M", "in sales generated for clients"), ("1", 0, "+$", "M", "in ad spend managed"),
           ("10", 0, "", "+ years", "selling and managing brands on marketplaces")],
    tabs_aria="Client results", viewer_hint="Keep scrolling for the next case", viewer_skip="Skip cases",
    cases=[
        dict(brand="Tatiana Irizar", cat="Beauty", meta="Beauty, Amazon US", logo="tatiana-irizar.webp", lw=105, lh=38,
             result="From $441 to $30.5K a month in 9 months.",
             quote="“Sellify took our Amazon sales from $3.5k/mo to $30k/mo in 9 months.”", who="Tatiana Irizar", role="founder",
             video="Watch her video testimonial", fig="chart", series="tatiana",
             months=["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
             aria="Chart of Tatiana Irizar's monthly Amazon sales: from $441 in May 2024 to $30,546 in January 2025.",
             cap="Fig. 1 · Monthly sales on Amazon US, May 2024 to January 2025", src="Source: Sellerboard, the brand's account."),
        dict(brand="Bullpadel USA", cat="Padel", meta="Padel", logo="bullpadel.webp", lw=125, lh=26,
             result="-20% ACoS and +110% revenue, in 8 months.",
             quote="“They rebuilt our entire PPC strategy.”", who="Carlos L.", role="CFO",
             fig="stats", img="515cgaxhbKL.jpg", alt="Bullpadel Vertex 05 padel racket", cap="Fig. 2 · Result in 8 months",
             stats=[dict(n=110, pre="+", label="revenue"), dict(n=20, pre="−", label="ACoS")]),
        dict(brand="Steepy", cat="Office accessories", meta="Office accessories", logo="steepy.webp", lw=120, lh=18,
             result="From $2.8K to $20.2K a month in 2024.",
             quote="“The Sellify team came in with a clear plan, took over the day-to-day operations, and completely optimized our listings.”",
             who="Alberto O.", role="founder",
             fig="chart", series="steepy",
             months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
             aria="Chart of Steepy's monthly Amazon sales: from $2,816 in January 2024 to $20,201 in December 2024.",
             cap="Fig. 3 · Monthly sales on Amazon, January to December 2024", src="Source: Sellerboard, the brand's products."),
        dict(brand="Zusset", cat="Padel", meta="Padel", logo="zusset.webp", lw=92, lh=22,
             result="From setup to first sale.",
             quote="“Being on Amazon was intimidating and we had no idea where to start. Alonso and his team handled our entire multi-channel launch.”",
             who="Carlos G.", role="CEO and founder",
             fig="launch", img="81eb+MPQm6L.jpg", alt="Zusset Solid Pro padel racket", cap="Fig. 4 · Launch",
             steps=["Account setup", "Multi-channel launch", "First sale"]),
    ],
    how_h="Getting started is simple.",
    steps=[("Book your audit", "30 minutes to review your account, or your plan to launch on Amazon."),
           ("Get your plan", "Written findings, ranked by what's costing you the most, plus a clear proposal."),
           ("Grow with your numbers in view", "We execute the plan, and every month we review your P&amp;L and next steps with you.")],
    terms_h="No fine print.",
    terms=[("No minimum term", "You stay because it works, not because a contract says so."),
           ("Cancel with one email", "One email is all it takes to end the service."),
           ("Your account stays yours", "We work inside your Amazon account. It never stops being yours."),
           ("You talk to Alonso", "Your contact is the founder, not a go-between.")],
    dash_h="Your numbers, always in view.",
    dash_p="Every month you get a report with your account's P&amp;L, and we walk you through it. Between reports, you have a dashboard with sales, advertising, and inventory, updated daily.",
    dash_list=["Monthly P&amp;L vs. last month and last year", "Advertising by campaign: spend, ACoS, and ROAS", "Inventory and days of cover by product"],
    dash_aria="Sample view of the Sellify client dashboard, with fictional data",
    dash_name="Client dashboard", dash_tag="Sample data", dash_chart="Daily sales, last 30 days",
    kpis=[("30-day sales", "$52,340", "+8%"), ("Net margin", "23.6%", "+1.8 pts"), ("ACoS", "21.4%", "-2.1 pts"), ("TACoS", "15.2%", "-1.4 pts")],
    dash_th=["Product", "Sales", "ACoS", "Cover"],
    dash_rows=[("Product A", "$24,910", "18.2%", "41 days"), ("Product B", "$17,480", "23.9%", "29 days"), ("Product C", "$9,950", "26.7%", "12 days")],
    founder_alt="Alonso Martini, founder of Sellify", founder_cap="Alonso Martini, founder",
    founder_h="A small agency, on purpose.", founder_role="Founder of Sellify",
    founder_p=["You want Amazon to be a profitable, predictable channel for your brand. That takes advertising, content, and inventory working toward one goal: your margin. The problem is that Amazon shows you sales, not profit, and it's easy to end up paying for growth without knowing whether you're making money.",
               "I'm Alonso Martini. I've spent more than 10 years selling and managing brands on marketplaces, and I founded Sellify to work with a few brands at a time and own their results as if they were mine. Behind every account is a dedicated team for operations, advertising, and content, and I personally review every report before it reaches you. We work in English and Spanish."],
    faq_h="Frequently asked questions.",
    faq=[("Do you work with brands that aren't on Amazon yet?", "Yes. We help you open the account, enroll your brand in Brand Registry, and launch your first products."),
         ("Do you require minimum sales?", "No. During the audit we decide together whether working with us makes sense."),
         ("Is there a minimum term?", "No. You work with us for as long as it works for you, and you cancel with one email."),
         ("Will I have access to my data?", "Yes. You get your dashboard and the monthly report, and your Amazon account stays yours at all times."),
         ("How much does it cost?", "It depends on scope and account size. After the audit, we send you a proposal with the exact cost.")],
    audit_h="Book your audit.", audit_p="Stop guessing what's making you money on Amazon.",
    audit_list=["30 minutes with me, reviewing your account", "Written findings, ranked by what's costing you the most", "A clear recommendation, whether or not you work with us"],
    audit_note="30 minutes on Google Meet. You pick the day and time.",
    form_h="Prefer to write first?",
    f_name="Name", f_name_ph="Your name", f_email_ph="you@brand.com",
    f_brand="Your Amazon store or website", f_brand_ph="amazon.com/stores/your-brand",
    f_market="Where do you sell today?", f_market_opts=["Amazon US", "Amazon Europe", "Not on Amazon yet"],
    f_sales="Monthly Amazon sales", f_sales_opts=["Not selling yet", "Under $10K", "$10K to $50K", "$50K to $200K", "Over $200K"],
    f_submit="Send on WhatsApp", f_note="Opens WhatsApp with your details ready to send. You can also call",
    foot_p="Amazon agency for brands that want to grow without giving up margin, in the US and Europe.",
    foot_aria="Footer", foot_site="Site", foot_contact="Contact", foot_calls="Calls",
    foot_nav=[("results", "Results"), ("how-it-works", "How it works"), ("dashboard", "Dashboard"), ("faq", "FAQ")],
    foot_legal="© 2026 Sellify Agency. Operated by Cortafuegos LLC.",
    foot_lang='<a href="/" hreflang="es" lang="es" data-set-lang="es">Español</a>',
    video_aria="Tatiana Irizar's testimonial", close="Close",
)

(ROOT / "index.html").write_text(page(ES), encoding="utf-8")
(ROOT / "en").mkdir(exist_ok=True)
(ROOT / "en" / "index.html").write_text(page(EN), encoding="utf-8")
for f in ("index.html", "en/index.html"):
    s = (ROOT / f).read_text(encoding="utf-8")
    assert "—" not in s, f + " contiene una raya larga"
    print(f, len(s), "bytes")
