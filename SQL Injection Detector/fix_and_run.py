#!/usr/bin/env python
import os
import sys
import subprocess

def fix_project():
    """Fix common issues and run the project"""
    
    print("🔧 Fixing SQL Injection Detector...")
    
    # Create required directories
    os.makedirs('backend', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Create empty __init__.py if missing
    init_file = 'backend/__init__.py'
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Backend module\n')
        print(f"✓ Created {init_file}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Flask', 'requests', 'beautifulsoup4'], 
                      check=True, capture_output=True)
        print("✓ Dependencies installed")
    except:
        print("⚠️ Could not auto-install dependencies. Run: pip install Flask requests beautifulsoup4")
    
    # Run the app
    print("\n🚀 Starting the application...")
    print("Access at: http://localhost:5000\n")
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry running manually: python app.py")

if __name__ == '__main__':
    fix_project()