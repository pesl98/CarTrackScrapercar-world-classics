#!/usr/bin/env python3
"""
Test the updated KoenExclusief scraper targeting Autowereld
"""
import sys
import logging
from multi_dealer_scraper import KoenExclusiefScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_autowereld_koen_scraper():
    """Test the KoenExclusief scraper on Autowereld"""
    print("Testing KoenExclusief scraper on Autowereld...")
    
    scraper = KoenExclusiefScraper()
    
    # Get the URL
    url = scraper.get_inventory_url()
    print(f"Testing URL: {url}")
    
    # Scrape the page
    cars = scraper.scrape_page(url)
    
    print(f"\nFound {len(cars)} cars:")
    
    if cars:
        for i, car in enumerate(cars[:5], 1):  # Show first 5
            print(f"\nCar {i}:")
            print(f"  ID: {car['autotrack_id']}")
            print(f"  Make: {car['make']}")
            print(f"  Model: {car['model']}")
            print(f"  Year: {car['year']}")
            print(f"  Price: €{car['price']:,}" if car['price'] else "Price: Not found")
            print(f"  Mileage: {car['mileage']:,} km" if car['mileage'] else "Mileage: Not found")
            print(f"  Fuel: {car['fuel_type']}")
            print(f"  Description: {car['description'][:100]}...")
            print(f"  Source: {car['source_url']}")
            print(f"  Image: {car['image_url']}")
    else:
        print("No cars found - checking what went wrong...")
        
        # Debug the page structure
        print("\nDebugging page structure...")
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"Page status: {response.status_code}")
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"Page length: {len(response.text)} characters")
            
            # Look for any divs with substantial content
            all_divs = soup.find_all('div')
            car_candidate_divs = []
            
            for div in all_divs:
                div_text = div.get_text().strip()
                if (len(div_text) > 100 and 
                    any(term in div_text.lower() for term in ['porsche', 'mercedes', 'bmw', 'auto', 'car']) and
                    any(term in div_text.lower() for term in ['€', 'euro', 'km', 'jaar', 'benzine', 'diesel'])):
                    car_candidate_divs.append(div)
            
            print(f"Found {len(car_candidate_divs)} potential car divs by content analysis")
            
            if car_candidate_divs:
                print("\nFirst potential car div content:")
                print(car_candidate_divs[0].get_text()[:300] + "...")
            
        except Exception as e:
            print(f"Debug error: {str(e)}")
    
    return cars

if __name__ == "__main__":
    test_autowereld_koen_scraper()