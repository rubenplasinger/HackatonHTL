# Outdoor Survival Provision Manager

Minimal Flask MVP for tracking outdoor survival provisions with SQLite persistence and simple planning calculators.

## Features

- Provision tracker with CRUD operations
- Consumption endpoint that prevents negative stock
- Hiking provision calculator
- Rationing calculator based on current stored provisions
- Calculator-to-tracker import endpoint

## Project Structure

```text
C:\HackatonHTL
|   Adventureplaner.py
|   models.py
|   requirements.txt
|   README.md
\---routes
    |   __init__.py
    |   calculator.py
    \---provisions.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python Adventureplaner.py
```

The API will start on `http://127.0.0.1:5000`.

## Example API Calls

Create a provision:

```bash
curl -X POST http://127.0.0.1:5000/provisions ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Water\",\"quantity\":10,\"unit\":\"L\"}"
```

List provisions:

```bash
curl http://127.0.0.1:5000/provisions
```

Consume stock:

```bash
curl -X POST http://127.0.0.1:5000/provisions/1/consume ^
  -H "Content-Type: application/json" ^
  -d "{\"quantity\":2}"
```

Calculate hiking needs:

```bash
curl -X POST http://127.0.0.1:5000/calculate/hiking ^
  -H "Content-Type: application/json" ^
  -d "{\"duration_days\":3,\"intensity\":\"high\"}"
```

Calculate rationing:

```bash
curl -X POST http://127.0.0.1:5000/calculate/rationing ^
  -H "Content-Type: application/json" ^
  -d "{\"days\":5}"
```

Import calculated items:

```bash
curl -X POST http://127.0.0.1:5000/provisions/from-calculation ^
  -H "Content-Type: application/json" ^
  -d "{\"items\":[{\"name\":\"Water\",\"quantity\":7.5,\"unit\":\"L\"},{\"name\":\"Food\",\"quantity\":7500,\"unit\":\"kcal\"}]}"
```
