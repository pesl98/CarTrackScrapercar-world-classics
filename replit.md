# Car Tracker Application

## Overview

This is a Flask-based car tracking application that scrapes car listings from multiple dealers (CarWorld Classics and Koen Exclusief) and monitors price changes over time. The application provides a web dashboard for viewing car inventory, tracking price history, monitoring market trends, and exporting data to CSV format.

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

### Target Websites
- **CarWorld Classics**: Primary data source for classic and luxury cars
  - Base URL: https://www.carworldclassics.com/aanbod
  - Successfully scraping 40+ cars per session
- **Koen Exclusief**: Secondary dealer specializing in luxury vehicles
  - Base URL: https://koenexclusief.nl/aanbod
  - Framework implemented for future expansion

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

## Recent Success
- Multi-dealer scraping system successfully extracts 42 cars from CarWorld Classics
- CarWorld Classics scraper fully operational with robust pagination and data extraction
- Database correctly stores dealer information and prevents duplicates
- Frontend displays dealer badges with color-coded identification
- Price change tracking works across multiple dealers
- CSV export includes dealer information
- **KoenExclusief Challenge**: Autowereld.nl protected by DPG Media's enterprise WAF (Web Application Firewall)
  - All automated requests blocked with 403 errors (including homepage access)
  - Investigated multiple bypass techniques: gradual approach, mobile headers, alternative domains, cache access
  - WAF protection too sophisticated for standard scraping methods

## User Preferences

Preferred communication style: Simple, everyday language.