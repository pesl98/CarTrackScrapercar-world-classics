#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def find_koen_car_elements():
    """Find actual car listing elements on Koen Exclusief"""
    url = "https://koenexclusief.nl/aanbod"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== ANALYZING KOEN EXCLUSIEF STRUCTURE ===")
        
        # Look for specific patterns that might contain car listings
        # Check for any elements containing price patterns (€)
        price_elements = soup.find_all(string=re.compile(r'€\s*[\d.,]+'))
        print(f"Found {len(price_elements)} elements with prices")
        
        # Check for elements containing car-related terms
        car_terms = ['porsche', '911', 'carrera', 'turbo', 'cayenne', 'macan']
        car_elements = []
        
        for term in car_terms:
            elements = soup.find_all(string=re.compile(term, re.IGNORECASE))
            car_elements.extend(elements)
        
        print(f"Found {len(car_elements)} elements mentioning car models")
        
        # Look for containers that might hold car data
        potential_containers = []
        
        # Look for divs with classes that might contain cars
        all_divs = soup.find_all('div', class_=True)
        for div in all_divs:
            div_text = div.get_text().lower()
            if any(term in div_text for term in ['porsche', '€', 'km', 'jaar']):
                if len(div_text.strip()) > 50:  # Skip very short elements
                    potential_containers.append(div)
        
        print(f"Found {len(potential_containers)} potential car containers")
        
        if potential_containers:
            print("\n=== FIRST POTENTIAL CAR CONTAINER ===")
            first_container = potential_containers[0]
            print(f"Classes: {first_container.get('class', [])}")
            print(f"Text content (first 500 chars):")
            print(first_container.get_text()[:500])
            print(f"\nHTML structure (first 800 chars):")
            print(str(first_container)[:800])
            
            # Look for images in this container
            images = first_container.find_all('img')
            if images:
                print(f"\nFound {len(images)} images in container")
                for img in images[:2]:
                    print(f"Image src: {img.get('src', 'No src')}")
                    print(f"Image alt: {img.get('alt', 'No alt')}")
            
            # Look for links in this container
            links = first_container.find_all('a', href=True)
            if links:
                print(f"\nFound {len(links)} links in container")
                for link in links[:2]:
                    print(f"Link href: {link['href']}")
                    print(f"Link text: {link.get_text().strip()[:100]}")
        
        # Check if this might be a JavaScript-loaded page
        scripts = soup.find_all('script')
        js_car_indicators = 0
        for script in scripts:
            script_text = script.get_text()
            if any(term in script_text.lower() for term in ['car', 'auto', 'vehicle', 'ajax', 'json']):
                js_car_indicators += 1
        
        print(f"\nFound {js_car_indicators} scripts that might load car data dynamically")
        
        return potential_containers
        
    except Exception as e:
        print(f"Error analyzing Koen Exclusief: {str(e)}")
        return []

if __name__ == "__main__":
    find_koen_car_elements()