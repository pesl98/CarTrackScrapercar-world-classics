#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def test_koen_exclusief():
    url = 'https://koenexclusief.nl/aanbod'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Print page structure for analysis
            print("Page structure analysis:")
            print("Title:", soup.title.string if soup.title else "No title")
            
            # Look for potential car container patterns
            potential_containers = [
                'div.row div.col',
                'div[class*="item"]',
                'div[class*="card"]',
                'div[class*="box"]',
                'div[class*="product"]',
                'div[class*="listing"]',
                'div[class*="vehicle"]',
                'div[class*="auto"]',
                'div[class*="aanbod"]',
                '.inventory div',
                '.cars div',
                '.vehicles div'
            ]
            
            # Also check for images which often indicate car listings
            car_images = soup.find_all('img', src=True)
            image_count = len([img for img in car_images if any(keyword in img.get('src', '').lower() or keyword in img.get('alt', '').lower() 
                              for keyword in ['car', 'auto', 'vehicle', 'bmw', 'mercedes', 'porsche', 'audi'])])
            print(f"Found {image_count} potential car images")
            
            selectors = potential_containers
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    # Analyze first few elements
                    for i, element in enumerate(elements[:3]):
                        print(f"\n--- Element {i+1} ---")
                        print(f"HTML snippet: {str(element)[:500]}...")
                        
                        # Look for links
                        links = element.find_all('a', href=True)
                        for link in links[:2]:
                            print(f"Link: {link.get('href')}")
                            print(f"Link text: {link.get_text(strip=True)[:100]}")
                    break
            else:
                print("No car elements found with common selectors")
                
                # Look for JavaScript or AJAX indicators
                scripts = soup.find_all('script')
                ajax_indicators = ['ajax', 'fetch', 'xhr', 'api/', 'json']
                for script in scripts:
                    script_text = script.string or ""
                    if any(indicator in script_text.lower() for indicator in ajax_indicators):
                        print("Found AJAX/dynamic loading indicators")
                        break
                
                # Check for specific Dutch car listing terms
                page_text = soup.get_text().lower()
                dutch_car_terms = ['porsche', 'bmw', 'mercedes', 'audi', 'volkswagen', 'auto', 'voertuig', 'prijs', 'jaar']
                found_terms = [term for term in dutch_car_terms if term in page_text]
                print(f"Found Dutch car terms: {found_terms}")
                
                # Look for any div with car brand names
                brand_divs = soup.find_all('div', string=re.compile(r'(Porsche|BMW|Mercedes|Audi)', re.I))
                print(f"Found {len(brand_divs)} divs with car brand names")
                
                # Check if there's a specific car listing API endpoint
                all_links = soup.find_all('a', href=True)
                api_links = [link['href'] for link in all_links if 'api' in link['href'].lower() or 'json' in link['href'].lower()]
                print(f"Potential API endpoints: {api_links[:5]}")
                
                print("First 1000 chars of body:")
                print(soup.get_text()[:1000])
                
        else:
            print(f"Failed to fetch page: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_koen_exclusief()