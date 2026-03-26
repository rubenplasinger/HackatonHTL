# Adventureplaner

Zusammengefuehrtes Flask-Projekt mit:

- Proviantverwaltung und Rechnern
- Lernphase
- Quiz
- Charakter-Editor
- Tourenplaner aus `app3` ohne Krankenhaus-Funktionen

## Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Adventureplaner.py
```

Danach im Browser:

- `http://127.0.0.1:5000/` fuer das Hauptmenue
- `http://127.0.0.1:5000/proviant`
- `http://127.0.0.1:5000/lernen`
- `http://127.0.0.1:5000/quiz/start`
- `http://127.0.0.1:5000/charakter`
- `http://127.0.0.1:5000/tourenplaner`

## Hinweise

- Der Tourenplaner nutzt `Open-Meteo` fuer Wetterdaten.
- Die Routenberechnung laeuft ueber den freien OSRM-Dienst.
- Krankenhaus-Endpunkte aus `app3` wurden bewusst nicht uebernommen.
