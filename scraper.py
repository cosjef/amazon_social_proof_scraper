"""
Amazon Product Sales Data Scraper v2.7.2

Description:
    A tool for automating the collection of Amazon product social proof metrics.
    Social proof is the tagline on an ASIN that states "X amount purchased in last month".
    
Features:
    - Google Sheets Integration: Reads ASINs and writes results
    - Batch Processing: Handles ASINs in configurable chunks
    - Progress Tracking: Resumes from last position if interrupted
    - Rate Limiting: Includes delays and CAPTCHA detection
    - Error Handling: Graceful handling of network and parsing errors

Configuration:
    All settings are located at the top of this script:
    - Google Sheet settings (SHEET_ID, WORKSHEET_NAME)
    - Data location settings (ASIN_COLUMN, START_ROW, RESULT_COLUMN)
    - Processing settings (CHUNK_SIZE, PAGE_LOAD_DELAY)
    - File settings (PROGRESS_FILE)

Dependencies:
    - gspread: Google Sheets API wrapper
    - requests: For HTTP requests
    - beautifulsoup4: For HTML parsing
    - google-oauth-oauthlib: For Google authentication
    
Usage:
    1. Configure settings in the User Configuration section
    2. Ensure client_secrets.json is present
    3. Run: python3 scraper.py

Note: 
    Respects Amazon's rate limits and includes CAPTCHA detection.
    Progress is saved after each chunk for reliability.
"""

import gspread
import requests
from bs4 import BeautifulSoup
[rest of the original file content...]