from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import backend modules with error handling
try:
    from backend.scanner import SQLiScanner
except ImportError as e:
    print(f"Error importing scanner: {e}")
    print("Make sure all backend files exist in the 'backend' folder")
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Ensure directories exist
os.makedirs('reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)

@app.route('/')
def index():
    """Home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {e}", 500

@app.route('/api/scan', methods=['POST'])
def scan():
    """Start a new scan"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        target_url = data.get('url')
        deep_scan = data.get('deep_scan', False)
        
        if not target_url:
            return jsonify({'error': 'Please provide a URL'}), 400
        
        # Validate URL
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        # Initialize scanner
        scanner = SQLiScanner(target_url, deep_scan)
        
        # Run scan
        vulnerabilities = scanner.start_scan()
        
        # Prepare response
        response = {
            'success': True,
            'target': target_url,
            'deep_scan': deep_scan,
            'total_vulnerabilities': len(vulnerabilities),
            'vulnerabilities': [],
            'scan_id': scanner.scan_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Format vulnerabilities for JSON response
        for vuln in vulnerabilities:
            response['vulnerabilities'].append({
                'parameter': vuln.get('parameter', 'Unknown'),
                'payload': vuln.get('payload', 'Unknown'),
                'type': vuln.get('finding', {}).get('type', 'Unknown'),
                'evidence': vuln.get('finding', {}).get('evidence', 'No evidence'),
                'severity': 'HIGH' if 'Error' in vuln.get('finding', {}).get('type', '') else 'MEDIUM',
                'location': vuln.get('location', 'Unknown')
            })
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get list of all scan reports"""
    try:
        reports = []
        reports_dir = 'reports'
        
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(reports_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            report_data = json.load(f)
                            reports.append({
                                'filename': filename,
                                'scan_id': report_data.get('scan_id'),
                                'target': report_data.get('target_url'),
                                'timestamp': report_data.get('scan_time'),
                                'vulnerabilities': report_data.get('summary', {}).get('total_vulnerabilities', 0)
                            })
                    except:
                        continue
        
        return jsonify({'reports': sorted(reports, key=lambda x: x.get('timestamp', ''), reverse=True)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Get specific scan report"""
    try:
        # Security: prevent directory traversal
        filename = os.path.basename(filename)
        filepath = os.path.join('reports', filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                report_data = json.load(f)
            return jsonify(report_data)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<filename>', methods=['GET'])
def export_report(filename):
    """Download report as JSON file"""
    try:
        filename = os.path.basename(filename)
        filepath = os.path.join('reports', filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     SQL INJECTION DETECTOR - WEB INTERFACE                ║
    ║                                                           ║
    ║     Server starting at: http://localhost:5000             ║
    ║                                                           ║
    ║     ⚠️  IMPORTANT: Only use on authorized targets!        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)