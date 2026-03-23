import json, pathlib, subprocess, sys

base = pathlib.Path(__file__).parent

meta    = json.loads((base / "content/meta.json").read_text(encoding="utf-8"))
css     = (base / "assets/css/paper.css").read_text(encoding="utf-8")
sources = json.loads((base / "sources/sources.json").read_text(encoding="utf-8"))

chapters_md = []
for fname in meta["chapters"]:
    p = base / "content" / fname
    if p.exists():
        chapters_md.append(p.read_text(encoding="utf-8"))

# Minimaler Markdown→HTML-Konverter (kein externes Package nötig)
import re

# Global figure counter (reset per build, shared across chapters)
_fig_counter = [0]

def md2html(md):
    lines = md.split("\n")
    out = []
    in_table = False
    in_ul = False
    in_ol = False
    in_blockquote = False
    buf = []

    def flush_buf():
        if buf:
            text = " ".join(buf).strip()
            if text:
                out.append("<p>" + inline(text) + "</p>")
            buf.clear()

    def inline(t):
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
        t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
        return t

    for line in lines:
        # Standalone figure: ![Caption](figures/...)
        m_fig = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', line.strip())
        if m_fig:
            flush_buf()
            if in_ul: out.append("</ul>"); in_ul=False
            if in_ol: out.append("</ol>"); in_ol=False
            cap, src = m_fig.group(1), m_fig.group(2)
            _fig_counter[0] += 1
            n = _fig_counter[0]
            out.append(
                f'<figure id="fig{n}">'
                f'<img src="{src}" alt="{cap}" style="max-width:100%;height:auto;border:1px solid #ccc;">'
                f'<figcaption><strong>Abbildung {n}:</strong> {inline(cap)}</figcaption>'
                f'</figure>'
            )
            continue

        # Headings
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            flush_buf()
            if in_ul: out.append("</ul>"); in_ul=False
            if in_ol: out.append("</ol>"); in_ol=False
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            continue

        # Blockquote
        if line.startswith("> "):
            flush_buf()
            out.append(f'<blockquote><p>{inline(line[2:])}</p></blockquote>')
            continue

        # Table row
        if "|" in line and line.strip().startswith("|"):
            flush_buf()
            if not in_table:
                out.append('<table>')
                in_table = True
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
            elif re.match(r'^\|[-| :]+\|$', line.strip()):
                pass  # separator row
            else:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        else:
            if in_table:
                out.append("</tbody></table>")
                in_table = False

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', line)
        if m:
            flush_buf()
            if not in_ul: out.append("<ul>"); in_ul=True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        else:
            if in_ul: out.append("</ul>"); in_ul=False

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            flush_buf()
            if not in_ol: out.append("<ol>"); in_ol=True
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        else:
            if in_ol: out.append("</ol>"); in_ol=False

        # HTML comment passthrough
        if line.strip().startswith("<!--"):
            continue

        # Blank line
        if not line.strip():
            flush_buf()
            continue

        buf.append(line)

    flush_buf()
    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    if in_table: out.append("</tbody></table>")

    return "\n".join(out)

# Quellen rendern
BADGE_LABELS = {
    "peer":"🎓 Peer-reviewed","institution":"🏛️ Institution","book":"📚 Verlag",
    "preprint":"🔬 Preprint","web":"🌐 Web","austria":"🇦🇹 Österreich",
    "openaccess":"🔓 Open Access","paywall":"🔒 Paywall","math":"🧮 Mathematik"
}

def score_color(s):
    return "#1a6b3c" if s>=9 else "#2e7d32" if s>=7 else "#e65100" if s>=5 else "#b71c1c"

def stars_html(sc):
    n = 5 if sc>=9 else 4 if sc>=7 else 3 if sc>=5 else 2
    return '★'*n + '<span style="color:#ddd">★</span>'*(5-n)

AGE_GROUP_LABELS = {
    "vorschule":  "👶 Vorschule (3–6)",
    "primarstufe": "🧒 Primarstufe (6–10)",
    "sek1":       "📘 SEK I (10–15)",
    "sek2":       "📗 SEK II (15–19)",
    "hochschule": "🎓 Hochschule",
    "lehrende":   "👩‍🏫 Lehrende/Studierende",
    "mixed":      "👥 Gemischt",
    "none":       "—",
}

def source_card(s, cited=False):
    badges = "".join(
        f'<span style="font-size:.68rem;padding:.1rem .45rem;border-radius:10px;'
        f'border:1px solid currentColor;margin-right:.25rem;white-space:nowrap">'
        f'{BADGE_LABELS.get(b,b)}</span>'
        for b in (s.get("badges") or [])
    )
    # "Verwendet im Artikel"-Badge
    if cited:
        badges += (
            '<span style="font-size:.68rem;padding:.1rem .45rem;border-radius:10px;'
            'background:#e8f5e9;color:#2e7d32;border:1px solid #81c784;'
            'margin-right:.25rem;white-space:nowrap;font-weight:600">✓ Im Artikel</span>'
        )
    # Altersgruppen-Badge
    age_group = s.get("age_group", "")
    if age_group and age_group in AGE_GROUP_LABELS and age_group != "none":
        badges += (
            f'<span style="font-size:.68rem;padding:.1rem .45rem;border-radius:10px;'
            f'background:#f3f4f6;color:#374151;border:1px solid #d1d5db;'
            f'margin-right:.25rem;white-space:nowrap">{AGE_GROUP_LABELS[age_group]}</span>'
        )

    url = s.get("url","#")
    title = s["title"]
    title_html = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url and url!="#" else title
    authors = ", ".join(s.get("authors") or [])
    year = s.get("year","")
    journal = s.get("journal","")
    abstract = s.get("abstract","")
    sc = s.get("score",3)
    sid = s.get("id","")
    age_grp = s.get("age_group","none") or "none"

    meta_line = authors
    if year: meta_line += f" · {year}"
    if journal: meta_line += f" · <em>{journal}</em>"

    card = (
        f'<div class="src-card" data-cited="{"1" if cited else "0"}" data-age="{age_grp}" data-type="{s.get("type","")}" '
        f'style="background:#fff;border:1px solid #ddd;border-left:5px solid {score_color(sc)};'
        f'border-radius:4px;padding:.85rem 1.1rem;margin-bottom:.75rem">'
        f'<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:.35rem">'
        f'<div style="flex:1">'
        f'<span style="font-size:.7rem;color:#999;font-family:monospace">[{sid}]</span> '
        f'<strong style="font-size:.9rem;line-height:1.4">{title_html}</strong><br>'
        f'<span style="font-size:.79rem;color:#666">{meta_line}</span>'
        f'</div>'
        f'<div style="font-size:.95rem;white-space:nowrap">'
        f'<span style="color:#f5a623">{stars_html(sc)}</span> '
        f'<span style="font-size:.7rem;color:#888">{sc}/10</span>'
        f'</div></div>'
        f'<div style="margin:.35rem 0">{badges}</div>'
        + (f'<p style="font-size:.82rem;color:#444;margin:.35rem 0 0;line-height:1.55">{abstract}</p>' if abstract else "")
        + '</div>'
    )
    return card

# Echte Quellen (ohne Schema-Einträge)
real_sources = [s for s in sources if not s.get("_comment") and not s.get("_schema") and s.get("id","") != "PLACEHOLDER"]

# Ermittle, welche Quellen im Fließtext zitiert werden
_all_chapters_text = " ".join(chapters_md).lower()

def _is_cited_in_text(source):
    """Prüft ob Quelle im Artikeltext vorkommt (Erstautor + Jahr)."""
    year = str(source.get("year", ""))
    if not year or year not in _all_chapters_text:
        return False
    authors = source.get("authors") or []
    if not authors:
        return False
    first_author = authors[0]
    # Nachnamen extrahieren (vor Komma)
    last_name = first_author.split(",")[0].strip().lower()
    if len(last_name) < 3:
        return False
    # Suche Nachname in der Nähe der Jahreszahl
    idx = 0
    while True:
        pos = _all_chapters_text.find(year, idx)
        if pos == -1:
            break
        window = _all_chapters_text[max(0, pos-120):pos+20]
        if last_name in window:
            return True
        idx = pos + 1
    return False

_cited_ids = {s["id"] for s in real_sources if _is_cited_in_text(s)}

# ── Zitat-Annotations-System ────────────────────────────────────────────────
# Baut Index: (lastname_lower, year_int) → source_id
def _build_cit_index():
    idx = {}
    for s in real_sources:
        authors = s.get("authors") or []
        if not authors:
            continue
        last = authors[0].split(",")[0].strip().lower()
        year = s.get("year")
        if year and last and len(last) >= 2:
            key = (last, int(year))
            if key not in idx:
                idx[key] = s["id"]
    return idx

_cit_idx = _build_cit_index()
_cit_locations = {}  # {source_id: [anchor_id, ...]} — gefüllt von _annotate_chapters

def _annotate_chapters(ch_list):
    """Umhüllt APA-Inline-Zitate mit klickbaren <span>-Elementen."""
    global _cit_locations
    _cit_locations = {}
    counters = {}
    # Passt auf: (Author, YEAR) und (A, Y; B, Y) sowie multi-Author-Formen
    cit_pat = re.compile(
        r'\(([A-Z\xc0-\xd6\xd8-\xf6\xf8-\xff][^()<>]*?\d{4}[a-z]?'
        r'(?:;\s*[A-Z\xc0-\xd6\xd8-\xf6\xf8-\xff][^()<>]*?\d{4}[a-z]?)*)\)'
    )
    def replace_cite(m):
        inner = m.group(1)
        parts = re.split(r';\s*', inner)
        annotated = []
        changed = False
        for part in parts:
            yr_m = re.search(r'(\d{4})[a-z]?\s*$', part.strip())
            if not yr_m:
                annotated.append(part)
                continue
            yr = int(yr_m.group(1))
            ln_m = re.match(r'([A-Z\xc0-\xd6\xd8-\xf6\xf8-\xff][a-z\xc0-\xd6\xd8-\xf6\xf8-\xff\-]+)', part.strip())
            if not ln_m:
                annotated.append(part)
                continue
            ln = ln_m.group(1).lower()
            sid = _cit_idx.get((ln, yr))
            if not sid:
                annotated.append(part)
                continue
            counters[sid] = counters.get(sid, 0) + 1
            n = counters[sid]
            anchor_id = f"cite-{sid}-{n}"
            _cit_locations.setdefault(sid, []).append(anchor_id)
            annotated.append(
                f'<span class="cite-inline" data-sid="{sid}" id="{anchor_id}">{part}</span>'
            )
            changed = True
        if not changed:
            return m.group(0)
        return '(' + '; '.join(annotated) + ')'
    return [cit_pat.sub(replace_cite, ch) for ch in ch_list]

# ── Tooltip-System ──────────────────────────────────────────────────────────
# cited_ids.json für quellen.html
(base / "sources" / "cited_ids.json").write_text(
    json.dumps(sorted(_cited_ids)), encoding="utf-8")

def _compact_src(s):
    return {"id": s.get("id",""), "title": s.get("title",""),
            "authors": (s.get("authors") or [])[:3],
            "year": s.get("year") or 0, "journal": s.get("journal",""),
            "abstract": (s.get("abstract") or "")[:300],
            "score": s.get("score",3),
            "url": s.get("url","") or "", "doi": s.get("doi","") or "",
            "badges": s.get("badges") or []}

_src_json = json.dumps([_compact_src(s) for s in real_sources],
                        ensure_ascii=False).replace("</", "<\\/")

_TOOLTIP_CSS = (
    "\n/* Literatur-Tooltip */\n"
    ".lit-ref{cursor:help;position:relative;display:block}\n"
    ".lit-ref:hover{background:rgba(26,78,138,.07);border-radius:3px}\n"
    ".src-tooltip{display:none;position:absolute;left:0;top:100%;z-index:9999;"
    "background:#fff;border:1px solid #c8d6e8;border-left:4px solid #1a4e8a;"
    "border-radius:6px;padding:.85rem 1.05rem;box-shadow:0 6px 24px rgba(0,0,0,.15);"
    "max-width:460px;min-width:300px;font-size:.79rem;line-height:1.5;color:#333;"
    "pointer-events:none;white-space:normal}\n"
    ".lit-ref:hover .src-tooltip{display:block}\n"
    ".tip-above .src-tooltip{top:auto;bottom:100%}\n"
    ".tip-title{font-weight:600;font-size:.87rem;margin-bottom:.2rem}\n"
    ".tip-title a{color:#1a4e8a;text-decoration:none}\n"
    ".tip-title a:hover{text-decoration:underline}\n"
    ".tip-meta{font-size:.74rem;color:#666;margin-bottom:.2rem}\n"
    ".tip-abstract{font-size:.76rem;color:#555;font-style:italic;margin-top:.3rem;"
    "border-top:1px solid #eee;padding-top:.3rem}\n"
    "/* Inline-Zitat klickbar */\n"
    ".cite-inline{cursor:pointer;color:#1a4e8a;text-decoration:underline dotted;"
    "text-underline-offset:2px;border-radius:2px;transition:background .1s}\n"
    ".cite-inline:hover{background:rgba(26,78,138,.11)}\n"
    "/* Zitat-Modal */\n"
    "#cite-modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.46);"
    "z-index:99998;align-items:center;justify-content:center}\n"
    "#cite-modal-overlay.open{display:flex}\n"
    "#cite-modal-box{background:#fff;border-radius:8px;padding:1.4rem 1.6rem;"
    "max-width:530px;width:92%;max-height:80vh;overflow-y:auto;"
    "box-shadow:0 8px 40px rgba(0,0,0,.28);position:relative;border-left:4px solid #1a4e8a}\n"
    "#cite-modal-close{position:absolute;top:.55rem;right:.75rem;background:none;"
    "border:none;font-size:1.4rem;cursor:pointer;color:#999;line-height:1;padding:.1rem .3rem}\n"
    "#cite-modal-close:hover{color:#333}\n"
    ".cite-modal-title{font-weight:600;font-size:.93rem;line-height:1.4;margin-bottom:.25rem}\n"
    ".cite-modal-title a{color:#1a4e8a;text-decoration:none}\n"
    ".cite-modal-title a:hover{text-decoration:underline}\n"
    ".cite-modal-meta{font-size:.78rem;color:#666;margin-bottom:.35rem}\n"
    ".cite-modal-badges{display:flex;flex-wrap:wrap;gap:.25rem;margin:.35rem 0}\n"
    ".cite-modal-badge{font-size:.67rem;padding:.08rem .4rem;border-radius:10px;"
    "border:1px solid currentColor;white-space:nowrap}\n"
    ".cite-modal-abstract{font-size:.8rem;color:#444;font-style:italic;line-height:1.55;"
    "border-top:1px solid #eee;padding-top:.35rem;margin-top:.35rem}\n"
)

_TOOLTIP_JS = (
    '<script>\n(function(){\n'
    'var D=' + _src_json + ';\n'
    'function tipHtml(s){\n'
    '  var u=s.url&&s.url!="#"?s.url:(s.doi?"https://doi.org/"+s.doi:"");\n'
    '  var ti=u?"<a href=\'"+u+"\' target=\'_blank\' rel=\'noopener\'>"+s.title+"</a>":s.title;\n'
    '  var n=s.score>=9?5:s.score>=7?4:s.score>=5?3:2;\n'
    '  var st="<span style=\'color:#f5a623\'>"+"\\u2605".repeat(n)+"</span>"\n'
    '        +"<span style=\'color:#ddd\'>"+"\\u2605".repeat(5-n)+"</span>"\n'
    '        +" <small style=\'color:#999\'>"+s.score+"/10</small>";\n'
    '  var m=[s.authors.join(", "),s.year,s.journal].filter(Boolean).join(" \\xb7 ");\n'
    '  var ab=s.abstract?"<div class=\'tip-abstract\'>"+s.abstract.slice(0,260)\n'
    '         +(s.abstract.length>260?"\\u2026":"")+"</div>":"";\n'
    '  return "<div class=\'tip-title\'>"+ti+"</div>"\n'
    '        +"<div class=\'tip-meta\'>"+m+" "+st+"</div>"+ab;\n'
    '}\n'
    'document.querySelectorAll("h2").forEach(function(h2){\n'
    '  if(h2.textContent.indexOf("Literatur")===-1)return;\n'
    '  var el=h2.nextElementSibling;\n'
    '  while(el&&el.tagName!=="H1"&&el.tagName!=="H2"){\n'
    '    if(el.tagName==="P"){\n'
    '      var tx=el.textContent;\n'
    '      var ym=tx.match(/(\\d{4})[a-z]?\\)/);\n'
    '      var lm=tx.match(/^(\\S+),/);\n'
    '      if(ym&&lm){\n'
    '        var yr=parseInt(ym[1]);var ln=lm[1].toLowerCase();\n'
    '        var src=D.find(function(s){\n'
    '          return s.year===yr&&(s.authors||[]).length>0\n'
    '            &&s.authors[0].split(",")[0].trim().toLowerCase()===ln;\n'
    '        });\n'
    '        if(src){\n'
    '          el.classList.add("lit-ref");\n'
    '          var tp=document.createElement("div");\n'
    '          tp.className="src-tooltip";tp.innerHTML=tipHtml(src);\n'
    '          el.appendChild(tp);\n'
    '          el.addEventListener("mouseenter",function(){\n'
    '            var r=el.getBoundingClientRect();\n'
    '            if(r.bottom+220>window.innerHeight)el.classList.add("tip-above");\n'
    '            else el.classList.remove("tip-above");\n'
    '          });\n'
    '        }\n'
    '      }\n'
    '    }\n'
    '    el=el.nextElementSibling;\n'
    '  }\n'
    '});\n'
    '// ── Inline-Zitat-Modal ──\n'
    'var _ov=document.createElement("div");_ov.id="cite-modal-overlay";\n'
    'var _bx=document.createElement("div");_bx.id="cite-modal-box";_ov.appendChild(_bx);\n'
    'document.body.appendChild(_ov);\n'
    '_ov.addEventListener("click",function(e){if(e.target===_ov)_ov.classList.remove("open");});\n'
    'document.addEventListener("keydown",function(e){if(e.key==="Escape")_ov.classList.remove("open");});\n'
    'var _BL={peer:"\\ud83c\\udf93 Peer-reviewed",institution:"\\ud83c\\udfd7\\ufe0f Institution",'
    'book:"\\ud83d\\udcda Verlag",preprint:"\\ud83d\\udd2c Preprint",'
    'web:"\\ud83c\\udf10 Web",austria:"\\ud83c\\udde6\\ud83c\\uddf9 \\xd6sterreich",'
    'openaccess:"\\ud83d\\udd13 Open Access",paywall:"\\ud83d\\udd12 Paywall",'
    'math:"\\ud83e\\udde0 Mathematik"};\n'
    'document.querySelectorAll(".cite-inline").forEach(function(sp){\n'
    '  sp.addEventListener("click",function(e){\n'
    '    e.preventDefault();e.stopPropagation();\n'
    '    var src=D.find(function(s){return s.id===sp.dataset.sid;});\n'
    '    if(!src)return;\n'
    '    var u=src.url&&src.url!="#"?src.url:(src.doi?"https://doi.org/"+src.doi:"");\n'
    '    var ti=u?"<a href=\'"+u+"\' target=\'_blank\' rel=\'noopener\'>"+src.title+"</a>":src.title;\n'
    '    var n=src.score>=9?5:src.score>=7?4:src.score>=5?3:2;\n'
    '    var st="<span style=\'color:#f5a623\'>"+"\\u2605".repeat(n)+"</span>"\n'
    '          +"<span style=\'color:#ddd\'>"+"\\u2605".repeat(5-n)+"</span>"\n'
    '          +" <small style=\'color:#888\'>"+src.score+"/10</small>";\n'
    '    var m=[src.authors.join(", "),src.year,src.journal].filter(Boolean).join(" \\xb7 ");\n'
    '    var bdg=(src.badges||[]).map(function(b){\n'
    '      return "<span class=\'cite-modal-badge\'>"+(_BL[b]||b)+"</span>";\n'
    '    }).join("");\n'
    '    var ab=src.abstract?"<div class=\'cite-modal-abstract\'>"+src.abstract+"</div>":"";\n'
    '    _bx.innerHTML="<button id=\'cite-modal-close\' onclick=\'document.getElementById"'
    '      +"(\\"cite-modal-overlay\\").classList.remove(\\"open\\")\'>&times;</button>"\n'
    '      +"<div class=\'cite-modal-title\'>"+ti+"</div>"\n'
    '      +"<div class=\'cite-modal-meta\'>"+m+" "+st+"</div>"\n'
    '      +(bdg?"<div class=\'cite-modal-badges\'>"+bdg+"</div>":"")\n'
    '      +ab;\n'
    '    _ov.classList.add("open");\n'
    '  });\n'
    '});\n'
    '})();\n</script>'
)

# Kapitel in HTML umwandeln
chapters_html = []
for i, md in enumerate(chapters_md, 1):
    html_chapter = md2html(md)
    # Erste h1 nummerieren
    html_chapter = re.sub(r'^<h1>(.*?)</h1>', f'<h1>{i}. \\1</h1>', html_chapter, count=1)
    chapters_html.append(html_chapter)

# Inline-Zitate annotieren (erzeugt auch _cit_locations für quellen.html)
chapters_html = _annotate_chapters(chapters_html)

# TOC
toc_items = ""
for html_ch in chapters_html:
    m = re.search(r'<h1>(.*?)</h1>', html_ch)
    if m:
        title = re.sub('<[^>]+>','', m.group(1))
        slug = re.sub(r'[^a-z0-9]+','-', title.lower()).strip('-')
        toc_items += f'<li><a href="#{slug}">{title}</a></li>\n'

# Autoren
authors_html = "<br>".join(
    f'{a["name"]}' + (f' &nbsp;·&nbsp; <em>{a["affiliation"]}</em>' if a.get("affiliation") else "")
    for a in (meta.get("authors") or [])
)

# Abstract
abstract_section = ""
if meta.get("abstract"):
    abstract_section = f'<section class="abstract"><h2>Abstract</h2><p>{meta["abstract"]}</p></section>'

# ── Weiterführende Literatur + Anhang 7 ─────────────────────────────────────

def _badge_inline(badges, cited=False):
    """Kompakte Badge-Zeile für Anhang 7."""
    parts = []
    if cited:
        parts.append('<span style="font-size:.63rem;padding:.05rem .32rem;border-radius:8px;'
                     'background:#e8f5e9;color:#2e7d32;border:1px solid #81c784;'
                     'white-space:nowrap;font-weight:600">✓ zitiert</span>')
    for b in (badges or []):
        lbl = BADGE_LABELS.get(b, b)
        parts.append(f'<span style="font-size:.63rem;padding:.05rem .32rem;border-radius:8px;'
                     f'border:1px solid currentColor;white-space:nowrap">{lbl}</span>')
    return ' '.join(parts)

def _weiterfuehrende_section():
    top = sorted(
        [s for s in real_sources if s["id"] in _cited_ids and s.get("score", 0) >= 9],
        key=lambda s: (-(s.get("score") or 0), -(s.get("year") or 0))
    )
    items = []
    for s in top:
        authors = ", ".join(s.get("authors") or [])
        year = s.get("year", "")
        title = s.get("title", "")
        journal = s.get("journal") or ""
        doi = s.get("doi") or ""
        url = s.get("url") or ""
        link = f"https://doi.org/{doi}" if doi else (url if url not in ("", "#") else "")
        title_html = (f'<a href="{link}" target="_blank" rel="noopener" '
                      f'style="color:#1a4e8a">{title}</a>') if link else title
        sc = s.get("score", 3)
        n = 5 if sc >= 9 else 4 if sc >= 7 else 3
        stars = f'<span style="color:#f5a623;font-size:.72rem">{"★"*n}{"☆"*(5-n)}</span>'
        bdg = _badge_inline(s.get("badges"), cited=True)
        meta_str = f'{authors} ({year})'
        if journal:
            meta_str += f'. <em>{journal}</em>'
        items.append(
            f'<p style="margin-bottom:.7rem;font-size:.84rem;line-height:1.5;'
            f'border-left:3px solid {score_color(sc)};padding-left:.6rem">'
            f'{meta_str}. {title_html} {stars}<br>'
            f'<span style="font-size:.75rem">{bdg}</span></p>'
        )
    return (
        '<section id="weiterfuehrende-literatur" style="margin-top:3rem">\n'
        '<h2>Weiterführende Literatur</h2>\n'
        f'<p style="font-size:.84rem;color:#555;margin-bottom:1.2rem">'
        f'{len(top)} empfohlene Quellen (im Artikel zitiert, Score ≥ 9) — '
        f'vollständiges Verzeichnis: <a href="quellen.html">quellen.html</a> · '
        f'<a href="HIER-LINK-EINFÜGEN" target="_blank">Online-Version</a></p>\n'
        + "\n".join(items)
        + '\n</section>'
    )

def _anhang7_section():
    items = []
    for s in sorted(real_sources, key=lambda x: x.get("id", "")):
        sid = s.get("id", "")
        cited = sid in _cited_ids
        authors = ", ".join(s.get("authors") or [])
        year = s.get("year", "")
        title = s.get("title", "")
        journal = s.get("journal", "")
        doi = s.get("doi", "") or ""
        url = s.get("url", "") or ""
        link = f"https://doi.org/{doi}" if doi else (url if url not in ("", "#") else "")
        title_html = (f'<a href="{link}" target="_blank" rel="noopener" '
                      f'style="color:#1a4e8a">{title}</a>') if link else title
        bdg = _badge_inline(s.get("badges"), cited=cited)
        meta_str = f'{authors} ({year})'
        if journal:
            meta_str += f'. <em>{journal}</em>'
        items.append(
            f'<div style="margin-bottom:.38rem;font-size:.78rem;line-height:1.45">'
            f'<span style="font-family:monospace;color:#aaa;font-size:.65rem">[{sid}]</span> '
            f'{meta_str}. {title_html} — {bdg}</div>'
        )
    return (
        '<section id="anhang-7" style="margin-top:3rem;border-top:2px solid #ddd;padding-top:2rem">\n'
        '<h2>Anhang 7: Vollständiges Quellenverzeichnis</h2>\n'
        f'<p style="font-size:.84rem;color:#555;margin-bottom:1.2rem">'
        f'{len(real_sources)} Quellen mit Qualitätslabels (Stand März 2026)</p>\n'
        + "\n".join(items)
        + '\n</section>'
    )

weiterfuehrende_section = _weiterfuehrende_section()
anhang7_section = _anhang7_section()

# (Quellenarchiv nur noch auf quellen.html — nicht mehr in standalone.html eingebettet)
sources_section = weiterfuehrende_section + "\n" + anhang7_section


# Statistiken berechnen
import math
all_text = " ".join(chapters_md)
word_count = len(all_text.split())
char_count = len(all_text)
# Sinnvolle Formeln: A4 ~450 Wörter/Seite (12pt, Akademisch), A5 = halb so viel (~250)
pages_a4 = math.ceil(word_count / 450)
pages_a5 = math.ceil(word_count / 250)

# Stats-Panel HTML (fixed top right)
stats_panel = f"""<div id="stats-panel" style="
  position:fixed;top:1rem;right:1rem;z-index:1000;
  background:rgba(255,255,255,0.97);border:1px solid #ddd;border-left:4px solid #1a4e8a;
  border-radius:6px;padding:.6rem .9rem;font-family:sans-serif;
  font-size:.76rem;line-height:1.6;box-shadow:0 2px 12px rgba(0,0,0,.1);
  min-width:140px;display:none;
">
  <div style="font-weight:700;color:#1a4e8a;margin-bottom:.3rem;font-size:.78rem">📄 Dokument</div>
  <div>Kapitel: <strong>{len(chapters_html)}</strong></div>
  <div>Quellen: <strong>{len(real_sources)}</strong></div>
  <div>Wörter: <strong>{word_count:,}</strong></div>
  <div style="border-top:1px solid #eee;margin-top:.3rem;padding-top:.3rem">
    ca. A4-Seiten: <strong>~{pages_a4}</strong></div>
  <div>ca. A5-Seiten: <strong>~{pages_a5}</strong></div>
  <div style="font-size:.65rem;color:#aaa;margin-top:.25rem">
    (≈ 450 Wö/A4, 250 Wö/A5)</div>
</div>"""

# Kapitel-Blöcke
def make_chapter_block(html_ch, i):
    m = re.search(r'<h1>(.*?)</h1>', html_ch)
    slug = ""
    if m:
        title = re.sub('<[^>]+>','', m.group(1))
        slug = re.sub(r'[^a-z0-9]+','-', title.lower()).strip('-')
    border = "border-top:none;margin-top:0" if i==1 else "border-top:1px solid #ddd;margin-top:3rem;padding-top:.5rem"
    return f'<div class="chapter-block" id="{slug}" style="{border}">{html_ch}</div>'

chapters_blocks = "\n".join(make_chapter_block(h, i) for i, h in enumerate(chapters_html, 1))

tex_filename = f"{meta['title'][:40].replace(' ','_').replace('/','_')}.tex"

# Finales HTML zusammenbauen
final = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{meta['title']}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],throwOnError:false}})"></script>
<style>
{css}
body {{ max-width:820px; margin:0 auto; padding:2.5rem 2rem 6rem; }}
.chapter-block {{ }}
#nav-cluster button:hover, #nav-cluster a:hover {{ background:#0d2e55 !important; }}
@media print {{ #nav-cluster{{display:none}} #stats-panel{{display:none}} }}
</style>
</head>
<body>
<div id="nav-cluster" class="no-print" style="position:fixed;bottom:1.2rem;right:1.2rem;display:flex;flex-direction:column;gap:.3rem;align-items:stretch;z-index:500">
  <button onclick="window.scrollTo({{top:0,behavior:'smooth'}})" style="background:#1a4e8a;color:#fff;border:none;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;cursor:pointer;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);white-space:nowrap">↑ oben</button>
  <button onclick="(function(){{var p=document.getElementById('stats-panel');p.style.display=p.style.display==='none'?'block':'none'}})()" style="background:#4a6fa5;color:#fff;border:none;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;cursor:pointer;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);white-space:nowrap">ℹ Info</button>
  <a href="presentation/index.html" style="background:#1a4e8a;color:#fff;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;text-decoration:none;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);text-align:center;white-space:nowrap">📊 Folien</a>
  <a href="quellen.html" style="background:#1a4e8a;color:#fff;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;text-decoration:none;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);text-align:center;white-space:nowrap">📚 Quellen</a>
  <button onclick="ltxOpenOverlay()" style="background:#1a4e8a;color:#fff;border:none;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;cursor:pointer;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);white-space:nowrap">↓ Export</button>
  <button onclick="window.print()" style="background:#1a4e8a;color:#fff;border:none;border-radius:20px;padding:.22rem .7rem;font-size:.72rem;cursor:pointer;font-family:sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.25);white-space:nowrap">🖨 Drucken</button>
</div>
{stats_panel}

<header class="paper-header">
  <h1>{meta['title']}</h1>
  {f'<p class="subtitle">{meta["subtitle"]}</p>' if meta.get("subtitle") else ""}
  <p class="authors">{authors_html}</p>
  <p class="meta">{meta.get("event","")} &nbsp;·&nbsp; {meta.get("date","")}<br>
    <small style="font-style:italic">{meta.get("note","")}</small></p>
</header>

{abstract_section}

<nav class="toc">
  <h2>Inhaltsverzeichnis</h2>
  <ol style="list-style:none;padding-left:1.2rem">{toc_items}</ol>
</nav>

<main>
{chapters_blocks}
</main>

{sources_section}

<script>
document.querySelectorAll('a[href^="#"]').forEach(function(a){{
  a.addEventListener('click',function(e){{
    var t=document.querySelector(a.getAttribute('href'));
    if(t){{e.preventDefault();t.scrollIntoView({{behavior:'smooth'}});}}
  }});
}});
</script>
</body>
</html>"""

# Tooltip-CSS in <style> einbetten
final = final.replace('</style>', _TOOLTIP_CSS + '</style>', 1)

out_path = base / "standalone.html"
out_path.write_text(final, encoding="utf-8")
print(f"OK: standalone.html — {len(final):,} Zeichen, {len(chapters_html)} Kapitel, {len(real_sources)} Quellen")

# ── LaTeX Export ──────────────────────────────────────────────────────────────

def escape_tex(t):
    """Escape LaTeX special characters (preserving order)."""
    t = t.replace('\\', '\u2060BACKSLASH\u2060')  # placeholder
    t = t.replace('&', r'\&')
    t = t.replace('%', r'\%')
    t = t.replace('$', r'\$')
    t = t.replace('#', r'\#')
    t = t.replace('_', r'\_')
    t = t.replace('{', r'\{')
    t = t.replace('}', r'\}')
    t = t.replace('~', r'\textasciitilde{}')
    t = t.replace('^', r'\textasciicircum{}')
    t = t.replace('\u2060BACKSLASH\u2060', r'\textbackslash{}')
    return t

def inline_tex(t):
    """Convert inline Markdown → LaTeX, preserving URLs and bare https:// links."""
    links = []
    bare_urls = []

    def save_link(m):
        links.append((m.group(1), m.group(2)))
        return f'XLINK{len(links)-1}X'

    def save_bare_url(m):
        bare_urls.append(m.group(0))
        return f'XBAREURL{len(bare_urls)-1}X'

    # Save [text](url) first, then bare https:// URLs (not already inside XLINK)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', save_link, t)
    t = re.sub(r'https?://\S+', save_bare_url, t)
    t = escape_tex(t)
    # Bold before italic
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'\*(.+?)\*', r'\\textit{\1}', t)
    t = re.sub(r'`(.+?)`', r'\\texttt{\1}', t)
    for i, url in enumerate(bare_urls):
        # Strip trailing punctuation that is unlikely part of URL
        clean = url.rstrip('.,;)')
        suffix = url[len(clean):]
        t = t.replace(f'XBAREURL{i}X', f'\\url{{{clean}}}{escape_tex(suffix)}')
    for i, (text, url) in enumerate(links):
        t = t.replace(f'XLINK{i}X', f'\\href{{{url}}}{{{escape_tex(text)}}}')
    return t

def md2latex(md):
    lines = md.split('\n')
    out = []
    in_itemize = False
    in_enumerate = False
    skip_table = False
    buf = []

    def flush():
        if buf:
            text = ' '.join(buf).strip()
            if text:
                out.append('\n' + inline_tex(text) + '\n')
            buf.clear()

    HCMDS = [r'\section', r'\subsection', r'\subsubsection', r'\paragraph']

    for line in lines:
        # Standalone figure: ![Caption](figures/...)
        m_fig = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', line.strip())
        if m_fig:
            flush()
            if in_itemize: out.append(r'\end{itemize}'); in_itemize = False
            if in_enumerate: out.append(r'\end{enumerate}'); in_enumerate = False
            cap, src = m_fig.group(1), m_fig.group(2)
            label = re.sub(r'[^a-z0-9]', '', cap.lower())[:20] or "fig"
            out.append(
                f'\\begin{{figure}}[htbp]\n'
                f'  \\centering\n'
                f'  \\includegraphics[width=\\linewidth]{{{src}}}\n'
                f'  \\caption{{{inline_tex(cap)}}}\n'
                f'  \\label{{fig:{label}}}\n'
                f'\\end{{figure}}'
            )
            continue

        # Heading
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            flush()
            if in_itemize: out.append(r'\end{itemize}'); in_itemize = False
            if in_enumerate: out.append(r'\end{enumerate}'); in_enumerate = False
            level = min(len(m.group(1)), 4) - 1
            out.append(f'\n{HCMDS[level]}{{{inline_tex(m.group(2))}}}\n')
            continue

        # Blockquote
        if line.startswith('> '):
            flush()
            out.append(f'\\begin{{quote}}\n{inline_tex(line[2:])}\n\\end{{quote}}')
            continue

        # Table: skip (complex; footnote instead)
        if '|' in line and line.strip().startswith('|'):
            flush()
            if not skip_table:
                out.append('% [Tabelle — siehe HTML-Version]\n')
                skip_table = True
            continue
        else:
            skip_table = False

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', line)
        if m:
            flush()
            if not in_itemize: out.append(r'\begin{itemize}'); in_itemize = True
            out.append(f'  \\item {inline_tex(m.group(1))}')
            continue
        else:
            if in_itemize: out.append(r'\end{itemize}'); in_itemize = False

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            flush()
            if not in_enumerate: out.append(r'\begin{enumerate}'); in_enumerate = True
            out.append(f'  \\item {inline_tex(m.group(1))}')
            continue
        else:
            if in_enumerate: out.append(r'\end{enumerate}'); in_enumerate = False

        if line.strip().startswith('<!--'): continue
        if not line.strip(): flush(); continue
        buf.append(line)

    flush()
    if in_itemize: out.append(r'\end{itemize}')
    if in_enumerate: out.append(r'\end{enumerate}')
    return '\n'.join(out)

BADGE_LABELS_SHORT = {
    "peer": "Peer-reviewed", "institution": "Institution", "book": "Verlag",
    "preprint": "Preprint", "web": "Web", "austria": "Österreich",
    "openaccess": "Open Access", "paywall": "Paywall", "math": "Mathematik"
}

# Farben für LaTeX-Pills je Badge-Typ
BADGE_TEX_COLORS = {
    "peer":        "teal",
    "institution": "blue!70!black",
    "book":        "violet!80!black",
    "preprint":    "orange!80!black",
    "web":         "gray",
    "austria":     "red!70!black",
    "openaccess":  "teal!80!black",
    "paywall":     "red!80!black",
    "math":        "blue!60!black",
}

def _badge_tex(badges, cited=False, bw=False):
    """Erzeugt \badgepill-Befehle für LaTeX. bw=True → einheitliches Grau."""
    parts = []
    if cited:
        parts.append(r'\badgepill[black!55]{zitiert}' if bw else r'\badgepill[green!50!black]{zitiert}')
    for b in (badges or []):
        color = "black!50" if bw else BADGE_TEX_COLORS.get(b, "gray")
        label = BADGE_LABELS_SHORT.get(b, b)
        parts.append(f'\\badgepill[{color}]{{{escape_tex(label)}}}')
    return r'\,' + ' '.join(parts) if parts else ''

def _weiterfuehrende_tex(bw=False):
    top = sorted(
        [s for s in real_sources if s["id"] in _cited_ids and s.get("score", 0) >= 9],
        key=lambda s: (-(s.get("score") or 0), -(s.get("year") or 0))
    )
    lines = [f'\\textit{{{len(top)} empfohlene Quellen (zitiert, Score $\\geq$ 9)}}\n\\medskip\n']
    for s in top:
        authors = escape_tex(", ".join(s.get("authors") or []))
        year = s.get("year", "")
        title = escape_tex(s.get("title", ""))
        journal = escape_tex(s.get("journal") or "")
        doi = s.get("doi") or ""
        bdg = _badge_tex(s.get("badges"), cited=True, bw=bw)
        entry = f'{authors} ({year}). \\textit{{{title}}}'
        if journal:
            entry += f'. {journal}'
        if doi:
            entry += f'. \\href{{https://doi.org/{doi}}}{{\\texttt{{\\small doi:{escape_tex(doi)}}}}}'
        if bdg:
            entry += f'\\\\ {bdg}'
        lines.append(f'\\begin{{itemize}}\\setlength{{\\itemsep}}{{0pt}}\\item {entry}\\end{{itemize}}')
    return "\n".join(lines)

def _anhang7_tex(bw=False):
    lines = [f'\\textit{{{len(real_sources)} Quellen mit Qualitätslabels}}\n\\medskip\n']
    for s in sorted(real_sources, key=lambda x: x.get("id", "")):
        sid = s.get("id", "")
        cited = sid in _cited_ids
        authors = escape_tex(", ".join(s.get("authors") or []))
        year = s.get("year", "")
        title = escape_tex(s.get("title", ""))
        if bw:
            cited_mark = r' {\scriptsize\fontfamily{qhvc}\selectfont[zitiert]}' if cited else ""
        else:
            cited_mark = r' {\scriptsize\fontfamily{qhvc}\selectfont\color{green!50!black}[zitiert]}' if cited else ""
        lines.append(
            f'\\noindent{{\\scriptsize\\ttfamily {escape_tex(sid)}}} '
            f'{authors} ({year}). \\textit{{{title}}}.{cited_mark}\\smallskip'
        )
    return "\n\n".join(lines)

# Build LaTeX body
chapters_tex = [md2latex(md) for md in chapters_md]
latex_body = '\n\n\\clearpage\n\n'.join(chapters_tex)

authors_tex = ' \\and '.join(
    a['name'] + (f"\\thanks{{{escape_tex(a['affiliation'])}}}" if a.get('affiliation') else '')
    for a in (meta.get('authors') or [])
)
abstract_tex = escape_tex(meta.get('abstract', ''))
title_tex    = escape_tex(meta['title'])
subtitle_tex = escape_tex(meta.get('subtitle', ''))
date_tex     = escape_tex(meta.get('date', ''))
event_tex    = escape_tex(meta.get('event', ''))
note_tex     = escape_tex(meta.get('note', ''))

def _make_latex_doc(bw=False):
    variant = "Schwarz-Weiß" if bw else "Farbe"
    # Badge-Pill-Makro: Farbe vs. Grau
    if bw:
        badgepill_def = (
            r"\newcommand{\badgepill}[2][gray]{%" + "\n"
            r"  \tcbox[on line,arc=3pt,boxrule=0.35pt,boxsep=0pt," + "\n"
            r"    left=3pt,right=3pt,top=1.5pt,bottom=1.5pt," + "\n"
            r"    colframe=black!40,colback=black!6," + "\n"
            r"    fontupper=\scriptsize\fontfamily{qhvc}\selectfont\color{black!65}%" + "\n"
            r"  ]{#2}}" + "\n"
        )
    else:
        badgepill_def = (
            r"\newcommand{\badgepill}[2][gray]{%" + "\n"
            r"  \tcbox[on line,arc=3pt,boxrule=0.35pt,boxsep=0pt," + "\n"
            r"    left=3pt,right=3pt,top=1.5pt,bottom=1.5pt," + "\n"
            r"    colframe=#1!45,colback=#1!10," + "\n"
            r"    fontupper=\scriptsize\fontfamily{qhvc}\selectfont\color{#1!75!black}%" + "\n"
            r"  ]{#2}}" + "\n"
        )
    return (
        f"% Automatisch generiert — {date_tex} ({variant})\n"
        f"% Auf Overleaf hochladen oder: pdflatex standalone.tex\n"
        r"\documentclass[a5paper,11pt,ngerman]{scrartcl}" + "\n"
        r"\usepackage[utf8]{inputenc}" + "\n"
        r"\usepackage[T1]{fontenc}" + "\n"
        r"\usepackage[ngerman]{babel}" + "\n"
        r"\usepackage[left=1.8cm,right=1.8cm,top=2cm,bottom=2cm]{geometry}" + "\n"
        r"\usepackage[stretch=20,shrink=20,babel=true,protrusion=true]{microtype}" + "\n"
        r"\usepackage{csquotes}" + "\n"
        r"\usepackage{setspace}" + "\n"
        r"\usepackage{xcolor}" + "\n"
        r"\usepackage{tcolorbox}" + "\n"
        r"\tcbuselibrary{skins}" + "\n"
        r"\usepackage{graphicx}" + "\n"
        + badgepill_def
        + r"\usepackage[hidelinks,unicode,breaklinks=true]{hyperref}" + "\n"
        r"\usepackage{xurl}" + "\n"
        r"\usepackage{parskip}" + "\n"
        r"\usepackage{multicol}" + "\n"
        r"\usepackage{booktabs}" + "\n"
        r"\setkomafont{disposition}{\fontfamily{qhvc}\selectfont\bfseries\normalcolor}" + "\n"
        r"\setstretch{1.15}" + "\n"
        r"\tolerance=9999" + "\n"
        r"\emergencystretch=5em" + "\n"
        r"\hyphenpenalty=50" + "\n"
        r"\exhyphenpenalty=50" + "\n"
        r"\setlength{\footskip}{15mm}" + "\n\n"
        f"\\title{{{title_tex}\\\\[0.4em]\\large {subtitle_tex}}}\n"
        f"\\author{{{authors_tex}}}\n"
        f"\\date{{{date_tex} \\\\ \\small {event_tex}}}\n\n"
        r"\begin{document}" + "\n"
        r"\sloppy" + "\n"
        r"\maketitle" + "\n\n"
        r"\begin{abstract}" + "\n"
        f"{abstract_tex}\n"
        r"\end{abstract}" + "\n\n"
        r"\tableofcontents" + "\n"
        r"\listoffigures" + "\n"
        r"\clearpage" + "\n\n"
        f"{latex_body}\n\n"
        r"\clearpage" + "\n"
        r"\section*{Weiterführende Literatur}" + "\n"
        r"\addcontentsline{toc}{section}{Weiterführende Literatur}" + "\n"
        f"{_weiterfuehrende_tex(bw=bw)}\n\n"
        r"\clearpage" + "\n"
        r"\section*{Anhang 7: Vollständiges Quellenverzeichnis}" + "\n"
        r"\addcontentsline{toc}{section}{Anhang 7: Vollständiges Quellenverzeichnis}" + "\n"
        r"\small" + "\n"
        r"\begin{multicols}{2}" + "\n"
        f"{_anhang7_tex(bw=bw)}\n"
        r"\end{multicols}" + "\n"
        r"\end{document}" + "\n"
    )

latex_doc    = _make_latex_doc(bw=False)
latex_doc_sw = _make_latex_doc(bw=True)

tex_path = base / "standalone.tex"
tex_path.write_text(latex_doc, encoding="utf-8")
print(f"OK: standalone.tex    — {len(latex_doc):,} Zeichen (Farbe, Overleaf-ready)")

tex_sw_path = base / "standalone_sw.tex"
tex_sw_path.write_text(latex_doc_sw, encoding="utf-8")
print(f"OK: standalone_sw.tex — {len(latex_doc_sw):,} Zeichen (Schwarz-Weiß)")

# ── LaTeX-Overlay: Body + Meta für client-seitige Generierung extrahieren ──
_body_idx = latex_doc.index('\\begin{document}')
_tex_body_raw = latex_doc[_body_idx:]
_tex_meta = {
    'titleLine': f'\\title{{{title_tex}\\\\[0.4em]\\large {subtitle_tex}}}',
    'authorLine': f'\\author{{{authors_tex}}}',
    'dateLine':   f'\\date{{{date_tex} \\\\ \\small {event_tex}}}',
}

_LATEX_OVERLAY_HTML = """\
<div id="latex-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9000;align-items:center;justify-content:center;padding:1rem">
<div style="background:#fff;border-radius:8px;padding:1.5rem 1.75rem 1.1rem;max-width:440px;width:100%;box-shadow:0 8px 32px rgba(0,0,0,.28);font-family:sans-serif;font-size:.86rem">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.8rem">
    <strong style="font-size:.95rem;color:#1a1a1a">Export</strong>
    <button onclick="document.getElementById('latex-overlay').style.display='none'" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:#aaa;line-height:1">×</button>
  </div>
  <div style="display:flex;gap:.3rem;margin-bottom:1rem" id="export-tabs">
    <button class="exp-tab exp-tab-active" onclick="expSwitchTab('latex')" id="exp-tab-latex" style="flex:1;padding:.4rem .6rem;border:1px solid #ddd;border-radius:5px;background:#1a4e8a;color:#fff;cursor:pointer;font-size:.78rem;font-family:inherit;font-weight:600">LaTeX</button>
    <button class="exp-tab" onclick="expSwitchTab('web')" id="exp-tab-web" style="flex:1;padding:.4rem .6rem;border:1px solid #ddd;border-radius:5px;background:#fff;color:#333;cursor:pointer;font-size:.78rem;font-family:inherit;font-weight:500">Web-Paket (ZIP)</button>
  </div>
  <div id="exp-panel-latex">
  <table style="width:100%;border-collapse:collapse;line-height:2">
    <tr>
      <td style="color:#555;width:36%;vertical-align:middle">Farbmodus</td>
      <td><label style="margin-right:.9rem"><input type="radio" name="ltx-color" value="farbe" checked> Farbe</label><label><input type="radio" name="ltx-color" value="sw"> Schwarz-Weiß</label></td>
    </tr>
    <tr>
      <td style="color:#555;vertical-align:middle">Schriftgröße</td>
      <td><select id="ltx-size" style="font-size:.84rem;padding:.2rem .4rem;border:1px solid #ccc;border-radius:4px;width:100%">
        <option value="9pt">9 pt — Taschenbuch</option>
        <option value="10pt">10 pt — Fachbuch Standard</option>
        <option value="10.5pt">10.5 pt — Luftig</option>
        <option value="11pt" selected>11 pt — Aktuell</option>
      </select></td>
    </tr>
    <tr>
      <td style="color:#555;vertical-align:middle">Zeilenabstand</td>
      <td><select id="ltx-stretch" style="font-size:.84rem;padding:.2rem .4rem;border:1px solid #ccc;border-radius:4px;width:100%">
        <option value="1.0">1.0 — Kompakt (Buchdruck)</option>
        <option value="1.15" selected>1.15 — Normal</option>
        <option value="1.25">1.25 — Luftig</option>
      </select></td>
    </tr>
    <tr>
      <td style="color:#555;vertical-align:middle">Ränder</td>
      <td><select id="ltx-margins" style="font-size:.84rem;padding:.2rem .4rem;border:1px solid #ccc;border-radius:4px;width:100%">
        <option value="eng">Eng (±1.5 cm)</option>
        <option value="normal" selected>Normal (±1.8 cm)</option>
        <option value="bundsteg">Bundsteg — innen 2.5 / außen 1.5 cm</option>
      </select></td>
    </tr>
  </table>
  <div style="background:#f5f5f2;border-radius:5px;padding:.4rem .85rem;margin:.75rem 0 .6rem;text-align:center;font-size:.83rem;color:#555">
    Geschätzte Seitenanzahl (A5): <strong id="ltx-pages" style="color:#1a4e8a;font-size:1rem">—</strong>
    <div style="font-size:.68rem;color:#bbb;margin-top:.05rem">Schätzung auf Basis der Wortzahl · Tabellen &amp; Abbildungen nicht eingerechnet</div>
  </div>
  <div id="ltx-compile-hint" style="display:none;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:5px;padding:.35rem .75rem;margin-bottom:.55rem;font-size:.79rem;color:#2e7d32">
    ✓ .tex-Datei heruntergeladen — bitte auf <strong>latexonline.cc</strong> hochladen und kompilieren.
  </div>
  <div style="margin-top:.4rem">
    <button onclick="ltxDownload()" style="width:100%;background:#1a4e8a;color:#fff;border:none;border-radius:5px;padding:.55rem .4rem;cursor:pointer;font-size:.83rem;font-family:sans-serif">↓ Herunterladen (.tex)</button>
  </div>
  <div style="text-align:center;margin-top:.4rem;font-size:.69rem;color:#bbb">
    Für PDF: .tex-Datei in Overleaf, pdflatex oder <a href="https://latexonline.cc" target="_blank" rel="noopener" style="color:#bbb">latexonline.cc</a> öffnen
  </div>
  </div>
  <div id="exp-panel-web" style="display:none">
    <p style="color:#555;line-height:1.5;margin-bottom:.8rem">Erstellt ein ZIP-Paket mit allem, was für eine Website nötig ist. Den Inhalt einfach in ein Verzeichnis auf einem Webserver (SFTP/FTP) hochladen — fertig.</p>
    <div style="background:#f5f5f2;border-radius:5px;padding:.6rem .85rem;margin-bottom:.8rem;font-size:.8rem;color:#555;line-height:1.5">
      <strong>Enthält:</strong><br>
      📄 Fachartikel (standalone.html)<br>
      📚 Quellenverzeichnis (quellen.html)<br>
      📖 Handbuch (handbuch.html)<br>
      📊 Präsentation (presentation/)<br>
      🎨 Stylesheets (assets/css/)<br>
      🏠 Landingpage (index.html)
    </div>
    <p style="font-size:.75rem;color:#999;margin-bottom:.8rem;line-height:1.4">Hinweis: Folienbilder der Präsentation werden nicht eingebettet. Für Folien mit eingebetteten KI-Bildern verwende den ⬇-Button in der Präsentation selbst.</p>
    <button onclick="webPaketDownload()" id="web-paket-btn" style="width:100%;background:#1a4e8a;color:#fff;border:none;border-radius:5px;padding:.55rem .4rem;cursor:pointer;font-size:.83rem;font-family:sans-serif">↓ Web-Paket herunterladen (.zip)</button>
  </div>
</div>
</div>"""

_LATEX_OVERLAY_DATA = (
    '<script>\n'
    f'window._LTX_BODY={json.dumps(_tex_body_raw, ensure_ascii=False)};\n'
    f'window._LTX_META={json.dumps(_tex_meta, ensure_ascii=False)};\n'
    f'window._LTX_WORDCOUNT={word_count};\n'
    '</script>\n'
)

_LATEX_OVERLAY_JS = (
    '<script>(function(){\n'
    'var WPP={"9pt":{"1.0":420,"1.15":365,"1.25":335},'
    '"10pt":{"1.0":360,"1.15":315,"1.25":288},'
    '"10.5pt":{"1.0":338,"1.15":295,"1.25":270},'
    '"11pt":{"1.0":315,"1.15":275,"1.25":252}};\n'
    'var MF={eng:1.10,normal:1.0,bundsteg:0.93};\n'
    'window.ltxOpenOverlay=function(){'
    'document.getElementById("latex-overlay").style.display="flex";'
    'ltxUpdateEstimate();};\n'
    'window.ltxUpdateEstimate=function(){'
    'var sz=document.getElementById("ltx-size").value;'
    'var st=document.getElementById("ltx-stretch").value;'
    'var mg=document.getElementById("ltx-margins").value;'
    'var wpp=(WPP[sz]||{})[st]||300;'
    'var factor=MF[mg]||1.0;'
    'var pages=Math.round(window._LTX_WORDCOUNT/(wpp*factor));'
    'document.getElementById("ltx-pages").textContent="~"+pages;};\n'
    'function _ltxBuild(){'
    'var sz=document.getElementById("ltx-size").value;'
    'var st=document.getElementById("ltx-stretch").value;'
    'var mg=document.getElementById("ltx-margins").value;'
    'var bw=document.querySelector(\'input[name="ltx-color"]:checked\').value==="sw";'
    'var ts=mg==="bundsteg";'
    'var co="a5paper,fontsize="+sz+",ngerman"+(ts?",twoside":"");'
    'var gm=ts?"\\\\usepackage[inner=2.5cm,outer=1.5cm,top=2cm,bottom=2cm,twoside]{geometry}"'
    ':mg==="eng"?"\\\\usepackage[left=1.5cm,right=1.5cm,top=2cm,bottom=2cm]{geometry}"'
    ':"\\\\usepackage[left=1.8cm,right=1.8cm,top=2cm,bottom=2cm]{geometry}";'
    'var bp=bw'
    '?"\\\\newcommand{\\\\badgepill}[2][gray]{%\\n  \\\\tcbox[on line,arc=3pt,boxrule=0.35pt,boxsep=0pt,\\n    left=3pt,right=3pt,top=1.5pt,bottom=1.5pt,\\n    colframe=black!40,colback=black!6,\\n    fontupper=\\\\scriptsize\\\\fontfamily{qhvc}\\\\selectfont\\\\color{black!65}%\\n  ]{#2}}"'
    ':"\\\\newcommand{\\\\badgepill}[2][gray]{%\\n  \\\\tcbox[on line,arc=3pt,boxrule=0.35pt,boxsep=0pt,\\n    left=3pt,right=3pt,top=1.5pt,bottom=1.5pt,\\n    colframe=#1!45,colback=#1!10,\\n    fontupper=\\\\scriptsize\\\\fontfamily{qhvc}\\\\selectfont\\\\color{#1!75!black}%\\n  ]{#2}}";'
    'var m=window._LTX_META;'
    'var d=new Date().toLocaleDateString("de-AT");'
    'var cm=bw?"Schwarz-Weiß":"Farbe";'
    'var pre=['
    '"% LaTeX Export — "+d+" ("+cm+", "+sz+", Abstand "+st+", Ränder "+mg+")",'
    '"% pdflatex standalone.tex  |  latexonline.cc",'
    '"\\\\documentclass["+co+"]{scrartcl}",'
    '"\\\\usepackage[utf8]{inputenc}",'
    '"\\\\usepackage[T1]{fontenc}",'
    '"\\\\usepackage[ngerman]{babel}",'
    'gm,'
    '"\\\\usepackage[stretch=20,shrink=20,babel=true,protrusion=true]{microtype}",'
    '"\\\\usepackage{csquotes}",'
    '"\\\\usepackage{setspace}",'
    '"\\\\usepackage{xcolor}",'
    '"\\\\usepackage{tcolorbox}",'
    '"\\\\tcbuselibrary{skins}",'
    '"\\\\usepackage{graphicx}",'
    'bp,'
    '"\\\\usepackage[hidelinks,unicode,breaklinks=true]{hyperref}",'
    '"\\\\usepackage{xurl}",'
    '"\\\\usepackage{parskip}",'
    '"\\\\usepackage{multicol}",'
    '"\\\\usepackage{booktabs}",'
    '"\\\\setkomafont{disposition}{\\\\fontfamily{qhvc}\\\\selectfont\\\\bfseries\\\\normalcolor}",'
    '"\\\\setstretch{"+st+"}",'
    '"\\\\tolerance=9999",'
    '"\\\\emergencystretch=5em",'
    '"\\\\hyphenpenalty=50",'
    '"\\\\exhyphenpenalty=50",'
    '"\\\\setlength{\\\\footskip}{15mm}",'
    '"",'
    'm.titleLine,m.authorLine,m.dateLine,""'
    '].join("\\n");'
    'return pre+window._LTX_BODY;}\n'
    'window.ltxDownload=function(){'
    'var sz=document.getElementById("ltx-size").value;'
    'var bw=document.querySelector(\'input[name="ltx-color"]:checked\').value==="sw";'
    'var tex=_ltxBuild();'
    'var fn="KI_Geometrie_"+sz+"_"+(bw?"sw":"farbe")+".tex";'
    'var bl=new Blob([tex],{type:"text/plain;charset=utf-8"});'
    'var a=document.createElement("a");'
    'a.href=URL.createObjectURL(bl);a.download=fn;'
    'document.body.appendChild(a);a.click();'
    'document.body.removeChild(a);URL.revokeObjectURL(a.href);'
    'document.getElementById("ltx-compile-hint").style.display="none";};\n'
    'document.addEventListener("DOMContentLoaded",function(){'
    'var ov=document.getElementById("latex-overlay");'
    'ov.addEventListener("click",function(e){if(e.target===ov)ov.style.display="none";});'
    '["ltx-size","ltx-stretch","ltx-margins"].forEach(function(id){'
    'var el=document.getElementById(id);if(el)el.addEventListener("change",ltxUpdateEstimate);});'
    'document.querySelectorAll(\'input[name="ltx-color"]\').forEach(function(el){'
    'el.addEventListener("change",ltxUpdateEstimate);});'
    'ltxUpdateEstimate();});'
    '\n'
    '/* ── Tab-Switch ── */\n'
    'window.expSwitchTab=function(tab){'
    'document.getElementById("exp-panel-latex").style.display=tab==="latex"?"block":"none";'
    'document.getElementById("exp-panel-web").style.display=tab==="web"?"block":"none";'
    'document.getElementById("exp-tab-latex").style.background=tab==="latex"?"#1a4e8a":"#fff";'
    'document.getElementById("exp-tab-latex").style.color=tab==="latex"?"#fff":"#333";'
    'document.getElementById("exp-tab-web").style.background=tab==="web"?"#1a4e8a":"#fff";'
    'document.getElementById("exp-tab-web").style.color=tab==="web"?"#fff":"#333";'
    '};\n'
    '/* ── Web-Paket (ZIP) ── */\n'
    'window.webPaketDownload=async function(){'
    'var btn=document.getElementById("web-paket-btn");'
    'btn.textContent="Wird erstellt …";btn.disabled=true;'
    'try{'
    'if(!window.JSZip){'
    'await new Promise(function(res,rej){'
    'var s=document.createElement("script");'
    's.src="https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js";'
    's.onload=res;s.onerror=rej;document.head.appendChild(s);});}'
    'var zip=new JSZip();'
    '/* Artikel (aktuelle Seite, bereinigt) */\n'
    'var clone=document.documentElement.cloneNode(true);'
    '["#nav-cluster","#stats-panel","#latex-overlay"].forEach(function(s){'
    'var el=clone.querySelector(s);if(el)el.remove();});'
    '/* Eingebettete Paket-Daten entfernen */\n'
    'clone.querySelectorAll("script").forEach(function(s){'
    'if(s.textContent.indexOf("_WEB_PAKET")>-1||s.textContent.indexOf("_LTX_")>-1)s.remove();});'
    'zip.file("standalone.html","<!DOCTYPE html>\\n"+clone.outerHTML);'
    '/* Text-Dateien aus eingebetteten Daten */\n'
    'var wpText=window._WEB_PAKET_TEXT||{};'
    'Object.keys(wpText).forEach(function(k){zip.file(k,wpText[k]);});'
    '/* Font-Dateien aus eingebetteten Daten (Base64 → binary) */\n'
    'var wpFonts=window._WEB_PAKET_FONTS||{};'
    'Object.keys(wpFonts).forEach(function(k){'
    'var f=wpFonts[k];'
    'if(f.t==="b64"){'
    'var raw=atob(f.d);var arr=new Uint8Array(raw.length);'
    'for(var i=0;i<raw.length;i++)arr[i]=raw.charCodeAt(i);'
    'zip.file(k,arr);'
    '}else{zip.file(k,f.d);}});'
    '/* Landingpage */\n'
    'var ti=document.title||"Forschungsartikel";'
    'zip.file("index.html","<!DOCTYPE html>\\n<html lang=\\"de\\">\\n<head>\\n"+'
    '"<meta charset=\\"UTF-8\\"/>\\n<meta name=\\"viewport\\" content=\\"width=device-width,initial-scale=1\\"/>\\n"+'
    '"<title>"+ti+"</title>\\n"+'
    '"<style>body{font-family:system-ui,sans-serif;max-width:680px;margin:4rem auto;padding:0 2rem;color:#222}"+'
    '"h1{font-size:1.4rem;margin-bottom:.5rem}p{color:#666;margin-bottom:2rem}"+'
    '"nav{display:flex;flex-direction:column;gap:.8rem}"+'
    '"a{display:inline-block;padding:.7rem 1.2rem;background:#163374;color:#fff;text-decoration:none;border-radius:6px;width:fit-content}"+'
    '"a:hover{background:#0f2456}</style>\\n</head>\\n<body>\\n"+'
    '"<h1>"+ti+"</h1>\\n<p>Wähle einen Bereich:</p>\\n<nav>\\n"+'
    '"<a href=\\"standalone.html\\">📄 Artikel lesen</a>\\n"+'
    '"<a href=\\"quellen.html\\">📚 Quelldatenbank</a>\\n"+'
    '"<a href=\\"presentation/index.html\\">📊 Präsentation</a>\\n"+'
    '"<a href=\\"handbuch.html\\">📖 Handbuch</a>\\n"+'
    '"</nav>\\n</body>\\n</html>");'
    '/* Download */\n'
    'var blob=await zip.generateAsync({type:"blob",compression:"DEFLATE",compressionOptions:{level:6}});'
    'var a=document.createElement("a");a.href=URL.createObjectURL(blob);'
    'a.download="web-paket.zip";a.click();URL.revokeObjectURL(a.href);'
    'btn.textContent="↓ Web-Paket herunterladen (.zip)";btn.disabled=false;'
    '}catch(e){alert("Fehler: "+e.message);btn.textContent="↓ Web-Paket herunterladen (.zip)";btn.disabled=false;}'
    '};\n'
    '})();</script>\n'
)

# ── Web-Paket: Dateien einbetten ──
import base64 as _b64
_wp_files = {}
for _wp_name, _wp_path in [
    ("quellen.html", base / "quellen.html"),
    ("handbuch.html", base / "handbuch.html"),
    ("assets/css/paper.css", base / "assets" / "css" / "paper.css"),
    ("presentation/index.html", base / "presentation" / "index.html"),
    ("presentation/stile.html", base / "presentation" / "stile.html"),
]:
    if _wp_path.exists():
        _wp_files[_wp_name] = _wp_path.read_text(encoding="utf-8")

# Fonts komplett einbetten (Base64 für woff2, Text für CSS)
_wp_fonts = {}
_fonts_dir = base / "presentation" / "fonts"
if _fonts_dir.exists():
    for _ff in _fonts_dir.iterdir():
        if _ff.suffix in ('.woff2', '.css'):
            if _ff.suffix == '.css':
                _wp_fonts[f"presentation/fonts/{_ff.name}"] = {"t": "text", "d": _ff.read_text(encoding="utf-8")}
            else:
                _wp_fonts[f"presentation/fonts/{_ff.name}"] = {"t": "b64", "d": _b64.b64encode(_ff.read_bytes()).decode()}

_WEB_PAKET_DATA = (
    '<script>\n'
    f'window._WEB_PAKET_TEXT={json.dumps(_wp_files, ensure_ascii=False).replace("</", "<\\/") if _wp_files else "{}"};\n'
    f'window._WEB_PAKET_FONTS={json.dumps(_wp_fonts, ensure_ascii=False).replace("</", "<\\/") if _wp_fonts else "{}"};\n'
    '</script>\n'
)

# Alles vor </body> einbauen
final_with_js = final.replace('</body>',
    _LATEX_OVERLAY_HTML + '\n' +
    _TOOLTIP_JS + '\n' +
    _LATEX_OVERLAY_DATA +
    _WEB_PAKET_DATA +
    _LATEX_OVERLAY_JS +
    '</body>', 1)
out_path.write_text(final_with_js, encoding="utf-8")
print(f"OK: Tooltip-JS + LaTeX-Overlay eingebaut")

# ── quellen.html: embedded data injizieren (funktioniert auch ohne Webserver via file://) ──
quellen_path = base / "quellen.html"
if quellen_path.exists():
    quellen_html = quellen_path.read_text(encoding="utf-8")
    src_json_embed  = json.dumps(sources, ensure_ascii=False).replace("</", "<\\/")
    cited_json_embed = json.dumps(sorted(_cited_ids), ensure_ascii=False)
    cit_loc_embed = json.dumps(_cit_locations, ensure_ascii=False).replace("</", "<\\/")
    inject_block = (
        f"<!-- DATA_INJECT_START -->"
        f"<script>window.SOURCES_DATA={src_json_embed};"
        f"window.CITED_IDS={cited_json_embed};"
        f"window.CIT_LOCATIONS={cit_loc_embed};</script>"
        f"<!-- DATA_INJECT_END -->"
    )
    quellen_new = re.sub(
        r'<!-- DATA_INJECT_START -->.*?<!-- DATA_INJECT_END -->',
        inject_block,
        quellen_html,
        flags=re.DOTALL
    )
    # Titel, Veranstaltung und Datum aus meta.json ersetzen
    import datetime
    datum_raw = meta.get("date", "")
    try:
        datum_fmt = datetime.datetime.strptime(datum_raw, "%Y-%m-%d").strftime("%-d. %B %Y")
    except Exception:
        datum_fmt = datum_raw
    quellen_new = quellen_new.replace("{{TITEL}}", meta.get("title", ""))
    quellen_new = quellen_new.replace("{{VERANSTALTUNG}}", meta.get("event", ""))
    quellen_new = quellen_new.replace("{{DATUM}}", datum_fmt)
    quellen_new = quellen_new.replace("{{RELEVANZ_TOPIC}}", meta.get("relevance_topic", "das Kernthema"))
    quellen_new = quellen_new.replace("{{RELEVANZ_3}}", meta.get("relevance_3", "Direkt zum Kernthema"))
    quellen_new = quellen_new.replace("{{RELEVANZ_2}}", meta.get("relevance_2", "Verwandtes Thema, nützlich"))
    quellen_new = quellen_new.replace("{{RELEVANZ_1}}", meta.get("relevance_1", "Allgemeiner Hintergrund, Kontext"))
    quellen_path.write_text(quellen_new, encoding="utf-8")
    print(f"OK: quellen.html     — {len(sources)} Quellen eingebettet (file://-kompatibel)")