# Car Tracker Application

## Overview

This is a Flask-based car tracking application that scrapes car listings from CarWorld Classics and monitors price changes over time. The application provides a web dashboard for viewing car inventory, tracking price history, and monitoring market trends.

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

### Web Scraper (`scraper.py`)
- Scrapes CarWorld Classics website
- Extracts car details and pricing information
- Tracks new listings and price changes

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
- **CarWorld Classics**: Primary data source for car listings
- Base URL: https://www.carworldclassics.com/aanbod

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
- June 22, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.