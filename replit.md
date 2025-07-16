# Car Tracker Application

## Overview

This is a Flask-based car tracking application that scrapes car listings from CarWorldClassics.com and monitors price changes over time. The application provides a web dashboard for viewing car inventory, tracking price history, monitoring market trends, and exporting data to CSV format.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Python 3.11
- **Database**: SQLite for data persistence with custom Database class
- **Web Scraping**: BeautifulSoup4 and requests for scraping car listings
- **Scheduling**: APScheduler for automated periodic scraping
- **Data Models**: Dataclasses for type-safe data structures

### Frontend Architecture
- **Framework**: Server-side rendered HTML with Bootstrap 5
- **Styling**: Custom CSS with CSS custom properties for theming
- **JavaScript**: Vanilla JavaScript for dynamic interactions
- **UI Components**: Responsive dashboard with car listings, statistics, and filtering

### Database Schema
- **cars table**: Stores car information (make, model, year, price, status)
- **price_history table**: Tracks price changes over time
- Uses SQLite with row factory for dict-like access

## Key Components

### Core Application (`app.py`)
- Flask web server with REST API endpoints
- Routes for dashboard, car listings, and statistics
- Pagination and filtering support for car listings

### Data Layer (`database.py`)
- SQLite database management
- CRUD operations for cars and price history
- Query methods with filtering and pagination

### Multi-Dealer Scraper (`multi_dealer_scraper.py`)
- Modular scraper framework supporting multiple dealers
- CarWorld Classics scraper with precise HTML parsing
- Koen Exclusief scraper for luxury car dealers
- Base scraper class for easy dealer expansion
- Dealer-specific data extraction and validation

### Legacy Single Scraper (`scraper.py`)
- Original CarWorld Classics scraper (kept for compatibility)
- Single-dealer implementation

### Scheduler (`scheduler.py`)
- Background task scheduling
- Daily scraping at 8 AM
- Additional scraping every 6 hours

### Data Models (`models.py`)
- Type-safe dataclasses for Car, PriceHistory, and DashboardStats
- Provides structure for data throughout the application

## Data Flow

1. **Scheduled Scraping**: APScheduler triggers scraping at configured intervals
2. **Data Extraction**: Scraper fetches and parses car listings from target website
3. **Data Storage**: New cars and price changes are stored in SQLite database
4. **API Endpoints**: Flask serves data through RESTful API endpoints
5. **Dashboard Display**: Frontend fetches data via AJAX and displays in responsive UI

## External Dependencies

### Python Packages
- **Flask**: Web framework and API server
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP client for web scraping
- **APScheduler**: Background task scheduling
- **Trafilatura**: Additional web scraping utilities

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements

### Target Website
- **CarWorld Classics**: Data source for classic and luxury cars
  - Base URL: https://www.carworldclassics.com/aanbod
  - Successfully scraping 45+ cars per session
  - Comprehensive inventory tracking with price monitoring

## Deployment Strategy

### Environment Setup
- Python 3.11 runtime environment
- PostgreSQL 16 module configured (though SQLite is currently used)
- UV package manager for dependency management

### Deployment Configuration
- Replit deployment with automated dependency installation
- Port 5000 for Flask application mapped to external port 80
- Parallel workflow execution for server startup

### Monitoring and Maintenance
- Scheduled scraping reduces manual intervention
- Dashboard provides real-time statistics and monitoring
- Price history tracking for trend analysis

## Changelog
- June 22, 2025: Initial setup with CarWorld Classics scraper
- June 22, 2025: Enhanced make/model extraction from URL patterns
- June 22, 2025: Fixed pagination logic to prevent infinite loops
- June 22, 2025: Added CSV export functionality for car data
- June 22, 2025: Implemented price change tracking with detailed history
- June 22, 2025: **Multi-dealer framework completed**
  - Created modular scraper architecture with base class
  - Successfully integrated CarWorld Classics (41 cars scraped)
  - Implemented Koen Exclusief scraper with Porsche specialization
  - Enhanced database schema with dealer_name field
  - Added dealer badges to frontend display
  - Updated scheduling system for multi-dealer support
- June 22, 2025: **Enhanced KoenExclusief scraper with AJAX support**
  - Analyzed website structure and implemented proper car detection
  - Added AJAX endpoint discovery for dynamic content loading
  - Enhanced Porsche model extraction with comprehensive variants
  - Handles both HTML parsing and JSON data processing
  - Properly detects empty inventory states and validates data quality
  - Ready for immediate scraping when dealer adds inventory
- June 22, 2025: **Completed JavaScript content handling for KoenExclusief**
  - Successfully identified and handled dynamic content loading via "aanbod-list-area" class
  - Implemented wait/retry mechanism for JavaScript-loaded car listings
  - Added graceful handling of empty inventory states (0 cars currently)
  - Scraper properly detects loading states and attempts AJAX endpoint discovery
  - Framework ready to capture cars when they become available on the site
- June 29, 2025: **Enhanced dashboard with new statistics**
  - Fixed Price Changes tile bug - corrected count from 42 to 0 (was counting all price records instead of actual changes)
  - Added "Cars Sold (7 days)" statistic showing recent sales activity
  - Added "Days Since Last Sold" statistic to track sales recency
  - Added "Cars Sold (14 days)" statistic for broader sales trend analysis
  - Added "New Cars (14 days)" statistic to track inventory additions
  - Updated database queries and frontend display for new metrics
  - Dashboard now provides 10 comprehensive statistics for market monitoring
- July 8, 2025: **Removed KoenExclusief scraper entirely**
  - Simplified system to focus exclusively on CarWorldClassics
  - Removed all KoenExclusief/Autowereld scraping code and related complexity
  - Updated documentation to reflect single-dealer focus
  - Streamlined multi_dealer_scraper.py for better maintainability
  - System now cleanly operates with only CarWorldClassics as data source
- July 9, 2025: **Fixed "Days on Market" calculation bug**
  - Days on market counter now correctly freezes when cars are sold
  - Previously continued counting after sale date, now stops at sold_date
  - Updated both car listing display and dashboard statistics calculation
  - Example: Car sold after 15 days shows "15 days" permanently, not increasing count
  - Applies to both individual car records and average days on market statistic
- July 9, 2025: **Added Total Value statistic to dashboard**
  - Confirmed average price calculation uses only active cars (not sold)
  - Added "Total Value" statistic showing sum of all active car prices
  - Currently showing €4,723,039 total value across 35 active cars
  - New statistic displayed in yellow tile with coins icon
  - Updated both backend database queries and frontend display
- July 9, 2025: **Added "First Seen" column to car listings table**
  - Added new column showing date when car was first detected by scraper
  - Displays in DD/MM/YYYY format for easy reading
  - Column positioned between "Fuel" and "Days on Market"
  - Updated table structure and JavaScript to handle 10 columns instead of 9
  - Provides valuable insight into when cars entered the market
- July 11, 2025: **Fixed critical scraping issue**
  - Updated CSS selector from `div.car-item` to `div.col-xl-6.col-lg-6.mb-5`
  - Fixed data extraction methods for new HTML structure
  - Resolved database key mismatch (current_price vs price)
  - Scraper now successfully finds 37 car elements and processes 34 valid cars
  - Added 1 new car and updated 29 existing cars during test run
  - System now properly detects sold cars and maintains accurate inventory
  - Fixed price extraction regex to handle European format (€ 289.992,-)
  - Successfully found and tracked the €109,911 car that was previously missing
  - Updated car status logic to properly mark cars as active when they reappear
- July 16, 2025: **Added separate average days statistics**
  - Split "Avg Days" into two separate statistics for better clarity
  - "Avg Days (Active)" shows average days only for cars currently online (21.3 days)
  - "Avg Days (All)" shows average days for all cars including sold ones (18.5 days)
  - Updated dashboard layout with new teal-colored tile for "Avg Days (All)"
  - Active cars tend to stay online longer than the overall average, providing market insights
- July 16, 2025: **Enhanced price changes filter for meaningful tracking**
  - Updated price changes to only show significant changes larger than €100
  - Filters out minor price fluctuations and display inconsistencies
  - Reduced noise from 33 minor changes to 8 meaningful price adjustments
  - Applied to both dashboard statistics and price changes modal display
  - Provides cleaner market trend analysis focused on substantial price movements

## Recent Success
- CarWorldClassics scraping system successfully extracts 45 cars per session
- Fully operational scraper with robust pagination and data extraction
- Database correctly stores car information and prevents duplicates
- Price change tracking monitors market fluctuations
- CSV export functionality for data analysis
- Dashboard provides comprehensive market statistics and insights

## Adapting for Other Car Dealers

This application is designed with a modular scraper architecture that makes it easy to add new car dealers. Follow this guide to create your own version for different dealers.

### Step 1: Fork or Copy the Project

1. **Create a new Replit project** by forking this one or copying all files to a new project
2. **Update the project name** in your Replit settings to reflect the new dealer
3. **Modify the replit.md file** to document your specific dealer configuration

### Step 2: Create a New Dealer Scraper

Create a new scraper class in `multi_dealer_scraper.py` by following this template:

```python
class YourDealerScraper(BaseDealerScraper):
    """Scraper for [Your Dealer Name]"""
    
    def __init__(self):
        super().__init__(
            dealer_name="Your Dealer Name",
            base_url="https://yourdealer.com"
        )
    
    def get_inventory_url(self, page: int = 1) -> str:
        """Return the URL for the dealer's inventory page"""
        return f"{self.base_url}/inventory?page={page}"
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        """Find car listing elements on the page"""
        # Update this CSS selector to match your dealer's HTML structure
        return soup.find_all('div', class_='car-listing')
    
    def extract_car_data(self, element) -> Optional[Dict]:
        """Extract car data from a single listing element"""
        try:
            # Customize these selectors for your dealer's HTML structure
            make_model = element.find('h3', class_='car-title')?.get_text(strip=True)
            price_element = element.find('span', class_='price')
            price = self._extract_price(price_element.get_text() if price_element else '')
            
            # Extract other fields as needed
            year = self._extract_year(make_model or '')
            mileage = self._extract_mileage(element.get_text())
            
            return {
                'autotrack_id': self._generate_id(element),
                'make': self._extract_make(make_model or ''),
                'model': self._extract_model(make_model or ''),
                'year': year,
                'mileage': mileage,
                'current_price': price,
                'description': make_model or '',
                'image_url': self._extract_image_url(element),
                'dealer_name': self.dealer_name
            }
        except Exception as e:
            logger.error(f"Error extracting car data: {e}")
            return None
```

### Step 3: Update the Multi-Dealer Configuration

In `multi_dealer_scraper.py`, add your new scraper to the `MultiDealerScraper` class:

```python
class MultiDealerScraper:
    def __init__(self, database):
        self.database = database
        self.dealers = [
            CarWorldClassicsScraper(),
            YourDealerScraper(),  # Add your new scraper here
        ]
```

### Step 4: Analyze the Target Website

Before implementing the scraper, analyze the dealer's website:

1. **Inspect the HTML structure** using browser developer tools
2. **Identify CSS selectors** for car listings, prices, titles, etc.
3. **Check for pagination** patterns and URL structures
4. **Test for anti-scraping measures** (rate limiting, CAPTCHA, etc.)
5. **Look for AJAX endpoints** that might load data dynamically

### Step 5: Implement Helper Methods

Customize these helper methods for your dealer's data format:

```python
def _extract_price(self, text: str) -> int:
    """Extract price from text - customize for your dealer's format"""
    # Example: "€25,000" -> 25000
    price_match = re.search(r'[\d,]+', text.replace('€', '').replace('.', ''))
    return int(price_match.group().replace(',', '')) if price_match else 0

def _generate_id(self, element) -> str:
    """Generate unique ID for the car listing"""
    # Use URL, data attributes, or other unique identifiers
    link = element.find('a')
    if link and link.get('href'):
        return link['href'].split('/')[-1]
    return f"car_{hash(element.get_text())}"
```

### Step 6: Test Your Scraper

Create a test script to verify your scraper works:

```python
# test_your_dealer.py
from multi_dealer_scraper import YourDealerScraper

def test_your_dealer():
    scraper = YourDealerScraper()
    cars = scraper.scrape_page(scraper.get_inventory_url())
    print(f"Found {len(cars)} cars")
    for car in cars[:3]:  # Show first 3 cars
        print(f"- {car['make']} {car['model']} - €{car['current_price']:,}")

if __name__ == "__main__":
    test_your_dealer()
```

### Step 7: Update Configuration

1. **Modify scheduling** in `scheduler.py` if needed for different scraping intervals
2. **Update database** if you need additional fields specific to your dealer
3. **Customize the frontend** to reflect your dealer's branding or specific needs

### Step 8: Handle Common Challenges

**Dynamic Content Loading:**
If the site uses JavaScript to load content, consider using Playwright:
```python
from playwright.sync_api import sync_playwright

def scrape_with_playwright(self, url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('.car-listing')  # Wait for content
        html = page.content()
        browser.close()
        return BeautifulSoup(html, 'html.parser')
```

**Rate Limiting:**
Add delays between requests:
```python
import time
import random

def scrape_page(self, url):
    time.sleep(random.uniform(1, 3))  # Random delay 1-3 seconds
    return super().scrape_page(url)
```

**Anti-Scraping Protection:**
- Use different User-Agent strings
- Implement proxy rotation if needed
- Add session management for sites requiring login

### Step 9: Deploy and Monitor

1. **Test thoroughly** with your specific dealer's website
2. **Monitor scraping logs** for errors or blocking
3. **Set up alerts** for when scraping fails
4. **Document any dealer-specific quirks** in your replit.md file

### Example: Real-World Implementation

For reference, see how `CarWorldClassicsScraper` is implemented for a working example of:
- HTML structure analysis
- Data extraction patterns
- Error handling
- Pagination logic

This modular approach allows you to quickly adapt the application for any car dealer website while maintaining the robust dashboard and analytics features.

### Quick Start Template

For a faster setup, copy this minimal scraper template and customize the marked sections:

```python
class QuickDealerScraper(BaseDealerScraper):
    def __init__(self):
        super().__init__(
            dealer_name="[CHANGE: Your Dealer Name]",
            base_url="[CHANGE: https://yourdealer.com]"
        )
    
    def get_inventory_url(self, page: int = 1) -> str:
        # CHANGE: Update URL pattern for your dealer
        return f"{self.base_url}/cars?page={page}"
    
    def find_car_elements(self, soup: BeautifulSoup) -> List:
        # CHANGE: Update CSS selector for car listings
        return soup.find_all('div', class_='[CHANGE: car-item]')
    
    def extract_car_data(self, element) -> Optional[Dict]:
        try:
            # CHANGE: Update selectors for your dealer's HTML
            title = element.find('[CHANGE: h2]', class_='[CHANGE: title]')?.get_text(strip=True)
            price_elem = element.find('[CHANGE: span]', class_='[CHANGE: price]')
            
            return {
                'autotrack_id': self._generate_id(element),
                'make': self._extract_make(title or ''),
                'model': self._extract_model(title or ''),
                'year': self._extract_year(title or ''),
                'current_price': self._extract_price(price_elem.get_text() if price_elem else ''),
                'description': title or '',
                'dealer_name': self.dealer_name
            }
        except Exception as e:
            logger.error(f"Error extracting car data: {e}")
            return None
```

### Configuration Options

**Environment Variables:**
Create a `.env` file for dealer-specific settings:
```
DEALER_NAME=Your Dealer Name
DEALER_URL=https://yourdealer.com
SCRAPE_INTERVAL_HOURS=6
MAX_PAGES_PER_SCRAPE=10
```

**Custom Scheduling:**
Modify `scheduler.py` for dealer-specific timing:
```python
# For dealers that update inventory at specific times
scheduler.add_job(
    func=scrape_job,
    trigger="cron",
    hour=9,  # 9 AM when dealer typically updates
    minute=0,
    id='dealer_morning_scrape'
)
```

### Troubleshooting Common Issues

**Issue: No cars found**
- Check CSS selectors with browser developer tools
- Verify the URL structure and pagination
- Test if the site requires cookies or headers

**Issue: Scraping blocked**
- Add delays between requests
- Rotate User-Agent strings
- Check if the site has robots.txt restrictions

**Issue: Missing data fields**
- Inspect HTML for data-* attributes
- Check if information is in JavaScript variables
- Look for hidden form fields with car data

This documentation provides everything needed to quickly adapt the car tracking system for any dealer website.

## User Preferences

Preferred communication style: Simple, everyday language.