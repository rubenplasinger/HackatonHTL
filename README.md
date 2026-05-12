# Adventureplaner

Flask-Projekt mit:

- Proviantverwaltung und Rechnern
- Lernphase
- Quiz
- Charakter-Editor
- Tourenplaner

## Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Adventureplaner.py
```

Danach im Browser:

- `http://127.0.0.1:5000/` für das Hauptmenü
- `http://127.0.0.1:5000/proviant`
- `http://127.0.0.1:5000/lernen`
- `http://127.0.0.1:5000/quiz/start`
- `http://127.0.0.1:5000/charakter`
- `http://127.0.0.1:5000/tourenplaner`

## Hinweise

- Der Tourenplaner nutzt `Open-Meteo` für Wetterdaten.
- Die Routenberechnung läuft über den freien OSRM-Dienst.
