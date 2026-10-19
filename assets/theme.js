/* ============================================================
   theme.js — Stil-Umschalter (6 Stile) für Startseite, Artikel,
   Quellenverzeichnis und Handbuch.
   - Im <head> laden: setzt <html data-theme="…"> vor dem ersten Rendern.
   - Baut das Auswahlmenü in jedes Element mit [data-theme-switch].
   - Auswahl wird in localStorage gespeichert und gilt für alle Seiten.
   - build.py bettet diese Datei in standalone.html ein.
   ============================================================ */
(function () {
  var KEY = "site_theme_v1";
  var THEMES = [
    { id: "akademie", name: "Akademie", desc: "Nachtblau, Signalrot · Fraunces", sw: ["#0d1626", "#1f3fbf", "#ff5a36", "#f6f5f1"] },
    { id: "klassik",  name: "Klassik",  desc: "Bordeaux, Creme, Gold · Playfair", sw: ["#2a1418", "#7a1f2b", "#b8892b", "#f8f3ea"] },
    { id: "nacht",    name: "Nacht",    desc: "Dunkelmodus für Bildschirmarbeit", sw: ["#05080f", "#131a27", "#7c9cff", "#ff7a59"] },
    { id: "labor",    name: "Labor",    desc: "Technisch · Space Grotesk", sw: ["#0a0a0a", "#0055ff", "#00c37a", "#f2f2f0"] },
    { id: "wald",     name: "Wald",     desc: "Tannengrün und Ocker", sw: ["#10241b", "#1f6b4f", "#d9921f", "#f3f3ec"] },
    { id: "minimal",  name: "Minimal",  desc: "Schwarz-Weiß, ein Akzent", sw: ["#111111", "#ffffff", "#e5484d", "#ebebeb"] }
  ];
  var ICON_PALETTE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a9 9 0 0 0 0 18c1.1 0 1.8-.8 1.8-1.7 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-.9.8-1.7 1.8-1.7H17a4 4 0 0 0 4-4c0-4.5-4-8.2-9-8.2z"/><circle cx="7.5" cy="11.5" r="1"/><circle cx="10" cy="7.5" r="1"/><circle cx="14.5" cy="7.5" r="1"/></svg>';
  var ICON_CHECK = '<svg class="ic tick" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

  function valid(id) { return THEMES.some(function (t) { return t.id === id; }); }
  function load() {
    try {
      var q = (location.search.match(/[?&]theme=([a-z]+)/) || [])[1];   // ?theme=nacht (z. B. für Screenshots)
      if (q && valid(q)) return q;
      var v = localStorage.getItem(KEY);
      return valid(v) ? v : "akademie";
    } catch (e) { return "akademie"; }
  }
  function apply(id) {
    if (id === "akademie") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", id);
    document.querySelectorAll(".theme-opt").forEach(function (b) { b.classList.toggle("active", b.dataset.t === id); });
    document.querySelectorAll(".theme-btn .tb-label").forEach(function (l) {
      var t = THEMES.filter(function (x) { return x.id === id; })[0]; l.textContent = t ? t.name : "Stil";
    });
  }

  var current = load();
  apply(current);

  window.setSiteTheme = function (id) {
    if (!valid(id)) return;
    current = id;
    try { localStorage.setItem(KEY, id); } catch (e) {}
    apply(id);
  };
  window.SITE_THEMES = THEMES;

  /* Stilwechsel in einem anderen Tab übernehmen */
  window.addEventListener("storage", function (e) { if (e.key === KEY && valid(e.newValue)) { current = e.newValue; apply(current); } });

  function build(host) {
    host.classList.add("theme-switch");
    host.innerHTML =
      '<button class="theme-btn" type="button" aria-haspopup="true" aria-label="Stil wählen">' + ICON_PALETTE + '<span class="tb-label">Stil</span></button>' +
      '<div class="theme-menu" role="menu"><div class="tm-head">Stil wählen</div>' +
      THEMES.map(function (t) {
        return '<button class="theme-opt" type="button" role="menuitemradio" data-t="' + t.id + '">' +
          '<span class="sw">' + t.sw.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join("") + '</span>' +
          '<span class="tn">' + t.name + '<span class="td">' + t.desc + '</span></span>' + ICON_CHECK + '</button>';
      }).join("") + '</div>';
    host.querySelector(".theme-btn").addEventListener("click", function (e) { e.stopPropagation(); host.classList.toggle("open"); });
    host.querySelectorAll(".theme-opt").forEach(function (b) {
      b.addEventListener("click", function () { window.setSiteTheme(b.dataset.t); host.classList.remove("open"); });
    });
  }

  function init() {
    document.querySelectorAll("[data-theme-switch]").forEach(build);
    apply(current);
    document.addEventListener("click", function (e) {
      document.querySelectorAll(".theme-switch.open").forEach(function (h) { if (!h.contains(e.target)) h.classList.remove("open"); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") document.querySelectorAll(".theme-switch.open").forEach(function (h) { h.classList.remove("open"); });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
