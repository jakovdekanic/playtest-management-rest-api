# Playtest Management REST API 

This is a standalone API for keeping track of playtests. I am a freelance playtester and I noticed that as I was getting more playtests it became harder to keep track of which games I tested, what developers I worked with and my earnings.

## Features

- Add a playtest, update a playtest, delete a playtest, view any or all playtests at one time
- Add a source, update a source, view any or all sources at one time
- Organize playtests by their source
- Keep track of the amount you're paid per playtest and what currency you're being paid in
- Keep track of playtests status

## Tech Stack

- Python
- SQLModel for the database models
- SQLite for the database storage
- Pytest for automated testing
- FastAPI for the web API

## Installation (Linux)

```bash
# Clone the repository into the directory you're in
git clone https://github.com/jakovdekanic/playtest-management-rest-api

# Go into the repository
cd playtest-management-rest-api

# Create a virtual environment for python
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install all required libraries in the virtual environment
pip install -r requirements.txt

# Run the REST API
fastapi dev app/main.py
```

While the REST API is running you can check out FastAPI's interactive API documentation at: http://127.0.0.1:8000/docs

## Running Tests

```bash
python -m pytest
```
