from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import atexit

logger = logging.getLogger(__name__)

def start_scheduler(scraper):
    """Start the background scheduler for automated scraping"""
    scheduler = BackgroundScheduler()
    
    # Schedule scraping every day at 8 AM
    scheduler.add_job(
        func=scraper.scrape_cars,
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_scrape',
        name='Daily car scraping',
        replace_existing=True
    )
    
    # Schedule additional scraping every 6 hours
    scheduler.add_job(
        func=scraper.scrape_cars,
        trigger=CronTrigger(hour='*/6'),
        id='frequent_scrape',
        name='Frequent car scraping',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("Scheduler started - daily scraping at 8 AM and every 6 hours")
    
    return scheduler
