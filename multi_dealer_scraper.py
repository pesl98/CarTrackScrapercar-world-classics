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
        # Check if they have cars ("0 Occasions" indicates no inventory)
        occasions_text = soup.get_text()
        if "0 Occasions" in occasions_text:
            logger.info("Koen Exclusief currently has 0 cars in inventory")
            return []
        
        # Try AJAX endpoints first
        session = requests.Session()
        session.headers.update(self.headers)
        
        ajax_data = self._try_ajax_endpoints(session)
        if ajax_data:
            return ajax_data  # Return raw data for AJAX processing
        
        # Look for car listing containers in HTML
        selectors_to_try = [
            'div.car-item',
            'div.vehicle-item',
            'div.occasion-item',
            'div.auto-item',
            'div[class*="car"]',
            'div[class*="vehicle"]',
            'div[class*="occasion"]',
            'div[class*="auto"]',
            'article.car',
            'div.listing-item'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements and len(elements) > 0:
                # Filter out navigation/header elements
                car_elements = []
                for elem in elements:
                    elem_text = elem.get_text().lower()
                    if (any(indicator in elem_text for indicator in ['€', 'km', 'jaar']) and
                        len(elem_text.strip()) > 50):
                        car_elements.append(elem)
                
                if car_elements:
                    logger.info(f"Found {len(car_elements)} valid car elements using: {selector}")
                    return car_elements
        
        # Enhanced fallback: look for structured car data
        car_containers = []
        
        # Look for elements with car-specific data attributes
        data_elements = soup.find_all(attrs=lambda x: x and any(
            k.startswith('data-') and any(term in k.lower() for term in ['car', 'auto', 'vehicle'])
            for k in x.keys()
        ))
        
        for elem in data_elements:
            elem_text = elem.get_text().lower()
            if (any(model in elem_text for model in ['porsche', '911', 'carrera', 'turbo', 'cayenne', 'macan']) and
                any(indicator in elem_text for indicator in ['€', 'km']) and
                len(elem_text.strip()) > 80):
                car_containers.append(elem)
        
        if car_containers:
            logger.info(f"Found {len(car_containers)} cars via data attributes")
            return car_containers
        
        # Final fallback: comprehensive content analysis
        all_elements = soup.find_all(['div', 'article', 'section'])
        for elem in all_elements:
            elem_text = elem.get_text().lower()
            
            # More comprehensive Porsche model detection
            porsche_indicators = ['porsche', '911', 'carrera', 'turbo', 'gt3', 'gt2', 'cayenne', 'macan', 'panamera', 'taycan', 'boxster', 'cayman']
            price_indicators = ['€', 'eur', 'euro']
            tech_indicators = ['km', 'kilometer', 'jaar', 'bouwjaar', 'pk', 'kw', 'benzine', 'diesel']
            
            if (any(model in elem_text for model in porsche_indicators) and
                any(price in elem_text for price in price_indicators) and
                any(tech in elem_text for tech in tech_indicators) and
                len(elem_text.strip()) > 100):
                car_containers.append(elem)
        
        logger.info(f"Final fallback found {len(car_containers)} potential car containers")
        return car_containers[:15]
    
    def extract_car_data(self, element) -> Optional[Dict]:
        try:
            # Extract text content for analysis
            text_content = element.get_text()
            
            # Generate ID from element content
            element_hash = hash(str(element)[:200]) % 1000000
            car_id = f"koen_{element_hash}"
            
            car_data = {
                'autotrack_id': car_id,
                'make': 'Porsche',  # Koen Exclusief specializes in Porsche
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': 'Benzine',  # Default for Porsche
                'description': '',
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Extract Porsche model from text
            porsche_models = ['911', 'Carrera', 'Turbo', 'GT3', 'GT2', 'Cayenne', 'Macan', 'Panamera', 'Taycan', 'Boxster', 'Cayman']
            for model in porsche_models:
                if model.lower() in text_content.lower():
                    car_data['model'] = model
                    break
            
            # Extract price (€ format)
            price_patterns = [
                r'€\s*([\d.,]+)',
                r'([\d.,]+)\s*€',
                r'(\d{5,})',  # At least 5 digits for car prices
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, text_content.replace('.', '').replace(',', ''))
                if price_match:
                    try:
                        car_data['price'] = int(price_match.group(1))
                        if car_data['price'] > 10000:  # Reasonable minimum
                            break
                    except ValueError:
                        continue
            
            # Extract year
            year_match = re.search(r'(19|20)\d{2}', text_content)
            if year_match:
                try:
                    car_data['year'] = int(year_match.group(0))
                except ValueError:
                    pass
            
            # Extract mileage (km)
            mileage_patterns = [
                r'([\d.,]+)\s*km',
                r'([\d.,]+)\s*KM',
                r'([\d.,]+)\s*kilometer'
            ]
            
            for pattern in mileage_patterns:
                mileage_match = re.search(pattern, text_content.replace('.', '').replace(',', ''))
                if mileage_match:
                    try:
                        car_data['mileage'] = int(mileage_match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Extract image
            img = element.find('img')
            if img and img.get('src'):
                src = img['src']
                # Handle relative URLs
                if src.startswith('/'):
                    car_data['image_url'] = f"{self.base_url}{src}"
                else:
                    car_data['image_url'] = src
            
            # Extract link for source URL
            link = element.find('a', href=True)
            if link:
                href = link['href']
                if href.startswith('/'):
                    car_data['source_url'] = f"{self.base_url}{href}"
                else:
                    car_data['source_url'] = href
            
            # Set description from the clean text
            car_data['description'] = text_content.strip()[:500]
            
            # Only return if we have valid data
            if car_data['price'] > 0 and car_data['model'] != 'Unknown':
                return car_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Koen Exclusief car data: {str(e)}")
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