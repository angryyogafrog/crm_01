# Flask CRM System

Ein einfaches CRM-System mit Flask, SQLite, Login, Kunden- und Lead-Verwaltung sowie REST API.

## Funktionen
- Registrierung und Login
- Kunden verwalten
- Leads verwalten
- REST API mit Swagger
- CSV-/Excel-Import und Export für Customers

## Setup
1. `python -m venv .venv`
2. `.\.venv\Scripts\Activate.ps1`
3. `python -m pip install -r requirements.txt`
4. `python app.py`
5. `http://127.0.0.1:5000`

## REST API
`http://127.0.0.1:5000/api/docs`