#!/usr/bin/env python3
"""
Advanced scraper for Autowereld using WAF bypass techniques
"""
import requests
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedAutoWereldScraper:
    """Advanced scraper with WAF bypass capabilities"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://www.autowereld.nl"
        self.target_url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?il=100"
        
        # Rotate through realistic user agents
        self.user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            # Chrome Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Safari Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Real IP ranges from Netherlands (to appear local)
        self.nl_ips = [
            '145.131.0.1',    # Academic network
            '213.75.0.1',     # KPN
            '84.241.0.1',     # Ziggo
            '217.121.0.1',    # T-Mobile
            '195.169.0.1'     # SURF
        ]
    
    def create_session(self):
        """Create a session with advanced anti-detection measures"""
        self.session = requests.Session()
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        
        # Comprehensive headers that mimic real browser
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8,en-US;q=0.7',
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
            'sec-ch-ua-platform': '"Windows"',
            'Pragma': 'no-cache'
        }
        
        # Add X-Forwarded-For with Dutch IP (appear local)
        headers['X-Forwarded-For'] = random.choice(self.nl_ips)
        headers['X-Real-IP'] = random.choice(self.nl_ips)
        
        self.session.headers.update(headers)
        
        # Configure session for robustness
        self.session.verify = False  # Skip SSL verification if needed
        self.session.timeout = 30
        
        # Add some realistic cookies
        self.session.cookies.update({
            'accept_cookies': '1',
            'language': 'nl',
            'timezone': 'Europe/Amsterdam'
        })
    
    def human_like_delay(self):
        """Add human-like random delays"""
        delay = random.uniform(2, 8)  # 2-8 seconds
        time.sleep(delay)
    
    def try_gradual_approach(self):
        """Gradually approach the target by visiting related pages first"""
        print("Attempting gradual approach to bypass WAF...")
        
        # Step 1: Visit main site
        try:
            print("1. Visiting main site...")
            response = self.session.get("https://www.autowereld.nl", timeout=30)
            print(f"Main site status: {response.status_code}")
            self.human_like_delay()
            
            if response.status_code != 200:
                return False
                
        except Exception as e:
            print(f"Main site failed: {e}")
            return False
        
        # Step 2: Try search page first
        try:
            print("2. Visiting search page...")
            search_url = "https://www.autowereld.nl/zoeken"
            self.session.headers['Referer'] = "https://www.autowereld.nl"
            response = self.session.get(search_url, timeout=30)
            print(f"Search page status: {response.status_code}")
            self.human_like_delay()
            
        except Exception as e:
            print(f"Search page failed: {e}")
        
        # Step 3: Try dealer search
        try:
            print("3. Trying dealer search...")
            dealer_search = "https://www.autowereld.nl/dealers"
            self.session.headers['Referer'] = "https://www.autowereld.nl/zoeken"
            response = self.session.get(dealer_search, timeout=30)
            print(f"Dealer search status: {response.status_code}")
            self.human_like_delay()
            
        except Exception as e:
            print(f"Dealer search failed: {e}")
        
        # Step 4: Now try the actual target
        try:
            print("4. Attempting target URL...")
            self.session.headers['Referer'] = "https://www.autowereld.nl/dealers"
            response = self.session.get(self.target_url, timeout=30)
            print(f"Target URL status: {response.status_code}")
            
            if response.status_code == 200:
                return response
            
        except Exception as e:
            print(f"Target URL failed: {e}")
        
        return False
    
    def try_different_endpoints(self):
        """Try different URL variations that might not be blocked"""
        print("Trying alternative endpoints...")
        
        alternatives = [
            # Try without query parameters
            "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",
            # Try just the dealer page
            "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/",
            # Try with different parameters
            "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?page=1",
            "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?limit=50",
        ]
        
        for url in alternatives:
            try:
                print(f"Trying: {url}")
                self.session.headers['Referer'] = "https://www.autowereld.nl/dealers"
                response = self.session.get(url, timeout=30)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("Success with alternative endpoint!")
                    return response
                
                self.human_like_delay()
                
            except Exception as e:
                print(f"Failed: {e}")
        
        return None
    
    def try_mobile_approach(self):
        """Try using mobile user agent which may have less strict filtering"""
        print("Trying mobile user agent approach...")
        
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Create new session with mobile headers
        mobile_session = requests.Session()
        mobile_session.headers.update(mobile_headers)
        mobile_session.verify = False
        
        try:
            # Try mobile version URL patterns
            mobile_urls = [
                self.target_url,
                self.target_url.replace('www.', 'm.'),  # Try mobile subdomain
                self.target_url + '&mobile=1'  # Try mobile parameter
            ]
            
            for url in mobile_urls:
                response = mobile_session.get(url, timeout=30)
                print(f"Mobile attempt {url}: {response.status_code}")
                
                if response.status_code == 200:
                    return response
                
                time.sleep(3)
        
        except Exception as e:
            print(f"Mobile approach failed: {e}")
        
        return None
    
    def try_api_endpoints(self):
        """Look for API endpoints that might not be protected"""
        print("Searching for unprotected API endpoints...")
        
        # Common API patterns for car listings
        api_patterns = [
            "/api/vehicles",
            "/api/cars",
            "/api/dealer/1003233/vehicles",
            "/api/aanbieder/1003233",
            "/ajax/cars",
            "/json/vehicles",
            "/ws/dealer/cars"
        ]
        
        for pattern in api_patterns:
            try:
                api_url = self.base_url + pattern
                print(f"Trying API: {api_url}")
                
                # Try with API headers
                api_headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://www.autowereld.nl/dealers'
                }
                
                response = self.session.get(api_url, headers=api_headers, timeout=10)
                print(f"API status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"Found JSON API endpoint with data: {len(data) if isinstance(data, list) else 'object'}")
                        return response
                    except:
                        print("Not JSON, but 200 response")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"API {pattern} failed: {e}")
        
        return None
    
    def scrape_with_bypass(self):
        """Main scraping method with multiple bypass techniques"""
        print("Starting advanced Autowereld scraping with WAF bypass...")
        
        for attempt in range(3):  # Try up to 3 different sessions
            print(f"\n=== Attempt {attempt + 1} ===")
            
            # Create fresh session for each attempt
            self.create_session()
            
            # Try different approaches in order of sophistication
            approaches = [
                self.try_gradual_approach,
                self.try_different_endpoints,
                self.try_mobile_approach,
                self.try_api_endpoints
            ]
            
            for approach in approaches:
                try:
                    result = approach()
                    if result and hasattr(result, 'status_code') and result.status_code == 200:
                        print(f"\nSuccess with {approach.__name__}!")
                        return self.extract_cars_from_response(result)
                    
                    # Random delay between approaches
                    time.sleep(random.uniform(5, 15))
                    
                except Exception as e:
                    print(f"Approach {approach.__name__} failed: {e}")
            
            print(f"Attempt {attempt + 1} failed, waiting before retry...")
            time.sleep(random.uniform(30, 60))  # Longer delay between attempts
        
        print("All bypass attempts failed")
        return []
    
    def extract_cars_from_response(self, response):
        """Extract car data from successful response"""
        print("Extracting car data from response...")
        
        try:
            # Check if it's JSON
            if 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                print("Processing JSON response")
                return self.extract_from_json(data)
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"Processing HTML response ({len(response.text)} chars)")
            
            # Look for car listings using the patterns we identified
            cars = []
            
            # Try the specific structure we saw in the screenshot
            car_elements = soup.select('div[class*="each_product_div"]')
            print(f"Found {len(car_elements)} product divs")
            
            if not car_elements:
                # Fallback: look for any car-related links
                car_links = soup.find_all('a', href=lambda x: x and 'occasions-kopen' in x)
                print(f"Fallback: found {len(car_links)} occasion links")
                
                for link in car_links[:10]:  # Limit to 10
                    car_data = self.extract_from_link(link)
                    if car_data:
                        cars.append(car_data)
            
            else:
                # Process the specific product divs
                for element in car_elements:
                    car_data = self.extract_from_element(element)
                    if car_data:
                        cars.append(car_data)
            
            print(f"Successfully extracted {len(cars)} cars")
            return cars
            
        except Exception as e:
            print(f"Error extracting cars: {e}")
            return []
    
    def extract_from_json(self, data):
        """Extract cars from JSON API response"""
        cars = []
        # Implementation depends on JSON structure
        # This would need to be adapted based on actual API response
        return cars
    
    def extract_from_element(self, element):
        """Extract car data from HTML element"""
        try:
            text = element.get_text()
            
            # Basic extraction
            car_data = {
                'autotrack_id': f"autowereld_{abs(hash(str(element)))}"[:12],
                'make': 'Unknown',
                'model': 'Unknown',
                'year': None,
                'price': 0,
                'mileage': None,
                'fuel_type': None,
                'description': text.strip()[:200],
                'image_url': None,
                'source_url': '',
                'dealer_name': 'KoenExclusief'
            }
            
            # Extract specific data (simplified for now)
            import re
            
            # Look for Porsche
            if 'porsche' in text.lower():
                car_data['make'] = 'Porsche'
                
                # Look for 911
                if '911' in text:
                    car_data['model'] = '911'
            
            # Look for price
            price_match = re.search(r'€\s*([\d.,]+)', text)
            if price_match:
                price_str = price_match.group(1).replace('.', '').replace(',', '')
                try:
                    car_data['price'] = int(price_str)
                except:
                    pass
            
            # Look for year
            year_match = re.search(r'(20\d{2})', text)
            if year_match:
                car_data['year'] = int(year_match.group(1))
            
            return car_data if car_data['make'] != 'Unknown' else None
            
        except Exception as e:
            print(f"Error extracting from element: {e}")
            return None
    
    def extract_from_link(self, link):
        """Extract basic car data from a link"""
        try:
            href = link.get('href', '')
            text = link.get_text()
            
            # Extract ID from URL
            import re
            id_match = re.search(r'/occasions-kopen/(\d+)', href)
            if not id_match:
                return None
            
            car_data = {
                'autotrack_id': f"autowereld_{id_match.group(1)}",
                'make': 'Unknown',
                'model': 'Unknown',
                'year': None,
                'price': 0,
                'mileage': None,
                'fuel_type': None,
                'description': text.strip(),
                'image_url': None,
                'source_url': href if href.startswith('http') else f"https://www.autowereld.nl{href}",
                'dealer_name': 'KoenExclusief'
            }
            
            # Basic extraction from link text
            if 'porsche' in text.lower():
                car_data['make'] = 'Porsche'
                if '911' in text:
                    car_data['model'] = '911'
            
            return car_data if car_data['make'] != 'Unknown' else None
            
        except Exception as e:
            print(f"Error extracting from link: {e}")
            return None

def test_advanced_scraper():
    """Test the advanced scraper"""
    scraper = AdvancedAutoWereldScraper()
    cars = scraper.scrape_with_bypass()
    
    print(f"\n=== RESULTS ===")
    print(f"Found {len(cars)} cars")
    
    for i, car in enumerate(cars[:5], 1):
        print(f"\nCar {i}:")
        print(f"  ID: {car['autotrack_id']}")
        print(f"  Make/Model: {car['make']} {car['model']}")
        print(f"  Year: {car['year']}")
        print(f"  Price: €{car['price']:,}" if car['price'] else "No price")
        print(f"  Description: {car['description'][:100]}...")
    
    return cars

if __name__ == "__main__":
    test_advanced_scraper()