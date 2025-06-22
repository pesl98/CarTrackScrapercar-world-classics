#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_koen_car_extraction():
    """Debug the specific car data extraction from KoenExclusief"""
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
        
        print("=== DEBUGGING KOEN CAR EXTRACTION ===")
        
        # Find the car container using the same logic as the scraper
        all_divs = soup.find_all('div')
        car_containers = []
        
        for div in all_divs:
            div_text = div.get_text().lower()
            
            has_porsche = any(model in div_text for model in ['porsche', '911', 'carrera', 'turbo', 'cayenne', 'macan'])
            has_price_info = any(indicator in div_text for indicator in ['€', 'eur', 'carrera', 'achterassturing'])
            has_reasonable_content = len(div_text.strip()) > 50
            
            if has_porsche and has_price_info and has_reasonable_content:
                car_containers.append(div)
        
        print(f"Found {len(car_containers)} car containers")
        
        if car_containers:
            # Analyze the first car container
            container = car_containers[0]
            
            print("\n=== CAR CONTAINER ANALYSIS ===")
            print(f"Container classes: {container.get('class', [])}")
            
            text_content = container.get_text()
            print(f"Full text content:")
            print(text_content)
            print(f"\nText length: {len(text_content)}")
            
            # Look for specific patterns
            print("\n=== PATTERN ANALYSIS ===")
            
            # Look for occasions links
            occasions_links = container.find_all('a', href=re.compile(r'/occasions-kopen/.*', re.I))
            if occasions_links:
                for link in occasions_links:
                    print(f"Occasions link: {link['href']}")
                    print(f"Link text: {link.get_text().strip()}")
            
            # Look for images
            images = container.find_all('img')
            if images:
                for img in images:
                    src = img.get('src', '')
                    print(f"Image: {src}")
                    print(f"Image alt: {img.get('alt', '')}")
            
            # Look for specific text patterns
            text_lower = text_content.lower()
            
            # Extract model details
            if '911' in text_lower:
                print("Found 911 model")
                if 'cabrio' in text_lower:
                    print("- Cabrio variant")
                if 'carrera' in text_lower:
                    print("- Carrera variant")
                if 'gts' in text_lower:
                    print("- GTS variant")
            
            # Extract year
            year_matches = re.findall(r'\b(19[8-9]\d|20[0-2]\d)\b', text_content)
            if year_matches:
                print(f"Found years: {year_matches}")
            
            # Extract price
            price_patterns = [
                r'€\s*([\d.,]+)',
                r'([\d.,]+)\s*€',
                r'\b(\d{5,})\b',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text_content.replace('.', '').replace(',', ''))
                if matches:
                    print(f"Price pattern '{pattern}' found: {matches}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_koen_car_extraction()