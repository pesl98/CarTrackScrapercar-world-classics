#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time

def test_koen_alternatives():
    """Test various alternative sources for KoenExclusief data"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }
    
    # Test different potential URLs for KoenExclusief
    urls_to_test = [
        "https://koenexclusief.nl/aanbod",
        "https://koenexclusief.nl/voorraad", 
        "https://koenexclusief.nl/occasions",
        "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",
        "https://www.autotrack.nl/dealer/koen-exclusief",
        "https://www.gaspedaal.nl/dealers/koen-exclusief",
        "https://occasion.nl/zoeken?dealer=koen-exclusief",
    ]
    
    working_urls = []
    
    for url in urls_to_test:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text().lower()
                
                # Check if it contains car-related content
                car_indicators = ['porsche', 'auto', 'occasions', 'voertuig', '€']
                found_indicators = [ind for ind in car_indicators if ind in text]
                
                if found_indicators:
                    print(f"✓ Contains car content: {found_indicators}")
                    working_urls.append(url)
                    
                    # Check for actual car listings
                    if 'porsche' in text and '€' in text:
                        print("✓ Appears to have actual car listings")
                        
                        # Sample some content
                        title = soup.find('title')
                        if title:
                            print(f"Title: {title.get_text()}")
                else:
                    print("- No car content detected")
            
            elif response.status_code == 403:
                print("✗ Blocked (403)")
            elif response.status_code == 404:
                print("✗ Not found (404)")
            else:
                print(f"✗ Error ({response.status_code})")
                
            time.sleep(1)  # Be respectful with requests
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Working URLs: {len(working_urls)}")
    for url in working_urls:
        print(f"  - {url}")
    
    return working_urls

if __name__ == "__main__":
    test_koen_alternatives()