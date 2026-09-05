#!/usr/bin/env python3
"""
Investigate Autowereld's anti-scraping mechanisms and find workarounds
"""
import requests
import time
import json
from bs4 import BeautifulSoup

def investigate_blocking_mechanisms():
    """Analyze how Autowereld blocks scrapers"""
    url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?il=100"
    
    print("Investigating Autowereld blocking mechanisms...")
    
    # Test 1: Basic request
    print("\n1. Testing basic request...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 403:
            print("403 Forbidden - Server is blocking requests")
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With browser headers
    print("\n2. Testing with browser headers...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success with browser headers!")
        elif response.status_code == 403:
            print("Still 403 - headers not sufficient")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: With session and cookies
    print("\n3. Testing with session management...")
    session = requests.Session()
    session.headers.update(headers)
    
    # First visit the main page to get cookies
    try:
        main_page = session.get("https://www.autowereld.nl/", timeout=10)
        print(f"Main page status: {main_page.status_code}")
        print(f"Cookies received: {session.cookies.get_dict()}")
        
        time.sleep(2)  # Wait a bit
        
        # Now try the target page
        response = session.get(url, timeout=10)
        print(f"Target page status: {response.status_code}")
        
        if response.status_code == 200:
            print("Success with session and cookies!")
        elif response.status_code == 403:
            print("Still 403 - session/cookies not sufficient")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Check for JavaScript requirements
    print("\n4. Checking for JavaScript requirements...")
    if 'response' in locals() and response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for anti-bot scripts
        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.string or ''
            if any(term in script_text.lower() for term in ['cloudflare', 'bot', 'captcha', 'challenge']):
                print(f"Detected anti-bot script: {script_text[:100]}...")
        
        # Look for noscript warnings
        noscripts = soup.find_all('noscript')
        if noscripts:
            print(f"Found noscript tags: {len(noscripts)}")
            for noscript in noscripts:
                print(f"Noscript content: {noscript.get_text()[:100]}...")
    
    # Test 5: Try different endpoints
    print("\n5. Testing alternative endpoints...")
    
    # Try without query parameters
    base_url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html"
    try:
        response = session.get(base_url, timeout=10)
        print(f"Base URL status: {response.status_code}")
    except Exception as e:
        print(f"Base URL error: {e}")
    
    # Try the dealer main page
    dealer_url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/"
    try:
        response = session.get(dealer_url, timeout=10)
        print(f"Dealer page status: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Look for car links
            car_links = soup.find_all('a', href=lambda x: x and 'occasions-kopen' in x)
            print(f"Found {len(car_links)} car links on dealer page")
            if car_links:
                print(f"Example link: {car_links[0].get('href')}")
    except Exception as e:
        print(f"Dealer page error: {e}")

def test_rate_limiting():
    """Test if rate limiting is the issue"""
    print("\n6. Testing rate limiting...")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'nl-NL,nl;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    session.headers.update(headers)
    
    url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?il=100"
    
    # Try multiple requests with delays
    for i in range(3):
        try:
            print(f"Request {i+1}...")
            response = session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("Success!")
                break
            elif response.status_code == 403:
                print("403 - waiting longer...")
                time.sleep(10)  # Wait 10 seconds
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def check_cloudflare_protection():
    """Check if Cloudflare or similar protection is active"""
    print("\n7. Checking for Cloudflare protection...")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    session.headers.update(headers)
    
    url = "https://www.autowereld.nl/aanbieder/autoservice-koen-exclusief-b-v-1003233/auto.html?il=100"
    
    try:
        response = session.get(url, timeout=10)
        
        # Check response headers for protection services
        protection_headers = ['cf-ray', 'server', 'x-powered-by', 'x-cache']
        print("Response headers analysis:")
        for header in protection_headers:
            if header in response.headers:
                print(f"{header}: {response.headers[header]}")
        
        # Check for challenge pages
        if response.status_code in [403, 503]:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text()}")
            
            # Look for challenge indicators
            challenge_indicators = ['challenge', 'cloudflare', 'just a moment', 'checking your browser']
            page_text = response.text.lower()
            for indicator in challenge_indicators:
                if indicator in page_text:
                    print(f"Detected protection: {indicator}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate_blocking_mechanisms()
    test_rate_limiting()
    check_cloudflare_protection()