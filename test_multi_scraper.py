#!/usr/bin/env python3
"""Test the multi-dealer scraper functionality"""

from database import Database
from multi_dealer_scraper import MultiDealerScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_multi_dealer_scraper():
    """Test the multi-dealer scraper"""
    try:
        # Initialize database
        db = Database()
        
        # Initialize multi-dealer scraper
        multi_scraper = MultiDealerScraper(db)
        
        logger.info("Starting multi-dealer scrape test...")
        
        # Run the scraper
        multi_scraper.scrape_all_dealers()
        
        # Get stats to see what was scraped
        stats = db.get_dashboard_stats()
        logger.info(f"Scraping complete. Total cars: {stats['total_cars']}")
        logger.info(f"Active cars: {stats['active_cars']}")
        
        # Show cars by dealer
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dealer_name, COUNT(*) as count
                FROM cars 
                WHERE is_sold = 0
                GROUP BY dealer_name
            """)
            dealer_counts = cursor.fetchall()
            
            for dealer in dealer_counts:
                logger.info(f"{dealer['dealer_name']}: {dealer['count']} cars")
        
    except Exception as e:
        logger.error(f"Error testing multi-dealer scraper: {str(e)}")

if __name__ == "__main__":
    test_multi_dealer_scraper()