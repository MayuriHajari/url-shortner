# URL Shortener API

Simple URL shortener built using FastAPI and SQLite.

## Setup

### Clone repository

```bash
git clone <repo-url>
cd VYSONM2A1
```

### Create virtual environment

```bash
python -m venv venv
```

### Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run server

```bash
uvicorn main:app --reload
```

---

## API Docs

```text
http://127.0.0.1:8000/docs
```

---

## Endpoints

### POST /shorten

Shortens a URL.

Example body:

```json
{
  "url": "https://google.com"
}
```

### GET /redirect?code=abc123

Redirects to original URL.