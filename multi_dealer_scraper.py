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
            # Extract car ID from data attribute or URL
            car_id = None
            
            # Try to find ID from various sources
            id_element = element.find('div', {'data-id': True})
            if id_element:
                car_id = id_element.get('data-id')
            
            if not car_id:
                link = element.find('a', href=True)
                if link:
                    href = link['href']
                    id_match = re.search(r'/(\d+)[-/]', href)
                    if id_match:
                        car_id = id_match.group(1)
            
            if not car_id:
                return None
            
            car_data = {
                'autotrack_id': car_id,
                'make': 'Unknown',
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'description': '',
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Extract make and model from URL
            link = element.find('a', href=True)
            if link:
                href = link['href']
                car_data['source_url'] = href
                
                url_match = re.search(r'/occasions-kopen/(\d+)-([^/?]+)', href)
                if url_match:
                    url_text = url_match.group(2)
                    url_parts = url_text.split('-')
                    
                    if len(url_parts) >= 2:
                        car_data['make'] = url_parts[0].capitalize()
                        model_parts = url_parts[1:5]
                        car_data['model'] = ' '.join(model_parts).title()
            
            # Extract price
            price_element = element.find('span', class_='price') or element.find('div', class_='price')
            if price_element:
                price_text = price_element.get_text()
                price_match = re.search(r'€\s*([\d.,]+)', price_text.replace('.', '').replace(',', ''))
                if price_match:
                    car_data['price'] = int(price_match.group(1))
            
            # Extract image
            img_element = element.find('img')
            if img_element and img_element.get('src'):
                car_data['image_url'] = img_element['src']
            
            return car_data if car_data['price'] > 0 else None
            
        except Exception as e:
            logger.error(f"Error extracting car data: {str(e)}")
            return None


class KoenExclusiefScraper(BaseDealerScraper):
    """Scraper for Koen Exclusief"""
    
    def __init__(self):
        super().__init__("KoenExclusief", "https://koenexclusief.nl")
    
    def get_inventory_url(self, page: int = 1) -> str:
        if page == 1:
            return f"{self.base_url}/aanbod"
        return f"{self.base_url}/aanbod?page={page}"
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        # Try multiple possible selectors for Koen Exclusief
        selectors = [
            'div.car-item',
            'div.vehicle-item', 
            'div.listing-item',
            'div[class*="car"]',
            'div[class*="vehicle"]',
            'div[class*="listing"]',
            'article',
            'div.product'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 2:  # More than just filters/headers
                logger.info(f"Using selector '{selector}' for Koen Exclusief")
                return elements
        
        # Fallback: look for divs with car images
        img_elements = soup.find_all('img')
        car_containers = []
        for img in img_elements:
            src = img.get('src', '').lower()
            alt = img.get('alt', '').lower()
            if any(keyword in src or keyword in alt for keyword in ['car', 'auto', 'vehicle', 'porsche', 'bmw']):
                container = img.find_parent(['div', 'article', 'section'])
                if container and container not in car_containers:
                    car_containers.append(container)
        
        return car_containers[:20]  # Limit to reasonable number
    
    def extract_car_data(self, element) -> Optional[Dict]:
        try:
            # For now, create a placeholder structure for Koen Exclusief
            # This would need to be customized based on their actual HTML structure
            
            car_data = {
                'autotrack_id': f"koen_{hash(str(element)[:100]) % 100000}",  # Temporary ID
                'make': 'Porsche',  # Since they specialize in Porsche
                'model': 'Unknown',
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'description': '',
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Extract text content for analysis
            text_content = element.get_text()
            
            # Try to extract price
            price_match = re.search(r'€\s*([\d.,]+)', text_content.replace('.', '').replace(',', ''))
            if price_match:
                try:
                    car_data['price'] = int(price_match.group(1))
                except:
                    pass
            
            # Extract link
            link = element.find('a', href=True)
            if link:
                car_data['source_url'] = link['href']
            
            # Extract image
            img = element.find('img')
            if img and img.get('src'):
                car_data['image_url'] = img['src']
            
            # Only return if we found a reasonable price
            return car_data if car_data['price'] > 50000 else None  # Reasonable minimum for luxury cars
            
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