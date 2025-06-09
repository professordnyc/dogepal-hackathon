"""
DOGEPAL - AI-powered spending analysis and optimization for local governments.
"""

__version__ = "0.1.0"

# Add the backend directory to the Python path
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
