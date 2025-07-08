import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import time
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseDealerScraper(ABC):
    """Base class for dealer-specific scrapers"""
    
    def __init__(self, dealer_name: str, base_url: str):
        self.dealer_name = dealer_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
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
            
            # Add small delay to be respectful
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            car_elements = self.find_car_elements(soup)
            
            logger.info(f"Found {len(car_elements)} car elements on {self.dealer_name}")
            
            cars = []
            for element in car_elements:
                try:
                    car_data = self.extract_car_data(element)
                    if car_data:
                        cars.append(car_data)
                except Exception as e:
                    logger.error(f"Error extracting car from element: {str(e)}")
                    continue
            
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
        # CarWorld Classics uses div.car-item for each car listing
        car_elements = soup.find_all('div', class_='car-item')
        return car_elements
    
    def extract_car_data(self, element) -> Optional[Dict]:
        """Extract car data from CarWorld Classics HTML element"""
        try:
            # Extract basic information
            title_elem = element.find('h3', class_='car-title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract price
            price_elem = element.find('span', class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else '0'
            price = self._extract_price(price_text)
            
            # Extract make and model from title
            make, model = self._extract_make_model(title)
            
            # Extract year
            year = self._extract_year(title)
            
            # Extract mileage
            mileage_elem = element.find('span', class_='mileage')
            mileage_text = mileage_elem.get_text(strip=True) if mileage_elem else ''
            mileage = self._extract_mileage(mileage_text)
            
            # Extract fuel type
            fuel_elem = element.find('span', class_='fuel')
            fuel_type = fuel_elem.get_text(strip=True) if fuel_elem else None
            
            # Extract image URL
            img_elem = element.find('img')
            image_url = img_elem.get('src') if img_elem else None
            if image_url and image_url.startswith('/'):
                image_url = self.base_url + image_url
            
            # Extract car ID from URL
            link_elem = element.find('a')
            car_url = link_elem.get('href') if link_elem else ''
            autotrack_id = self._extract_car_id(car_url)
            
            car_data = {
                'autotrack_id': autotrack_id,
                'make': make,
                'model': model,
                'year': year,
                'mileage': mileage,
                'fuel_type': fuel_type,
                'description': title,
                'image_url': image_url,
                'price': price,
                'dealer_name': self.dealer_name
            }
            
            # Only return if we have valid data
            if car_data['price'] > 0 and car_data['make'] != 'Unknown':
                return car_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting CarWorldClassics car data: {str(e)}")
            return None
    
    def _extract_price(self, price_text: str) -> int:
        """Extract price from text"""
        # Remove currency symbols and spaces
        price_clean = re.sub(r'[€$,.\s]', '', price_text)
        
        # Extract numbers
        price_match = re.search(r'(\d+)', price_clean)
        if price_match:
            return int(price_match.group(1))
        return 0
    
    def _extract_make_model(self, title: str) -> tuple:
        """Extract make and model from title"""
        # Common car makes
        makes = ['Porsche', 'BMW', 'Mercedes', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Ferrari', 'Lamborghini', 'Bentley', 'Rolls-Royce', 'Aston Martin', 'Jaguar', 'Maserati', 'McLaren', 'Bugatti', 'Lotus', 'TVR', 'Morgan', 'Caterham', 'Ariel', 'Noble', 'Pagani', 'Koenigsegg', 'Spyker', 'Wiesmann', 'Gumpert', 'Artega', 'Melkus', 'Isdera', 'Bitter', 'Alpina', 'Brabus', 'Carlsson', 'Kleemann', 'Lorinser', 'Renntech', 'Schnitzer', 'Hamann', 'Vorsteiner', 'Mansory', 'Gemballa', 'Techart', 'Ruf', 'Singer', 'Gunther Werks', 'Emory', 'Rauh-Welt Begriff', 'LEICA', 'Ford', 'Chevrolet', 'Dodge', 'Cadillac', 'Lincoln', 'Chrysler', 'Jeep', 'Ram', 'GMC', 'Buick', 'Pontiac', 'Oldsmobile', 'Saturn', 'Hummer', 'Saab', 'Volvo', 'Peugeot', 'Citroën', 'Renault', 'Opel', 'Fiat', 'Alfa Romeo', 'Lancia', 'Maserati', 'Ferrari', 'Lamborghini', 'Pagani', 'Lada', 'Dacia', 'Skoda', 'Seat', 'Cupra', 'Toyota', 'Honda', 'Nissan', 'Mazda', 'Subaru', 'Mitsubishi', 'Suzuki', 'Isuzu', 'Lexus', 'Infiniti', 'Acura', 'Hyundai', 'Kia', 'Genesis', 'Daewoo', 'SsangYong', 'Tata', 'Mahindra', 'Maruti', 'Bajaj', 'TVS', 'Hero', 'Royal Enfield', 'Triumph', 'Harley-Davidson', 'Indian', 'Victory', 'Ducati', 'Kawasaki', 'Yamaha', 'Suzuki', 'Honda', 'BMW', 'KTM', 'Husqvarna', 'Aprilia', 'Moto Guzzi', 'Vespa', 'Piaggio', 'Kymco', 'SYM', 'Peugeot']
        
        for make in makes:
            if make.lower() in title.lower():
                # Extract model (everything after make)
                make_index = title.lower().find(make.lower())
                model_part = title[make_index + len(make):].strip()
                
                # Clean up model name
                model = re.sub(r'^\W+', '', model_part)  # Remove leading non-word chars
                model = model.split()[0] if model else 'Unknown'  # Take first word
                
                return make, model
        
        return 'Unknown', 'Unknown'
    
    def _extract_year(self, title: str) -> Optional[int]:
        """Extract year from title"""
        year_match = re.search(r'(19|20)\d{2}', title)
        if year_match:
            year = int(year_match.group())
            if 1900 <= year <= 2024:
                return year
        return None
    
    def _extract_mileage(self, mileage_text: str) -> Optional[int]:
        """Extract mileage from text"""
        if not mileage_text:
            return None
        
        # Look for patterns like "50,000 km" or "50000"
        mileage_match = re.search(r'([\d,]+)', mileage_text.replace('.', ','))
        if mileage_match:
            mileage_str = mileage_match.group(1).replace(',', '')
            try:
                return int(mileage_str)
            except ValueError:
                pass
        
        return None
    
    def _extract_car_id(self, car_url: str) -> str:
        """Extract car ID from URL"""
        if not car_url:
            return f"cwc_{random.randint(100000, 999999)}"
        
        # Extract ID from URL patterns
        id_match = re.search(r'/(\d+)', car_url)
        if id_match:
            return id_match.group(1)
        
        # Fallback: use last part of URL
        return car_url.split('/')[-1] or f"cwc_{random.randint(100000, 999999)}"


class MultiDealerScraper:
    """Main scraper that coordinates multiple dealers"""
    
    def __init__(self, database):
        self.database = database
        self.dealers = [
            CarWorldClassicsScraper(),
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
            
            logger.info(f"Completed {dealer_scraper.dealer_name}: {new_cars} new, {updated_cars} updated")
            return new_cars, updated_cars
            
        except Exception as e:
            logger.error(f"Error scraping {dealer_scraper.dealer_name}: {str(e)}")
            return 0, 0