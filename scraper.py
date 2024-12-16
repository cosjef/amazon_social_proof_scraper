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
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
from google.auth.transport.requests import Request
import pickle
import time
import random
from datetime import datetime

print("Starting script...")

#######################
# User Configuration  #
#######################

# Google Sheet Settings
SHEET_ID = "1-po9aIh1bGu9BXsDvA5wW8bvgWSpX4O4eoHm0lB7R1Y"  # ID from Google Sheets URL
WORKSHEET_NAME = "Artext Wholesale"  # Name of the specific worksheet/tab

# Data Location Settings
ASIN_COLUMN = 3        # Column containing ASINs (3 = Column C)
START_ROW = 3          # First row containing actual data (skips headers)
RESULT_COLUMN = 'I'    # Column where results will be written

# Processing Settings
CHUNK_SIZE = 130       # Number of ASINs to process in one batch
PAGE_LOAD_DELAY = 2    # Delay between requests in seconds

# File Settings
PROGRESS_FILE = 'scraper_progress.json'  # Tracks progress between runs

#######################
# System Configuration #
#######################

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_credentials():
    """Gets valid user credentials from storage.
    
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def construct_amazon_url(asin):
    """Construct Amazon URL from ASIN"""
    asin = ''.join(c for c in asin if c.isalnum())
    return f"https://www.amazon.com/dp/{asin}"

def is_captcha_page(soup):
    return bool(soup.find('input', {'id': 'captchacharacters'})) or 'robot check' in soup.get_text().lower()

def load_progress():
    """Load the last processed ASIN index"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            last_index = data.get('last_processed_index', 0)
            print(f"Resuming from ASIN index {last_index}")
            return last_index
    return 0

def save_progress(last_index):
    """Save the last processed ASIN index"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({
            'last_processed_index': last_index,
            'last_updated': datetime.now().isoformat()
        }, f)
    print(f"Progress saved: completed through ASIN index {last_index}")

def process_chunk(asins, start_index):
    """Process a chunk of ASINs and return the data"""
    end_index = min(start_index + CHUNK_SIZE, len(asins))
    print(f"\nProcessing ASINs {start_index} to {end_index-1}")
    print(f"Started at: {datetime.now().strftime('%I:%M %p')}")
    
    data = []
    products_with_data = 0
    products_processed = 0
    
    session = requests.Session()
    session.headers.update(headers)
    
    for index in range(start_index, end_index):
        try:
            asin = asins[index]
            if not asin.strip():
                continue
            
            url = construct_amazon_url(asin)
            print(f"Processing ASIN {index}: {asin}")
            
            response = session.get(url)
            time.sleep(PAGE_LOAD_DELAY)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if is_captcha_page(soup):
                print("CAPTCHA detected - stopping batch")
                return data, products_processed, products_with_data, index
            
            bought_element = None
            match_found = False
            
            # Try specific ID selector
            specific_element = soup.select_one("#social-proofing-faceout-title-tk_bought > span")
            if specific_element and 'month' in specific_element.text.lower():
                bought_element = specific_element
                match_found = True
            
            # If not found, try pattern matching
            if not match_found:
                for element in soup.find_all(['span', 'div', 'p']):
                    if element.string and 'bought' in element.string.lower() and 'month' in element.string.lower():
                        bought_element = element
                        match_found = True
                        break
            
            products_processed += 1
            
            if bought_element:
                bought_count = bought_element.get_text(strip=True)
                print(f"Found: {bought_count}")
                data.append([asin, bought_count])
                products_with_data += 1
                
        except Exception as e:
            print(f"Error processing ASIN {index}: {str(e)}")
            continue
            
    return data, products_processed, products_with_data, end_index - 1

# Browser Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

# Main execution block
try:
    print("Initializing...")
    credentials = get_credentials()
    client = gspread.authorize(credentials)
    
    # Connect to the spreadsheet with error checking
    print("\nConnecting to Google Sheet...")
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        print(f"Found spreadsheet. Available worksheets: {[ws.title for ws in spreadsheet.worksheets()]}")
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        print(f"Successfully connected to worksheet: {WORKSHEET_NAME}")
        
    except gspread.exceptions.SpreadsheetNotFound:
        raise Exception(f"Could not find spreadsheet with ID: {SHEET_ID}")
    except gspread.exceptions.WorksheetNotFound:
        raise Exception(f"Could not find worksheet named: {WORKSHEET_NAME}")
    except Exception as e:
        raise Exception(f"Failed to access Google Sheet: {str(e)}")

    # Get ASINs from specified column
    print(f"\nReading ASINs from column {ASIN_COLUMN}...")
    try:
        all_values = sheet.col_values(ASIN_COLUMN)
        
        if len(all_values) < START_ROW:
            raise Exception(f"Sheet only has {len(all_values)} rows, needs at least {START_ROW}")
            
        asins = [asin for asin in all_values[START_ROW-1:] if asin.strip()]
        
        if not asins:
            raise Exception(f"No valid ASINs found after row {START_ROW}")
            
        total_asins = len(asins)
        print(f"Found {total_asins} valid ASINs to process")
        
    except Exception as e:
        raise Exception(f"Error reading ASINs: {str(e)}")

    # Load last processed position
    start_index = load_progress()
    
    print(f"Starting from index: {start_index}")
    print(f"Will process up to index: {min(start_index + CHUNK_SIZE, total_asins)}")
    
    if start_index >= total_asins:
        print("All ASINs have been processed!")
        exit()
    
    # Process current chunk
    chunk_data, processed, with_data, last_processed = process_chunk(asins, start_index)
    
    # Save progress
    save_progress(last_processed)
    
    print(f"\nChunk Summary:")
    print(f"ASINs processed in this chunk: {processed}")
    print(f"Products with data found: {with_data}")
    print(f"Last processed index: {last_processed}")
    
    # Write results to sheet
    if chunk_data:
        print("\nWriting results to sheet...")
        for entry in chunk_data:
            row_index = asins.index(entry[0]) + START_ROW
            sheet.update(values=[[entry[1]]], range_name=f'{RESULT_COLUMN}{row_index}')
            time.sleep(1)  # Small delay between sheet updates
    
    remaining = total_asins - (last_processed + 1)
    print(f"\nStatus: {last_processed + 1} ASINs processed, {remaining} remaining")
    
    if remaining > 0:
        print(f"Run the script again to process the next {min(CHUNK_SIZE, remaining)} ASINs")
    else:
        print("All ASINs have been processed!")

except Exception as e:
    print(f"\nError: {str(e)}")
    print("Progress has been saved - run the script again to continue from the last successful position")
