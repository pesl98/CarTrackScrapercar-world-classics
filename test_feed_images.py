#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def test_feed_images_detection():
    """Test specific detection of feed_images from the screenshot"""
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
        
        print("=== TESTING FEED IMAGES DETECTION ===")
        
        # Look for the specific image from screenshot: /webservices/feed_images/42827054/42827054-0.jpg
        feed_images = soup.find_all('img', src=re.compile(r'/webservices/feed_images/\d+/'))
        print(f"Found {len(feed_images)} feed_images")
        
        for img in feed_images:
            print(f"Feed image: {img['src']}")
            print(f"Alt text: {img.get('alt', 'No alt')}")
            
            # Find parent containers
            parent = img.find_parent('div')
            if parent:
                print(f"Direct parent classes: {parent.get('class', [])}")
                
                # Look for specific classes from screenshot
                each_product = img.find_parent('div', class_=re.compile(r'.*each_product_div.*'))
                if each_product:
                    print(f"Found each_product_div parent: {each_product.get('class', [])}")
                
                car_cls = img.find_parent('div', class_=re.compile(r'.*each_car_cls.*'))
                if car_cls:
                    print(f"Found each_car_cls parent: {car_cls.get('class', [])}")
            
            print("---")
        
        # Also check for occasions links from screenshot
        occasions_links = soup.find_all('a', href=re.compile(r'/occasions-kopen/.*', re.I))
        print(f"\nFound {len(occasions_links)} occasions links")
        
        for link in occasions_links[:3]:
            href = link['href']
            print(f"Link: {href}")
            if 'porsche' in href.lower():
                print(f"  -> Porsche link!")
            
            # Check parent container
            parent = link.find_parent('div', class_=True)
            if parent:
                print(f"  Parent classes: {parent.get('class', [])}")
        
        # Test the exact selectors
        print(f"\n=== TESTING EXACT SELECTORS ===")
        
        selectors = [
            'div.each_product_div',
            'div[class*="each_car_cls"]',
            'div.col-lg-6.each_product_div',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            print(f"Selector '{selector}': {len(elements)} elements")
            if elements:
                for i, elem in enumerate(elements[:2]):
                    text = elem.get_text()[:100].strip()
                    print(f"  Element {i+1}: {text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_feed_images_detection()