#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def test_carworld_urls():
    url = 'https://www.carworldclassics.com/aanbod'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find car elements
            car_elements = soup.find_all('div', {'class': 'each-product'})
            print(f"Found {len(car_elements)} car elements")
            
            # Test first few cars
            for i, element in enumerate(car_elements[:5]):
                print(f"\n--- Car {i+1} ---")
                
                # Find link
                link = element.find('a', href=True)
                if link:
                    href = link['href']
                    print(f"URL: {href}")
                    
                    # Test different patterns
                    patterns = [
                        r'/occasions-kopen/(\d+)-([^/?]+)',
                        r'/(\d+)-([^/?]+)',
                        r'kopen/(\d+)-([^/?]+)',
                        r'/(\d+)[-/]([^/?]+)',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            print(f"Pattern '{pattern}' matched:")
                            print(f"  ID: {match.group(1)}")
                            print(f"  Rest: {match.group(2)}")
                            
                            # Parse make/model
                            parts = match.group(2).split('-')
                            if len(parts) >= 2:
                                make = parts[0].capitalize()
                                model = ' '.join(parts[1:6]).title()
                                print(f"  Make: {make}")
                                print(f"  Model: {model}")
                            break
                    else:
                        print("No pattern matched")
                        
                    # Also check link text
                    link_text = link.get_text(strip=True)
                    if link_text:
                        print(f"Link text: {link_text}")
                else:
                    print("No link found")
                    
        else:
            print(f"Failed to fetch page: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_carworld_urls()