# Forschungsartikel-Template

## Startmodus

Wenn der User **„Leg los"** (oder sinngemäß) schreibt, stelle zuerst diese Fragen — alle auf einmal, in einer einzigen Nachricht, kompakt als nummerierte Liste:

1. **Thema** — Was ist das genaue Thema des Artikels? (1–2 Sätze)
2. **Autor** — Name und ggf. Institution / Rolle?
3. **Veranstaltung** — Für welche Konferenz, Tagung oder welchen Anlass?
4. **Datum** — Wann findet die Veranstaltung statt?
5. **Quellenanzahl** — Wie viele Quellen sollen recherchiert werden? (Vorschlag: 80–120)
6. **Kapitelstruktur** — Soll Claude die Kapitel 3–8 automatisch festlegen, oder hast du Wunschthemen für einzelne Kapitel?
7. **Sprache** — Deutsch? Oder eine andere Sprache für den Artikel?
8. **Besondere Schwerpunkte** — Gibt es bestimmte Aspekte, die unbedingt vorkommen sollen? Bestimmte Länder, Zielgruppen, Institutionen?
9. **Bildstil für Präsentation** — Sollen KI-generierte Hintergrundbilder für die Folien erstellt werden? Falls ja: welcher visuelle Stil? Beispiele: *Architektur-Fotografie, Aquarell, Abstrakt-Geometrisch, Minimalismus, Naturlandschaft, Technologie*. Oder: „Nein, keine Bilder."

Sobald der User diese Fragen beantwortet hat, beginne **sofort autonom** mit der Arbeit — ohne weitere Rückfragen. Arbeite Schritt für Schritt durch die Arbeitsschritte unten bis alles fertig ist.

Wenn der User direkt ein Thema oder alle Infos nennt (ohne „Leg los"), beginne ebenfalls sofort — die Fragen sind dann nicht nötig.

---

## Sofortauftrag (nach Klärung der Einstiegsfragen)

Arbeite **vollständig autonom** durch alle Schritte. Keine Zusammenfassungen zwischendurch, keine Bestätigungen, keine Rückfragen — außer es fehlt eine Information, die für den Fortschritt zwingend nötig ist.

---

## Arbeitsschritte (in dieser Reihenfolge)

### Schritt 1 — meta.json befüllen
Lies das Thema, den Autor und die Veranstaltung aus der ersten Nachricht des Users.
Trage alle Informationen in `content/meta.json` ein. Abstract zunächst leer lassen (`""`), wird nach dem Schreiben der Kapitel ergänzt.

### Schritt 2 — Kapitelstruktur festlegen
Lege basierend auf dem Thema sinnvolle Titel für Kapitel 3–8 fest. Kapitel 1, 2, 9 und 10 haben immer dieselbe Rolle (siehe Kapitelstruktur unten). Trage die Dateinamen in `meta.json` ein.

### Schritt 3 — Quellen recherchieren
Recherchiere **mindestens 80, idealerweise 100–150** internationale Quellen zum Thema.

Qualitätskriterien:
- Mindestens 60 % peer-reviewed (Badge: `peer`)
- Schwerpunkt auf den Jahren 2022–2026 (Recency 3)
- Wichtige ältere Grundlagenwerke einschließen (Authority 4, Recency 1–2)
- Österreich-Bezug suchen und kennzeichnen wenn vorhanden (Badge: `austria`)
- Englisch- und deutschsprachige Quellen, bei internationalen Themen auch andere Sprachen

Trage jede Quelle vollständig in `sources/sources.json` ein (Schema: siehe unten).
IDs beginnen bei **S001** und laufen fortlaufend.

### Schritt 4 — Kapitel schreiben
Schreibe alle 10 Kapitel als Markdown-Dateien in `content/`.

Pro Kapitel:
- Länge: 800–1.500 Wörter Fließtext (Einleitung und Ausblick kürzer, Hauptkapitel länger)
- Sprache: Deutsch, wissenschaftlich aber zugänglich, österreichische Variante
- Zitierweise: APA 7, Inline: `(Nachname, Jahr)` oder `(Nachname & Nachname, Jahr)`
- Am Ende jedes Kapitels: `## Literatur (Kapitelname)` mit vollständigen APA-7-Referenzen der in diesem Kapitel zitierten Quellen
- Jede im Text zitierte Quelle **muss** in `sources.json` vorhanden sein — sonst wird sie nicht als klickbarer Link erkannt

Abschnittsstruktur innerhalb der Kapitel:
- `## Kapitelname` (H2) als Einstieg
- `### Abschnitt` (H3) für Unterabschnitte
- `#### Detail` (H4) sparsam verwenden

### Schritt 5 — Abstract und source_count ergänzen
Schreibe einen Abstract (3–5 Sätze, auf Deutsch) und trage ihn in `meta.json` ein.
Aktualisiere `source_count` auf die tatsächliche Anzahl der Quellen in `sources.json`.

### Schritt 6 — Build ausführen
```bash
cd /pfad/zum/projektordner
python3 build.py
```
Prüfe die Ausgabe auf Fehler. Wenn Fehler auftreten, behebe sie und führe den Build erneut aus.

### Schritt 7 — Präsentation erstellen
Erstelle `presentation/index.html` als Präsentation für die Veranstaltung.
Vorlage: `presentation/index.html` im Template-Ordner.
Folienanzahl: abhängig von Vortragslänge — Faustregel: ~1 Folie pro Minute. Typisch: Titel + Agenda (2), Kapiteltrennfolien (1 pro Kapitel), Inhaltsfolien (2–4 pro Kapitel), Fazit + Danke (2–3).

**Grundprinzip Text vs. Bild:**
- Text sitzt immer fix an derselben Position (oben links, `center: false` in Reveal.js)
- Bilder sind reine Dekoration: dahinter blass oder seitlicher Verlauf
- `overflow: hidden` auf allen Sections verhindert, dass Text herausläuft

**Typografie-Design:**
- Serifenlose Systemschrift als Standard (system-ui)
- Wissenschaftlich aber zugänglich — keine übertriebene Gestaltung
- H3 in Versalien mit Letter-Spacing als Kategoriebeschriftung
- Bullets als Strich (–), nicht als Punkt

**Pflicht: `_slideVisual()` Funktion implementieren**
Jede Folie bekommt eine thematisch passende Bildbeschreibung. Die Funktion analysiert h1/h2/h3-Text per Regex und gibt einen visuellen Prompt zurück, der zum Folieninhalt passt (z. B. Volksschule → Schulbank mit Bauklötzen). Kein Foto-Stil, kein Text im Bild. Standard: Engineering-Schematik / Blaupausen-Ästhetik.

**UI-Elemente (alle in `presentation/index.html` integriert):**
- `#fab-cluster` — eingeklappte Werkzeugbox (⚙-Button öffnet/schließt)
- `✦` — Alle Folien mit KI-Bildern generieren (fal.ai Flux Schnell)
- `◎` — Nur aktuelle Folie neu generieren
- `⊞` — Panel: 3 Layout-Varianten wählen
- `Aa` — Panel: 8 Schriftstil-Themes (Google Fonts)
- `◉` — Panel: Hintergrundfarbe für aktuelle Folie
- `⊡` — Einstellungen als JSON herunterladen
- `◈` — Link zu `stile.html` (Bildstil-Auswahl)

**3 Layout-Varianten (Panel `⊞`):**
- `rein` — Kein Bild, klarer Hintergrund
- `gradient` — Verlauf von links (weiß) nach rechts (volles Bild). Der Verlauf wird per Canvas API direkt ins Bild eingebacken (`_processImageWithGradient`): Bild laden → 1280×720 Canvas → weißes `fillRect` mit `createLinearGradient` drüber → als JPEG Data-URL zurück. Kein CSS-Layer, kein z-index-Problem. Opacity 1.
- `bg` — Bild blass im gesamten Hintergrund (`data-background-opacity: 0.18`)

**8 Schriftstil-Themes (Panel `Aa`):**
1. System — system-ui (neutral)
2. Fraunces + Inter — eleganter Serif
3. Space Grotesk — geometrisch/technisch
4. Syne — ultra-bold Graphic Display
5. Bricolage Grotesque — zeitgenössisch, variabel
6. Barlow Condensed — kondensiert, Lettering-Style
7. Caveat Brush — lockeres Hand Lettering
8. Satisfy — eleganter Brush Script

Alle Themes via Google Fonts CDN geladen. Headings verwenden den Display-Font, Fließtext Inter oder system-ui. Aktivierung per dynamisch injiziertem `<style id="font-theme-style">`. Unbekannte gespeicherte IDs fallen automatisch auf `system` zurück.

**`stile.html` — Bildstil-Galerie:**
18 vordefinierte Stile (Blueprint, Aquarell, Holzschnitt, Pop Art, Bleistift, Realistische Sticker mit Pop-Art-Energie und Themenbezug, Klemmbausteine, Naturmaterialien usw.). Auswahl speichert Prompt in localStorage (`fal_presentation_style_prompt`). `index.html` lauscht via `window.addEventListener('storage', ...)` auf Änderungen dieses Keys: Stil-Wechsel in `stile.html` (anderer Tab) löst automatisch `generateAllImages()` aus — kein manuelles Drücken von ✦ nötig.

**Bildgenerierung (fal.ai Flux Schnell):**
```js
POST https://fal.run/fal-ai/flux/schnell
Authorization: Key <window.FAL_KEY>
Body: { prompt, image_size: "landscape_16_9", num_inference_steps: 4, num_images: 1 }
```
Bilder werden in `localStorage['fal_slide_bg_v4']` gecacht (55 Min. TTL).

Falls der User in Frage 9 einen Bildstil gewählt hat:
- Setze die Variable `_DEFAULT_STYLE` auf den passenden englischen Prompt (kein Text, keine Buchstaben, kein Jahr im Bild).
- `IMG_STYLE` wird beim Start aus localStorage geladen oder fällt auf `_DEFAULT_STYLE` zurück.
- Der User wählt den Stil im Browser über `stile.html` (◈-Button).

### Schritt 8 — index.html anpassen
Passe `index.html` an: Titel, Untertitel, Autor, Datum, Veranstaltung.

---

## Verzeichnisstruktur

```
projektordner/
├── CLAUDE.md                   ← Diese Datei (Arbeitsanweisung)
├── build.py                    ← Build-Script (nicht verändern)
├── index.html                  ← Landingpage (Titel/Meta anpassen)
├── standalone.html             ← Wird durch Build erzeugt
├── standalone.tex              ← Wird durch Build erzeugt
├── standalone_sw.tex           ← Wird durch Build erzeugt
├── quellen.html                ← Wird durch Build aktualisiert
├── handbuch.html               ← Dokumentation (nicht verändern)
├── content/
│   ├── meta.json               ← Projektmetadaten (befüllen!)
│   ├── 01_einleitung.md        ← Kapitel (schreiben!)
│   ├── 02_grundlagen.md
│   ├── 03_*.md
│   ├── ...
│   └── 10_ausblick.md
├── sources/
│   └── sources.json            ← Alle Quellen (befüllen!)
├── figures/                    ← Abbildungen ablegen (PNG empfohlen)
├── assets/css/paper.css        ← Stylesheet (nicht verändern)
├── API Key.js                  ← fal.ai API-Schlüssel (nicht weitergeben!)
└── presentation/
    ├── index.html              ← Präsentationsfolien (erstellen!)
    ├── logo-weiss.png          ← Logo für dunkle Folien
    └── logo-blau.png           ← Logo für helle Folien
```

---

## Kapitelstruktur

| Nr. | Dateiname | Inhalt | Rolle |
|-----|-----------|--------|-------|
| 1 | `01_einleitung.md` | Warum dieses Thema? Aktuelle Entwicklungen, Zäsuren, Forschungsfragen, Aufbau des Artikels | **fix** |
| 2 | `02_grundlagen.md` | Theoretischer Hintergrund, Definitionen, Konzepte, historische Einordnung | **fix** |
| 3 | `03_*.md` | Themenspezifisch — Claude wählt sinnvollen Fokus | **flexibel** |
| 4 | `04_*.md` | Themenspezifisch | **flexibel** |
| 5 | `05_*.md` | Themenspezifisch | **flexibel** |
| 6 | `06_*.md` | Themenspezifisch | **flexibel** |
| 7 | `07_*.md` | Themenspezifisch | **flexibel** |
| 8 | `08_*.md` | Themenspezifisch | **flexibel** |
| 9 | `09_herausforderungen.md` | Risiken, Grenzen, kritische Perspektiven, ethische Fragen | **fix** |
| 10 | `10_ausblick.md` | Fazit, Zukunftsperspektiven, offene Fragen, Handlungsempfehlungen | **fix** |

---

## sources.json — Schema

Jede Quelle als JSON-Objekt:

```json
{
  "id": "S001",
  "title": "Vollständiger Titel des Werks",
  "authors": ["Nachname, V.", "Nachname2, V2."],
  "year": 2024,
  "journal": "Name der Zeitschrift oder des Verlags",
  "type": "journal",
  "lang": "en",
  "authority": 4,
  "recency": 3,
  "relevance": 3,
  "score": 10,
  "badges": ["peer", "openaccess"],
  "abstract": "Kurzzusammenfassung auf Deutsch (2–4 Sätze).",
  "doi": "10.xxxx/xxxxx",
  "url": "https://...",
  "local": null,
  "retrieved": "2026-03-22",
  "notes": ""
}
```

**Feldwerte:**

`type`: `journal` | `conference` | `book` | `preprint` | `report` | `web`

`lang`: `de` | `en` | (andere ISO-639-1-Codes)

`authority` (1–4):
- 4 = Renommiertes Peer-Review-Journal (Nature, Science, top Fachzeitschriften)
- 3 = Solides Peer-Review-Journal oder angesehener Verlag
- 2 = Konferenzbericht, Institution, Lehrbuch
- 1 = Web, Blog, graue Literatur

`recency` (1–3):
- 3 = 2023–2026
- 2 = 2019–2022
- 1 = vor 2019

`relevance` (1–3):
- 3 = Kernthema, direkt relevant
- 2 = Verwandtes Thema, nützlich
- 1 = Hintergrund, Kontext

`score` = authority + recency + relevance (3–10)

`badges` (Mehrfachauswahl):
- `peer` — Peer-reviewed
- `institution` — Behörde, Organisation, Hochschule
- `book` — Buch oder Buchkapitel
- `preprint` — Noch nicht peer-reviewed
- `web` — Webquelle
- `austria` — Österreich-Bezug
- `openaccess` — Frei zugänglich
- `paywall` — Nur mit Zugang
- `math` — Stark mathematisch

---

## Zitierweise im Text

Inline-Zitate werden automatisch erkannt wenn sie einem dieser Muster entsprechen:

```
(Nachname, Jahr)
(Nachname & Nachname, Jahr)
(Nachname et al., Jahr)
(Nachname, Jahr; Nachname2, Jahr2)
```

Damit die automatische Verlinkung funktioniert, muss der **Nachname der ersten Autorin/des ersten Autors** exakt mit dem ersten Eintrag in `authors` in sources.json übereinstimmen (Groß/Kleinschreibung egal).

---

## Stil-Hinweise

- Deutsch, österreichische Variante (z. B. „heuer", „Schüler:innen" oder „Schülerinnen und Schüler")
- Wissenschaftlich aber zugänglich — keine unnötige Fachterminologie
- Geschlechtergerechte Sprache (Doppelpunkt-Form oder ausschreiben)
- Keine Emojis im Fließtext
- Keine übertriebenen Versprechen über KI-Fähigkeiten
- Lokal-Bezug stärken wo möglich (nationale Institutionen, Hochschulen, Bildungsministerium)
- Konkrete Beispiele und Zahlen bevorzugen — keine vagen Aussagen

---

## Build-Befehl

```bash
python3 build.py
```

Erzeugt:
- `standalone.html` — vollständiger interaktiver Artikel
- `standalone.tex` / `standalone_sw.tex` — LaTeX-Export (Farbe / S/W)
- Aktualisiert `quellen.html`

Bei Fehler: Fehlermeldung lesen, Problem in der genannten Datei beheben, erneut ausführen.

---

## Abbildungen

Abbildungen in `figures/` ablegen (PNG bevorzugt).
Im Kapitel-Markdown einbinden:

```markdown
![Beschriftung der Abbildung](figures/dateiname.png)
```

Wird automatisch als nummerierte `<figure>` (HTML) und `\begin{figure}` (LaTeX) gerendert.

---

## KI-Bildgenerierung (fal.ai Flux)

Der ✦-Button in der Präsentation ruft die fal.ai REST API auf und generiert Hintergrundbilder für alle Kapitel- und Titelfolien.

**Voraussetzungen:**
- `API Key.js` im Projektstamm mit einem gültigen fal.ai API-Key
- `<script src="../API Key.js"></script>` im `<head>` von `presentation/index.html`

**Bedienung:**
- ✦ = Bilder generieren (erster Durchgang)
- ↺ = Alle Bilder neu generieren
- Pro Klick: alle chapter-slides + title-slides erhalten ein neues Bild

**Stil anpassen:**
Die Variable `IMG_STYLE` am Anfang des Script-Blocks in `presentation/index.html` bestimmt den visuellen Stil:
```js
var IMG_STYLE = "architectural photography, blue tones, minimal, elegant, ultra wide";
```

**Sicherheit:**
`API Key.js` enthält den privaten API-Key. Vor Weitergabe des Projekts entweder:
- Die Datei löschen, oder
- Den Key durch eine leere Zeichenkette ersetzen: `window.FAL_KEY = "";`

---

## Qualitätskontrolle vor Abschluss

- [ ] Alle 10 Kapitel vorhanden und inhaltlich vollständig?
- [ ] Jede im Text zitierte Quelle in sources.json vorhanden?
- [ ] `meta.json` vollständig (Titel, Abstract, Autoren, Datum, source_count)?
- [ ] `python3 build.py` läuft ohne Fehler durch?
- [ ] `standalone.html` öffnet sich im Browser korrekt?
- [ ] Präsentation erstellt? `_DEFAULT_STYLE` / `_slideVisual()` implementiert?
- [ ] FAB-Cluster vorhanden (⚙, ✦, ◎, ⊞, Aa, ◉, ⊡, ◈)?
- [ ] `stile.html` verlinkt und mit passenden Stilen befüllt?
- [ ] `index.html` mit korrektem Titel und Datum?
- [ ] `API Key.js` vorhanden (oder bewusst leer gelassen)?
