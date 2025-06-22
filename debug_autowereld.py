#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_autowereld_koen():
    """Debug Autowereld listing for Koen Exclusief"""
    url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"=== ANALYZING AUTOWERELD KOEN EXCLUSIEF ===")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Print page title
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        # Look for car listing patterns
        print("\n=== LOOKING FOR CAR ELEMENTS ===")
        
        # Try different selectors that might contain car listings
        selectors_to_try = [
            'div.item',
            'div.car-item',
            'div.vehicle',
            'div.listing',
            'article',
            'div[class*="auto"]',
            'div[class*="car"]',
            'div[class*="item"]',
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements and len(elements) > 2:
                print(f"Found {len(elements)} elements with selector: {selector}")
                print("Sample element:")
                print(str(elements[0])[:500])
                print("---")
        
        # Look for any elements containing car brands or price patterns
        print("\n=== LOOKING FOR CAR-SPECIFIC CONTENT ===")
        
        # Check for price patterns
        price_elements = soup.find_all(string=re.compile(r'€\s*[\d.,]+'))
        print(f"Found {len(price_elements)} price elements")
        
        # Check for car brands
        car_brands = ['porsche', 'bmw', 'mercedes', 'audi', 'volkswagen', 'ferrari', 'lamborghini']
        brand_mentions = 0
        for brand in car_brands:
            if brand in soup.get_text().lower():
                brand_mentions += 1
                print(f"Found mention of: {brand}")
        
        # Look for structured data or specific containers
        print("\n=== ANALYZING PAGE STRUCTURE ===")
        
        # Find all divs and look for car-specific classes
        all_divs = soup.find_all('div')
        car_divs = []
        
        for div in all_divs:
            div_classes = div.get('class', [])
            div_text = div.get_text().lower()
            
            # Look for divs that might contain car information
            if (any('car' in str(cls).lower() for cls in div_classes) or
                any('auto' in str(cls).lower() for cls in div_classes) or
                any('vehicle' in str(cls).lower() for cls in div_classes) or
                ('€' in div_text and any(brand in div_text for brand in car_brands))):
                car_divs.append(div)
        
        print(f"Found {len(car_divs)} potential car containers")
        
        if car_divs:
            print("\n=== FIRST POTENTIAL CAR CONTAINER ===")
            first_car = car_divs[0]
            print(f"Classes: {first_car.get('class', [])}")
            print(f"Text content (first 300 chars):")
            print(first_car.get_text()[:300])
            print(f"\nHTML structure (first 500 chars):")
            print(str(first_car)[:500])
            
            # Look for links and images
            links = first_car.find_all('a', href=True)
            images = first_car.find_all('img')
            
            if links:
                print(f"\nFound {len(links)} links:")
                for link in links[:3]:
                    print(f"  - {link['href']} ({link.get_text().strip()[:50]})")
            
            if images:
                print(f"\nFound {len(images)} images:")
                for img in images[:3]:
                    print(f"  - {img.get('src', 'No src')} (alt: {img.get('alt', 'No alt')})")
        
        return car_divs
        
    except Exception as e:
        print(f"Error analyzing Autowereld: {str(e)}")
        return []

if __name__ == "__main__":
    debug_autowereld_koen()