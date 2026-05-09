import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import re

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.forms = []
        self.parameters = []
        
    def extract_forms(self, url, html_content):
        """Extract all forms from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        found_forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name', ''),
                    'value': input_tag.get('value', '')
                }
                if input_data['name']:  # Only add named inputs
                    form_data['inputs'].append(input_data)
            
            if form_data['inputs']:  # Only add forms with inputs
                found_forms.append(form_data)
        
        return found_forms
    
    def extract_parameters_from_url(self, url):
        """Extract URL parameters"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        param_list = []
        for key, values in params.items():
            param_list.append({
                'name': key,
                'value': values[0] if values else '',
                'location': 'url'
            })
        
        return param_list
    
    def crawl_links(self, html_content, current_url):
        """Extract and validate links from the page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(current_url, href)
            
            # Only stay within same domain
            if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                if full_url not in self.visited_urls:
                    links.append(full_url)
        
        return links
    
    def scan_page(self, url):
        """Scan a single page for injection points"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Extract URL parameters
                url_params = self.extract_parameters_from_url(url)
                self.parameters.extend(url_params)
                
                # Extract forms
                forms = self.extract_forms(url, response.text)
                self.forms.extend(forms)
                
                # Extract links for further crawling
                links = self.crawl_links(response.text, url)
                
                return {
                    'url': url,
                    'parameters': url_params,
                    'forms': forms,
                    'links': links
                }
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
        
        return None
    
    def start_crawl(self, max_pages=10):
        """Start crawling from base URL"""
        results = []
        urls_to_visit = [self.base_url]
        
        while urls_to_visit and len(results) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            print(f"Crawling: {current_url}")
            self.visited_urls.add(current_url)
            
            page_data = self.scan_page(current_url)
            if page_data:
                results.append(page_data)
                
                # Add new links to visit
                for link in page_data['links']:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
        
        return results