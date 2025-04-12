"""
Diagnostic script to check if channels package is installed
and accessible in the current Python environment.
"""

import sys

print(f"Python executable being used: {sys.executable}")
print(f"Python version: {sys.version}")
print("\n--- Checking for Django Channels ---")

try:
    import django
    print(f"Django is installed (version {django.__version__})")
except ImportError:
    print("Django is NOT installed!")

try:
    import channels
    print(f"Channels is installed! Version: {channels.__version__}")
except ImportError:
    print("ERROR: Channels is NOT installed or not in the Python path")

print("\nPython path (where Python looks for modules):")
for path in sys.path:
    print(f" - {path}")

print("\n--- Solution if channels is not found ---")
print("1. Make sure you activate the virtual environment:")
print("   .\env\Scripts\activate")
print("2. Install channels:")
print("   pip install channels==4.0.0 daphne==4.0.0")
print("3. Verify installation:")
print("   pip list | findstr channels")
