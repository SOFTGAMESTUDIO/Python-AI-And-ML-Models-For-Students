import re
import time
import requests
from .payloads import DB_ERROR_PATTERNS, SUCCESS_INDICATORS

class SQLiDetector:
    def __init__(self):
        self.findings = []
        
    def detect_error_based(self, response_text):
        """Detect SQL injection via database errors"""
        errors_found = []
        
        for pattern in DB_ERROR_PATTERNS:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                errors_found.append({
                    'type': 'Error-Based SQLi',
                    'pattern': pattern,
                    'evidence': matches[0]
                })
        
        return errors_found
    
    def detect_boolean_based(self, original_response, test_response, original_length, test_length):
        """Detect SQL injection via boolean differences"""
        findings = []
        
        # Compare response lengths
        length_diff = abs(test_length - original_length)
        if length_diff > 100:  # Significant difference
            findings.append({
                'type': 'Boolean-Based SQLi',
                'evidence': f'Response length changed from {original_length} to {test_length}',
                'confidence': 'Medium'
            })
        
        # Compare content
        for indicator in SUCCESS_INDICATORS:
            if indicator.lower() in original_response.lower():
                if indicator.lower() not in test_response.lower():
                    findings.append({
                        'type': 'Boolean-Based SQLi',
                        'evidence': f"'{indicator}' disappeared in response",
                        'confidence': 'High'
                    })
        
        return findings
    
    def detect_time_based(self, response_time, threshold=5):
        """Detect SQL injection via time delays"""
        if response_time > threshold:
            return [{
                'type': 'Time-Based Blind SQLi',
                'evidence': f'Response delayed by {response_time:.2f} seconds',
                'confidence': 'High'
            }]
        return []
    
    def detect_union_based(self, response_text):
        """Detect UNION-based SQL injection"""
        findings = []
        
        # Look for column numbers or data in response
        union_patterns = [
            r'(\d+)\s*,\s*(\d+)',
            r'column\s+(\d+)',
            r'NULL,\s*NULL',
            r'admin.*password',
            r'username.*password'
        ]
        
        for pattern in union_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                findings.append({
                    'type': 'Union-Based SQLi',
                    'evidence': f'Pattern found: {pattern}',
                    'confidence': 'Medium'
                })
        
        return findings
    
    def analyze_response(self, original_response, test_response, response_time):
        """Comprehensive response analysis"""
        all_findings = []
        
        # Run all detection methods
        all_findings.extend(self.detect_error_based(test_response))
        all_findings.extend(self.detect_union_based(test_response))
        all_findings.extend(self.detect_time_based(response_time))
        
        return all_findings