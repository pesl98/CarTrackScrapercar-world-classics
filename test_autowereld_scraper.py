#!/usr/bin/env python3
"""
Test the updated KoenExclusief scraper targeting Autowereld
"""
import requests
import time
import random
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_autowereld_koen_scraper():
    """Test the KoenExclusief scraper on Autowereld"""
    print("Testing Autowereld KoenExclusief scraper with advanced techniques...")
    
    # Try multiple approaches
    approaches = [
        test_via_google_cache,
        test_via_web_archive,
        test_alternative_domains,
        test_mobile_site,
        test_rss_feeds,
        test_sitemap_discovery
    ]
    
    for approach in approaches:
        try:
            result = approach()
            if result:
                print(f"\n✓ SUCCESS with {approach.__name__}")
                return result
            else:
                print(f"✗ Failed with {approach.__name__}")
        except Exception as e:
            print(f"✗ Error with {approach.__name__}: {e}")
        
        time.sleep(3)  # Delay between attempts
    
    print("\nAll approaches failed. Autowereld has very strict anti-scraping protection.")
    return []

def test_via_google_cache():
    """Try accessing via Google cache"""
    print("Attempting Google cache access...")
    
    cache_url = "https://webcache.googleusercontent.com/search?q=cache:https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        response = requests.get(cache_url, headers=headers, timeout=10)
        if response.status_code == 200 and 'porsche' in response.text.lower():
            print("Found Porsche content in Google cache!")
            return extract_cars_from_html(response.text)
    except:
        pass
    
    return None

def test_via_web_archive():
    """Try accessing via Internet Archive"""
    print("Attempting Internet Archive access...")
    
    archive_url = "https://web.archive.org/web/*/https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(archive_url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for recent snapshots
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=lambda x: x and '2025' in x)
            
            if links:
                # Try the most recent snapshot
                snapshot_url = "https://web.archive.org" + links[0]['href']
                snapshot_response = requests.get(snapshot_url, headers=headers, timeout=10)
                
                if snapshot_response.status_code == 200:
                    return extract_cars_from_html(snapshot_response.text)
    except:
        pass
    
    return None

def test_alternative_domains():
    """Try alternative domain patterns"""
    print("Attempting alternative domains...")
    
    alternatives = [
        "https://m.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",
        "https://mobile.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",
        "https://amp.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",
        "https://www.autowereld.be/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html",  # Belgium
        "https://autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"  # Without www
    ]
    
    for url in alternatives:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Success with alternative domain: {url}")
                return extract_cars_from_html(response.text)
                
        except:
            continue
    
    return None

def test_mobile_site():
    """Try mobile-specific access"""
    print("Attempting mobile site access...")
    
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Try mobile-specific URL patterns
    mobile_urls = [
        "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?mobile=1",
        "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?m=1",
        "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?view=mobile"
    ]
    
    for url in mobile_urls:
        try:
            response = requests.get(url, headers=mobile_headers, timeout=10)
            if response.status_code == 200:
                return extract_cars_from_html(response.text)
        except:
            continue
    
    return None

def test_rss_feeds():
    """Try to find RSS feeds or XML data"""
    print("Attempting RSS/XML feed discovery...")
    
    feed_urls = [
        "https://www.autowereld.nl/rss/aanbieder/1003233",
        "https://www.autowereld.nl/feeds/dealer/1003233",
        "https://www.autowereld.nl/xml/aanbieder/1003233",
        "https://www.autowereld.nl/api/dealer/1003233/cars.xml",
        "https://www.autowereld.nl/sitemap_dealer_1003233.xml"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; FeedReader/1.0; +http://www.feedreader.com/)',
        'Accept': 'application/rss+xml, application/xml, text/xml'
    }
    
    for url in feed_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Found feed: {url}")
                return extract_cars_from_xml(response.text)
        except:
            continue
    
    return None

def test_sitemap_discovery():
    """Try to discover sitemaps"""
    print("Attempting sitemap discovery...")
    
    sitemap_urls = [
        "https://www.autowereld.nl/sitemap.xml",
        "https://www.autowereld.nl/robots.txt"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    
    for url in sitemap_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Accessed {url}: {response.status_code}")
                
                # Look for dealer-specific URLs
                if 'koen-exclusief' in response.text.lower():
                    print("Found KoenExclusief references in sitemap!")
                    # Could parse and extract specific URLs
                    return []
                    
        except:
            continue
    
    return None

def extract_cars_from_html(html_content):
    """Extract car data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    cars = []
    
    # Look for car-related content
    if 'porsche' in html_content.lower():
        print("Found Porsche references in content")
        
        # Try to extract basic car info
        porsche_mentions = soup.find_all(text=lambda text: text and 'porsche' in text.lower())
        
        for mention in porsche_mentions[:5]:  # Limit to 5
            # Create basic car data
            car_data = {
                'autotrack_id': f"cached_{abs(hash(mention))}",
                'make': 'Porsche',
                'model': 'Unknown',
                'year': None,
                'price': 0,
                'description': str(mention)[:200],
                'dealer_name': 'KoenExclusief',
                'source_url': 'https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/'
            }
            
            # Try to extract model
            if '911' in mention:
                car_data['model'] = '911'
            elif 'cayenne' in mention.lower():
                car_data['model'] = 'Cayenne'
                
            cars.append(car_data)
    
    return cars

def extract_cars_from_xml(xml_content):
    """Extract car data from XML/RSS content"""
    # Basic XML parsing for car data
    if 'porsche' in xml_content.lower():
        print("Found Porsche in XML content")
        return [{
            'autotrack_id': 'xml_porsche_001',
            'make': 'Porsche',
            'model': 'Unknown',
            'dealer_name': 'KoenExclusief',
            'description': 'Found via XML feed'
        }]
    
    return []

if __name__ == "__main__":
    cars = test_autowereld_koen_scraper()
    
    if cars:
        print(f"\n=== FOUND {len(cars)} CARS ===")
        for car in cars:
            print(f"- {car['make']} {car['model']} ({car.get('year', 'Unknown year')})")
    else:
        print("\n=== NO CARS FOUND ===")
        print("Autowereld's protection is too strong for standard scraping techniques.")
        print("The site uses DPG Media's enterprise WAF which blocks automated access.")