/* ============================================================
   icons.js — Einheitliches SVG-Icon-Set (24 × 24, Linienstil)
   ------------------------------------------------------------
   Einzige Quelle für alle Icons im Projekt:
   - HTML-Seiten:  <span data-icon="book"></span>  → wird automatisch ersetzt
   - JavaScript:   icon("book")  → SVG-String
   - build.py liest das JSON-Objekt unten direkt aus dieser Datei.
   Das Objekt zwischen ICONS_START und ICONS_END muss gültiges JSON bleiben.
   ============================================================ */
window.ICONS = /* ICONS_START */{
  "mark":        "<path d='M9 4H5v16h4M15 4h4v16h-4'/><circle cx='12' cy='12' r='1.7' fill='currentColor' stroke='none'/>",
  "article":     "<path d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/><path d='M14 3v5h5'/><path d='M9 13h6M9 17h4'/>",
  "slides":      "<rect x='3' y='4' width='18' height='12' rx='1.5'/><path d='M12 16v4M8 20h8'/><path d='M7 12l3-3 2 2 4-4'/>",
  "library":     "<path d='M4 4h3v16H4zM9 4h3v16H9z'/><path d='M14.5 4.8l2.9-.8 3.6 15.3-2.9.7z'/>",
  "handbook":    "<path d='M3 5.5C3 4.7 3.7 4 4.5 4H10a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H3z'/><path d='M21 5.5c0-.8-.7-1.5-1.5-1.5H14a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h7z'/>",
  "syllabus":    "<rect x='3' y='5' width='18' height='16' rx='1.5'/><path d='M3 10h18M8 3v4M16 3v4'/><path d='M7 14h3M7 17h6'/>",
  "home":        "<path d='M4 10.5L12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z'/>",
  "arrow-left":  "<path d='M19 12H5M11 6l-6 6 6 6'/>",
  "arrow-right": "<path d='M5 12h14M13 6l6 6-6 6'/>",
  "arrow-up":    "<path d='M12 19V5M6 11l6-6 6 6'/>",
  "arrow-up-right": "<path d='M7 17L17 7M8 7h9v9'/>",
  "download":    "<path d='M12 4v11M7 10l5 5 5-5'/><path d='M4 19h16'/>",
  "info":        "<circle cx='12' cy='12' r='9'/><path d='M12 11v5'/><path d='M12 7.5v.5'/>",
  "printer":     "<path d='M7 9V3h10v6'/><rect x='3' y='9' width='18' height='8' rx='1.5'/><path d='M7 14h10v7H7z'/>",
  "search":      "<circle cx='11' cy='11' r='6.5'/><path d='M20 20l-4.2-4.2'/>",
  "filter":      "<path d='M4 5h16l-6 7.5V19l-4 1.5v-8z'/>",
  "sort":        "<path d='M7 4v16M3 16l4 4 4-4'/><path d='M17 20V4M13 8l4-4 4 4'/>",
  "copy":        "<rect x='8' y='8' width='12' height='12' rx='1.5'/><path d='M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8'/>",
  "link":        "<path d='M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1'/><path d='M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1'/>",
  "external":    "<path d='M14 4h6v6M20 4l-9 9'/><path d='M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5'/>",
  "folder":      "<path d='M3 7a2 2 0 0 1 2-2h4l2 2.5h8a2 2 0 0 1 2 2V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/>",
  "check":       "<path d='M5 12.5l4.5 4.5L19 7.5'/>",
  "x":           "<path d='M6 6l12 12M18 6L6 18'/>",
  "play":        "<path d='M8 5.5v13l10.5-6.5z'/>",
  "stop":        "<rect x='6.5' y='6.5' width='11' height='11' rx='1.5'/>",
  "clock":       "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
  "quote":       "<path d='M10 7H6a2 2 0 0 0-2 2v3h6zM10 12c0 3-1.5 5-4.5 5.5'/><path d='M20 7h-4a2 2 0 0 0-2 2v3h6zM20 12c0 3-1.5 5-4.5 5.5'/>",
  "star":        "<path d='M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z'/>",
  "list":        "<path d='M9 6h11M9 12h11M9 18h11'/><path d='M4.5 6h.01M4.5 12h.01M4.5 18h.01'/>",
  "grid":        "<rect x='4' y='4' width='7' height='7' rx='1'/><rect x='13' y='4' width='7' height='7' rx='1'/><rect x='4' y='13' width='7' height='7' rx='1'/><rect x='13' y='13' width='7' height='7' rx='1'/>",
  "chart":       "<path d='M4 20h16'/><path d='M7 16v-5M12 16V6M17 16v-8'/>",
  "code":        "<path d='M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16'/>",
  "terminal":    "<rect x='3' y='4' width='18' height='16' rx='1.5'/><path d='M7 9l3 3-3 3M12 15h5'/>",
  "github":      "<path d='M9 19c-4 1.5-4-2-6-2.5M15 21v-3.5a3 3 0 0 0-.9-2.4c3-.3 6-1.5 6-6.6a5.2 5.2 0 0 0-1.4-3.6 4.8 4.8 0 0 0-.1-3.6s-1.1-.3-3.7 1.4a12.8 12.8 0 0 0-6.6 0C5.7 1 4.6 1.3 4.6 1.3a4.8 4.8 0 0 0-.1 3.6A5.2 5.2 0 0 0 3 8.5c0 5.1 3 6.3 6 6.6a3 3 0 0 0-.9 2.3V21'/>",

  "gear":        "<circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z'/>",
  "sparkles":    "<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/><path d='M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z'/>",
  "refresh":     "<path d='M20 11a8 8 0 0 0-14.3-4.9L4 8'/><path d='M4 4v4h4'/><path d='M4 13a8 8 0 0 0 14.3 4.9L20 16'/><path d='M20 20v-4h-4'/>",
  "target":      "<circle cx='12' cy='12' r='8.5'/><circle cx='12' cy='12' r='4.5'/><circle cx='12' cy='12' r='.8'/>",
  "layout":      "<rect x='3' y='4' width='18' height='16' rx='1.5'/><path d='M3 9h18M10 9v11'/>",
  "type":        "<path d='M4 7V5h16v2M12 5v14M9 19h6'/>",
  "palette":     "<path d='M12 3a9 9 0 0 0 0 18c1.1 0 1.8-.8 1.8-1.7 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-.9.8-1.7 1.8-1.7H17a4 4 0 0 0 4-4c0-4.5-4-8.2-9-8.2z'/><circle cx='7.5' cy='11.5' r='1'/><circle cx='10' cy='7.5' r='1'/><circle cx='14.5' cy='7.5' r='1'/>",
  "save":        "<path d='M5 3h11l4 4v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z'/><path d='M8 3v5h7V3M7 21v-7h10v7'/>",
  "image":       "<rect x='3' y='4' width='18' height='16' rx='1.5'/><circle cx='9' cy='10' r='1.8'/><path d='M21 16l-5-5-9 9'/>",
  "package":     "<path d='M12 3l8 4.5v9L12 21l-8-4.5v-9z'/><path d='M4 7.5l8 4.5 8-4.5M12 12v9'/>",
  "pptx":        "<path d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/><path d='M14 3v5h5'/><path d='M9.5 18v-6h2.3a1.8 1.8 0 0 1 0 3.6H9.5'/>",
  "loader":      "<path d='M12 3a9 9 0 1 0 9 9'/>",

  "peer":        "<path d='M12 3l7 3v5.5c0 4.3-2.9 8-7 9.5-4.1-1.5-7-5.2-7-9.5V6z'/><path d='M8.8 12.2l2.2 2.2 4.3-4.4'/>",
  "institution": "<path d='M3 9.5L12 4l9 5.5'/><path d='M5 10v8M9.5 10v8M14.5 10v8M19 10v8'/><path d='M3 20.5h18'/>",
  "book":        "<path d='M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z'/><path d='M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3'/>",
  "preprint":    "<path d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/><path d='M14 3v5h5'/><path d='M9 13h6M9 16.5h6' stroke-dasharray='2 2'/>",
  "web":         "<circle cx='12' cy='12' r='9'/><path d='M3 12h18'/><path d='M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z'/>",
  "austria":     "<rect x='3' y='5.5' width='18' height='13' rx='1.5' fill='#c8102e' stroke='none'/><rect x='3' y='9.8' width='18' height='4.4' fill='#fff' stroke='none'/><rect x='3' y='5.5' width='18' height='13' rx='1.5' fill='none' stroke='currentColor' stroke-opacity='.25'/>",
  "openaccess":  "<rect x='5' y='11' width='14' height='10' rx='1.5'/><path d='M8 11V7a4 4 0 0 1 7.7-1.5'/><path d='M12 15v2'/>",
  "paywall":     "<rect x='5' y='11' width='14' height='10' rx='1.5'/><path d='M8 11V7a4 4 0 0 1 8 0v4'/><path d='M12 15v2'/>",
  "math":        "<path d='M18 5H6l6 7-6 7h12'/>",
  "empirical":   "<path d='M4 20h16'/><rect x='5.5' y='12' width='3' height='5' rx='.5'/><rect x='10.5' y='7' width='3' height='10' rx='.5'/><rect x='15.5' y='10' width='3' height='7' rx='.5'/>",
  "review":      "<path d='M12 3l9 4.5-9 4.5-9-4.5z'/><path d='M3 12l9 4.5 9-4.5'/><path d='M3 16.5L12 21l9-4.5'/>",
  "theory":      "<path d='M9 18h6M10 21h4'/><path d='M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3z'/>",
  "practice":    "<rect x='5' y='4' width='14' height='17' rx='1.5'/><path d='M9 4V3h6v1'/><path d='M8.5 12l2 2 4-4M8.5 17.5h7'/>",
  "technology":  "<rect x='6' y='6' width='12' height='12' rx='1.5'/><rect x='9.5' y='9.5' width='5' height='5' rx='.5'/><path d='M9.5 2.5V6M14.5 2.5V6M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5'/>",
  "cited":       "<path d='M5 12.5l4.5 4.5L19 7.5'/>"
}/* ICONS_END */;

/* Badge-Beschriftungen — gemeinsam für quellen.html und Präsentation */
window.BADGE_LABELS = {
  peer: "Peer-reviewed", institution: "Institution", book: "Buch / Verlag",
  preprint: "Preprint", web: "Web", austria: "Österreich",
  openaccess: "Open Access", paywall: "Paywall", math: "Mathematik",
  empirical: "Empirisch", review: "Review", theory: "Theorie",
  practice: "Praxis", technology: "Technologie"
};

window.icon = function (name, cls) {
  var body = window.ICONS[name];
  if (!body) return "";
  return '<svg class="ic' + (cls ? " " + cls : "") + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    body + "</svg>";
};

window.hydrateIcons = function (root) {
  (root || document).querySelectorAll("[data-icon]").forEach(function (el) {
    el.innerHTML = window.icon(el.getAttribute("data-icon"), el.getAttribute("data-icon-class") || "");
  });
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function () { window.hydrateIcons(); });
} else {
  window.hydrateIcons();
}
