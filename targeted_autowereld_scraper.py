#!/usr/bin/env python3
"""
Targeted scraper for Autowereld using successful WAF bypass approach
"""
import requests
import time
import random
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_bypass_session():
    """Create session with successful bypass configuration"""
    session = requests.Session()
    
    # Use headers that successfully bypassed WAF
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    session.headers.update(headers)
    session.verify = False
    session.timeout = 30
    
    return session

def discover_site_structure():
    """Discover the actual site structure and find correct URLs"""
    print("Discovering Autowereld site structure...")
    
    session = create_bypass_session()
    
    # Start with main page
    try:
        response = session.get("https://www.autowereld.nl", timeout=30)
        print(f"Main page status: {response.status_code}")
        
        if response.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for navigation links to understand site structure
        nav_links = soup.find_all('a', href=True)
        dealer_urls = []
        search_urls = []
        
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text().lower()
            
            # Look for dealer-related links
            if any(term in href.lower() for term in ['dealer', 'aanbieder', 'verkoper']):
                full_url = href if href.startswith('http') else f"https://www.autowereld.nl{href}"
                dealer_urls.append(full_url)
                print(f"Found dealer link: {full_url}")
            
            # Look for search-related links
            if any(term in text for term in ['zoek', 'search', 'auto']) and 'href' in link.attrs:
                full_url = href if href.startswith('http') else f"https://www.autowereld.nl{href}"
                search_urls.append(full_url)
                print(f"Found search link: {full_url}")
        
        return dealer_urls, search_urls
        
    except Exception as e:
        print(f"Error discovering structure: {e}")
        return None, None

def try_direct_dealer_access():
    """Try to access the dealer page using discovered structure"""
    print("Attempting direct dealer access...")
    
    session = create_bypass_session()
    
    # Try different dealer ID formats based on the URL pattern
    dealer_patterns = [
        "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233",
        "https://www.autowereld.nl/dealer/1003233",
        "https://www.autowereld.nl/dealers/1003233",
        "https://www.autowereld.nl/aanbieder/1003233"
    ]
    
    for url in dealer_patterns:
        try:
            print(f"Trying dealer URL: {url}")
            
            # Set proper referer
            session.headers['Referer'] = "https://www.autowereld.nl"
            response = session.get(url, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("Success! Found working dealer page")
                return analyze_dealer_page(response, session)
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    return None

def analyze_dealer_page(response, session):
    """Analyze successful dealer page response"""
    print("Analyzing dealer page content...")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for car listing links or AJAX endpoints
    cars_found = []
    
    # Method 1: Look for direct car links
    car_links = soup.find_all('a', href=lambda x: x and any(term in x for term in ['auto', 'occasions', 'voertuig']))
    print(f"Found {len(car_links)} potential car links")
    
    for link in car_links[:10]:  # Limit to 10
        href = link.get('href')
        text = link.get_text().strip()
        
        if href and text:
            full_url = href if href.startswith('http') else f"https://www.autowereld.nl{href}"
            print(f"Car link: {text[:50]}... -> {full_url}")
            
            # Try to extract basic info
            car_data = extract_basic_car_info(text, full_url)
            if car_data:
                cars_found.append(car_data)
    
    # Method 2: Look for AJAX/JSON endpoints in page source
    page_text = response.text
    ajax_patterns = [
        r'/api/[^"\']*',
        r'/ajax/[^"\']*', 
        r'/json/[^"\']*',
        r'\.json[^"\']*',
        r'dealer[^"\']*\.php',
        r'vehicles[^"\']*\.php'
    ]
    
    for pattern in ajax_patterns:
        matches = re.findall(pattern, page_text)
        for match in matches:
            print(f"Found potential AJAX endpoint: {match}")
            
            # Try to access it
            ajax_url = match if match.startswith('http') else f"https://www.autowereld.nl{match}"
            cars_from_ajax = try_ajax_endpoint(ajax_url, session)
            if cars_from_ajax:
                cars_found.extend(cars_from_ajax)
    
    # Method 3: Look for embedded JSON data
    script_tags = soup.find_all('script')
    for script in script_tags:
        script_content = script.string or ''
        
        # Look for JSON data that might contain car info
        if any(term in script_content.lower() for term in ['vehicles', 'cars', 'auto', 'porsche']):
            print(f"Found potential car data in script: {script_content[:100]}...")
            
            # Try to extract JSON
            json_matches = re.findall(r'\{[^}]*(?:auto|car|vehicle|porsche)[^}]*\}', script_content, re.IGNORECASE)
            for json_str in json_matches:
                try:
                    # Simple parsing attempt
                    if 'porsche' in json_str.lower():
                        print(f"Found Porsche data: {json_str}")
                except:
                    pass
    
    print(f"Total cars found: {len(cars_found)}")
    return cars_found

def try_ajax_endpoint(url, session):
    """Try to access AJAX endpoint for car data"""
    try:
        # Set AJAX headers
        ajax_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = session.get(url, headers=ajax_headers, timeout=10)
        print(f"AJAX {url}: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Successfully parsed JSON from {url}")
                return extract_cars_from_json(data)
            except:
                # Not JSON, but might contain useful data
                if any(term in response.text.lower() for term in ['porsche', 'auto', 'car']):
                    print(f"Found car-related content in {url}")
        
    except Exception as e:
        print(f"AJAX error for {url}: {e}")
    
    return []

def extract_cars_from_json(data):
    """Extract car data from JSON response"""
    cars = []
    
    # Handle different JSON structures
    if isinstance(data, list):
        for item in data:
            car = extract_car_from_json_item(item)
            if car:
                cars.append(car)
    elif isinstance(data, dict):
        # Look for car arrays in common key names
        for key in ['cars', 'vehicles', 'items', 'data', 'results']:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    car = extract_car_from_json_item(item)
                    if car:
                        cars.append(car)
    
    return cars

def extract_car_from_json_item(item):
    """Extract car data from a single JSON item"""
    if not isinstance(item, dict):
        return None
    
    # Look for car-related fields
    car_data = {
        'autotrack_id': '',
        'make': 'Unknown',
        'model': 'Unknown',
        'year': None,
        'price': 0,
        'mileage': None,
        'fuel_type': None,
        'description': '',
        'image_url': None,
        'source_url': '',
        'dealer_name': 'KoenExclusief'
    }
    
    # Map common field names
    field_mappings = {
        'id': 'autotrack_id',
        'make': 'make',
        'brand': 'make', 
        'model': 'model',
        'year': 'year',
        'price': 'price',
        'mileage': 'mileage',
        'km': 'mileage',
        'fuel': 'fuel_type',
        'description': 'description',
        'image': 'image_url',
        'url': 'source_url'
    }
    
    for json_key, car_key in field_mappings.items():
        if json_key in item:
            car_data[car_key] = item[json_key]
    
    # Only return if we have meaningful data
    if car_data['make'] != 'Unknown' or car_data['price'] > 0:
        return car_data
    
    return None

def extract_basic_car_info(text, url):
    """Extract basic car info from text and URL"""
    car_data = {
        'autotrack_id': '',
        'make': 'Unknown',
        'model': 'Unknown',
        'year': None,
        'price': 0,
        'mileage': None,
        'fuel_type': None,
        'description': text,
        'image_url': None,
        'source_url': url,
        'dealer_name': 'KoenExclusief'
    }
    
    # Extract ID from URL
    id_match = re.search(r'(\d{6,})', url)
    if id_match:
        car_data['autotrack_id'] = f"autowereld_{id_match.group(1)}"
    
    # Look for make/model in text
    if 'porsche' in text.lower():
        car_data['make'] = 'Porsche'
        
        if '911' in text:
            car_data['model'] = '911'
        elif 'cayenne' in text.lower():
            car_data['model'] = 'Cayenne'
        elif 'macan' in text.lower():
            car_data['model'] = 'Macan'
    
    # Look for price
    price_match = re.search(r'€\s*([\d.,]+)', text)
    if price_match:
        try:
            price_str = price_match.group(1).replace('.', '').replace(',', '')
            car_data['price'] = int(price_str)
        except:
            pass
    
    # Look for year
    year_match = re.search(r'(20\d{2})', text)
    if year_match:
        car_data['year'] = int(year_match.group(1))
    
    return car_data if car_data['make'] != 'Unknown' else None

def main():
    """Main execution function"""
    print("=== Targeted Autowereld Scraper ===")
    
    # Step 1: Discover site structure
    dealer_urls, search_urls = discover_site_structure()
    
    # Step 2: Try direct dealer access
    cars = try_direct_dealer_access()
    
    if cars:
        print(f"\n=== SUCCESS: Found {len(cars)} cars ===")
        for i, car in enumerate(cars[:5], 1):
            print(f"\nCar {i}:")
            print(f"  ID: {car['autotrack_id']}")
            print(f"  Make/Model: {car['make']} {car['model']}")
            print(f"  Year: {car['year']}")
            print(f"  Price: €{car['price']:,}" if car['price'] else "No price")
            print(f"  URL: {car['source_url']}")
    else:
        print("No cars found with current approach")
    
    return cars

if __name__ == "__main__":
    main()