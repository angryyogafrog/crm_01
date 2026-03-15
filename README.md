# Simple CRM System

This project is a simple CRM (Customer Relationship Management) web application built with **Flask**.  
It allows managing customers and leads through a web interface and a REST API.

## Features
- SQLite database with Flask-SQLAlchemy
- User authentication (login, logout, password hashing)
- REST API for customers and leads
- Swagger API documentation
- CSV and Excel import/export with basic validation

## Technologies
Python, Flask, Flask-SQLAlchemy, Flask-Login, SQLite, Pandas

## Run the project

Install dependencies

pip install -r requirements.txt

Initialize the database

python init_db.py

Start the application

python app.py

Open in browser

http://127.0.0.1:5000

Swagger API documentation

http://127.0.0.1:5000/api/docs