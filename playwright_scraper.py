#!/usr/bin/env python3
"""
Playwright-based scraper for Autowereld Koen Exclusief listings
"""
import asyncio
import re
import logging
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AutowereldKoenScraper:
    """Playwright scraper for Autowereld Koen Exclusief dealer page"""
    
    def __init__(self):
        self.dealer_name = "KoenExclusief"
        self.base_url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"
        self.browser = None
        self.page = None
    
    async def start_browser(self):
        """Start Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        # Set user agent and viewport
        await self.page.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
    
    async def close_browser(self):
        """Close Playwright browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_cars(self) -> List[Dict]:
        """Scrape cars from Autowereld Koen Exclusief page"""
        try:
            logger.info(f"Scraping {self.base_url}")
            
            # Navigate to the page with increased limit
            url_with_limit = f"{self.base_url}?il=100"
            await self.page.goto(url_with_limit, wait_until='networkidle')
            
            # Wait for car listings to load
            await self.page.wait_for_selector('.car-item, .listing-item, .vehicle-item, [class*="car"], [class*="vehicle"]', timeout=10000)
            
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find car elements - try different selectors
            car_elements = self._find_car_elements(soup)
            
            logger.info(f"Found {len(car_elements)} car elements")
            
            cars = []
            for element in car_elements:
                car_data = self._extract_car_data(element)
                if car_data:
                    car_data['dealer_name'] = self.dealer_name
                    cars.append(car_data)
            
            logger.info(f"Successfully extracted {len(cars)} cars")
            return cars
            
        except Exception as e:
            logger.error(f"Error scraping Autowereld: {str(e)}")
            return []
    
    def _find_car_elements(self, soup: BeautifulSoup) -> List:
        """Find car listing elements on Autowereld page"""
        # Try various selectors for Autowereld car listings
        selectors = [
            '.car-item',
            '.listing-item', 
            '.vehicle-item',
            '.vehicle-listing',
            '.car-listing',
            '[class*="car-"]',
            '[class*="vehicle-"]',
            '[class*="listing-"]',
            '.search-result-item',
            '.result-item'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                # Filter for actual car listings (must have car-related content)
                valid_cars = []
                for elem in elements:
                    elem_text = elem.get_text().lower()
                    elem_html = str(elem).lower()
                    
                    # Check for car indicators
                    has_car_content = any(term in elem_text for term in [
                        'porsche', 'mercedes', 'bmw', 'audi', 'volkswagen',
                        'km', 'euro', '€', 'benzine', 'diesel'
                    ])
                    
                    has_car_link = any(term in elem_html for term in [
                        'occasions', 'auto', 'car', 'voertuig'
                    ])
                    
                    if has_car_content or has_car_link:
                        valid_cars.append(elem)
                
                if valid_cars:
                    logger.info(f"Filtered to {len(valid_cars)} valid car elements")
                    return valid_cars
        
        # Fallback: look for any divs containing car-related content
        all_divs = soup.find_all('div')
        car_divs = []
        
        for div in all_divs:
            div_text = div.get_text().strip()
            div_html = str(div).lower()
            
            # Must have substantial content and car indicators
            if (len(div_text) > 100 and 
                any(term in div_text.lower() for term in ['porsche', 'mercedes', 'bmw', 'audi']) and
                any(term in div_text.lower() for term in ['€', 'euro', 'km', 'benzine', 'diesel'])):
                
                # Avoid nested elements
                is_nested = any(div in other.descendants for other in car_divs)
                if not is_nested:
                    car_divs.append(div)
        
        logger.info(f"Fallback found {len(car_divs)} car divs")
        return car_divs[:20]  # Limit to avoid processing too many
    
    def _extract_car_data(self, element) -> Optional[Dict]:
        """Extract car data from a single element"""
        try:
            elem_text = element.get_text()
            elem_html = str(element)
            
            # Initialize car data
            car_data = {
                'autotrack_id': '',
                'make': 'Unknown',
                'model': 'Unknown', 
                'year': None,
                'mileage': None,
                'fuel_type': None,
                'description': elem_text.strip()[:200],
                'image_url': None,
                'source_url': '',
                'price': 0
            }
            
            # Extract car ID from any links
            links = element.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Look for ID patterns in URLs
                id_match = re.search(r'(\d{6,})', href)
                if id_match:
                    car_data['autotrack_id'] = id_match.group(1)
                    car_data['source_url'] = href
                    break
            
            # If no ID found, generate from content hash
            if not car_data['autotrack_id']:
                car_data['autotrack_id'] = str(abs(hash(elem_text[:100])))[:8]
            
            # Extract make and model
            make_model = self._extract_make_model(elem_text, elem_html)
            car_data.update(make_model)
            
            # Extract price
            price = self._extract_price(elem_text)
            if price:
                car_data['price'] = price
            
            # Extract year
            year = self._extract_year(elem_text)
            if year:
                car_data['year'] = year
            
            # Extract mileage
            mileage = self._extract_mileage(elem_text)
            if mileage:
                car_data['mileage'] = mileage
            
            # Extract fuel type
            fuel_type = self._extract_fuel_type(elem_text)
            if fuel_type:
                car_data['fuel_type'] = fuel_type
            
            # Extract image URL
            img = element.find('img', src=True)
            if img:
                car_data['image_url'] = img['src']
            
            # Only return if we have meaningful data
            if car_data['price'] > 0 or any(term in car_data['make'].lower() for term in ['porsche', 'mercedes', 'bmw', 'audi']):
                return car_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting car data: {str(e)}")
            return None
    
    def _extract_make_model(self, text: str, html: str) -> Dict[str, str]:
        """Extract make and model from text"""
        text_lower = text.lower()
        
        # Common makes
        makes = {
            'porsche': 'Porsche',
            'mercedes': 'Mercedes-Benz', 
            'bmw': 'BMW',
            'audi': 'Audi',
            'volkswagen': 'Volkswagen',
            'ford': 'Ford',
            'toyota': 'Toyota'
        }
        
        make = 'Unknown'
        model = 'Unknown'
        
        # Find make
        for key, value in makes.items():
            if key in text_lower:
                make = value
                break
        
        # Extract model for known makes
        if make == 'Porsche':
            porsche_models = ['911', 'carrera', 'turbo', 'gt3', 'cayenne', 'macan', 'panamera', 'boxster', 'cayman']
            for model_name in porsche_models:
                if model_name in text_lower:
                    model = model_name.upper() if model_name == '911' else model_name.title()
                    break
        
        elif make == 'Mercedes-Benz':
            # Look for Mercedes model patterns like C-Class, E-Class, etc.
            model_match = re.search(r'([a-z]-class|[a-z]\d{2,3}|cls|slk|ml)', text_lower)
            if model_match:
                model = model_match.group(1).upper()
        
        elif make == 'BMW':
            # Look for BMW model patterns like 3 Series, X5, etc.
            model_match = re.search(r'([x]?\d+\s*series?|[x]?\d+)', text_lower)
            if model_match:
                model = model_match.group(1).upper()
        
        return {'make': make, 'model': model}
    
    def _extract_price(self, text: str) -> Optional[int]:
        """Extract price from text"""
        # Look for price patterns
        price_patterns = [
            r'€\s*([\d.,]+)',
            r'([\d.,]+)\s*€',
            r'([\d.,]+)\s*euro',
            r'prijs[:\s]*([\d.,]+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text.lower())
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    return int(price_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        # Look for 4-digit years
        year_match = re.search(r'(19\d{2}|20\d{2})', text)
        if year_match:
            year = int(year_match.group(1))
            if 1990 <= year <= 2025:
                return year
        
        return None
    
    def _extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage from text"""
        # Look for km patterns
        km_patterns = [
            r'([\d.,]+)\s*km',
            r'([\d.,]+)\s*kilometer'
        ]
        
        for pattern in km_patterns:
            match = re.search(pattern, text.lower())
            if match:
                km_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    return int(km_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_fuel_type(self, text: str) -> Optional[str]:
        """Extract fuel type from text"""
        text_lower = text.lower()
        
        fuel_types = {
            'benzine': 'Benzine',
            'diesel': 'Diesel', 
            'hybrid': 'Hybrid',
            'elektrisch': 'Elektrisch',
            'lpg': 'LPG',
            'gas': 'Gas'
        }
        
        for key, value in fuel_types.items():
            if key in text_lower:
                return value
        
        return None

async def test_autowereld_scraper():
    """Test the Autowereld scraper"""
    scraper = AutowereldKoenScraper()
    
    try:
        await scraper.start_browser()
        cars = await scraper.scrape_cars()
        
        print(f"Found {len(cars)} cars:")
        for i, car in enumerate(cars[:5]):  # Show first 5
            print(f"\nCar {i+1}:")
            print(f"  Make: {car['make']}")
            print(f"  Model: {car['model']}")
            print(f"  Year: {car['year']}")
            print(f"  Price: €{car['price']:,}" if car['price'] else "Price: Not found")
            print(f"  Mileage: {car['mileage']:,} km" if car['mileage'] else "Mileage: Not found")
            print(f"  Fuel: {car['fuel_type']}")
            print(f"  ID: {car['autotrack_id']}")
        
        return cars
        
    finally:
        await scraper.close_browser()

if __name__ == "__main__":
    asyncio.run(test_autowereld_scraper())