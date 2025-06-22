#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_koen_exclusief():
    """Debug Koen Exclusief website structure"""
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
            
            # Print page title
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text()}")
            
            # Look for car-related content
            page_text = soup.get_text().lower()
            car_keywords = ['porsche', 'auto', 'car', 'voertuig', 'aanbod', 'voorraad', 'inventory']
            found_keywords = [kw for kw in car_keywords if kw in page_text]
            if found_keywords:
                print(f"Found keywords: {found_keywords}")
            
            # Look for potential car listing containers
            selectors = [
                ('div', re.compile(r'.*item.*')),
                ('div', re.compile(r'.*car.*')),
                ('div', re.compile(r'.*product.*')),
                ('article', None),
                ('div', re.compile(r'.*listing.*')),
            ]
            
            for tag, class_pattern in selectors:
                if class_pattern:
                    elements = soup.find_all(tag, class_=class_pattern)
                else:
                    elements = soup.find_all(tag)
                
                if elements and len(elements) > 2:
                    print(f"Found {len(elements)} elements: {tag} with pattern {class_pattern}")
                    print("Sample element:")
                    print(str(elements[0])[:500])
                    return elements
            
            print("No car listing elements found")
                
        except Exception as e:
            print(f"Error with {url}: {str(e)}")
            continue
    
    return []

if __name__ == "__main__":
    debug_koen_exclusief()