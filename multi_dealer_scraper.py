#!/usr/bin/env python3
import logging
import requests
from bs4 import BeautifulSoup
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BaseDealerScraper(ABC):
    """Base class for dealer-specific scrapers"""
    
    def __init__(self, dealer_name: str, base_url: str):
        self.dealer_name = dealer_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    @abstractmethod
    def get_inventory_url(self, page: int = 1) -> str:
        """Get URL for inventory page"""
        pass
    
    @abstractmethod
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        """Find car listing elements on the page"""
        pass
    
    @abstractmethod
    def extract_car_data(self, element) -> Optional[Dict]:
        """Extract car data from a single element"""
        pass
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape a single page and return car data"""
        try:
            logger.info(f"Scraping {self.dealer_name}: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to fetch {url}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            car_elements = self.find_car_elements(soup)
            
            logger.info(f"Found {len(car_elements)} car elements on {self.dealer_name}")
            
            cars = []
            for element in car_elements:
                car_data = self.extract_car_data(element)
                if car_data:
                    car_data['dealer_name'] = self.dealer_name
                    cars.append(car_data)
            
            return cars
            
        except Exception as e:
            logger.error(f"Error scraping {self.dealer_name}: {str(e)}")
            return []


class CarWorldClassicsScraper(BaseDealerScraper):
    """Scraper for CarWorld Classics"""
    
    def __init__(self):
        super().__init__("CarWorldClassics", "https://www.carworldclassics.com")
    
    def get_inventory_url(self, page: int = 1) -> str:
        if page == 1:
            return f"{self.base_url}/aanbod"
        return f"{self.base_url}/aanbod?page={page}"
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        return soup.find_all('div', {'class': 'each-product'})
    
    def extract_car_data(self, element) -> Optional[Dict]:
        try:
            # Extract car ID from the link URL (based on debug output)
            link = element.find('a', href=True)
            if not link:
                return None
            
            href = link['href']
            # Extract ID from URL like /occasions-kopen/43705952-porsche-911-...
            id_match = re.search(r'/occasions-kopen/(\d+)-', href)
            if not id_match:
                return None
            
            car_id = id_match.group(1)
            
            car_data = {
                'autotrack_id': car_id,
                'make': 'Unknown',
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'description': '',
                'image_url': None,
                'source_url': href,
                'price': 0
            }
            
            # Extract make and model from the structured content
            h6_element = element.find('h6')
            if h6_element:
                car_data['make'] = h6_element.get_text().strip()
            
            # Find the description paragraph
            p_element = element.find('p')
            if p_element:
                car_data['model'] = p_element.get_text().strip()
            
            # Extract price from the price column (col-5 text-end)
            price_col = element.find('div', {'class': ['col-5', 'text-end']})
            if price_col:
                price_h6 = price_col.find('h6')
                if price_h6:
                    price_text = price_h6.get_text().strip()
                    # Parse price like "€ 299.911,-"
                    price_match = re.search(r'€\s*([\d.]+)', price_text)
                    if price_match:
                        try:
                            # Remove dots and convert to int
                            price_str = price_match.group(1).replace('.', '')
                            car_data['price'] = int(price_str)
                        except ValueError:
                            pass
            
            # Extract mileage and year from the table
            table = element.find('table')
            if table:
                td_elements = table.find_all('td')
                if len(td_elements) >= 2:
                    # First td: mileage (e.g., "4.500 km")
                    mileage_text = td_elements[0].get_text().strip()
                    mileage_match = re.search(r'([\d.]+)', mileage_text)
                    if mileage_match:
                        try:
                            car_data['mileage'] = int(mileage_match.group(1).replace('.', ''))
                        except ValueError:
                            pass
                    
                    # Second td: year (e.g., "02-2025")
                    year_text = td_elements[1].get_text().strip()
                    year_match = re.search(r'(\d{4})', year_text)
                    if year_match:
                        try:
                            car_data['year'] = int(year_match.group(1))
                        except ValueError:
                            pass
            
            # Extract image
            img_element = element.find('img')
            if img_element and img_element.get('src'):
                car_data['image_url'] = img_element['src']
            
            # Only return if we have valid data
            if car_data['price'] > 0 and car_data['make'] != 'Unknown':
                return car_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting CarWorldClassics car data: {str(e)}")
            return None


class KoenExclusiefScraper(BaseDealerScraper):
    """Enhanced scraper for Koen Exclusief via Autowereld listing"""
    
    def __init__(self):
        super().__init__("KoenExclusief", "https://www.autowereld.nl")
    
    def get_inventory_url(self, page: int = 1) -> str:
        # Use the Autowereld page for Koen Exclusief with high limit
        return "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?il=100"
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Override scrape_page with WAF bypass using gradual approach"""
        try:
            logger.info(f"Scraping {self.dealer_name}: {url}")
            
            session = requests.Session()
            session.headers.update({
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
                'Cache-Control': 'max-age=0'
            })
            
            # WAF Bypass: Gradual approach
            import time
            
            # Step 1: Visit main site first to establish session
            try:
                logger.info("Establishing session with main site...")
                main_response = session.get("https://www.autowereld.nl", timeout=15)
                if main_response.status_code != 200:
                    logger.error(f"Main site failed: {main_response.status_code}")
                    return []
                time.sleep(2)
            except Exception as e:
                logger.error(f"Main site access failed: {str(e)}")
                return []
            
            # Step 2: Try dealer page variants
            session.headers['Referer'] = "https://www.autowereld.nl"
            
            dealer_urls = [
                # Original URL
                url,
                # Without query parameters
                url.split('?')[0],
                # Just dealer base
                "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/",
                # Alternative formats
                "https://www.autowereld.nl/aanbieder/1003233/auto.html"
            ]
            
            response = None
            for dealer_url in dealer_urls:
                try:
                    logger.info(f"Trying dealer URL: {dealer_url}")
                    response = session.get(dealer_url, timeout=15)
                    
                    if response.status_code == 200:
                        logger.info(f"Success with: {dealer_url}")
                        break
                    else:
                        logger.warning(f"Failed {dealer_url}: {response.status_code}")
                        time.sleep(3)
                        
                except Exception as e:
                    logger.warning(f"Error with {dealer_url}: {str(e)}")
                    time.sleep(3)
            
            if not response or response.status_code != 200:
                logger.error("All dealer URL attempts failed")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if content is loading via JavaScript
            aanbod_area = soup.find('div', class_='aanbod-list-area')
            if aanbod_area and 'Eén moment graag' in aanbod_area.get_text():
                logger.info("Detected JavaScript loading, waiting and retrying")
                
                # Wait and try again
                import time
                time.sleep(3)
                
                response = session.get(url, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # If still loading, look for pre-loaded car data elsewhere
                if 'Eén moment graag' in soup.get_text():
                    logger.info("Content still loading, looking for alternative car data")
                    
                    # Look for any Porsche links that might be pre-loaded
                    porsche_links = soup.find_all('a', href=re.compile(r'/occasions-kopen/.*porsche.*', re.I))
                    if porsche_links:
                        logger.info(f"Found {len(porsche_links)} Porsche links outside loading area")
                        
                        cars = []
                        for link in porsche_links[:5]:  # Limit to avoid processing too many
                            # Create a basic car entry from the link
                            href = link.get('href', '')
                            link_text = link.get_text().strip()
                            
                            # Extract car ID from URL
                            id_match = re.search(r'/occasions-kopen/(\d+)-', href)
                            if id_match:
                                car_id = id_match.group(1)
                                
                                # Basic car data from link
                                car_data = {
                                    'autotrack_id': car_id,
                                    'make': 'Porsche',
                                    'model': self._extract_porsche_model_from_url(href),
                                    'year': self._extract_year_from_url(href),
                                    'mileage': None,
                                    'fuel_type': 'Benzine',
                                    'description': link_text,
                                    'image_url': f"/webservices/feed_images/{car_id}/{car_id}-0.jpg",
                                    'source_url': href,
                                    'price': 0,
                                    'dealer_name': self.dealer_name
                                }
                                
                                cars.append(car_data)
                        
                        if cars:
                            logger.info(f"Extracted {len(cars)} cars from pre-loaded links")
                            return cars
            
            # Standard processing
            car_elements = self.find_car_elements(soup)
            logger.info(f"Found {len(car_elements)} car elements on {self.dealer_name}")
            
            cars = []
            for element in car_elements:
                car_data = self.extract_car_data(element)
                if car_data:
                    car_data['dealer_name'] = self.dealer_name
                    cars.append(car_data)
            
            return cars
            
        except Exception as e:
            logger.error(f"Error scraping {self.dealer_name}: {str(e)}")
            return []
    
    def _extract_porsche_model_from_url(self, url: str) -> str:
        """Extract Porsche model from URL"""
        url_lower = url.lower()
        
        # Common Porsche models
        models = {
            '911': '911',
            'carrera': '911 Carrera',
            'turbo': '911 Turbo', 
            'gt3': '911 GT3',
            'gts': 'GTS',
            'cayenne': 'Cayenne',
            'macan': 'Macan',
            'panamera': 'Panamera',
            'boxster': 'Boxster',
            'cayman': 'Cayman'
        }
        
        for key, model in models.items():
            if key in url_lower:
                return model
        
        return '911'  # Default for Porsche
    
    def _extract_year_from_url(self, url: str) -> Optional[int]:
        """Extract year from URL if present"""
        year_match = re.search(r'(\d{4})', url)
        if year_match:
            year = int(year_match.group(1))
            if 1990 <= year <= 2025:  # Reasonable year range
                return year
        return None
    
    def _try_ajax_endpoints(self, session: requests.Session) -> List[Dict]:
        """Try to fetch car data from potential AJAX endpoints"""
        logger.info("Attempting to find AJAX endpoints for dynamic car loading")
        
        # Since JavaScript loading was detected, try minimal AJAX approach
        ajax_endpoints = [
            "/load-more-products",
            "/api/aanbod",
            "/pages/load-aanbod"
        ]
        
        for endpoint in ajax_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = session.get(url, timeout=5)  # Shorter timeout
                
                if response.status_code == 200 and len(response.text) > 100:
                    content = response.text.lower()
                    if any(term in content for term in ['porsche', 'occasions-kopen', 'feed_images']):
                        logger.info(f"Found potential car content via AJAX: {endpoint}")
                        return []  # Return empty for now, structure detected
                        
            except:
                continue
        
        logger.info("No accessible AJAX endpoints found")
        return []
    
    def _extract_cars_from_html(self, soup):
        """Extract cars from HTML soup (helper for AJAX responses)"""
        car_elements = []
        
        # Look for the patterns from screenshot
        selectors = [
            'div.each_product_div',
            'div[class*="each_car_cls"]',
            'a[href*="occasions-kopen"][href*="porsche"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                car_elements.extend(elements)
        
        return car_elements[:10] if car_elements else []
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        # Based on the screenshot, look for the specific Autowereld structure
        # Look for divs with class containing "each_product_div" and "each_car_cls"
        car_elements = []
        
        # Primary selector: each_product_div with each_car_cls pattern
        specific_selectors = [
            'div[class*="each_product_div"][class*="each_car_cls"]',
            'div.each_product_div',
            'div[class*="each_car_cls"]'
        ]
        
        for selector in specific_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                
                # Validate these are actual car listings
                valid_cars = []
                for elem in elements:
                    # Check for occasions-kopen link and feed_images as seen in screenshot
                    has_occasions_link = elem.find('a', href=lambda x: x and 'occasions-kopen' in x)
                    has_feed_image = elem.find('img', src=lambda x: x and 'feed_images' in x)
                    has_car_text = any(term in elem.get_text().lower() for term in ['porsche', 'mercedes', 'bmw', 'audi'])
                    
                    if has_occasions_link or has_feed_image or has_car_text:
                        valid_cars.append(elem)
                
                if valid_cars:
                    logger.info(f"Validated {len(valid_cars)} car elements")
                    car_elements.extend(valid_cars)
        
        # If no specific elements found, try broader search
        if not car_elements:
            # Look for any div containing occasions-kopen links
            occasions_links = soup.find_all('a', href=lambda x: x and 'occasions-kopen' in x)
            logger.info(f"Found {len(occasions_links)} occasions-kopen links")
            
            for link in occasions_links:
                # Find the parent container that holds the car data
                container = link.find_parent('div')
                while container:
                    # Look for a container with substantial content
                    container_text = container.get_text().strip()
                    if (len(container_text) > 50 and 
                        any(term in container_text.lower() for term in ['porsche', 'mercedes', 'bmw', 'audi']) and
                        container not in car_elements):
                        car_elements.append(container)
                        break
                    container = container.find_parent('div')
        
        # Final fallback: look for feed_images containers
        if not car_elements:
            feed_images = soup.find_all('img', src=lambda x: x and 'feed_images' in x)
            logger.info(f"Found {len(feed_images)} feed_images")
            
            for img in feed_images:
                container = img.find_parent('div')
                while container and container not in car_elements:
                    container_text = container.get_text().strip()
                    if len(container_text) > 100:  # Substantial content
                        car_elements.append(container)
                        break
                    container = container.find_parent('div')
        
        logger.info(f"Total found {len(car_elements)} car elements")
        return car_elements
    
    def extract_car_data(self, element) -> Optional[Dict]:
        try:
            # Handle AJAX data (dict) vs HTML elements
            if isinstance(element, dict):
                return self._extract_from_ajax_data(element)
            else:
                return self._extract_from_html_element(element)
                
        except Exception as e:
            logger.error(f"Error extracting Koen Exclusief car data: {str(e)}")
            return None
    
    def _extract_from_ajax_data(self, data: Dict) -> Optional[Dict]:
        """Extract car data from AJAX JSON response"""
        try:
            car_data = {
                'autotrack_id': f"koen_ajax_{data.get('id', hash(str(data)) % 1000000)}",
                'make': 'Porsche',
                'model': data.get('model', 'Unknown'),
                'year': data.get('year'),
                'mileage': data.get('mileage') or data.get('km'),
                'fuel_type': data.get('fuel_type', 'Benzine'),
                'description': data.get('description', ''),
                'image_url': data.get('image_url') or data.get('image'),
                'source_url': data.get('url', ''),
                'price': data.get('price', 0)
            }
            
            # Handle various price formats
            if not car_data['price'] and 'prijs' in data:
                car_data['price'] = data['prijs']
            
            # Extract price from string if needed
            if isinstance(car_data['price'], str):
                price_match = re.search(r'([\d.,]+)', car_data['price'].replace('.', '').replace(',', ''))
                if price_match:
                    car_data['price'] = int(price_match.group(1))
            
            # Handle relative URLs
            if car_data['image_url'] and car_data['image_url'].startswith('/'):
                car_data['image_url'] = f"{self.base_url}{car_data['image_url']}"
            
            if car_data['source_url'] and car_data['source_url'].startswith('/'):
                car_data['source_url'] = f"{self.base_url}{car_data['source_url']}"
            
            return car_data if car_data['price'] > 0 else None
            
        except Exception as e:
            logger.error(f"Error processing AJAX car data: {str(e)}")
            return None
    
    def _extract_from_html_element(self, element) -> Optional[Dict]:
        """Extract car data from Autowereld HTML element"""
        try:
            text_content = element.get_text()
            elem_html = str(element)
            
            # Initialize car data
            car_data = {
                'autotrack_id': '',
                'make': 'Unknown',
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'description': text_content.strip()[:200],
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Extract car ID from any links
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                # Look for ID patterns in URLs
                id_match = re.search(r'(\d{6,})', href)
                if id_match:
                    car_data['autotrack_id'] = f"autowereld_{id_match.group(1)}"
                    if href.startswith('/'):
                        car_data['source_url'] = f"https://www.autowereld.nl{href}"
                    else:
                        car_data['source_url'] = href
                    break
            
            # If no ID found, generate from content hash
            if not car_data['autotrack_id']:
                car_data['autotrack_id'] = f"autowereld_{abs(hash(text_content[:100]))}"[:12]
            
            # Extract make and model from text
            text_lower = text_content.lower()
            
            # Common makes detection
            makes = {
                'porsche': 'Porsche',
                'mercedes': 'Mercedes-Benz', 
                'bmw': 'BMW',
                'audi': 'Audi',
                'volkswagen': 'Volkswagen',
                'ford': 'Ford',
                'toyota': 'Toyota',
                'peugeot': 'Peugeot',
                'renault': 'Renault',
                'opel': 'Opel'
            }
            
            # Find make
            for key, value in makes.items():
                if key in text_lower:
                    car_data['make'] = value
                    break
            
            # Extract Porsche models specifically (since this is KoenExclusief)
            if car_data['make'] == 'Porsche':
                porsche_models = ['911', 'carrera', 'turbo', 'gt3', 'gts', 'cayenne', 'macan', 'panamera', 'boxster', 'cayman']
                for model_name in porsche_models:
                    if model_name in text_lower:
                        if model_name == '911':
                            car_data['model'] = '911'
                        else:
                            car_data['model'] = model_name.title()
                        break
            
            # Extract specific model from common Porsche naming patterns
            if '911' in text_lower:
                car_data['model'] = '911'
                # Look for specific 911 variants
                if 'carrera' in text_lower:
                    if 'gts' in text_lower:
                        car_data['model'] = '911 Carrera GTS'
                    elif 'turbo' in text_lower:
                        car_data['model'] = '911 Turbo'
                    else:
                        car_data['model'] = '911 Carrera'
                elif 'turbo' in text_lower:
                    car_data['model'] = '911 Turbo'
                elif 'gt3' in text_lower:
                    car_data['model'] = '911 GT3'
            elif 'cayenne' in text_lower:
                car_data['model'] = 'Cayenne'
            elif 'macan' in text_lower:
                car_data['model'] = 'Macan'
            elif 'panamera' in text_lower:
                car_data['model'] = 'Panamera'
            elif 'taycan' in text_lower:
                car_data['model'] = 'Taycan'
            elif 'boxster' in text_lower:
                car_data['model'] = 'Boxster'
            elif 'cayman' in text_lower:
                car_data['model'] = 'Cayman'
            
            # Extract year - look for 4-digit years
            year_match = re.search(r'\b(19[8-9]\d|20[0-2]\d)\b', text_content)
            if year_match:
                car_data['year'] = int(year_match.group(1))
            
            # Extract price - be more flexible with pricing
            price_patterns = [
                r'€\s*([\d.,]+)',
                r'([\d.,]+)\s*€',
                r'\b(\d{5,})\b',  # At least 5 digits
            ]
            
            for pattern in price_patterns:
                price_matches = re.findall(pattern, text_content.replace('.', '').replace(',', ''))
                for match in price_matches:
                    try:
                        price_value = int(match)
                        if 15000 <= price_value <= 2000000:  # Reasonable range for Porsche
                            car_data['price'] = price_value
                            break
                    except ValueError:
                        continue
                if car_data['price'] > 0:
                    break
            
            # Extract mileage
            mileage_patterns = [
                r'([\d.,]+)\s*km',
                r'([\d.,]+)\s*KM',
                r'([\d.,]+)\s*kilometer'
            ]
            
            for pattern in mileage_patterns:
                mileage_match = re.search(pattern, text_content.replace('.', '').replace(',', ''))
                if mileage_match:
                    try:
                        mileage_value = int(mileage_match.group(1))
                        if 0 <= mileage_value <= 500000:
                            car_data['mileage'] = mileage_value
                            break
                    except ValueError:
                        continue
            
            # Extract image from feed_images pattern
            img = element.find('img', src=re.compile(r'/webservices/feed_images/'))
            if img:
                car_data['image_url'] = f"{self.base_url}{img['src']}"
            else:
                # Fallback to any img
                img = element.find('img')
                if img and img.get('src'):
                    src = img['src']
                    if src.startswith('/'):
                        car_data['image_url'] = f"{self.base_url}{src}"
                    elif src.startswith('http'):
                        car_data['image_url'] = src
            
            # Extract occasions link
            if link:
                href = link['href']
                if href.startswith('/'):
                    car_data['source_url'] = f"{self.base_url}{href}"
                else:
                    car_data['source_url'] = href
            
            # Create description from meaningful text
            clean_text = ' '.join(text_content.split())
            car_data['description'] = clean_text[:500]
            
            # More lenient validation - accept if we have Porsche content
            has_porsche_content = any(term in text_lower for term in ['porsche', '911', 'carrera', 'turbo'])
            has_meaningful_content = len(clean_text.strip()) > 20
            
            if has_porsche_content and has_meaningful_content:
                logger.info(f"Extracted KoenExclusief car: {car_data['make']} {car_data['model']} ({car_data['year']}) - {car_data['price']}")
                return car_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting HTML car data: {str(e)}")
            return None


class MultiDealerScraper:
    """Main scraper that coordinates multiple dealers"""
    
    def __init__(self, database):
        self.database = database
        self.dealers = [
            CarWorldClassicsScraper(),
            KoenExclusiefScraper()
        ]
    
    def scrape_all_dealers(self):
        """Scrape all configured dealers"""
        total_new = 0
        total_updated = 0
        
        for dealer_scraper in self.dealers:
            new_cars, updated_cars = self.scrape_dealer(dealer_scraper)
            total_new += new_cars
            total_updated += updated_cars
        
        logger.info(f"Multi-dealer scraping completed. New cars: {total_new}, Updated: {total_updated}")
        return total_new, total_updated
    
    def scrape_dealer(self, dealer_scraper: BaseDealerScraper):
        """Scrape a specific dealer"""
        logger.info(f"Starting scrape for {dealer_scraper.dealer_name}")
        
        new_cars = 0
        updated_cars = 0
        current_car_ids = []
        seen_car_ids = set()
        page = 1
        
        try:
            while True:
                url = dealer_scraper.get_inventory_url(page)
                cars_on_page = dealer_scraper.scrape_page(url)
                
                if not cars_on_page:
                    logger.info(f"No cars found on page {page} for {dealer_scraper.dealer_name}")
                    break
                
                # Check for duplicates
                new_cars_on_page = 0
                for car_data in cars_on_page:
                    car_key = f"{car_data['autotrack_id']}_{dealer_scraper.dealer_name}"
                    if car_key not in seen_car_ids:
                        new_cars_on_page += 1
                        seen_car_ids.add(car_key)
                
                if new_cars_on_page == 0:
                    logger.info(f"No new cars on page {page} for {dealer_scraper.dealer_name}, stopping")
                    break
                
                # Process cars
                for car_data in cars_on_page:
                    current_car_ids.append(car_data['autotrack_id'])
                    
                    existing_car = self.database.get_car_by_autotrack_id(
                        car_data['autotrack_id'], dealer_scraper.dealer_name
                    )
                    
                    if existing_car:
                        if existing_car['current_price'] != car_data['price']:
                            self.database.update_car_price(existing_car['id'], car_data['price'])
                            updated_cars += 1
                            logger.info(f"Updated price for {dealer_scraper.dealer_name} car {car_data['autotrack_id']}")
                        
                        self.database.update_car_last_seen(existing_car['id'])
                    else:
                        self.database.add_car(car_data)
                        new_cars += 1
                        logger.info(f"Added new car from {dealer_scraper.dealer_name}: {car_data['make']} {car_data['model']}")
                
                page += 1
                if page > 10:  # Safety limit
                    break
            
            # Mark cars as sold for this dealer
            if current_car_ids:
                self.database.mark_cars_as_sold(current_car_ids, dealer_scraper.dealer_name)
            
        except Exception as e:
            logger.error(f"Error scraping {dealer_scraper.dealer_name}: {str(e)}")
        
        logger.info(f"Completed {dealer_scraper.dealer_name}: {new_cars} new, {updated_cars} updated")
        return new_cars, updated_cars