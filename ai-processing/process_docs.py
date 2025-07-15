#!/usr/bin/env python3
"""
Backward compatibility wrapper for the original CLI interface
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import the process command from the main CLI
from cli import process

if __name__ == "__main__":
    # Invoke the process command directly for backward compatibility
    process()
