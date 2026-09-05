#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_aanbod_list_area():
    """Debug the aanbod-list-area container content"""
    url = "https://koenexclusief.nl/aanbod"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== DEBUGGING AANBOD-LIST-AREA CONTENT ===")
        
        # Find the aanbod-list-area container
        aanbod_area = soup.find('div', class_='aanbod-list-area')
        if not aanbod_area:
            print("ERROR: aanbod-list-area not found!")
            return
        
        print("Found aanbod-list-area container")
        print(f"Container classes: {aanbod_area.get('class', [])}")
        
        # Analyze the structure within
        print(f"\nContainer HTML (first 1000 chars):")
        print(str(aanbod_area)[:1000])
        
        # Look for all child elements
        direct_children = aanbod_area.find_all(recursive=False)
        print(f"\nDirect children: {len(direct_children)}")
        
        for i, child in enumerate(direct_children):
            print(f"Child {i+1}: {child.name} - {child.get('class', [])}")
        
        # Look for specific patterns from screenshot
        print(f"\n=== LOOKING FOR CAR PATTERNS ===")
        
        # Check for each_product_div within area
        product_divs = aanbod_area.find_all('div', class_=re.compile(r'.*each_product_div.*'))
        print(f"Found {len(product_divs)} each_product_div elements")
        
        # Check for each_car_cls within area
        car_cls_divs = aanbod_area.find_all('div', class_=re.compile(r'.*each_car_cls.*'))
        print(f"Found {len(car_cls_divs)} each_car_cls elements")
        
        # Check for col-lg-6 within area
        col_divs = aanbod_area.find_all('div', class_=re.compile(r'.*col-lg-6.*'))
        print(f"Found {len(col_divs)} col-lg-6 elements")
        
        # Check for any images within area
        all_images = aanbod_area.find_all('img')
        print(f"Found {len(all_images)} images in aanbod-list-area")
        
        feed_images = aanbod_area.find_all('img', src=re.compile(r'/webservices/feed_images/'))
        print(f"Found {len(feed_images)} feed_images in aanbod-list-area")
        
        # Check for any links within area
        all_links = aanbod_area.find_all('a', href=True)
        print(f"Found {len(all_links)} links in aanbod-list-area")
        
        occasions_links = aanbod_area.find_all('a', href=re.compile(r'/occasions-kopen/'))
        print(f"Found {len(occasions_links)} occasions links in aanbod-list-area")
        
        # Look for any text containing car info
        area_text = aanbod_area.get_text()
        has_porsche = 'porsche' in area_text.lower()
        has_911 = '911' in area_text.lower()
        has_carrera = 'carrera' in area_text.lower()
        
        print(f"\nText analysis:")
        print(f"Contains 'porsche': {has_porsche}")
        print(f"Contains '911': {has_911}")
        print(f"Contains 'carrera': {has_carrera}")
        print(f"Text length: {len(area_text)}")
        
        if has_porsche or has_911 or has_carrera:
            print(f"Sample text (first 500 chars):")
            print(area_text[:500])
        
        # Look for all divs with substantial content
        all_divs = aanbod_area.find_all('div')
        substantial_divs = []
        
        for div in all_divs:
            div_text = div.get_text().strip()
            if len(div_text) > 50 and any(term in div_text.lower() for term in ['porsche', '911', 'carrera']):
                substantial_divs.append(div)
        
        print(f"\nFound {len(substantial_divs)} divs with substantial car content")
        for i, div in enumerate(substantial_divs[:3]):
            print(f"Substantial div {i+1}: {div.get('class', [])} - {div.get_text()[:100]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_aanbod_list_area()