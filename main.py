import httpx
from selectolax.parser import HTMLParser
import csv
import time
from urllib.parse import urljoin
from dataclasses import dataclass , asdict ,fields
from typing import Optional
import json

@dataclass
class Product:
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_brand: Optional[str] = None
    rating: Optional[float] = None
    no_of_reviews: Optional[int] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None

def get_html(url):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)  # Set a timeout for the request
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return HTMLParser(response.text)
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
        return None

# Find all product elements 
def parse_products_url(html):
    # Iterate over all product elements
    for product in html.css('li.VcGDfKKy_dvNbxUqm29K'):
        # Get the product URL
        product_url = product.css_first('a').attributes['href']
        if product_url:
            product_url = urljoin('https://www.rei.com', product_url)
            yield product_url
        else:
            break

def parse_pages_products_urls(page_url):
    page_number = 1
    while True:
        if page_number == 1:
            url = page_url
        else:
             url = f"{page_url}?page={page_number}"      

        print(f"Fetching: {url}")

        html = get_html(url)
        if html is None:
            print("Failed to fetch page or last page reached")
            break
        productsUrls = list(parse_products_url(html))

        if not productsUrls:
            print("No more products urls found.")
            break  
        for product_url in productsUrls:
            yield product_url
       # time.sleep(1)  # Wait before fetching the next page
        page_number += 1

def get_product_data(html: HTMLParser, selector: str):
    try:
        # Extract the text and replace HTML entities
        text = html.css_first(selector).text()
        text = text.replace('\xa0', '').replace('&nbsp;', '')  # Replace non-breaking spaces
        return text.strip()
    except AttributeError:
        return None
    
def clean_data(data, str_remove=None):
    strs_to_remove = ['$', '#', 'Item']
    if str_remove:
        strs_to_remove.append(str_remove)
    for str in strs_to_remove:
        if str in data:
            data = data.replace(str, '')
    return data


def parse_product_page(html):
    product = Product()
    product.product_id = int(clean_data(get_product_data(html, 'span#product-item-number')))
    product.product_brand = get_product_data(html, 'a#product-brand-link')
    product.product_name = clean_data(get_product_data(html, 'h1#product-page-title'),product.product_brand)
    product.rating = float(get_product_data(html, '.cdr-rating__number_15-0-0'))
    product.no_of_reviews = int(get_product_data(html, '.cdr-rating__count_15-0-0 > span:nth-of-type(2)'))
   
    # Extract and process current price
    current_price_text = get_product_data(html, 'span.price-value.price-value--sale')
    if current_price_text:
        try:
            product.current_price = float(clean_data(current_price_text))
        except ValueError:
            product.current_price = None
    else:
        product.current_price = None

    # Extract and process original price
    original_price_text = get_product_data(html, 'span.price-component__compare--value')
    if original_price_text:
        try:
            product.original_price = float(clean_data(original_price_text))
        except ValueError:
            product.original_price = None
    else:
        product.original_price = None

    return asdict(product)

def export_to_csv(products):
    fieldnames = [field.name for field in fields(Product)]
    with open('products.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    print("Data exported to CSV file.")

def append_to_csv(products):
    fieldnames = [field.name for field in fields(Product)]
    with open('products.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerows(products)
    print("Data appended to CSV file.")

def export_to_json(products):
    with open('products.json', 'w',encoding='utf-8') as file:
        json.dump(products, file, indent=4)
    print("Data exported to JSON file.")

def append_to_json(products):
    with open('products.json', 'a',encoding='utf-8') as file:
        json.dump(products, file, indent=4)
    print("Data appended to JSON file.")

def main():
    URL = 'https://www.rei.com/c/camping-and-hiking/f/scd-deals'
    products_urls = parse_pages_products_urls(URL)
    products=[]

    for product_url in products_urls:
        #print("parsing product data :"+ product_url)
        html = get_html(product_url)
        product = parse_product_page(html)
        #append_to_csv([product])
        #append_to_json([product])
        products.append(product)
        #time.sleep(0.5)

    export_to_csv(products)
    export_to_json(products)
    print("###########   Done parsing all products data   ###########")

if __name__ == '__main__':  
   main()
