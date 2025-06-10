#!/usr/bin/env python3
"""
Client Activity Monitor - Main Entry Point

This module serves as the entry point for the Client Activity Monitor application.
It initializes the controller and starts the GUI application.

The application monitors user activity across multiple Oracle databases to identify
security-relevant changes made within a 24-hour window.

Usage:
    python main.py
    
    Or via Poetry:
    poetry run python src/client_activity_monitor/main.py

Requirements:
    - Python 3.10+
    - Oracle Instant Client
    - Valid Kerberos configuration
    - Database access permissions
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for the Client Activity Monitor application."""
    try:
        # Import here to ensure path is set up
        from client_activity_monitor.controller.main_controller import MainController
        
        # Create and run the application
        controller = MainController()
        controller.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  poetry install")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()