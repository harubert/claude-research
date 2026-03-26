# Forschungsartikel-Template

## Startmodus

Wenn der User **„Leg los"** (oder sinngemäß) schreibt:

**ALLERERSTER SCHRITT: `content/meta.json` lesen.** Prüfe ob `title` einen echten Titel enthält (NICHT mit `[` beginnend).

### Fall A: meta.json ist bereits befüllt (title beginnt NICHT mit `[`)

**STELL KEINE EINZIGE FRAGE.** Alle Informationen stehen bereits in meta.json:

| Feld | Bedeutung | Beispiel |
|------|-----------|---------|
| `title` | Artikeltitel | "KI im Geometrieunterricht" |
| `subtitle` | Untertitel | "Von der Volksschule bis..." |
| `authors` | Autor + Institution | `[{"name":"...","affiliation":"..."}]` |
| `date` | Veranstaltungsdatum | "2026-04-09" |
| `event` | Veranstaltung | "20. Tag der Geometrie" |
| `lang` | Sprache | "de" |
| `target_sources` | Ziel-Quellenanzahl | 100 |
| `image_style` | Bildstil Präsentation | "watercolor, soft tones" |
| `notes` | Besondere Schwerpunkte | "Fokus auf Österreich..." |
| `chapter_mode` | "auto" oder "custom" | "auto" |
| `chapter_wishes` | Kapitelwünsche (wenn custom) | "" |
| `relevance_topic` | Kernthema für Relevanz | "KI im Geometrieunterricht" |
| `relevance_3` / `relevance_2` / `relevance_1` | Relevanz-Stufen | "" (dann selbst befüllen) |
| `mode` | "article" oder "course" | "article" |
| `course` | LV-Daten (nur bei mode: "course") | `{"type":"seminar","units":12,...}` |

Sage nur: „Projekt gelesen: [Titel]. Starte mit der Arbeit." — und beginne **sofort** mit Schritt 1. Falls `mode: "course"`: nach Schritt 9 automatisch weiter zu Schritt 10 (Syllabus).

### Fall B: meta.json enthält noch Platzhalter (title beginnt mit `[`)

Stelle diese Fragen — alle auf einmal, kompakt als nummerierte Liste:

1. **Modus** — Nur Fachartikel, oder auch eine Lehrveranstaltung dazu? (Artikel / Lehrveranstaltung)
2. **Thema** — Was ist das genaue Thema? (1–2 Sätze)
3. **Autor** — Name und ggf. Institution / Rolle?
4. **Veranstaltung** — Für welche Konferenz, Tagung oder welchen Anlass?
5. **Datum** — Wann findet die Veranstaltung statt?
6. **Quellenanzahl** — Wie viele Quellen sollen recherchiert werden? (Vorschlag: 80–120)
7. **Kapitelstruktur** — Soll Claude die Kapitel 3–8 automatisch festlegen, oder hast du Wunschthemen für einzelne Kapitel?
8. **Sprache** — Deutsch? Oder eine andere Sprache für den Artikel?
9. **Besondere Schwerpunkte** — Gibt es bestimmte Aspekte, die unbedingt vorkommen sollen? Bestimmte Länder, Zielgruppen, Institutionen?
10. **Bildstil für Präsentation** — Sollen KI-generierte Hintergrundbilder für die Folien erstellt werden? Falls ja: welcher visuelle Stil? Oder: „Nein, keine Bilder."

**Falls Lehrveranstaltung (Frage 1 = "Lehrveranstaltung")**, zusätzlich fragen:
11. **LV-Typ** — Vorlesung, Seminar, Übung oder Kombination?
12. **Einheiten** — Wie viele Einheiten? Wie viele Stunden pro Einheit?
13. **ECTS** — Wie viele Credits?
14. **Semester** — In welchem Semester? (z.B. WS 2026/27)
15. **Beurteilung** — Wie wird beurteilt? (z.B. Portfolio, Klausur, Präsentation)
16. **Zielgruppe** — Wer sind die Studierenden? (z.B. Master Lehramt Mathematik)

Sobald der User diese Fragen beantwortet hat, beginne **sofort autonom** mit der Arbeit.

Wenn der User direkt ein Thema oder alle Infos nennt (ohne „Leg los"), beginne ebenfalls sofort — die Fragen sind dann nicht nötig.

---

## Sofortauftrag (nach Klärung der Einstiegsfragen)

**KRITISCH — Autonomes Arbeiten — LIES DAS DREIMAL:**

Du MUSST vollständig autonom durch ALLE Schritte arbeiten — von Schritt 1 bis Schritt 9, ohne Unterbrechung, ohne eine einzige Rückfrage.

**VERBOTEN (absolut, ausnahmslos):**
- ❌ Rückfragen an den User: „Soll ich...?", „Möchtest du...?", „Wie soll ich...?"
- ❌ Zusammenfassungen: „Ich habe jetzt X gemacht. Soll ich weitermachen?"
- ❌ Bestätigungen abwarten: „Passt das so?", „Soll ich fortfahren?"
- ❌ Optionen anbieten: „Wir könnten A oder B machen — was bevorzugst du?"
- ❌ Pausen nach einzelnen Schritten
- ❌ Stoppen nach dem ersten Build
- ❌ Fragen die bereits durch meta.json beantwortet sind

**PFLICHT:**
- ✅ Durcharbeiten von Schritt 1 bis Schritt 9 in einem Durchgang
- ✅ Bei Unklarheiten: selbst die beste Entscheidung treffen und weitermachen
- ✅ Bei Fehlern: selbst beheben und weitermachen
- ✅ Erst bei Schritt 9 (Übergabe) den User wieder ansprechen

**Einzige Ausnahme:** Ein API-Key oder Login-Credential fehlt physisch und kann nicht erraten werden. Alles andere löst du selbst.

---

## Arbeitsschritte (in dieser Reihenfolge)

### Schritt 1 — meta.json befüllen
Lies das Thema, den Autor und die Veranstaltung aus der ersten Nachricht des Users.
Trage alle Informationen in `content/meta.json` ein. Abstract zunächst leer lassen (`""`), wird nach dem Schreiben der Kapitel ergänzt.

**Relevanz-Kategorien:** Befülle auch die Felder `relevance_topic`, `relevance_3`, `relevance_2` und `relevance_1` passend zum Thema des Artikels. Diese Texte erscheinen im Quellenverzeichnis und steuern, wie die Relevanz-Dimension (1–3) beim Bewerten neuer Quellen interpretiert wird. Beispiel:
```json
"relevance_topic": "KI im Geometrieunterricht",
"relevance_3": "Direkt: KI + Geometrie + Bildung",
"relevance_2": "KI + Mathematik oder Geometrie + Didaktik",
"relevance_1": "Allgemein KI-Bildung, Rahmendokumente"
```

### Schritt 2 — Kapitelstruktur festlegen
Lege basierend auf dem Thema sinnvolle Titel für Kapitel 3–8 fest. Kapitel 1, 2, 9 und 10 haben immer dieselbe Rolle (siehe Kapitelstruktur unten). Trage die Dateinamen in `meta.json` ein.

### Schritt 3a — Erste Quellenrunde (5–10 Quellen) → sofort Build
Recherchiere zunächst **5–10 Kernquellen** zum Thema, trage sie in `sources/sources.json` ein und führe sofort `python3 build.py` aus. So sieht der User bereits nach wenigen Minuten die interaktive Quelldatenbank mit Kategorien, Badges und Scores — auch wenn sie noch leer ist.

Qualitätskriterien:
- Mindestens 60 % peer-reviewed (Badge: `peer`)
- Schwerpunkt auf den Jahren 2022–2026 (Recency 3)
- Wichtige ältere Grundlagenwerke einschließen (Authority 4, Recency 1–2)
- Österreich-Bezug suchen und kennzeichnen wenn vorhanden (Badge: `austria`)
- Englisch- und deutschsprachige Quellen, bei internationalen Themen auch andere Sprachen

IDs beginnen bei **S001** und laufen fortlaufend.

### Schritt 3b — Kapitelgerüst anlegen und ersten Build ausführen
Lege sofort alle 10 Kapitel als Markdown-Dateien in `content/` an — zunächst als **Gerüst** mit Überschriften, 2–3 Einstiegssätzen und 2–3 Zitaten aus den bereits vorhandenen Quellen. Dann `python3 build.py` ausführen, damit der User frühzeitig eine funktionierende Seite sieht.

### Schritt 3c — Weitere Quellen recherchieren (bis Zielanzahl)
Recherchiere weitere Quellen bis das Ziel aus `meta.json` → `target_sources` erreicht ist (Standard: 100).

**KRITISCH — Jede gefundene Quelle MUSS eingetragen werden:**
Wenn du eine relevante Quelle findest, trage sie **sofort** in `sources.json` ein — nicht erst sammeln und später eintragen. Nach jedem Recherche-Block (je ~10 Quellen): zähle die tatsächlichen Einträge in `sources.json` und vergleiche mit dem Ziel. Wenn die Zielanzahl noch nicht erreicht ist: weiter recherchieren.

Arbeite in Blöcken von **10 Quellen**: recherchieren → eintragen → `python3 build.py` → nächster Block. So sieht der User den Fortschritt live im Browser.

### Schritt 3d — URLs und DOIs verifizieren
Für jede Quelle in `sources.json` die einen `url`- oder `doi`-Eintrag hat: **WebFetch aufrufen** und prüfen ob Titel und Autor auf der Zielseite mit dem Eintrag übereinstimmen. Vorgehen:

- URL stimmt → keine Änderung
- URL führt woanders hin → korrekte URL recherchieren und eintragen
- Seite nicht erreichbar / kein Zugriff → `"url": null` setzen, DOI wenn vorhanden behalten
- DOI vorhanden aber keine URL → DOI-Resolver prüfen: `https://doi.org/<doi>`

Ziel: Kein toter Link und kein irreführender Link im Quellenverzeichnis. Dieser Schritt dauert, ist aber entscheidend für wissenschaftliche Glaubwürdigkeit.

### Schritt 3e — Quellen-PDFs herunterladen
Versuche für jede Quelle in `sources.json` das PDF oder den Volltext lokal zu speichern. Ablage in `sources/pdf/`.

Vorgehen pro Quelle:
1. Prüfe ob `url` auf ein frei zugängliches PDF zeigt (Open Access, `badges` enthält `openaccess`)
2. Falls ja: WebFetch → PDF in `sources/pdf/S001_Nachname_Jahr.pdf` speichern
3. Falls Paywall: Abstract + verfügbare Textausschnitte als `sources/pdf/S001_Nachname_Jahr_excerpt.txt` speichern
4. Falls DOI vorhanden: `https://doi.org/<doi>` als Fallback prüfen (manche DOIs führen zu freien Versionen)
5. Falls nichts verfügbar: `download_status: "unavailable"` setzen

Aktualisiere in `sources.json` pro Quelle:
```json
"download_status": "full",       // "full" | "partial" | "unavailable" | null
"local_file": "sources/pdf/S001_Dilling_2024.pdf",
"tags": ["core", "read"]         // Optionales Tagging
```

**Dateinamen-Konvention:** `S{ID}_{Erstautor}_{Jahr}.pdf` (bzw. `_excerpt.txt`)

Arbeite in Blöcken von 10 Quellen, dann `python3 build.py`. Dieser Schritt ist optional — wenn der User `target_downloads: 0` in meta.json setzt, überspringe ihn.

**Tags** (optional, vom User oder Claude vergeben):
- `core` / `supplementary` — Relevanz für den Artikel
- `read` / `unread` / `skimmed` — Lesestatus
- `chapter_01` ... `chapter_10` — Kapitelzuordnung
- `methodology` / `empirical` / `review` / `theory` — Quellentyp

### Schritt 3f — Quellenanzahl prüfen
Zähle die Einträge in `sources.json` und vergleiche mit `target_sources` aus `meta.json`. Wenn die Zielanzahl noch nicht erreicht ist: zurück zu Schritt 3c und weitere Quellen recherchieren. Erst wenn das Ziel erreicht ist: weiter zu Schritt 4.

### Schritt 4 — Kapitel vollständig ausschreiben (mit Build nach jedem Kapitel)
Schreibe die 10 Kapitel nacheinander. **Nach jedem fertiggestellten Kapitel sofort `python3 build.py` ausführen** — so wächst der Artikel sichtbar im Browser mit, Kapitel für Kapitel.

Pro Kapitel:
- Länge: 800–1.500 Wörter Fließtext (Einleitung und Ausblick kürzer, Hauptkapitel länger)
- Sprache: Deutsch, wissenschaftlich aber zugänglich, österreichische Variante
- Zitierweise: APA 7, Inline: `(Nachname, Jahr)` oder `(Nachname & Nachname, Jahr)`
- Am Ende jedes Kapitels: `## Literatur (Kapitelname)` mit vollständigen APA-7-Referenzen der in diesem Kapitel zitierten Quellen
- Jede im Text zitierte Quelle **muss** in `sources.json` vorhanden sein — sonst wird sie nicht als klickbarer Link erkannt

**KRITISCH — Überschriftenhierarchie:**
Die erste Zeile jedes Kapitels **muss** eine H1-Überschrift sein (`# Kapitelname`). `build.py` sucht per Regex nach `<h1>`-Tags, um das Inhaltsverzeichnis zu generieren. Beginnt ein Kapitel mit H2 (`##`) statt H1, bleibt das Inhaltsverzeichnis leer.

Abschnittsstruktur innerhalb der Kapitel:
- `# Kapitelname` (H1) als **erste Zeile** — erzeugt den TOC-Eintrag
- `## Abschnitt` (H2) für Unterabschnitte
- `### Detail` (H3) sparsam verwenden

### Schritt 5 — Abstract und source_count ergänzen
Schreibe einen Abstract (3–5 Sätze, auf Deutsch) und trage ihn in `meta.json` ein.
Aktualisiere `source_count` auf die tatsächliche Anzahl der Quellen in `sources.json`.

### Schritt 6 — Finaler Build
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

### Schritt 9 — Übergabe an den User
Wenn alle Schritte abgeschlossen sind (Artikel, Quellen, Präsentation, Build fehlerfrei), schreibe dem User eine freundliche Abschlussnachricht:

> Die Literatur-Review und der Artikel sind abgeschlossen. Die Präsentation ist erstellt. Du kannst jetzt alles im Browser anschauen:
>
> - **standalone.html** — Fachartikel
> - **quellen.html** — Quellenverzeichnis
> - **presentation/index.html** — Folien (⚙ → ✦ für Bildgenerierung)
>
> Sag mir, was du ändern möchtest — einzelne Kapitel überarbeiten, mehr Quellen ergänzen, die Präsentation anpassen, oder etwas ganz anderes. Wie soll es weitergehen?

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
  "notes": "",
  "download_status": null,
  "local_file": null,
  "tags": []
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

`relevance` (1–3) — **gemessen am Kernthema aus `meta.json` → `relevance_topic`:**
- 3 = entspricht `relevance_3` aus meta.json (direkt zum Kernthema)
- 2 = entspricht `relevance_2` aus meta.json (verwandtes Thema)
- 1 = entspricht `relevance_1` aus meta.json (allgemeiner Hintergrund)

Wenn die `relevance_*`-Felder in meta.json noch leer sind, befülle sie in Schritt 1 passend zum Thema. Diese Texte erscheinen im Quellenverzeichnis und steuern die korrekte Einordnung neuer Quellen.

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

**KRITISCH — Falsche Zitierweise:**

```
❌ VERBOTEN: [S02], [S001], [S012] — diese IDs sind nicht klickbar und werden von build.py nicht erkannt
✅ KORREKT:  (Nachname, Jahr), (Nachname & Nachname, Jahr), (Nachname et al., Jahr)
```

**Nach dem Schreiben jedes Kapitels obligatorisch:**
Prüfe mit grep ob `[S` im Text vorkommt und ersetze jeden Fund durch die korrekte APA-Notation `(Nachname, Jahr)`. Suche in sources.json nach der ID, lies `authors[0]` und `year` und forme daraus das Inline-Zitat.

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
- [ ] Jedes Kapitel beginnt mit `# Kapitelname` (H1)? Inhaltsverzeichnis im Browser prüfen!
- [ ] Kein `[S...]`-Muster im Fließtext? (grep -r "\[S" content/ darf nichts liefern)
- [ ] Jede im Text zitierte Quelle in sources.json vorhanden?
- [ ] `meta.json` vollständig (Titel, Abstract, Autoren, Datum, source_count)?
- [ ] `python3 build.py` läuft ohne Fehler durch?
- [ ] `standalone.html` öffnet sich im Browser korrekt?
- [ ] Präsentation erstellt? `_DEFAULT_STYLE` / `_slideVisual()` implementiert?
- [ ] FAB-Cluster vorhanden (⚙, ✦, ◎, ⊞, Aa, ◉, ⊡, ◈)?
- [ ] `stile.html` verlinkt und mit passenden Stilen befüllt?
- [ ] `index.html` mit korrektem Titel und Datum?
- [ ] `API Key.js` vorhanden (oder bewusst leer gelassen)?
- [ ] Falls LV-Modus: `syllabus.html` erstellt und korrekt?

---

## Lehrveranstaltungs-Modus (optional)

Wenn in `meta.json` das Feld `"mode": "course"` gesetzt ist, wird zusätzlich zum Fachartikel ein Lehrveranstaltungs-Paket erstellt.

### Zusätzliche Felder in meta.json

```json
{
  "mode": "course",
  "course": {
    "type": "seminar",
    "units": 12,
    "hours_per_unit": 2,
    "ects": 3,
    "semester": "WS 2026/27",
    "dates": ["2026-10-07", "2026-10-14"],
    "learning_outcomes": [
      "Die Studierenden können ...",
      "Die Studierenden sind in der Lage ..."
    ],
    "assessment": "Portfolio + Abschlusspräsentation",
    "target_audience": "Master Lehramt Mathematik",
    "prerequisites": "Grundlagen der Mathematikdidaktik"
  }
}
```

**`course.type`** steuert den Inhalt:
- `"vorlesung"` — Nur Input-Folien, Zusammenfassungen. Keine Arbeitsaufträge.
- `"seminar"` — Input + Diskussionsfragen + Leseaufträge + Studierenden-Präsentationen.
- `"uebung"` — Aufgabenblätter + Lösungshinweise + Bewertungskriterien.
- `"kombination"` — Mix je nach Einheit.

### Schritt 10 — Syllabus und Stoffverteilung (nur bei mode: "course")

Nach Schritt 9 (Übergabe des Artikels) weiter:

1. **Syllabus erstellen** (`syllabus.html`):
   - Titel, LV-Typ, ECTS, Semester
   - Lernziele (aus meta.json oder vom Artikel abgeleitet)
   - Terminplan (Datum + Thema + Pflichtlektüre pro Einheit)
   - Beurteilungskriterien
   - Pflichtliteratur (Top-Quellen aus sources.json, score ≥ 8)

2. **Stoffverteilungsplan** (in syllabus.html integriert):
   - Pro Einheit: Kapitelzuordnung, Kernthemen, empfohlene Quellen
   - Bei Seminar/Übung: Arbeitsaufträge oder Diskussionsfragen pro Einheit
   - Quellen mit Tag `core` als Pflichtlektüre markieren

3. **Beispiel-PowerPoint** für Einheit 1:
   - Generiert mit pptxgenjs (wie Präsentation)
   - Enthält: Organisatorisches, Semesterüberblick, inhaltlicher Einstieg
   - Dient als Vorlage — der Lehrende erstellt die weiteren Einheiten selbst

**Bewusste Einschränkung:** Es werden NICHT 12 fertige PowerPoints generiert. Lehre erfordert didaktische Planung die stark von Zielgruppe, Vorwissen und Institution abhängt. Das Template liefert das Gerüst (Syllabus + Stoffverteilung + eine Beispiel-Einheit), nicht das fertige Produkt.

### Verzeichnisstruktur (LV-Modus)

```
projektordner/
├── ... (alles wie bisher)
├── syllabus.html            ← Überblick + Stoffverteilung
└── course/
    └── unit_01.pptx         ← Beispiel-PowerPoint für Einheit 1
```
