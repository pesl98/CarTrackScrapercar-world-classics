import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarScraper:
    def __init__(self, database):
        self.db = database
        self.base_url = "https://www.carworldclassics.com"
        self.target_url = "https://www.carworldclassics.com/aanbod"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
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
    
    def scrape_cars(self):
        """Main scraping function"""
        logger.info("Starting car scraping...")
        
        new_cars = 0
        updated_cars = 0
        current_car_ids = []
        
        try:
            # Get all pages - CarWorld Classics likely uses different pagination
            page = 1
            while True:
                # Try different URL patterns for CarWorld Classics
                if page == 1:
                    url = self.target_url  # First page might not need pagination
                else:
                    url = f"{self.target_url}?page={page}"  # Try common pagination pattern
                
                logger.info(f"Scraping page {page}: {url}")
                
                cars_on_page = self._scrape_page(url)
                
                if not cars_on_page:
                    logger.info(f"No more cars found on page {page}, stopping")
                    break
                
                for car_data in cars_on_page:
                    current_car_ids.append(car_data['autotrack_id'])
                    
                    existing_car = self.db.get_car_by_autotrack_id(car_data['autotrack_id'])
                    
                    if existing_car:
                        # Check if price has changed
                        if existing_car['current_price'] != car_data['price']:
                            self.db.update_car_price(existing_car['id'], car_data['price'])
                            updated_cars += 1
                            logger.info(f"Updated price for car {car_data['autotrack_id']}: {existing_car['current_price']} -> {car_data['price']}")
                        
                        # Update last seen
                        self.db.update_car_last_seen(existing_car['id'])
                    else:
                        # New car
                        self.db.add_car(car_data)
                        new_cars += 1
                        logger.info(f"Added new car: {car_data['make']} {car_data['model']} - {car_data['price']}")
                
                page += 1
                time.sleep(2)  # Be respectful to the server
            
            # Mark cars as sold if they're not in current listings
            self.db.mark_cars_as_sold(current_car_ids)
            
            logger.info(f"Scraping completed. New cars: {new_cars}, Updated cars: {updated_cars}")
            
            return {
                'new_cars': new_cars,
                'updated_cars': updated_cars,
                'total_current': len(current_car_ids)
            }
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise
    
    def _scrape_page(self, url):
        """Scrape a single page of car listings"""
        try:
            # Add a delay and try to access the main page first
            time.sleep(3)
            
            # First, try to get the main homepage to establish session
            main_page_url = "https://www.carworldclassics.com"
            logger.info(f"First accessing main homepage: {main_page_url}")
            main_response = self.session.get(main_page_url, timeout=30)
            
            if main_response.status_code == 200:
                logger.info("Successfully accessed main homepage")
                time.sleep(2)
            
            logger.info(f"Now accessing inventory page: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cars = []
            
            # Based on the HTML structure you showed, look for the correct selectors
            car_elements = []
            
            # Try different selectors to find car listings for CarWorld Classics
            selectors_to_try = [
                ('div', {'class': re.compile(r'.*car.*item.*')}),
                ('div', {'class': re.compile(r'.*vehicle.*')}),
                ('article', {'class': re.compile(r'.*car.*')}),
                ('div', {'class': re.compile(r'.*product.*')}),
                ('a', {'href': re.compile(r'.*/auto/.*')}),
                ('a', {'href': re.compile(r'.*/car/.*')}),
                ('a', {'href': re.compile(r'.*/detail/.*')}),
                ('div', {'class': re.compile(r'.*grid.*')}),
                ('div', {'class': re.compile(r'.*listing.*')}),
                ('*', {'data-id': True}),
                ('*', {'data-car-id': True})
            ]
            
            for tag, attrs in selectors_to_try:
                car_elements = soup.find_all(tag, attrs)
                if car_elements:
                    logger.info(f"Found {len(car_elements)} elements using {tag} with {attrs}")
                    break
            
            logger.info(f"Found {len(car_elements)} potential car elements on page")
            
            # Debug: log the page structure if no cars found
            if len(car_elements) == 0:
                logger.warning("No car elements found. Page structure analysis:")
                # Look for any divs that might contain cars
                all_divs = soup.find_all('div', limit=20)
                for i, div in enumerate(all_divs):
                    classes = div.get('class') if hasattr(div, 'get') else None
                    if classes:
                        logger.info(f"Div {i}: classes = {classes}")
                
                # Look for any links that might be cars
                all_links = soup.find_all('a', href=True, limit=10)
                for i, link in enumerate(all_links):
                    href = link.get('href') if hasattr(link, 'get') else None
                    if href:
                        logger.info(f"Link {i}: href = {href}")
                        
                # Save a sample of the HTML for debugging
                logger.info("First 500 characters of page content:")
                logger.info(str(soup)[:500])
            
            for element in car_elements:
                try:
                    car_data = self._extract_car_data(element)
                    if car_data:
                        cars.append(car_data)
                except Exception as e:
                    logger.warning(f"Error extracting car data: {str(e)}")
                    continue
            
            return cars
            
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            if "403" in str(e):
                logger.error("Access forbidden - the website may be blocking automated requests")
            return []
    
    def _extract_car_data(self, element):
        """Extract car data from a single car element"""
        try:
            car_data = {}
            
            # Try to find AutoTrack ID from various sources
            autotrack_id = None
            
            # Check data attributes
            autotrack_id = element.get('data-vehicle-id') or element.get('data-id')
            
            # Check href links
            if not autotrack_id:
                link = element.find('a', href=True)
                if link:
                    href = link['href']
                    id_match = re.search(r'/voertuig/(\d+)', href)
                    if id_match:
                        autotrack_id = id_match.group(1)
            
            # Try to extract from any text that looks like an ID
            if not autotrack_id:
                text = element.get_text()
                id_match = re.search(r'\b(\d{6,})\b', text)
                if id_match:
                    autotrack_id = id_match.group(1)
            
            if not autotrack_id:
                logger.warning("Could not find AutoTrack ID for car element")
                return None
            
            car_data['autotrack_id'] = autotrack_id
            
            # Extract make and model
            make_model_element = element.find('h2') or element.find('h3') or \
                               element.find(class_=lambda x: x and 'title' in x.lower()) or \
                               element.find(class_=lambda x: x and 'name' in x.lower())
            
            if make_model_element:
                make_model_text = make_model_element.get_text(strip=True)
                parts = make_model_text.split(' ', 1)
                car_data['make'] = parts[0] if parts else 'Unknown'
                car_data['model'] = parts[1] if len(parts) > 1 else 'Unknown'
            else:
                car_data['make'] = 'Unknown'
                car_data['model'] = 'Unknown'
            
            # Extract price
            price_element = element.find(class_=lambda x: x and 'price' in x.lower()) or \
                           element.find(text=re.compile(r'€|EUR|\$'))
            
            if price_element:
                if hasattr(price_element, 'get_text'):
                    price_text = price_element.get_text()
                else:
                    price_text = str(price_element)
                
                price_match = re.search(r'[\d.,]+', price_text.replace(',', '').replace('.', ''))
                if price_match:
                    try:
                        car_data['price'] = int(price_match.group().replace(',', '').replace('.', ''))
                    except ValueError:
                        car_data['price'] = 0
                else:
                    car_data['price'] = 0
            else:
                car_data['price'] = 0
            
            # Extract year
            year_element = element.find(text=re.compile(r'\b(19|20)\d{2}\b'))
            if year_element:
                year_match = re.search(r'\b(19|20)(\d{2})\b', str(year_element))
                if year_match:
                    car_data['year'] = int(year_match.group())
                else:
                    car_data['year'] = None
            else:
                car_data['year'] = None
            
            # Extract mileage
            mileage_element = element.find(text=re.compile(r'\d+\s*(km|miles)'))
            if mileage_element:
                mileage_match = re.search(r'(\d+(?:,\d{3})*)\s*(?:km|miles)', str(mileage_element))
                if mileage_match:
                    try:
                        car_data['mileage'] = int(mileage_match.group(1).replace(',', ''))
                    except ValueError:
                        car_data['mileage'] = None
                else:
                    car_data['mileage'] = None
            else:
                car_data['mileage'] = None
            
            # Extract image URL
            img_element = element.find('img')
            if img_element:
                img_src = img_element.get('src') or img_element.get('data-src')
                if img_src:
                    car_data['image_url'] = urljoin(self.base_url, img_src)
                else:
                    car_data['image_url'] = None
            else:
                car_data['image_url'] = None
            
            # Extract description/details
            desc_element = element.find(class_=lambda x: x and ('desc' in x.lower() or 'detail' in x.lower()))
            if desc_element:
                car_data['description'] = desc_element.get_text(strip=True)[:500]  # Limit length
            else:
                car_data['description'] = ''
            
            # Extract fuel type
            fuel_element = element.find(text=re.compile(r'\b(benzine|diesel|electric|hybrid|lpg)\b', re.I))
            if fuel_element:
                fuel_match = re.search(r'\b(benzine|diesel|electric|hybrid|lpg)\b', str(fuel_element), re.I)
                if fuel_match:
                    car_data['fuel_type'] = fuel_match.group(1).lower()
                else:
                    car_data['fuel_type'] = None
            else:
                car_data['fuel_type'] = None
            
            return car_data
            
        except Exception as e:
            logger.error(f"Error extracting car data: {str(e)}")
            return None
