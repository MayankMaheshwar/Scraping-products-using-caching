import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import List
import os
from models import Product
import json
from settings import settings
import redis

# Initialize Redis
r = redis.Redis(host='localhost', port=6379, db=0)

class Scraper:
    def __init__(self, max_pages: int, proxy: str = None):
        self.max_pages = max_pages
        self.proxy = proxy
        self.base_url = "https://dentalstall.com/shop/"

    def fetch_page(self, page_num: int):
        url = f"{self.base_url}?page={page_num}"
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            response = requests.get(url, proxies=proxies)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            sleep(5)
            return self.fetch_page(page_num)

    def parse_products(self, html: str) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for item in soup.select('.product-item'):
            title = item.select_one('.product-title').text.strip()
            price = float(item.select_one('.product-price').text.strip().replace('$', ''))
            image_url = item.select_one('.product-image')['src']
            product = Product(product_title=title, product_price=price, path_to_image=image_url)
            products.append(product)
        return products

    def scrape(self) -> List[Product]:
        all_products = []
        for page_num in range(1, self.max_pages + 1):
            html = self.fetch_page(page_num)
            products = self.parse_products(html)
            all_products.extend(products)
        return all_products

    def cache_products(self, products: List[Product]):
        cached_products = r.get("products")
        if cached_products:
            cached_products = json.loads(cached_products)
        else:
            cached_products = []

        updated_products = []
        for product in products:
            if not any(p['product_title'] == product.product_title and p['product_price'] == product.product_price for p in cached_products):
                updated_products.append(product)

        if updated_products:
            with open('products.json', 'w') as f:
                json.dump([product.dict() for product in updated_products], f)
            r.set("products", json.dumps([product.dict() for product in products]))

        return len(updated_products)
