#!/usr/bin/env python
"""
Quick script to check if channels is installed correctly
"""

import sys

def check_module_installed(module_name):
    try:
        __import__(module_name)
        print(f"✓ {module_name} is installed!")
        return True
    except ImportError:
        print(f"✗ {module_name} is NOT installed!")
        return False

if __name__ == "__main__":
    print("Checking Django Channels and dependencies...")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check Django
    django_installed = check_module_installed("django")
    
    # Check Channels
    channels_installed = check_module_installed("channels")
    
    # Check Daphne
    daphne_installed = check_module_installed("daphne")
    
    # If any required module is missing, provide suggestions
    if not all([django_installed, channels_installed, daphne_installed]):
        print("\n== SUGGESTED FIXES ==")
        print("1. Make sure you've activated your virtual environment (if using one)")
        print("2. Install required packages:")
        print("   pip install channels==4.0.0 daphne==4.0.0")
        print("3. If installing in a virtual environment, make sure you're using the correct pip:")
        print("   python -m pip install channels==4.0.0 daphne==4.0.0")
        print("4. If the issue persists, try upgrading pip:")
        print("   python -m pip install --upgrade pip")
        print("5. Then reinstall the packages.")
        sys.exit(1)
    else:
        print("\nAll required modules are installed correctly!")
        sys.exit(0)
