#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_carworld_structure():
    """Debug CarWorld Classics HTML structure"""
    url = "https://www.carworldclassics.com/aanbod"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for car elements
        car_elements = soup.find_all('div', {'class': 'each-product'})
        print(f"Found {len(car_elements)} car elements")
        
        if car_elements:
            first_car = car_elements[0]
            print("\n=== FIRST CAR ELEMENT ===")
            print(first_car.prettify()[:2000])
            
            # Try to find price elements
            print("\n=== PRICE ANALYSIS ===")
            price_candidates = []
            for tag in ['span', 'div', 'strong', 'p']:
                elements = first_car.find_all(tag)
                for elem in elements:
                    text = elem.get_text().strip()
                    if '€' in text or re.search(r'\d{4,}', text):
                        price_candidates.append(f"{tag}.{elem.get('class', 'no-class')}: {text}")
            
            for candidate in price_candidates[:10]:  # Show first 10
                print(candidate)
            
            # Try to find links
            print("\n=== LINK ANALYSIS ===")
            links = first_car.find_all('a', href=True)
            for link in links[:3]:
                print(f"Link: {link['href']}")
        
    except Exception as e:
        print(f"Error debugging: {str(e)}")

if __name__ == "__main__":
    debug_carworld_structure()