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
    """Enhanced scraper for Koen Exclusief with AJAX support"""
    
    def __init__(self):
        super().__init__("KoenExclusief", "https://koenexclusief.nl")
    
    def get_inventory_url(self, page: int = 1) -> str:
        if page == 1:
            return f"{self.base_url}/aanbod"
        return f"{self.base_url}/aanbod?page={page}"
    
    def _try_ajax_endpoints(self, session: requests.Session) -> List[Dict]:
        """Try to fetch car data from potential AJAX endpoints"""
        ajax_endpoints = [
            "/pages/fetch-related-data",
            "/pages/find-autodata-vehicle-data",
            "/api/cars",
            "/api/aanbod",
            "/data/cars.json"
        ]
        
        for endpoint in ajax_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = session.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            logger.info(f"Found {len(data)} cars via AJAX endpoint: {endpoint}")
                            return data
                        elif isinstance(data, dict) and 'cars' in data:
                            cars = data['cars']
                            logger.info(f"Found {len(cars)} cars via AJAX endpoint: {endpoint}")
                            return cars
                    except:
                        # Not JSON, continue
                        pass
            except:
                continue
        
        return []
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        # Based on screenshot, look for specific KoenExclusief structure
        # Primary selectors from actual HTML structure
        primary_selectors = [
            'div.each_product_div',
            'div[class*="each_car_cls"]',
            'div.col-lg-6.each_product_div',
        ]
        
        car_elements = []
        for selector in primary_selectors:
            elements = soup.select(selector)
            if elements:
                # Filter for actual car listings (must contain Porsche content)
                valid_cars = []
                for elem in elements:
                    elem_text = elem.get_text().lower()
                    
                    # Check for car indicators from screenshot structure
                    has_car_link = elem.find('a', href=re.compile(r'/occasions-kopen/.*porsche.*', re.I))
                    has_car_image = elem.find('img', src=re.compile(r'/webservices/feed_images/'))
                    has_porsche_text = any(term in elem_text for term in ['porsche', '911', 'carrera', 'turbo'])
                    
                    if has_car_link or has_car_image or has_porsche_text:
                        valid_cars.append(elem)
                
                if valid_cars:
                    logger.info(f"Found {len(valid_cars)} car elements using selector: {selector}")
                    return valid_cars
        
        # Secondary approach: look for feed_images (car photos)
        feed_images = soup.find_all('img', src=re.compile(r'/webservices/feed_images/\d+/'))
        if feed_images:
            logger.info(f"Found {len(feed_images)} car images, extracting containers")
            car_containers = []
            
            for img in feed_images:
                # Find parent container that holds the car data
                container = img.find_parent('div', class_=re.compile(r'.*product.*|.*car.*|.*each.*'))
                if container and container not in car_containers:
                    car_containers.append(container)
            
            if car_containers:
                logger.info(f"Extracted {len(car_containers)} car containers from images")
                return car_containers
        
        # Tertiary approach: look for occasions links
        occasions_links = soup.find_all('a', href=re.compile(r'/occasions-kopen/.*porsche.*', re.I))
        if occasions_links:
            logger.info(f"Found {len(occasions_links)} occasions links")
            car_containers = []
            
            for link in occasions_links:
                # Find parent container
                container = link.find_parent(['div'], class_=True)
                if container and container not in car_containers:
                    car_containers.append(container)
            
            if car_containers:
                logger.info(f"Extracted {len(car_containers)} car containers from links")
                return car_containers
        
        # Final fallback: look for any divs containing Porsche and price info
        all_divs = soup.find_all('div')
        car_containers = []
        
        for div in all_divs:
            div_text = div.get_text().lower()
            div_classes = ' '.join(div.get('class', []))
            
            # Check for Porsche content and pricing
            has_porsche = any(model in div_text for model in ['porsche', '911', 'carrera', 'turbo', 'cayenne', 'macan'])
            has_price_info = any(indicator in div_text for indicator in ['€', 'eur', 'carrera', 'achterassturing'])
            has_reasonable_content = len(div_text.strip()) > 50
            
            if has_porsche and has_price_info and has_reasonable_content:
                car_containers.append(div)
        
        # Remove duplicates and nested containers
        unique_containers = []
        for container in car_containers:
            # Check if this container is not contained within another
            is_nested = any(container in other.descendants for other in unique_containers)
            if not is_nested:
                unique_containers.append(container)
        
        logger.info(f"Final fallback found {len(unique_containers)} car containers")
        return unique_containers[:20]
    
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
        """Extract car data from HTML element"""
        try:
            text_content = element.get_text()
            
            # Generate ID from element content or use link if available
            link = element.find('a', href=True)
            if link and 'occasions-kopen' in link['href']:
                # Extract ID from the occasions link
                link_match = re.search(r'/occasions-kopen/(\d+)-', link['href'])
                if link_match:
                    car_id = f"koen_{link_match.group(1)}"
                else:
                    car_id = f"koen_link_{hash(link['href']) % 1000000}"
            else:
                element_hash = hash(str(element)[:200]) % 1000000
                car_id = f"koen_html_{element_hash}"
            
            car_data = {
                'autotrack_id': car_id,
                'make': 'Porsche',
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': 'Benzine',
                'description': '',
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Enhanced model extraction based on screenshot content
            # Look for specific patterns like "Porsche 911 Cabrio 991 3.0 Carrera GTS"
            text_lower = text_content.lower()
            
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