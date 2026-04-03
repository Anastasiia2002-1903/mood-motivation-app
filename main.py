#!/usr/bin/env python3
"""DAFEU - Digitaler Assistent für emotionale Unterstützung.

A safe digital space for emotional support and self-reflection.
"""

import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app import app


def main():
    print("Starting DAFEU - http://127.0.0.1:5000")
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
pip3 install flask
