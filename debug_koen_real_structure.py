#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def analyze_koen_real_structure():
    """Analyze the actual structure shown in the screenshot"""
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
        
        print("=== ANALYZING REAL KOEN EXCLUSIEF STRUCTURE ===")
        
        # Based on screenshot, look for specific patterns:
        # - div class="col-lg-6 each_product_div each_car_cls_70"
        # - div class="col-lg-6 each_product_div each_car_cls_25"
        
        # Try the exact selectors from screenshot
        selectors_from_screenshot = [
            'div.each_product_div',
            'div[class*="each_car_cls"]',
            'div.each_product_div.each_car_cls_70',
            'div.each_product_div.each_car_cls_25',
            'div.col-lg-6.each_product_div',
        ]
        
        car_elements = []
        for selector in selectors_from_screenshot:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                # Analyze first few elements
                for i, elem in enumerate(elements[:3]):
                    print(f"\n--- Element {i+1} ---")
                    print(f"Classes: {elem.get('class', [])}")
                    
                    # Look for links like in screenshot
                    links = elem.find_all('a', href=True)
                    if links:
                        for link in links:
                            href = link['href']
                            if 'occasions-kopen' in href or 'porsche' in href.lower():
                                print(f"Car link: {href}")
                    
                    # Look for images
                    images = elem.find_all('img')
                    if images:
                        for img in images:
                            src = img.get('src', '')
                            if 'feed_images' in src or 'product-img' in img.get('class', []):
                                print(f"Car image: {src}")
                    
                    # Look for car info
                    text = elem.get_text()
                    if 'porsche' in text.lower() or '911' in text:
                        print(f"Car text: {text[:200]}")
                
                if elements:
                    car_elements = elements
                    break
        
        # Also check for the specific pattern from screenshot:
        # /webservices/feed_images/42827054/42827054-0.jpg
        feed_images = soup.find_all('img', src=re.compile(r'/webservices/feed_images/\d+/'))
        if feed_images:
            print(f"\nFound {len(feed_images)} feed images (car photos)")
            for img in feed_images[:3]:
                print(f"Feed image: {img['src']}")
                # Find parent container
                container = img.find_parent('div', class_=re.compile(r'.*product.*|.*car.*'))
                if container:
                    print(f"Container classes: {container.get('class', [])}")
        
        # Look for occasions links pattern from screenshot
        occasions_links = soup.find_all('a', href=re.compile(r'/occasions-kopen/.*porsche.*'))
        if occasions_links:
            print(f"\nFound {len(occasions_links)} occasions links")
            for link in occasions_links[:3]:
                print(f"Occasions link: {link['href']}")
                print(f"Link text: {link.get_text().strip()}")
        
        return car_elements
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

if __name__ == "__main__":
    analyze_koen_real_structure()