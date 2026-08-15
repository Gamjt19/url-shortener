import random
import string

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import URL
from .redis_client import redis_client
from .schemas import URLCreate, URLResponse, URLStats



app = FastAPI(
    title="URL Shortener API",
    version="1.0.0",
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        random.choices(characters, k=length)
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/shorten", response_model=URLResponse)
def shorten_url(
    data: URLCreate,
    db: Session = Depends(get_db),
):
    short_code = generate_short_code()

    while db.query(URL).filter(
        URL.short_code == short_code
    ).first():
        short_code = generate_short_code()

    url = URL(
        original_url=str(data.original_url),
        short_code=short_code,
    )

    db.add(url)
    db.commit()
    db.refresh(url)

    redis_client.set(
        short_code,
        str(data.original_url),
    )

    return {
        "original_url": str(data.original_url),
        "short_url": f"/{short_code}",
    }


@app.get("/{short_code}")
def redirect_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    original_url = redis_client.get(short_code)

    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found",
        )

    if not original_url:
        original_url = url.original_url

        redis_client.set(
            short_code,
            original_url,
        )

    url.click_count += 1

    db.commit()

    return RedirectResponse(
        url=original_url,
        status_code=307,
    )


@app.get(
    "/stats/{short_code}",
    response_model=URLStats,
)
def url_stats(
    short_code: str,
    db: Session = Depends(get_db),
):
    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found",
        )

    return {
        "original_url": url.original_url,
        "short_url": f"/{url.short_code}",
        "created_at": url.created_at,
        "click_count": url.click_count,
    }
