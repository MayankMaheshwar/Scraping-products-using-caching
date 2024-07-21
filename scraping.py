import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import List
import os
from models import Product
import json
from settings import settings
import redis

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
        
        for item in soup.select('.product'):
            title_element = item.select_one('.woo-loop-product__title a')
            price_element = item.select_one('.price ins .woocommerce-Price-amount bdi') or item.select_one('.price .woocommerce-Price-amount bdi')
            image_element = item.select_one('.mf-product-thumbnail img')

            if not title_element or not price_element or not image_element:
                continue

            title = title_element.text.strip()
            try:
                price = float(price_element.text.strip().replace('₹', '').replace(',', ''))
            except ValueError:
                continue
            image_url = image_element['src']
            
            product = Product(product_title=title, product_price=price, path_to_image=image_url)
            products.append(product)
        
        return products

    def scrape(self) -> List[Product]:
        all_products = []
        for page_num in range(1, self.max_pages + 1):
            html = self.fetch_page(page_num)
            products = self.parse_products(html)
            print(f'products MayankP{page_num}', products)
            all_products.extend(products)
        return all_products

    def cache_products(self, products: List[Product]):
        cached_products = r.get("products")
        if cached_products:
            cached_products = json.loads(cached_products)
        else:
            cached_products = []

        cached_products_dict = {p['product_title']: p for p in cached_products}

        updated_products = []
        for product in products:
            cached_product = cached_products_dict.get(product.product_title)
            if cached_product:
                if cached_product['product_price'] != product.product_price:
                    updated_products.append(product.dict())
                    cached_products_dict[product.product_title] = product.dict()
            else:
                updated_products.append(product.dict())
                cached_products_dict[product.product_title] = product.dict()

        if updated_products:
            with open('products.json', 'w') as f:
                json.dump([product.dict() for product in products], f)
            
            r.set("products", json.dumps(list(cached_products_dict.values())))

        return len(updated_products)
