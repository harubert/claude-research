import json, pathlib, subprocess, sys

base = pathlib.Path(__file__).parent

meta    = json.loads((base / "content/meta.json").read_text(encoding="utf-8"))
# site.css (Designsystem) + paper.css (Artikel) werden inline eingebettet.
# Font-Pfade sind relativ zu assets/css/ → für standalone.html (Projektstamm) umschreiben.
theme_js = (base / "assets/theme.js").read_text(encoding="utf-8")
css     = ((base / "assets/css/site.css").read_text(encoding="utf-8") + "\n" +
           (base / "assets/css/paper.css").read_text(encoding="utf-8")
          ).replace("../../presentation/fonts/", "presentation/fonts/")
sources = json.loads((base / "sources/sources.json").read_text(encoding="utf-8"))

# ── Icons: einzige Quelle ist assets/icons.js (JSON zwischen ICONS_START / ICONS_END) ──
_icons_js = (base / "assets/icons.js").read_text(encoding="utf-8")
ICONS = json.loads(_icons_js.split("/* ICONS_START */", 1)[1].split("/* ICONS_END */", 1)[0])

def ic(name, cls=""):
    """Inline-SVG-Icon als HTML-String."""
    body = ICONS.get(name, "")
    if not body:
        return ""
    return (f'<svg class="ic{(" " + cls) if cls else ""}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>')

import re

def _strip_comments(md):
    """Entfernt (auch mehrzeilige) HTML-Kommentare aus Markdown."""
    return re.sub(r'<!--.*?-->', '', md, flags=re.S)

chapters_md = []
for fname in meta["chapters"]:
    p = base / "content" / fname
    if p.exists():
        chapters_md.append(_strip_comments(p.read_text(encoding="utf-8")))

# Forschungsdesiderata (optional, nach der Literaturarbeit befüllt)
_fd_path = base / "content" / "forschungsdesiderata.md"
fd_md = _strip_comments(_fd_path.read_text(encoding="utf-8")) if _fd_path.exists() else ""

# Minimaler Markdown→HTML-Konverter (kein externes Package nötig)

# Kursiv: *text* — aber nicht das Gender-Sternchen (Schüler*innen):
# öffnendes * nicht direkt nach einem Buchstaben, schließendes nicht direkt davor.
_EM_RE = re.compile(r'(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])')

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
        t = _EM_RE.sub(r'<em>\1</em>', t)
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
    "peer":"Peer-reviewed","institution":"Institution","book":"Buch / Verlag",
    "preprint":"Preprint","web":"Web","austria":"Österreich",
    "openaccess":"Open Access","paywall":"Paywall","math":"Mathematik",
    "empirical":"Empirisch","review":"Review","theory":"Theorie",
    "practice":"Praxis","technology":"Technologie"
}

# Eigene, themenspezifische Badges aus meta.json:
#   "custom_badges": {"sek1": {"label": "SEK I", "desc": "Sekundarstufe I", "icon": "school", "color": "#0e7490"}}
CUSTOM_BADGES = meta.get("custom_badges") or {}
for _k, _v in CUSTOM_BADGES.items():
    BADGE_LABELS[_k] = (_v or {}).get("label", _k)

def badge_html(b):
    """Badge-Pill mit Icon (Klassen aus site.css). Unbekannte Badges bekommen das Icon 'tag'."""
    c = CUSTOM_BADGES.get(b) or {}
    icon = ic(c.get("icon") or b) or ic("tag")
    style = f' style="color:{c["color"]}"' if c.get("color") else ""
    return f'<span class="badge badge-{b}"{style}>{icon}{BADGE_LABELS.get(b, b)}</span>'

def score_color(s):
    return "var(--s5)" if s>=9 else "var(--s4)" if s>=7 else "var(--s3)" if s>=5 else "var(--s2)"

def stars_html(sc):
    n = 5 if sc>=9 else 4 if sc>=7 else 3 if sc>=5 else 2
    return ('<span class="stars">' + ic("star", "on")*n + ic("star", "off")*(5-n) + '</span>')

AGE_GROUP_LABELS = {
    "vorschule":  "Vorschule (3–6)",
    "primarstufe": "Primarstufe (6–10)",
    "sek1":       "SEK I (10–15)",
    "sek2":       "SEK II (15–19)",
    "hochschule": "Hochschule",
    "lehrende":   "Lehrende/Studierende",
    "mixed":      "Gemischt",
    "none":       "—",
}

def source_card(s, cited=False):
    badges = "".join(badge_html(b) for b in (s.get("badges") or []))
    # "Verwendet im Artikel"-Badge
    if cited:
        badges += f'<span class="badge badge-cited">{ic("check")}Im Artikel</span>'
    # Altersgruppen-Badge
    age_group = s.get("age_group", "")
    if age_group and age_group in AGE_GROUP_LABELS and age_group != "none":
        badges += f'<span class="badge badge-age">{AGE_GROUP_LABELS[age_group]}</span>'

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
        f'style="background:var(--surface);border:1px solid var(--line);border-left:3px solid {score_color(sc)};'
        f'border-radius:var(--radius-sm);padding:.85rem 1.1rem;margin-bottom:.75rem;font-family:var(--font-ui)">'
        f'<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:.35rem">'
        f'<div style="flex:1">'
        f'<span style="font:.68rem var(--font-mono);color:var(--faint)">{sid}</span> '
        f'<strong style="font-size:.9rem;line-height:1.4">{title_html}</strong><br>'
        f'<span style="font-size:.79rem;color:var(--muted)">{meta_line}</span>'
        f'</div>'
        f'<div style="white-space:nowrap">{stars_html(sc)}<span class="score-num">{sc}/10</span></div></div>'
        f'<div style="margin:.35rem 0;display:flex;flex-wrap:wrap;gap:.3rem">{badges}</div>'
        + (f'<p style="font-size:.82rem;color:var(--muted);margin:.35rem 0 0;line-height:1.55">{abstract}</p>' if abstract else "")
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
    ".lit-ref{cursor:help;position:relative;display:block;border-radius:4px;transition:background .12s}\n"
    ".lit-ref:hover{background:rgba(31,63,191,.05)}\n"
    ".src-tooltip{display:none;position:absolute;left:0;top:100%;z-index:9999;"
    "background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);"
    "padding:1rem 1.15rem;box-shadow:var(--shadow-lg);font-family:var(--font-ui);"
    "max-width:460px;min-width:300px;font-size:.79rem;line-height:1.5;color:var(--text);"
    "pointer-events:none;white-space:normal}\n"
    ".lit-ref:hover .src-tooltip{display:block}\n"
    ".tip-above .src-tooltip{top:auto;bottom:100%}\n"
    ".tip-title{font-weight:600;font-size:.87rem;line-height:1.4;margin-bottom:.3rem}\n"
    ".tip-title a{color:var(--heading);text-decoration:none}\n"
    ".tip-meta{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;font-size:.74rem;color:var(--muted)}\n"
    ".tip-abstract{font-size:.76rem;color:var(--muted);margin-top:.55rem;"
    "border-top:1px solid var(--line);padding-top:.55rem}\n"
    "/* Inline-Zitat klickbar */\n"
    ".cite-inline{cursor:pointer;color:var(--primary);text-decoration:underline;"
    "text-decoration-style:dotted;text-decoration-color:color-mix(in srgb,var(--primary) 55%,transparent);"
    "text-underline-offset:3px;border-radius:3px;transition:background .12s}\n"
    ".cite-inline:hover{background:var(--primary-soft);text-decoration-style:solid}\n"
    "/* Zitat-Modal */\n"
    "#cite-modal-overlay{display:none;position:fixed;inset:0;background:rgba(13,22,38,.55);"
    "-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);"
    "z-index:99998;align-items:center;justify-content:center;padding:1rem}\n"
    "#cite-modal-overlay.open{display:flex}\n"
    "#cite-modal-box{background:var(--surface);border-radius:14px;padding:1.6rem 1.75rem 1.5rem;"
    "max-width:560px;width:100%;max-height:80vh;overflow-y:auto;font-family:var(--font-ui);"
    "box-shadow:var(--shadow-lg);position:relative;border-top:3px solid var(--accent)}\n"
    "#cite-modal-close{position:absolute;top:.8rem;right:.8rem;background:none;width:32px;height:32px;"
    "border:none;cursor:pointer;color:var(--faint);border-radius:8px;display:grid;place-items:center}\n"
    "#cite-modal-close:hover{color:var(--text);background:var(--paper)}\n"
    ".cite-modal-kicker{font:600 .66rem/1 var(--font-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:.7rem}\n"
    ".cite-modal-title{font-family:var(--font-display);font-weight:600;font-size:1.15rem;line-height:1.3;margin:0 2rem .45rem 0;color:var(--heading)}\n"
    ".cite-modal-title a{color:inherit;text-decoration:none}\n"
    ".cite-modal-title a:hover{color:var(--primary)}\n"
    ".cite-modal-meta{display:flex;flex-wrap:wrap;align-items:center;gap:.45rem;font-size:.8rem;color:var(--muted);margin-bottom:.6rem}\n"
    ".cite-modal-badges{display:flex;flex-wrap:wrap;gap:.3rem;margin:.5rem 0}\n"
    ".cite-modal-abstract{font-family:var(--font-read);font-size:.9rem;color:var(--text);line-height:1.6;"
    "border-top:1px solid var(--line);padding-top:.8rem;margin-top:.8rem}\n"
    ".cite-modal-link{display:inline-flex;align-items:center;gap:.35rem;margin-top:1rem;font-size:.8rem;font-weight:600;"
    "color:var(--primary);text-decoration:none}\n"
    ".cite-modal-link:hover{text-decoration:underline}\n"
)

# Icon-Bausteine für das client-seitige Tooltip-/Modal-Rendering
_JS_ICONS = json.dumps({
    "on": ic("star", "on"), "off": ic("star", "off"),
    "x": ic("x"), "ext": ic("external"),
    "badges": {b: badge_html(b) for b in set(BADGE_LABELS) | {x for s in real_sources for x in (s.get("badges") or [])}},
}, ensure_ascii=False).replace("</", "<\\/")

_TOOLTIP_JS = (
    '<script>\n(function(){\n'
    'var D=' + _src_json + ';\n'
    'var IC=' + _JS_ICONS + ';\n'
    'function starsHtml(sc){var n=sc>=9?5:sc>=7?4:sc>=5?3:2;\n'
    '  return "<span class=\'stars\'>"+IC.on.repeat(n)+IC.off.repeat(5-n)+"</span><span class=\'score-num\'>"+sc+"/10</span>";}\n'
    'function tipHtml(s){\n'
    '  var u=s.url&&s.url!="#"?s.url:(s.doi?"https://doi.org/"+s.doi:"");\n'
    '  var ti=u?"<a href=\'"+u+"\' target=\'_blank\' rel=\'noopener\'>"+s.title+"</a>":s.title;\n'
    '  var st=starsHtml(s.score);\n'
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
    'document.querySelectorAll(".cite-inline").forEach(function(sp){\n'
    '  sp.addEventListener("click",function(e){\n'
    '    e.preventDefault();e.stopPropagation();\n'
    '    var src=D.find(function(s){return s.id===sp.dataset.sid;});\n'
    '    if(!src)return;\n'
    '    var u=src.url&&src.url!="#"?src.url:(src.doi?"https://doi.org/"+src.doi:"");\n'
    '    var ti=u?"<a href=\'"+u+"\' target=\'_blank\' rel=\'noopener\'>"+src.title+"</a>":src.title;\n'
    '    var st=starsHtml(src.score);\n'
    '    var m=[src.authors.join(", "),src.year,src.journal].filter(Boolean).join(" \\xb7 ");\n'
    '    var bdg=(src.badges||[]).map(function(b){\n'
    '      return IC.badges[b]||"<span class=\'badge\'>"+b+"</span>";\n'
    '    }).join("");\n'
    '    var ab=src.abstract?"<div class=\'cite-modal-abstract\'>"+src.abstract+"</div>":"";\n'
    '    var lk=u?"<a class=\'cite-modal-link\' href=\'"+u+"\' target=\'_blank\' rel=\'noopener\'>Zur Quelle "+IC.ext+"</a>":"";\n'
    '    _bx.innerHTML="<button id=\'cite-modal-close\' aria-label=\'Schließen\' onclick=\'document.getElementById"'
    '      +"(\\"cite-modal-overlay\\").classList.remove(\\"open\\")\'>"+IC.x+"</button>"\n'
    '      +"<div class=\'cite-modal-kicker\'>Quelle "+src.id+"</div>"\n'
    '      +"<div class=\'cite-modal-title\'>"+ti+"</div>"\n'
    '      +"<div class=\'cite-modal-meta\'><span>"+m+"</span>"+st+"</div>"\n'
    '      +(bdg?"<div class=\'cite-modal-badges\'>"+bdg+"</div>":"")\n'
    '      +ab+lk;\n'
    '    _ov.classList.add("open");\n'
    '  });\n'
    '});\n'
    '})();\n</script>'
)

# Kapitel in HTML umwandeln
chapters_html = []
for i, md in enumerate(chapters_md, 1):
    html_chapter = md2html(md)
    # Erste h1 nummerieren (Kapitelnummer als eigene Zeile über dem Titel)
    html_chapter = re.sub(r'^<h1>(.*?)</h1>',
                          f'<h1><span class="ch-num">Kapitel {i:02d}</span>\\1</h1>',
                          html_chapter, count=1)
    chapters_html.append(html_chapter)

# Forschungsdesiderata: H1 ohne Kapitelnummer, jedes Vorhaben (H2) als Karte
fd_html = md2html(fd_md) if fd_md.strip() else ""
if fd_html:
    fd_html = re.sub(r'<h1>(.*?)</h1>',
                     r'<h1><span class="ch-num">Ausblick für die Forschung</span>\1</h1>',
                     fd_html, count=1)
    _fd_parts = re.split(r'(?=<h2>)', fd_html)
    fd_html = _fd_parts[0] + '<div class="fd-grid">' + "".join(
        f'<div class="fd-card">{part}</div>' for part in _fd_parts[1:]) + '</div>'

# Inline-Zitate annotieren — Kapitel und Desiderata in einem Durchlauf
# (erzeugt auch _cit_locations für quellen.html)
_annotated = _annotate_chapters(chapters_html + [fd_html])
chapters_html, fd_html = _annotated[:-1], _annotated[-1]

def _chapter_title(html_ch):
    """Kapiteltitel ohne Nummern-Label, als Klartext."""
    m = re.search(r'<h1>(.*?)</h1>', html_ch)
    if not m:
        return None
    inner = re.sub(r'<span class="ch-num">.*?</span>', '', m.group(1))
    return re.sub('<[^>]+>', '', inner).strip()

def _chapter_slug(i, title):
    return f"{i}-" + re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# TOC
toc_items = ""
for i, html_ch in enumerate(chapters_html, 1):
    title = _chapter_title(html_ch)
    if title:
        toc_items += (f'<li><a href="#{_chapter_slug(i, title)}">'
                      f'<span style="font:600 .7rem var(--font-mono);color:var(--faint);min-width:1.6rem">{i:02d}</span>'
                      f'<span>{title}</span></a></li>\n')
if fd_html:
    toc_items += ('<li><a href="#forschungsdesiderata">'
                  '<span style="font:600 .7rem var(--font-mono);color:var(--accent);min-width:1.6rem">FD</span>'
                  '<span>Forschungsdesiderata</span></a></li>\n')

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
        parts.append(f'<span class="badge badge-cited">{ic("check")}zitiert</span>')
    for b in (badges or []):
        parts.append(badge_html(b))
    return ('<span style="display:inline-flex;flex-wrap:wrap;gap:.25rem;vertical-align:middle">'
            + ''.join(parts) + '</span>')

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
        title_html = (f'<a href="{link}" target="_blank" rel="noopener">{title}</a>') if link else title
        sc = s.get("score", 3)
        bdg = _badge_inline(s.get("badges"), cited=True)
        meta_str = f'{authors} ({year})'
        if journal:
            meta_str += f'. <em>{journal}</em>'
        items.append(
            f'<div style="margin-bottom:.8rem;padding:.8rem 1rem;background:var(--surface);'
            f'border:1px solid var(--line);border-left:3px solid {score_color(sc)};border-radius:var(--radius-sm);'
            f'font:.84rem/1.55 var(--font-ui)">'
            f'<div>{meta_str}. {title_html}</div>'
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin-top:.45rem">'
            f'{stars_html(sc)}{bdg}</div></div>'
        )
    return (
        '<section id="weiterfuehrende-literatur" style="margin-top:3rem">\n'
        '<h2>Weiterführende Literatur</h2>\n'
        f'<p style="font:.84rem/1.5 var(--font-ui);color:var(--muted);margin-bottom:1.2rem">'
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
        title_html = (f'<a href="{link}" target="_blank" rel="noopener">{title}</a>') if link else title
        bdg = _badge_inline(s.get("badges"), cited=cited)
        meta_str = f'{authors} ({year})'
        if journal:
            meta_str += f'. <em>{journal}</em>'
        items.append(
            f'<div style="display:grid;grid-template-columns:3.2rem 1fr;gap:.5rem;padding:.55rem 0;'
            f'border-bottom:1px solid var(--line);font:.8rem/1.5 var(--font-ui)">'
            f'<span style="font:.68rem/1.9 var(--font-mono);color:var(--faint)">{sid}</span>'
            f'<div>{meta_str}. {title_html}<div style="margin-top:.3rem">{bdg}</div></div></div>'
        )
    return (
        '<section id="anhang-7" style="margin-top:4rem;border-top:1px solid var(--line-strong);padding-top:2.5rem">\n'
        '<h2>Anhang 7: Vollständiges Quellenverzeichnis</h2>\n'
        f'<p style="font:.84rem/1.5 var(--font-ui);color:var(--muted);margin-bottom:1.2rem">'
        f'{len(real_sources)} Quellen mit Qualitätslabels</p>\n'
        + "\n".join(items)
        + '\n</section>'
    )

weiterfuehrende_section = _weiterfuehrende_section()
anhang7_section = _anhang7_section()

# (Quellenarchiv nur noch auf quellen.html — nicht mehr in standalone.html eingebettet)
fd_section = (f'<section class="chapter-block fd-section" id="forschungsdesiderata">{fd_html}</section>'
              if fd_html else "")
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
def _stat(label, value):
    return (f'<div style="display:flex;justify-content:space-between;gap:1.5rem;padding:.3rem 0;'
            f'border-bottom:1px solid var(--line)"><span style="color:var(--muted)">{label}</span>'
            f'<strong style="font-family:var(--font-mono);font-weight:600">{value}</strong></div>')

stats_panel = f"""<div id="stats-panel" class="no-print" style="
  position:fixed;top:calc(var(--topbar-h) + .75rem);right:1rem;z-index:1000;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:.9rem 1.1rem .8rem;font:.78rem/1.5 var(--font-ui);box-shadow:var(--shadow-lg);
  min-width:220px;display:none;
">
  <div class="kicker" style="margin-bottom:.5rem"><span class="dot"></span>Dokument</div>
  {_stat("Kapitel", len(chapters_html))}
  {_stat("Quellen", len(real_sources))}
  {_stat("Wörter", f"{word_count:,}".replace(",", "."))}
  {_stat("A4-Seiten", f"~{pages_a4}")}
  {_stat("A5-Seiten", f"~{pages_a5}")}
  <div style="font-size:.66rem;color:var(--faint);margin-top:.45rem">≈ 450 Wörter/A4, 250 Wörter/A5</div>
</div>"""

# Kapitel-Blöcke
def make_chapter_block(html_ch, i):
    title = _chapter_title(html_ch)
    slug = _chapter_slug(i, title) if title else ""
    return f'<div class="chapter-block" id="{slug}">{html_ch}</div>'

chapters_blocks = "\n".join(make_chapter_block(h, i) for i, h in enumerate(chapters_html, 1))

tex_filename = f"{meta['title'][:40].replace(' ','_').replace('/','_')}.tex"

# Finales HTML zusammenbauen
final = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{meta['title']}</title>
<script>{theme_js}</script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],throwOnError:false}})"></script>
<style>
{css}
#to-top {{ position:fixed; right:1.25rem; bottom:1.25rem; width:42px; height:42px; border-radius:50%;
  background:var(--ink); color:#fff; border:0; cursor:pointer; display:grid; place-items:center;
  box-shadow:var(--shadow); opacity:0; pointer-events:none; transform:translateY(8px);
  transition:opacity .2s, transform .2s, background .15s; z-index:700; }}
#to-top.show {{ opacity:1; pointer-events:auto; transform:none; }}
#to-top:hover {{ background:var(--primary); }}
@media print {{ #nav-cluster, #stats-panel, #to-top {{ display:none }} }}
</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="index.html">
      <span class="brand-mark">{ic("mark")}</span>
      <span class="brand-text"><span class="brand-title">{meta['title']}</span><span class="brand-sub">Fachartikel</span></span>
    </a>
    <nav>
      <a class="active" href="standalone.html">{ic("article")}<span class="nav-label">Artikel</span></a>
      <a href="quellen.html">{ic("library")}<span class="nav-label">Quellen</span></a>
      <a href="presentation/index.html">{ic("slides")}<span class="nav-label">Folien</span></a>
      <a href="handbuch.html">{ic("handbook")}<span class="nav-label">Handbuch</span></a>
    </nav>
    <div class="tb-tools"><div data-theme-switch></div></div>
    <div id="nav-cluster" class="tb-tools" style="border-left:0;padding-left:0;margin-left:0">
      <button class="tb-btn" data-tip="Dokumentinfo" onclick="(function(){{var p=document.getElementById('stats-panel');p.style.display=p.style.display==='none'?'block':'none'}})()">{ic("info")}</button>
      <button class="tb-btn" data-tip="Export: LaTeX / Web-Paket" onclick="ltxOpenOverlay()">{ic("download")}</button>
      <button class="tb-btn" data-tip="Drucken" onclick="window.print()">{ic("printer")}</button>
    </div>
  </div>
  <div class="progress" id="read-progress"></div>
</header>
{stats_panel}
<button id="to-top" class="no-print" aria-label="Nach oben" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">{ic("arrow-up")}</button>

<header class="paper-header">
  <div class="kicker"><span class="dot"></span>{meta.get("event","")} &nbsp;/&nbsp; {meta.get("date","")}</div>
  <h1>{meta['title']}</h1>
  {f'<p class="subtitle">{meta["subtitle"]}</p>' if meta.get("subtitle") else ""}
  <p class="authors">{authors_html}</p>
  <p class="meta">{len(chapters_html)} Kapitel &nbsp;·&nbsp; {len(real_sources)} Quellen &nbsp;·&nbsp; ca. {pages_a4} Seiten
    <small>{meta.get("note","")}</small></p>
</header>

{abstract_section}

<nav class="toc">
  <h2>Inhaltsverzeichnis</h2>
  <ol>{toc_items}</ol>
</nav>

<main>
{chapters_blocks}
{fd_section}
</main>

{sources_section}

<script>
document.querySelectorAll('a[href^="#"]').forEach(function(a){{
  a.addEventListener('click',function(e){{
    var t=document.querySelector(a.getAttribute('href'));
    if(t){{e.preventDefault();t.scrollIntoView({{behavior:'smooth'}});}}
  }});
}});
(function(){{
  var bar=document.getElementById('read-progress'), top=document.getElementById('to-top');
  function upd(){{
    var h=document.documentElement, max=h.scrollHeight-h.clientHeight;
    if(bar) bar.style.width=(max>0?(h.scrollTop/max*100):0)+'%';
    if(top) top.classList.toggle('show', h.scrollTop>600);
  }}
  window.addEventListener('scroll',upd,{{passive:true}}); upd();
}})();
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
    t = _EM_RE.sub(r'\\textit{\1}', t)
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
    "openaccess": "Open Access", "paywall": "Paywall", "math": "Mathematik",
    "empirical": "Empirisch", "review": "Review", "theory": "Theorie",
    "practice": "Praxis", "technology": "Technologie"
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
        label = BADGE_LABELS_SHORT.get(b) or BADGE_LABELS.get(b, b)
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
if fd_md.strip():
    chapters_tex.append(md2latex(fd_md))
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

# Schrift im LaTeX-Export: meta.json → "latex_font": "serif" (Charter, Standard) | "sans" (Helvetica)
_LATEX_FONT = (r"\usepackage[scaled=.92]{helvet}" + "\n" + r"\renewcommand{\familydefault}{\sfdefault}" + "\n"
               if meta.get("latex_font") == "sans" else r"\usepackage{charter}" + "\n")

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
        + _LATEX_FONT +
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

_EXP_SEL = 'style="font:.84rem var(--font-ui);padding:.42rem .5rem;border:1px solid var(--line-strong);border-radius:6px;width:100%;background:var(--surface);color:var(--text)"'
_EXP_TD = 'style="border:0;padding:.2rem 0;vertical-align:middle"'
_EXP_TDL = 'style="border:0;padding:.2rem 0;vertical-align:middle;color:var(--muted);width:36%"'
_EXP_ROW = 'style="display:flex;align-items:center;gap:.5rem"'
_LATEX_OVERLAY_HTML = f"""\
<div id="latex-overlay" style="display:none;position:fixed;inset:0;background:rgba(13,22,38,.55);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);z-index:9000;align-items:center;justify-content:center;padding:1rem">
<div style="background:var(--surface);border-radius:14px;padding:1.5rem 1.6rem 1.2rem;max-width:460px;width:100%;box-shadow:var(--shadow-lg);font:.86rem/1.5 var(--font-ui);color:var(--text);border-top:3px solid var(--accent)">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
    <div><div class="kicker" style="margin-bottom:.35rem">Export</div><strong style="font:600 1.15rem/1.2 var(--font-display);color:var(--heading)">Artikel herunterladen</strong></div>
    <button aria-label="Schließen" onclick="document.getElementById('latex-overlay').style.display='none'" style="background:none;border:none;cursor:pointer;color:var(--faint);width:32px;height:32px;border-radius:8px;display:grid;place-items:center">{ic("x")}</button>
  </div>
  <div style="display:flex;gap:.25rem;margin-bottom:1.1rem;background:var(--paper);padding:.25rem;border-radius:8px" id="export-tabs">
    <button class="exp-tab exp-tab-active" onclick="expSwitchTab('latex')" id="exp-tab-latex" style="flex:1;padding:.45rem .6rem;border:0;border-radius:6px;background:var(--surface);color:var(--heading);cursor:pointer;font:600 .78rem var(--font-ui);box-shadow:var(--shadow-sm)">LaTeX</button>
    <button class="exp-tab" onclick="expSwitchTab('web')" id="exp-tab-web" style="flex:1;padding:.45rem .6rem;border:0;border-radius:6px;background:transparent;color:var(--muted);cursor:pointer;font:600 .78rem var(--font-ui)">Web-Paket (ZIP)</button>
  </div>
  <div id="exp-panel-latex">
  <table style="width:100%;border-collapse:collapse;line-height:2;margin:0;font-size:.84rem">
    <tr>
      <td {_EXP_TDL}>Farbmodus</td>
      <td {_EXP_TD}><label style="margin-right:.9rem"><input type="radio" name="ltx-color" value="farbe" checked> Farbe</label><label><input type="radio" name="ltx-color" value="sw"> Schwarz-Weiß</label></td>
    </tr>
    <tr>
      <td {_EXP_TDL}>Schrift</td>
      <td {_EXP_TD}><label style="margin-right:.9rem"><input type="radio" name="ltx-font" value="serif" checked> Serif (Charter)</label><label><input type="radio" name="ltx-font" value="sans"> Serifenlos (Helvetica)</label></td>
    </tr>
    <tr>
      <td {_EXP_TDL}>Schriftgröße</td>
      <td {_EXP_TD}><select id="ltx-size" {_EXP_SEL}>
        <option value="9pt">9 pt — Taschenbuch</option>
        <option value="10pt">10 pt — Fachbuch Standard</option>
        <option value="10.5pt">10.5 pt — Luftig</option>
        <option value="11pt" selected>11 pt — Aktuell</option>
      </select></td>
    </tr>
    <tr>
      <td {_EXP_TDL}>Zeilenabstand</td>
      <td {_EXP_TD}><select id="ltx-stretch" {_EXP_SEL}>
        <option value="1.0">1.0 — Kompakt (Buchdruck)</option>
        <option value="1.15" selected>1.15 — Normal</option>
        <option value="1.25">1.25 — Luftig</option>
      </select></td>
    </tr>
    <tr>
      <td {_EXP_TDL}>Ränder</td>
      <td {_EXP_TD}><select id="ltx-margins" {_EXP_SEL}>
        <option value="eng">Eng (±1.5 cm)</option>
        <option value="normal" selected>Normal (±1.8 cm)</option>
        <option value="bundsteg">Bundsteg — innen 2.5 / außen 1.5 cm</option>
      </select></td>
    </tr>
  </table>
  <div style="background:var(--paper);border-radius:8px;padding:.6rem .85rem;margin:.9rem 0 .45rem;display:flex;align-items:baseline;justify-content:space-between;gap:1rem">
    <span style="color:var(--muted);font-size:.8rem">Geschätzte Seitenanzahl (A5)</span>
    <strong id="ltx-pages" style="font:600 1.1rem var(--font-mono);color:var(--primary)">—</strong>
  </div>
  <div style="font-size:.68rem;color:var(--faint);margin-bottom:.8rem">Schätzung auf Basis der Wortzahl · Tabellen &amp; Abbildungen nicht eingerechnet</div>
  <div id="ltx-compile-hint" style="display:none;background:#e9f6ef;border:1px solid #b5dfc7;border-radius:6px;padding:.4rem .75rem;margin-bottom:.55rem;font-size:.79rem;color:var(--s5)">
    .tex-Datei heruntergeladen — bitte auf <strong>latexonline.cc</strong> hochladen und kompilieren.
  </div>
  <button class="btn btn-primary" onclick="ltxDownload()" style="width:100%">{ic("download")}Herunterladen (.tex)</button>
  <div style="text-align:center;margin-top:.55rem;font-size:.69rem;color:var(--faint)">
    Für PDF: .tex-Datei in Overleaf, pdflatex oder <a href="https://latexonline.cc" target="_blank" rel="noopener" style="color:var(--muted)">latexonline.cc</a> öffnen
  </div>
  </div>
  <div id="exp-panel-web" style="display:none">
    <p style="color:var(--muted);line-height:1.55;margin-bottom:.8rem;font-size:.84rem">Erstellt ein ZIP-Paket mit allem, was für eine Website nötig ist. Den Inhalt einfach in ein Verzeichnis auf einem Webserver (SFTP/FTP) hochladen — fertig.</p>
    <div style="background:var(--paper);border-radius:8px;padding:.7rem .9rem;margin-bottom:.8rem;font-size:.8rem;line-height:1.9">
      <div class="kicker" style="margin-bottom:.3rem">Enthält</div>
      <div {_EXP_ROW}>{ic("article")}Fachartikel (standalone.html)</div>
      <div {_EXP_ROW}>{ic("library")}Quellenverzeichnis (quellen.html)</div>
      <div {_EXP_ROW}>{ic("handbook")}Handbuch (handbuch.html)</div>
      <div {_EXP_ROW}>{ic("slides")}Präsentation (presentation/)</div>
      <div {_EXP_ROW}>{ic("code")}Stylesheets &amp; Icons (assets/)</div>
      <div {_EXP_ROW}>{ic("home")}Startseite (index.html)</div>
    </div>
    <p style="font-size:.74rem;color:var(--faint);margin-bottom:.8rem;line-height:1.45">Hinweis: Folienbilder der Präsentation werden nicht eingebettet. Für Folien mit eingebetteten KI-Bildern den Deployment-Export in der Präsentation selbst verwenden.</p>
    <button class="btn btn-primary" onclick="webPaketDownload()" id="web-paket-btn" style="width:100%">{ic("package")}Web-Paket herunterladen (.zip)</button>
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
    '/* Schrift im Export vorbelegen: wie im Artikel gewählt (Stil-Menü) */'
    'var h=document.documentElement,sans=h.getAttribute("data-font")==="sans"'
    '||(!h.getAttribute("data-font")&&h.getAttribute("data-theme")==="labor");'
    'var r=document.querySelector(\'input[name="ltx-font"][value="\'+(sans?"sans":"serif")+\'"]\');if(r)r.checked=true;'
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
    'var sf=document.querySelector(\'input[name="ltx-font"]:checked\').value==="sans";'
    'var fnt=sf?"\\\\usepackage[scaled=.92]{helvet}\\n\\\\renewcommand{\\\\familydefault}{\\\\sfdefault}"'
    ':"\\\\usepackage{charter}";'
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
    '"% LaTeX Export — "+d+" ("+cm+", "+(sf?"serifenlos":"Serif")+", "+sz+", Abstand "+st+", Ränder "+mg+")",'
    '"% pdflatex standalone.tex  |  latexonline.cc",'
    '"\\\\documentclass["+co+"]{scrartcl}",'
    '"\\\\usepackage[utf8]{inputenc}",'
    '"\\\\usepackage[T1]{fontenc}",'
    'fnt,'
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
    'var sf=document.querySelector(\'input[name="ltx-font"]:checked\').value==="sans";'
    'var base=(document.title||"artikel").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"")'
    '.replace(/[^A-Za-z0-9]+/g,"_").replace(/^_|_$/g,"").slice(0,40)||"artikel";'
    'var fn=base+"_"+sz+"_"+(sf?"sans":"serif")+"_"+(bw?"sw":"farbe")+".tex";'
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
    '["latex","web"].forEach(function(t){var b=document.getElementById("exp-tab-"+t),on=t===tab;'
    'b.style.background=on?"var(--surface)":"transparent";b.style.color=on?"var(--heading)":"var(--muted)";'
    'b.style.boxShadow=on?"var(--shadow-sm)":"none";});'
    '};\n'
    '/* ── Web-Paket (ZIP) ── */\n'
    'window.webPaketDownload=async function(){'
    'var btn=document.getElementById("web-paket-btn");var _wpLabel=btn.innerHTML;'
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
    '/* Landingpage (Fallback, falls index.html nicht eingebettet) */\n'
    'var ti=document.title||"Forschungsartikel";'
    'if(!wpText["index.html"])zip.file("index.html","<!DOCTYPE html>\\n<html lang=\\"de\\">\\n<head>\\n"+'
    '"<meta charset=\\"UTF-8\\"/>\\n<meta name=\\"viewport\\" content=\\"width=device-width,initial-scale=1\\"/>\\n"+'
    '"<title>"+ti+"</title>\\n"+'
    '"<style>body{font-family:system-ui,sans-serif;max-width:680px;margin:4rem auto;padding:0 2rem;color:#222}"+'
    '"h1{font-size:1.4rem;margin-bottom:.5rem}p{color:#666;margin-bottom:2rem}"+'
    '"nav{display:flex;flex-direction:column;gap:.8rem}"+'
    '"a{display:inline-block;padding:.7rem 1.2rem;background:#1f3fbf;color:#fff;text-decoration:none;border-radius:6px;width:fit-content}"+'
    '"a:hover{background:#162e8f}</style>\\n</head>\\n<body>\\n"+'
    '"<h1>"+ti+"</h1>\\n<p>Wähle einen Bereich:</p>\\n<nav>\\n"+'
    '"<a href=\\"standalone.html\\">Artikel lesen</a>\\n"+'
    '"<a href=\\"quellen.html\\">Quelldatenbank</a>\\n"+'
    '"<a href=\\"presentation/index.html\\">Präsentation</a>\\n"+'
    '"<a href=\\"handbuch.html\\">Handbuch</a>\\n"+'
    '"</nav>\\n</body>\\n</html>");'
    '/* Download */\n'
    'var blob=await zip.generateAsync({type:"blob",compression:"DEFLATE",compressionOptions:{level:6}});'
    'var a=document.createElement("a");a.href=URL.createObjectURL(blob);'
    'a.download="web-paket.zip";a.click();URL.revokeObjectURL(a.href);'
    'btn.innerHTML=_wpLabel;btn.disabled=false;'
    '}catch(e){alert("Fehler: "+e.message);btn.innerHTML=_wpLabel;btn.disabled=false;}'
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
    ("assets/css/site.css", base / "assets" / "css" / "site.css"),
    ("assets/icons.js", base / "assets" / "icons.js"),
    ("assets/theme.js", base / "assets" / "theme.js"),
    ("index.html", base / "index.html"),
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

# (Ausdrücke vorab berechnen — Backslashes in f-Strings erst ab Python 3.12 erlaubt)
_wp_text_js  = json.dumps(_wp_files, ensure_ascii=False).replace("</", "<\\/") if _wp_files else "{}"
_wp_fonts_js = json.dumps(_wp_fonts, ensure_ascii=False).replace("</", "<\\/") if _wp_fonts else "{}"
_WEB_PAKET_DATA = (
    '<script>\n'
    f'window._WEB_PAKET_TEXT={_wp_text_js};\n'
    f'window._WEB_PAKET_FONTS={_wp_fonts_js};\n'
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
        f"window.CIT_LOCATIONS={cit_loc_embed};"
        f"window.CUSTOM_BADGES={json.dumps(CUSTOM_BADGES, ensure_ascii=False)};</script>"
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
        # Monatsnamen selbst setzen — "%-d" und "%B" sind plattform- bzw. locale-abhängig
        _d = datetime.datetime.strptime(datum_raw, "%Y-%m-%d")
        _monate = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli",
                   "August", "September", "Oktober", "November", "Dezember"]
        datum_fmt = f"{_d.day}. {_monate[_d.month - 1]} {_d.year}"
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