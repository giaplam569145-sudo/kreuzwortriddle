# Feature-Vorschläge & Anforderungsanalyse: Crossword Riddle Framework

**Datum:** Mai 2026
**Autor:** Jules (Software Engineer)
**Status:** Vorschlag / RFC
**Projekt:** Crossword Riddle Framework (`kreuzwortriddle`)

---

## 1. Einleitung & Ist-Zustands-Analyse

Das **Crossword Riddle Framework** ist ein spezialisiertes Python-Werkzeug zur algorithmischen Generierung von Kreuzworträtseln, optimiert für das Zusammenspiel mit Large Language Models (LLMs) und Agenten.

### Aktueller Funktionsumfang (Ist-Zustand)
- **Kernbibliothek (`kreuzwortriddle.py`, `grid_generator.py`, `models.py`):**
  - Backtracking-Gitterplatzierung von Wörtern auf Basis vorgegebener Fragen, Antworten und Orientierungen.
  - Kollisions-, Berührungs- und Randprüfungen (`_can_place_at`).
  - Problemerkennung und Feedback für LLMs (`get_problematic_questions`).
  - Progressives Bonuswort-Enthüllungssystem (`BonusRevealSystem`) mit Häufigkeitszählung.
  - Modulares Spielmodi-System (`GameMode` in `gamemode.py`, z. B. `ThemeBasedRiddle`, `NumberRiddle`, `ReverseRiddle`).
- **Schnittstellen:**
  - Standardisierte Python-Schnittstelle (`LLMKreuzwortAPI`).
  - Flask-basierte REST-API (`rest_api.py`) mit Session-State.
  - Model Context Protocol (MCP) Server (`mcp_server.py`) über Stdio für Agenten-Tools.
- **Qualitätssicherung:**
  - 49 automatisierte Pytest-Tests (`test_framework.py`).
  - Vollständige Typisierung mit mypy und ruff-Linter-Regeln.

### Erkannte Herausforderungen & Markt-/Anforderungsanalyse
Kreuzworträtsel-Generatoren und LLM-Tools im Produktionsumfeld benötigen typischerweise:
1. **Verwertbare Ausgabeformate:** Aktuell liefert das Framework 2D-Arrays aus Zeichenstrings (`List[List[str]]`). Endanwender und Redaktionen benötigen jedoch druckreife PDFs, skalierbare SVGs, interaktive Web-Widgets oder Standard-Formate wie IPUZ / PUZ.
2. **Unterstützung bei der Gitterbefüllung:** Wenn ein LLM oder Anwender 4–5 Wörter vorgibt, ist es oft schwierig, manuell passende Füllwörter zu finden, die an bestimmten Kreuzungen exakt passen (z. B. ein Wort mit `?E?L?N`).
3. **Interaktivität & Rätsel lösen:** Es fehlt eine Solver-Logik zur Validierung von Benutzereingaben beim eigentlichen Rätselraten (z. B. Spielstände, Hints, Fortschritt, Fehler-Highlighting).
4. **Vielfalt an Gittertypen:** Derzeit werden nur klassische Freiform-Kreuzwortgitter unterstützt. Beliebte Rätseltypen im deutschsprachigen Raum sind vor allem **Schwedenrätsel** (Fragetexte und Richtungspfeile direkt in Gitterblöcken) sowie symmetrische Zeitungsrätsel mit Blindfeldern (Black Cells).
5. **Gitter-Qualitätsmetriken:** LLMs wissen nicht objektiv, wie gut ein generiertes Gitter ist (z. B. Dichte, Vernetzungsgrad, isolierte Äste, Schwierigkeitsgrad).
6. **Persistenz & Session-Management:** Die Flask-Session serialisiert Instanzen via Signed Cookies (Pickle), was für skalierbare Multi-User-Web-Apps ungeeignet ist.
7. **Sprachliche Feinheiten:** Deutsche Kreuzworträtsel erfordern oft feste Regeln für Umlaute (Ä -> AE, Ö -> OE, Ü -> UE, ß -> SS) oder Mehrsprachigkeit.

---

## 2. Übersicht der Feature-Vorschläge

Die folgenden 8 Features wurden ausgewählt, um den Nutzen des Frameworks für LLMs, Entwickler und Endanwender signifikant zu steigern.

| # | Feature | Kategorie | Priorität | Komplexität | Zielgruppe |
|---|---|---|---|---|---|
| **1** | **Multi-Format Export- & Rendering-Engine** (PDF, SVG, HTML, IPUZ) | Visualisierung & Export | **Hoch** | Mittel | Endanwender, Redakteure, Web-Entwickler |
| **2** | **Wörterbuch- & Wort-Vorschlags-Engine** (Pattern-Matching & Auto-Fill) | Algorithmen & Core | **Hoch** | Mittel | LLM-Agenten, Rätsel-Autoren |
| **3** | **Interaktives Gameplay- & Solver-System** (Check, Hints, Scoring) | Interaktivität & Game | **Hoch** | Niedrig | Web- & Mobile-Apps, Gamification |
| **4** | **Schwedenrätsel- & Pfeil-Gitter-Unterstützung** (In-Grid Clues) | Layout & Varianten | **Mittel** | Hoch | Deutsche Medien, Print, Verlage |
| **5** | **Gitterqualitäts- & Schwierigkeits-Metriken** (Score & Feedback) | Analyse & LLM-Prompting | **Mittel** | Niedrig | LLM-Agenten, Evaluierung |
| **6** | **Symmetrische Gittergenerierung & Block-Zellen** (American/Newspaper-Style) | Layout & Ästhetik | **Mittel** | Hoch | Rätsel-Enthusiasten, Zeitungen |
| **7** | **Persistenzschicht & Puzzle-Verwaltung** (SQLite/JSON Storage) | Backend & Architektur | **Mittel** | Mittel | SaaS-Betreiber, Multi-User-Apps |
| **8** | **Erweiterte Sprach- & Umlaut-Normalisierung** (Custom Charsets) | Domänenlogik | **Niedrig** | Gering | Mehrsprachige Nutzung, Lokalisierung |

---

## 3. Detaillierte Feature-Spezifikationen

---

### Feature 1: Multi-Format Export- & Rendering-Engine
**Status:** Empfohlen für Meilenstein 1
**Schlagworte:** SVG, PDF, HTML5, IPUZ, Standalone-Export

#### Motivation & Problemstellung
Aktuell gibt `get_grid()` lediglich eine zweidimensionale Matrix `List[List[str]]` zurück. Möchte ein Entwickler oder LLM das fertige Rätsel anzeigen, muss er selbst Rendering-Code schreiben. Es fehlen druckfertige Formate (PDF/Print) sowie standardisierte Formate für Rätsel-Apps (z. B. `.ipuz` / `.puz`).

#### Detaillierte Spezifikation
- **SVG-Export (`render_svg(show_answers=False, cell_size=40)`):**
  - Vektorbasierte, gestochen scharfe Grafiken für Web und Print.
  - Optionale Anzeige von Aufgabennummern in den Zellecken (`cell_number`).
  - Separates Rendern von "Blanko-Rätsel" (für Spieler) und "Lösungs-Rätsel" (für Korrektur).
- **Interaktiver HTML5/CSS-Export (`render_html()`):**
  - Generiert eine eigenständige, responsive HTML-Datei mit Grid-Layout und dynamischer Tastaturbedienung (Pfeiltasten, Backspace, Buchstabensprung).
- **PDF-Export (`export_pdf(filename, title="Kreuzworträtsel")`):**
  - Drucklayout im DIN-A4-Format mit Rätselgitter oben und Frageblöcken (Waagerecht / Senkrecht) darunter.
- **IPUZ-Standard-Export (`export_ipuz()`):**
  - Export im offenen JSON-basierten IPUZ-Format (kompatibel mit bekannten Apps wie Across Lite, Puzzazz).

#### Geplante Klassen & Methoden
```python
class GridRenderer:
    def to_svg(self, riddle: KreuzwortRiddle, show_answers: bool = False) -> str: ...
    def to_html(self, riddle: KreuzwortRiddle, interactive: bool = True) -> str: ...
    def to_ipuz(self, riddle: KreuzwortRiddle) -> Dict[str, Any]: ...

# Integration in LLMKreuzwortAPI
api.export_svg(filepath="puzzle.svg", show_answers=False)
api.export_html(filepath="puzzle.html")
```

#### Auswirkungen auf REST & MCP
- REST: `GET /api/export/svg`, `GET /api/export/html`, `GET /api/export/ipuz`
- MCP Tool: `export_riddle(format: "svg" | "html" | "ipuz") -> TextContent`

---

### Feature 2: Wörterbuch- & Wort-Vorschlags-Engine (Pattern Matching & Auto-Fill)
**Status:** Empfohlen für Meilenstein 1
**Schlagworte:** Dictionary, Regex-Lookup, Lückenfüller, LLM-Assistent

#### Motivation & Problemstellung
LLMs generieren oft eine Reihe schöner thematischer Fragen, scheitern aber daran, dass 1–2 Wörter geometrisch nicht ins Gitter passen oder ein freier Schnittpunkt ungenutzt bleibt. Eine interne oder anbindbare Wörterbuch-Engine erlaubt es dem System, passende Füllwörter für bestimmte Muster (z. B. `B _ R _ _ N`) vorzuschlagen.

#### Detaillierte Spezifikation
- **Muster-Suche (`find_matching_words(pattern: str, length: int)`):**
  - Sucht in einer Wortliste nach Wörtern, die zu einem Regex/Masken-Muster passen (z. B. `.E.L..` -> `BERLIN`).
  - Ermöglicht dem LLM, gezielt nach Wörtern zu fragen, um Gitterlücken zu schließen.
- **Schnittstellen-Erweiterung (`get_crossing_suggestions()`):**
  - Analysiert bestehende Platzierungen und meldet dem LLM: *"An Position (x=4, y=2) könnte ein vertikales 5-Buchstaben-Wort mit 'E' an Index 1 kreuzen. Mögliche Antworten: [ELBE, EBENE, EISEN]"*.
- **Plug-and-Play Wordlists:**
  - Standardmäßig mit einer kompakten, lizenzfreien deutschen Wortliste (ca. 5.000 gängige Begriffe).
  - Möglichkeit, benutzerdefinierte Wörterbücher oder Fachthemen-Wortlisten (z. B. Medizin, Geographie) zu laden.

#### Architektur & Code-Beispiel
```python
class WordDictionary:
    def __init__(self, words: Optional[List[str]] = None): ...
    def search(self, pattern: str) -> List[str]: ...
    def suggest_crossings(self, riddle: KreuzwortRiddle) -> List[Dict[str, Any]]: ...
```

---

### Feature 3: Interaktives Gameplay- & Solver-System (Gamification)
**Status:** Empfohlen für Meilenstein 1
**Schlagworte:** Rätselprüfung, User Input, Hints, Validierung, Highscore

#### Motivation & Problemstellung
Bislang ist das Framework rein auf die *Generierung* ausgerichtet. Möchte man das Framework in eine mobile App, ein Web-Spiel oder einen interaktiven Lern-Bot einbinden, muss die Überprüfung von Benutzereingaben, das Bereitstellen von Hilfen (Hints) und die Punkteberechnung separat implementiert werden.

#### Detaillierte Spezifikation
- **Eingabevalidierung (`check_solution(user_grid)` oder `check_word(number, answer)`):**
  - Prüft vollständige oder partielle Eingaben des Nutzers gegen die Musterlösung.
  - Liefert differenziertes Feedback: `CORRECT`, `WRONG_CELLS: [(x, y)]`, `COMPLETED: bool`.
- **Progressive Hinweisstufen (Hint-System):**
  - Stufe 1: Bestätigen, ob das gewählte Wort bisher fehlerfrei ist.
  - Stufe 2: Aufdecken eines einzelnen Buchstabens in einer aktiven Zelle (kostet Punkte).
  - Stufe 3: Zusätzlicher Hinweis zum Fragetext.
- **Scoring-Modell:**
  - Punkteberechnung basierend auf benötigter Zeit, Fehleranzahl und beanspruchten Hinweisen.

#### Architektur-Entwurf
```mermaid
graph LR
    User[Spieler / Client] -->|Eingabe: Wort 1 = 'BARLIN'| Solver[PuzzleSolver API]
    Solver -->|Vergleich mit Placements| Riddle[KreuzwortRiddle]
    Solver -->|Antwort: Fehler an Index 1 (A != E)| User
    User -->|Request: Hint für Wort 1| Solver
    Solver -->|Buchstabe 'E' aufgedeckt| User
```

---

### Feature 4: Schwedenrätsel- & Pfeil-Gitter-Unterstützung (In-Grid Clues)
**Status:** Empfohlen für Meilenstein 2
**Schlagworte:** Schwedenrätsel, Arrow Clues, Printmedien, D-A-CH-Standard

#### Motivation & Problemstellung
Im deutschsprachigen Raum ist das sogenannte **Schwedenrätsel** die mit Abstand beliebteste Variante: Der Fragetext steht nicht separat neben oder unter dem Gitter, sondern befindet sich direkt in einer Blindzelle, mit einem Pfeil (→, ↓, ↳, etc.), der in das erste Lösungsfeld weist.

#### Detaillierte Spezifikation
- **Erweitertes Datenmodell `ClueCell`:**
  - Zellen, die keinen Buchstaben, sondern einen Kurzfragetext und eine Richtungsindikation tragen.
- **Pfeil-Routing-Logik:**
  - Horizontale Pfeile: Startet direkt rechts neben der Fragezelle.
  - Vertikale Pfeile: Startet direkt unter der Fragezelle.
  - Abknickende Pfeile (z. B. Frage oben, Pfeil nach rechts und unten).
- **Kompaktierung von Fragetexten:**
  - Begrenzung der Fragen auf z. B. maximal 30 Zeichen oder automatische Silbentrennung für die visuelle Darstellung in kleinen Gitterkästchen.

---

### Feature 5: Gitterqualitäts- & Schwierigkeits-Metriken
**Status:** Empfohlen für Meilenstein 2
**Schlagworte:** Analytics, Metriken, Dichte, Interlocking Score, Difficulty

#### Motivation & Problemstellung
Ein LLM kann derzeit zwar Fragen hinzufügen und prüfen, ob ein Gitter generiert werden kann (`status: success`), es hat aber keine Einsicht in die *Qualität* und *Ästhetik* des erzeugten Rätsels. Manche Gitter sind extrem weitläufig mit vielen isolierten "Ästen", während professionelle Rätsel eine dichte, stark vernetzte Struktur aufweisen.

#### Detaillierte Spezifikation
- **Metrik-Kennzahlen (`api.get_quality_metrics()`):**
  - **Grid Density:** Verhältnis von belegten Buchstaben-Zellen zur Bounding-Box des Gitters.
  - **Interlocking Factor:** Durchschnittliche Anzahl von Kreuzungen pro Wort (Zielwert: ≥ 1.5).
  - **Isolated Words Count:** Anzahl von Wörtern, die nur über einen einzigen Schnittpunkt verfügen.
  - **Aspect Ratio:** Seitenverhältnis des belegten Bereichs (verhindert unschöne, schmale Schläuche).
  - **Estimated Difficulty:** Basierend auf Wortlängen, seltenen Buchstaben (Q, X, Y, Z) und Kreuzungsdichte.
- **Rückgabe an LLMs:**
  ```json
  {
    "status": "success",
    "metrics": {
      "density_percent": 42.5,
      "interlocking_score": 1.8,
      "bounding_box": {"width": 11, "height": 9},
      "isolated_words": 0,
      "quality_rating": "A"
    }
  }
  ```

---

### Feature 6: Symmetrische Gittergenerierung & Block-Zellen (Newspaper-Style)
**Status:** Empfohlen für Meilenstein 2
**Schlagworte:** 180-Grad-Rotationssymmetrie, Blindfelder, American Crossword

#### Motivation & Problemstellung
Klassische Zeitungs-Kreuzworträtsel (z. B. New York Times, The Guardian, Süddeutsche) weisen oft eine vollständige 180°-Rotationssymmetrie der schwarzen Felder (Block Cells) auf. In diesem Modus ist fast jede Zelle kreuzend belegt.

#### Detaillierte Spezifikation
- **Gitter-Masken (Grid Templates):**
  - Vordefinierte oder dynamisch erzeugte symmetrische Schablonen (z. B. 11x11, 15x15).
- **Constraint Satisfaction Problem (CSP) Solver:**
  - Erweiterung des `GridGenerator`, um Wörter in vorgegebene Lücken (Slots) einzusetzen.
- **Neuer GameMode `SymmetricCrosswordMode`:**
  - Passt sich nahtlos in das bestehende `gamemode.py`-System ein.

---

### Feature 7: Persistenzschicht & Puzzle-Verwaltung (Storage Layer)
**Status:** Empfohlen für Meilenstein 2
**Schlagworte:** SQLite, JSON-Speicher, Puzzle IDs, REST Statefulness

#### Motivation & Problemstellung
Aktuell speichert die REST-API den Zustand in der Flask-Session (Client-seitig als Pickle-Cookie). Das führt bei größeren Gittern zu Cookie-Größenlimits und verhindert das Teilen, Abrufen oder kollaborative Bearbeiten von Rätseln über permanente IDs.

#### Detaillierte Spezifikation
- **Puzzle-Repository (`PuzzleStore`):**
  - Speichern von Rätseln unter einer eindeutigen UUID (z. B. `puzzle_a8f93...`).
  - Storage-Adapter: wahlweise File-JSON (für einfache Setups) oder SQLite (für Produktionsbetrieb).
- **REST-API Erweiterung:**
  - `POST /api/puzzles` -> Erstellt neues Puzzle, liefert `puzzle_id`.
  - `GET /api/puzzles/<id>` -> Lädt existierendes Puzzle.
  - `PUT /api/puzzles/<id>/questions` -> Fügt Fragen hinzu.
  - `GET /api/puzzles` -> Listet vorhandene Rätsel auf.

---

### Feature 8: Erweiterte Sprach- & Umlaut-Normalisierung
**Status:** Empfohlen für Meilenstein 3
**Schlagworte:** Umlaute, Diakritika, Mehrsprachigkeit, Internationalisierung

#### Motivation & Problemstellung
Im Deutschen werden Umlaute in Kreuzworträtseln traditionell oft aufgelöst (`Ä` -> `AE`, `Ö` -> `OE`, `Ü` -> `UE`, `ß` -> `SS`), in anderen Fällen als eigenständige Buchstaben gewertet. Aktuell akzeptiert `isalpha()` Umlaute, normalisiert sie aber nicht, was zu unvorhergesehenen Kreuzungskonflikten führen kann.

#### Detaillierte Spezifikation
- **Normalisierungs-Strategien (`UmlautStrategy`):**
  - `EXPAND` (Default im deutschen Rätselbau): `ÜBER` -> `UEBER`.
  - `PRESERVE`: `ÜBER` bleibt `ÜBER`.
  - `STRIP_ACCENTS`: Für Französisch/Spanisch (`é` -> `E`).
- **Konfigurierbar über API-Initialisierung:**
  ```python
  api = LLMKreuzwortAPI(umlaut_strategy="expand")
  ```

---

## 4. Priorisierungsmatrix & Roadmap

```
WERT FÜR NUTZER / LLM
   ▲
   │   [F2: Wort-Vorschläge]      [F1: Multi-Format Export]
   │   [F3: Solver / Gameplay]    [F5: Qualitäts-Metriken]
   │
   │   [F8: Umlaut-Normalisierung] [F4: Schwedenrätsel]
   │                              [F7: Persistenz / DB]
   │                              [F6: Symmetrische Gitter]
   └────────────────────────────────────────────────────────► TECHNISCHER AUFWAND
```

### Empfohlene Release-Planung

#### Phase 1: Sofortiger Mehrwert (v1.2)
1. **Feature 1:** Multi-Format Export (SVG & HTML Rendering).
2. **Feature 3:** Solver- & Lösungsprüfungs-API.
3. **Feature 5:** Qualitätsmetriken für besseres LLM-Feedback.

#### Phase 2: Erweiterte Intelligenz & Persistenz (v1.3)
1. **Feature 2:** Pattern-Matching Wörterbuch-Engine.
2. **Feature 7:** SQLite-Persistenz & UUID-basierte REST-Routen.

#### Phase 3: Premium-Layouts & Internationalisierung (v2.0)
1. **Feature 4:** Schwedenrätsel mit Pfeilen.
2. **Feature 6:** Symmetrische Newspaper-Gitter.
3. **Feature 8:** Umlaut- und Sprach-Normalisierungs-Pipeline.

---

## 5. Fazit

Mit diesen 8 Vorschlägen entwickelt sich das **Crossword Riddle Framework** von einem reinen Prototyp-Generator zu einer vollwertigen, produktionsreifen Rätsel-Plattform. Insbesondere die Kombination aus **Multi-Format Export (SVG/HTML)**, **Wörterbuch-gestütztem Auto-Fill** und **interaktivem Gameplay-System** schließt die Lücke zwischen generativer KI und greifbarem Endanwender-Erlebnis.
