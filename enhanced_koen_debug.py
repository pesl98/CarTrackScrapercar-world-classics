#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import json

def analyze_koen_website_deeply():
    """Deeply analyze KoenExclusief website structure for future scraping"""
    url = "https://koenexclusief.nl/aanbod"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== DEEP ANALYSIS OF KOEN EXCLUSIEF ===")
        
        # Look for JavaScript variables or AJAX endpoints
        scripts = soup.find_all('script')
        ajax_endpoints = []
        js_variables = []
        
        for script in scripts:
            script_text = script.get_text()
            
            # Look for AJAX URLs
            ajax_patterns = [
                r'ajax[^"\']*["\']([^"\']+)["\']',
                r'fetch[^"\']*["\']([^"\']+)["\']',
                r'XMLHttpRequest[^"\']*["\']([^"\']+)["\']',
                r'url[^"\']*:[^"\']*["\']([^"\']+)["\']',
            ]
            
            for pattern in ajax_patterns:
                matches = re.findall(pattern, script_text, re.IGNORECASE)
                ajax_endpoints.extend(matches)
            
            # Look for car-related variables
            if any(term in script_text.lower() for term in ['car', 'auto', 'vehicle', 'porsche']):
                js_variables.append(script_text[:200])
        
        if ajax_endpoints:
            print(f"Found {len(ajax_endpoints)} potential AJAX endpoints:")
            for endpoint in set(ajax_endpoints):
                if any(term in endpoint.lower() for term in ['car', 'auto', 'api', 'data']):
                    print(f"  - {endpoint}")
        
        # Look for form elements that might trigger car loading
        forms = soup.find_all('form')
        filters = soup.find_all(['select', 'input'], attrs={'name': True})
        
        print(f"\nFound {len(forms)} forms and {len(filters)} filter elements")
        
        # Check for data attributes that might contain API info
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        
        data_attrs = {}
        for elem in elements_with_data:
            for attr, value in elem.attrs.items():
                if attr.startswith('data-') and any(term in str(value).lower() for term in ['url', 'api', 'ajax', 'car', 'auto']):
                    data_attrs[attr] = value
        
        if data_attrs:
            print(f"\nFound relevant data attributes:")
            for attr, value in data_attrs.items():
                print(f"  {attr}: {value}")
        
        # Look for meta tags with car counts or status
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = meta.get('content', '')
            if any(term in content.lower() for term in ['porsche', 'auto', 'car']):
                print(f"Meta tag: {meta.get('name', meta.get('property', 'unknown'))} = {content}")
        
        # Check page source for any hidden car data
        page_text = soup.get_text()
        if "0 Occasions" in page_text:
            print("\n✓ Confirmed: Currently shows '0 Occasions' - no inventory")
        
        # Look for container structure that would hold cars
        potential_containers = soup.find_all('div', class_=re.compile(r'.*(list|grid|container|items?).*', re.I))
        print(f"\nFound {len(potential_containers)} potential car container elements")
        
        # Look for pagination or load-more elements
        pagination = soup.find_all(['div', 'nav'], class_=re.compile(r'.*(pag|load|more).*', re.I))
        if pagination:
            print(f"Found {len(pagination)} pagination/load-more elements")
        
        return {
            'has_inventory': "0 Occasions" not in page_text,
            'ajax_endpoints': list(set(ajax_endpoints)),
            'data_attributes': data_attrs,
            'container_count': len(potential_containers)
        }
        
    except Exception as e:
        print(f"Error analyzing KoenExclusief: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_koen_website_deeply()