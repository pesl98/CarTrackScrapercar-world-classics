#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def test_koen_alternatives():
    """Test various alternative sources for KoenExclusief data"""
    url = "https://koenexclusief.nl/aanbod"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== TESTING ALTERNATIVE KOEN EXCLUSIEF APPROACHES ===")
        
        # 1. Look for any Porsche links anywhere on the page
        all_porsche_links = soup.find_all('a', href=re.compile(r'porsche', re.I))
        print(f"Found {len(all_porsche_links)} links containing 'porsche'")
        
        for i, link in enumerate(all_porsche_links[:5]):
            href = link.get('href', '')
            text = link.get_text().strip()
            print(f"  Link {i+1}: {href[:80]} - {text[:50]}")
        
        # 2. Look for occasions-kopen links specifically
        occasions_links = soup.find_all('a', href=re.compile(r'/occasions-kopen/', re.I))
        print(f"\nFound {len(occasions_links)} occasions-kopen links")
        
        for i, link in enumerate(occasions_links[:5]):
            href = link.get('href', '')
            text = link.get_text().strip()
            print(f"  Occasions {i+1}: {href[:80]} - {text[:50]}")
        
        # 3. Look for feed_images anywhere
        feed_images = soup.find_all('img', src=re.compile(r'/webservices/feed_images/', re.I))
        print(f"\nFound {len(feed_images)} feed_images")
        
        for i, img in enumerate(feed_images[:3]):
            src = img.get('src', '')
            alt = img.get('alt', '')
            print(f"  Image {i+1}: {src[:80]} - {alt[:30]}")
        
        # 4. Look for specific car model text in the HTML
        html_text = soup.get_text().lower()
        car_models = ['911', 'carrera', 'turbo', 'cayenne', 'macan', 'panamera']
        
        print(f"\nCar model mentions in page text:")
        for model in car_models:
            count = html_text.count(model)
            print(f"  {model}: {count} mentions")
        
        # 5. Look for any JavaScript that might load cars
        scripts = soup.find_all('script')
        print(f"\nFound {len(scripts)} script tags")
        
        for i, script in enumerate(scripts):
            script_content = script.get_text() if script.string else ""
            if any(term in script_content.lower() for term in ['ajax', 'load', 'car', 'aanbod', 'product']):
                print(f"  Script {i+1} contains car/loading related terms")
                if 'ajax' in script_content.lower():
                    # Look for URLs in the script
                    urls = re.findall(r'["\']([^"\']*(?:load|fetch|get|api)[^"\']*)["\']', script_content)
                    for url in urls[:3]:
                        print(f"    Potential endpoint: {url}")
        
        # 6. Check specific div classes that might contain data
        potential_containers = soup.find_all('div', class_=re.compile(r'.*(?:car|product|item|listing).*', re.I))
        print(f"\nFound {len(potential_containers)} divs with car/product related classes")
        
        for i, div in enumerate(potential_containers[:5]):
            classes = div.get('class', [])
            text = div.get_text().strip()[:100]
            print(f"  Container {i+1}: {classes} - {text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_koen_alternatives()