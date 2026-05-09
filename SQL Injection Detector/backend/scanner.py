import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
import json
import re

# Import with fallback
try:
    from .payloads import SQLI_PAYLOADS
except ImportError:
    # Fallback payloads if import fails
    SQLI_PAYLOADS = ["' OR '1'='1", "' OR 1=1 --", "' AND SLEEP(5) --"]

try:
    from .detectors import SQLiDetector
except ImportError:
    # Fallback detector
    class SQLiDetector:
        def analyze_response(self, original, test, time):
            return []

try:
    from .crawler import WebCrawler
except ImportError:
    # Fallback crawler
    class WebCrawler:
        def __init__(self, url):
            self.base_url = url
        def start_crawl(self, max_pages=5):
            return []

class SQLiScanner:
    def __init__(self, target_url, deep_scan=False):
        self.target_url = target_url
        self.deep_scan = deep_scan
        self.scan_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.vulnerabilities = []
        
        # Initialize detector
        try:
            self.detector = SQLiDetector()
        except:
            self.detector = SQLiDetector()
    
    def build_test_url(self, original_url, param_name, original_value, payload):
        """Build test URL with injected payload"""
        try:
            parsed = urlparse(original_url)
            params = parse_qs(parsed.query)
            
            if param_name in params:
                test_value = original_value + payload
                params[param_name] = [test_value]
            
            new_query = urlencode(params, doseq=True)
            new_url = urlunparse(parsed._replace(query=new_query))
            
            return new_url
        except:
            return original_url + f"&{param_name}={original_value}{payload}"
    
    def test_parameter(self, url, param_name, param_value, location='url', form_data=None, method='get'):
        """Test a single parameter for SQL injection"""
        results = []
        
        try:
            # Send original request
            if location == 'url':
                original_response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            else:
                if method.lower() == 'post':
                    original_response = requests.post(url, data=form_data, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                else:
                    original_response = requests.get(url, params=form_data, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            original_content = original_response.text
            original_length = len(original_content)
            
        except Exception as e:
            print(f"Error getting original response: {e}")
            return results
        
        # Test each payload (limit to prevent long scans)
        test_payloads = SQLI_PAYLOADS[:30] if not self.deep_scan else SQLI_PAYLOADS[:50]
        
        for payload in test_payloads:
            try:
                start_time = time.time()
                
                if location == 'url':
                    test_url = self.build_test_url(url, param_name, param_value, payload)
                    test_response = requests.get(test_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                else:
                    if method.lower() == 'post':
                        test_form_data = form_data.copy() if form_data else {}
                        test_form_data[param_name] = param_value + payload
                        test_response = requests.post(url, data=test_form_data, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    else:
                        test_form_data = form_data.copy() if form_data else {}
                        test_form_data[param_name] = param_value + payload
                        test_response = requests.get(url, params=test_form_data, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                
                response_time = time.time() - start_time
                test_content = test_response.text
                
                # Simple detection logic
                findings = []
                
                # Check for database errors
                error_patterns = [
                    'sql syntax', 'mysql', 'oracle', 'postgresql', 'sqlite',
                    'odbc', 'driver', 'unclosed quotation', 'warning.*mysql'
                ]
                
                for pattern in error_patterns:
                    if re.search(pattern, test_content, re.IGNORECASE):
                        findings.append({
                            'type': 'Error-Based SQLi',
                            'evidence': f'Database error pattern found: {pattern}',
                            'confidence': 'High'
                        })
                        break
                
                # Check for time-based injection
                if response_time > 5:
                    findings.append({
                        'type': 'Time-Based Blind SQLi',
                        'evidence': f'Response delayed by {response_time:.2f} seconds',
                        'confidence': 'High'
                    })
                
                # Check for content length changes
                if abs(len(test_content) - original_length) > 200:
                    findings.append({
                        'type': 'Boolean-Based SQLi',
                        'evidence': f'Response length changed from {original_length} to {len(test_content)}',
                        'confidence': 'Medium'
                    })
                
                if findings:
                    for finding in findings:
                        results.append({
                            'parameter': param_name,
                            'payload': payload,
                            'location': location,
                            'finding': finding,
                            'response_time': f"{response_time:.2f}s",
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Stop if critical finding
                    if finding['type'] == 'Error-Based SQLi':
                        break
                        
            except requests.Timeout:
                results.append({
                    'parameter': param_name,
                    'payload': payload,
                    'location': location,
                    'finding': {
                        'type': 'Time-Based SQLi',
                        'evidence': 'Request timeout - possible injection',
                        'confidence': 'Medium'
                    }
                })
            except Exception as e:
                print(f"Error testing {param_name}: {e}")
        
        return results
    
    def scan_url_parameters(self, url):
        """Scan all URL parameters"""
        vulnerabilities = []
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if not params:
                return vulnerabilities
            
            print(f"\n🔍 Scanning URL parameters on: {url}")
            
            for param_name, param_values in params.items():
                original_value = param_values[0] if param_values else ''
                print(f"  Testing parameter: {param_name} = '{original_value[:50]}'")
                
                findings = self.test_parameter(url, param_name, original_value, 'url')
                vulnerabilities.extend(findings)
                
                if findings:
                    print(f"    ⚠️ Found {len(findings)} potential vulnerabilities!")
        except Exception as e:
            print(f"Error scanning URL parameters: {e}")
        
        return vulnerabilities
    
    def start_scan(self):
        """Start the main scanning process"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║           SQL INJECTION SCANNER                          ║
║           Target: {self.target_url[:50]}                 ║
║           Deep Scan: {self.deep_scan}                    ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # Scan URL parameters
        url_vulns = self.scan_url_parameters(self.target_url)
        self.vulnerabilities.extend(url_vulns)
        
        # Deep scan if enabled
        if self.deep_scan:
            print("\n🔍 Deep scan mode - crawling for more parameters...")
            try:
                # Simple crawling - find links on page
                response = requests.get(self.target_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and self.target_url.split('/')[2] in href:
                        print(f"  Found linked page: {href[:50]}")
                        page_vulns = self.scan_url_parameters(href)
                        self.vulnerabilities.extend(page_vulns)
            except Exception as e:
                print(f"Deep scan error: {e}")
        
        # Generate report
        self.generate_report()
        
        return self.vulnerabilities
    
    def generate_report(self):
        """Generate scan report"""
        report = {
            'scan_id': self.scan_id,
            'target_url': self.target_url,
            'scan_time': datetime.now().isoformat(),
            'deep_scan': self.deep_scan,
            'summary': {
                'total_vulnerabilities': len(self.vulnerabilities),
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'vulnerabilities': []
        }
        
        # Categorize vulnerabilities
        for vuln in self.vulnerabilities:
            finding_type = vuln.get('finding', {}).get('type', 'Unknown')
            if 'Error' in finding_type:
                report['summary']['critical'] += 1
                severity = 'CRITICAL'
            elif 'Time' in finding_type:
                report['summary']['high'] += 1
                severity = 'HIGH'
            else:
                report['summary']['medium'] += 1
                severity = 'MEDIUM'
            
            report['vulnerabilities'].append({
                'parameter': vuln.get('parameter', 'Unknown'),
                'payload': vuln.get('payload', 'Unknown'),
                'location': vuln.get('location', 'Unknown'),
                'type': finding_type,
                'evidence': vuln.get('finding', {}).get('evidence', 'N/A'),
                'severity': severity,
                'response_time': vuln.get('response_time', 'N/A'),
                'timestamp': vuln.get('timestamp', datetime.now().isoformat())
            })
        
        # Save report
        try:
            os.makedirs('reports', exist_ok=True)
            report_filename = f"reports/scan_{self.scan_id}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📊 Scan completed! Report saved to: {report_filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
        
        return report