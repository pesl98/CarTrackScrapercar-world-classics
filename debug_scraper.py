#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_koen_exclusief_structure():
    """Debug Koen Exclusief HTML structure"""
    urls_to_try = [
        "https://koenexclusief.nl/aanbod",
        "https://koenexclusief.nl/voorraad",
        "https://koenexclusief.nl/auto",
        "https://koenexclusief.nl/cars",
        "https://koenexclusief.nl",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in urls_to_try:
        try:
            print(f"\n=== TRYING URL: {url} ===")
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status code: {response.status_code}")
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Print page title and basic info
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text()}")
            
            # Look for any text content that mentions cars or inventory
            page_text = soup.get_text().lower()
            car_keywords = ['porsche', 'auto', 'car', 'voertuig', 'aanbod', 'voorraad', 'inventory']
            found_keywords = [kw for kw in car_keywords if kw in page_text]
            if found_keywords:
                print(f"Found car-related keywords: {found_keywords}")
            
            # Check for common car listing patterns
            potential_elements = []
            
            # Look for various container patterns
            patterns = [
                soup.find_all('div', class_=re.compile(r'.*item.*')),
                soup.find_all('div', class_=re.compile(r'.*car.*')),
                soup.find_all('div', class_=re.compile(r'.*product.*')),
                soup.find_all('article'),
                soup.find_all('div', class_=re.compile(r'.*listing.*')),
            ]
            
            for pattern in patterns:
                if pattern and len(pattern) > 1:
                    potential_elements.append((len(pattern), pattern))
            
            if potential_elements:
                potential_elements.sort(key=lambda x: x[0], reverse=True)
                count, elements = potential_elements[0]
                print(f"Found {count} potential car elements")
                if elements:
                    print("First element sample:")
                    print(str(elements[0])[:500])
                break
            else:
                print("No obvious car listing elements found")
                
        except Exception as e:
            print(f"Error with {url}: {str(e)}")
            continue
        
        # Look for car elements with various selectors
        selectors_to_try = [
            ('div', {'class': 'car-item'}),
            ('div', {'class': 'vehicle-item'}), 
            ('div', {'class': 'listing-item'}),
            ('div', {'class': re.compile(r'.*car.*')}),
            ('div', {'class': re.compile(r'.*vehicle.*')}),
            ('div', {'class': re.compile(r'.*product.*')}),
            ('article', {}),
            ('div', {'class': 'item'}),
        ]
        
        car_elements = []
        for tag, attrs in selectors_to_try:
            elements = soup.find_all(tag, attrs)
            if elements and len(elements) > 2:
                print(f"Found {len(elements)} elements with selector {tag}.{attrs}")
                car_elements = elements
                break
        
        if not car_elements:
            # Fallback: look for divs with images that might be cars
            img_elements = soup.find_all('img')
            car_containers = []
            for img in img_elements:
                src = img.get('src', '').lower()
                alt = img.get('alt', '').lower()
                if any(keyword in src or keyword in alt for keyword in ['car', 'auto', 'vehicle', 'porsche', 'bmw']):
                    container = img.find_parent(['div', 'article', 'section'])
                    if container and container not in car_containers:
                        car_containers.append(container)
            car_elements = car_containers[:10]
            print(f"Fallback: Found {len(car_elements)} containers with car images")
        
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
    debug_koen_exclusief_structure()