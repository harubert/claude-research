/* ============================================================
   theme.js — Stil- und Schrift-Umschalter für Startseite, Artikel,
   Quellenverzeichnis und Handbuch.
   - Im <head> laden: setzt <html data-theme|data-font|data-size> vor dem ersten Rendern.
   - Baut das Auswahlmenü in jedes Element mit [data-theme-switch].
   - Auswahl wird in localStorage gespeichert und gilt für alle Seiten.
   - URL-Parameter für Links/Screenshots: ?theme=print&font=sans&size=l
   - build.py bettet diese Datei in standalone.html ein.
   ============================================================ */
(function () {
  var KEYS = { theme: "site_theme_v1", font: "site_font_v1", size: "site_size_v1" };
  var THEMES = [
    { id: "akademie", name: "Akademie", desc: "Nachtblau, Signalrot · Fraunces", sw: ["#0d1626", "#1f3fbf", "#ff5a36", "#f6f5f1"] },
    { id: "print",    name: "Print",    desc: "Schwarz-Weiß wie eine Drucksache", sw: ["#000000", "#ffffff", "#000000", "#ffffff"] },
    { id: "klassik",  name: "Klassik",  desc: "Bordeaux, Creme, Gold · Playfair", sw: ["#2a1418", "#7a1f2b", "#b8892b", "#f8f3ea"] },
    { id: "nacht",    name: "Nacht",    desc: "Dunkelmodus für Bildschirmarbeit", sw: ["#05080f", "#131a27", "#7c9cff", "#ff7a59"] },
    { id: "labor",    name: "Labor",    desc: "Technisch · Space Grotesk", sw: ["#0a0a0a", "#0055ff", "#00c37a", "#f2f2f0"] },
    { id: "wald",     name: "Wald",     desc: "Tannengrün und Ocker", sw: ["#10241b", "#1f6b4f", "#d9921f", "#f3f3ec"] },
    { id: "minimal",  name: "Minimal",  desc: "Schwarz-Weiß, ein Akzent", sw: ["#111111", "#ffffff", "#e5484d", "#ebebeb"] }
  ];
  /* Schrift des Fließtexts: "auto" = Vorgabe des Stils */
  var FONTS = [
    { id: "auto",  name: "Auto",       cls: "" },
    { id: "serif", name: "Serif",      cls: "f-serif" },
    { id: "sans",  name: "Serifenlos", cls: "" }
  ];
  var SIZES = [
    { id: "s", name: "Klein" }, { id: "m", name: "Normal" }, { id: "l", name: "Groß" }
  ];
  var DEFAULTS = { theme: "akademie", font: "auto", size: "m" };
  var LISTS = { theme: THEMES, font: FONTS, size: SIZES };
  var ATTR = { theme: "data-theme", font: "data-font", size: "data-size" };

  var ICON_PALETTE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a9 9 0 0 0 0 18c1.1 0 1.8-.8 1.8-1.7 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-.9.8-1.7 1.8-1.7H17a4 4 0 0 0 4-4c0-4.5-4-8.2-9-8.2z"/><circle cx="7.5" cy="11.5" r="1"/><circle cx="10" cy="7.5" r="1"/><circle cx="14.5" cy="7.5" r="1"/></svg>';
  var ICON_CHECK = '<svg class="ic tick" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

  function valid(kind, id) { return LISTS[kind].some(function (t) { return t.id === id; }); }
  function load(kind) {
    try {
      var q = (location.search.match(new RegExp("[?&]" + kind + "=([a-z]+)")) || [])[1];
      if (q && valid(kind, q)) return q;
      var v = localStorage.getItem(KEYS[kind]);
      return valid(kind, v) ? v : DEFAULTS[kind];
    } catch (e) { return DEFAULTS[kind]; }
  }
  var state = { theme: load("theme"), font: load("font"), size: load("size") };

  function apply() {
    var html = document.documentElement;
    Object.keys(ATTR).forEach(function (k) {
      if (state[k] === DEFAULTS[k]) html.removeAttribute(ATTR[k]); else html.setAttribute(ATTR[k], state[k]);
    });
    document.querySelectorAll("[data-pick]").forEach(function (b) {
      var p = b.dataset.pick.split(":");
      b.classList.toggle("active", state[p[0]] === p[1]);
    });
    var t = THEMES.filter(function (x) { return x.id === state.theme; })[0];
    document.querySelectorAll(".theme-btn .tb-label").forEach(function (l) { l.textContent = t ? t.name : "Stil"; });
    document.dispatchEvent(new CustomEvent("sitethemechange", { detail: state }));
  }
  apply();

  window.setSiteOption = function (kind, id) {
    if (!valid(kind, id)) return;
    state[kind] = id;
    try { localStorage.setItem(KEYS[kind], id); } catch (e) {}
    apply();
  };
  window.setSiteTheme = function (id) { window.setSiteOption("theme", id); };
  window.getSiteOptions = function () { return { theme: state.theme, font: state.font, size: state.size }; };
  window.SITE_THEMES = THEMES;

  /* Änderung in einem anderen Tab übernehmen */
  window.addEventListener("storage", function (e) {
    Object.keys(KEYS).forEach(function (k) {
      if (e.key === KEYS[k] && valid(k, e.newValue)) { state[k] = e.newValue; apply(); }
    });
  });

  function seg(kind, list) {
    return '<div class="tm-row">' + list.map(function (o) {
      return '<button class="tm-seg ' + (o.cls || "") + '" type="button" data-pick="' + kind + ':' + o.id + '">' + o.name + '</button>';
    }).join("") + '</div>';
  }

  function build(host) {
    host.classList.add("theme-switch");
    host.innerHTML =
      '<button class="theme-btn" type="button" aria-haspopup="true" aria-label="Stil und Schrift wählen">' + ICON_PALETTE + '<span class="tb-label">Stil</span></button>' +
      '<div class="theme-menu" role="menu"><div class="tm-head">Stil</div>' +
      THEMES.map(function (t) {
        return '<button class="theme-opt" type="button" role="menuitemradio" data-pick="theme:' + t.id + '">' +
          '<span class="sw">' + t.sw.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join("") + '</span>' +
          '<span class="tn">' + t.name + '<span class="td">' + t.desc + '</span></span>' + ICON_CHECK + '</button>';
      }).join("") +
      '<div class="tm-sep"></div><div class="tm-head">Schrift im Text</div>' + seg("font", FONTS) +
      '<div class="tm-head">Schriftgröße</div>' + seg("size", SIZES) + '</div>';
    host.querySelector(".theme-btn").addEventListener("click", function (e) { e.stopPropagation(); host.classList.toggle("open"); });
    host.querySelectorAll("[data-pick]").forEach(function (b) {
      b.addEventListener("click", function () {
        var p = b.dataset.pick.split(":");
        window.setSiteOption(p[0], p[1]);
        if (p[0] === "theme") host.classList.remove("open");
      });
    });
  }

  function init() {
    document.querySelectorAll("[data-theme-switch]").forEach(build);
    apply();
    document.addEventListener("click", function (e) {
      document.querySelectorAll(".theme-switch.open").forEach(function (h) { if (!h.contains(e.target)) h.classList.remove("open"); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") document.querySelectorAll(".theme-switch.open").forEach(function (h) { h.classList.remove("open"); });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
