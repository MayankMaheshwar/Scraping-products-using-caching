from fastapi import FastAPI, Depends, HTTPException, status, Header
from typing import List, Optional
from scraping import Scraper
from models import Product
from settings import settings

app = FastAPI()

def get_current_user(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {settings.auth_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

@app.post("/scrape", dependencies=[Depends(get_current_user)])
def scrape_products(max_pages: int = settings.max_pages, proxy: str = settings.proxy):
    scraper = Scraper(max_pages, proxy)
    products = scraper.scrape()
    updated_count = scraper.cache_products(products)
    return {"status": f"{updated_count} products scraped and updated."}
