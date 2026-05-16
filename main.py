import random
import string

from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyHttpUrl
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import URL, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


# --- Dependency ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Helpers ---

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


# --- Schemas ---

class ShortenRequest(BaseModel):
    url: AnyHttpUrl

class ShortenResponse(BaseModel):
    short_code: str


# --- Endpoints ---

@app.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten_url(payload: ShortenRequest = Body(...), db: Session = Depends(get_db)):
    """Accept a long URL and return a unique short code."""
    original = str(payload.url)

    # Reuse existing code if the URL was already shortened
    existing = db.query(URL).filter(URL.original_url == original).first()
    if existing:
        return ShortenResponse(short_code=existing.short_code)

    # Generate a collision-free short code
    for _ in range(10):
        code = generate_short_code()
        if not db.query(URL).filter(URL.short_code == code).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique short code.")

    url_entry = URL(original_url=original, short_code=code)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)

    return ShortenResponse(short_code=url_entry.short_code)


@app.get("/redirect")
def redirect_url(code: str, db: Session = Depends(get_db)):
    """Look up the short code and redirect to the original URL."""
    url_entry = db.query(URL).filter(URL.short_code == code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short code not found.")

    return RedirectResponse(url=url_entry.original_url, status_code=302)

@app.delete("/urls/{code}", status_code=200)
def delete_short_code(
    code: str,
    db: Session = Depends(get_db)
):
    url_entry = db.query(URL).filter(
        URL.short_code == code
    ).first()

    if not url_entry:
        raise HTTPException(
            status_code=404,
            detail="Short code not found."
        )

    db.delete(url_entry)
    db.commit()

    return {
        "message": "Short code deleted successfully."
    }