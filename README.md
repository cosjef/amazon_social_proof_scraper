# Amazon Social Proof Scraper

A Python-based tool for scraping and analyzing Amazon product social proof data. Social proof is the tagline on an ASIN that states "X amount purchased in last month"

## Overview

This script automates the collection of Amazon's social proof metrics by:
- Reading ASINs from a specified Google Sheet
- Scraping the "X purchased in last month" data from Amazon
- Writing results back to the Google Sheet
- Handling rate limiting and progress tracking

## Prerequisites

- Python 3.x
- Google Sheets API access
- client_secrets.json file from Google Cloud Console

## Installation

1. Clone this repository
2. Create and activate a Python virtual environment
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure credentials:
   - Copy `client_secrets.json.example` to `client_secrets.json`
   - Add your Google API credentials
   - The `token.pickle` file will be generated on first run

## Google Sheet Template

Your Google Sheet should be structured as follows:

| A          | B        | C           | D      | E      | F      | G      | H      | I               |
|------------|----------|-------------|--------|--------|--------|--------|--------|-----------------|
| Product    | Category | ASIN        | ...    | ...    | ...    | ...    | ...    | Social Proof    |
| Product 1  | Cat A    | B08XXXXXX   | ...    | ...    | ...    | ...    | ...    | [auto-filled]   |
| Product 2  | Cat B    | B07XXXXXX   | ...    | ...    | ...    | ...    | ...    | [auto-filled]   |

Key points:
- ASINs must be in Column C (configurable in script)
- Results will be written to Column I (configurable in script)
- Data starts from row 3 (configurable in script)
- ASINs should be clean (script will remove non-alphanumeric characters)
- Other columns can contain any data you need

## Configuration

The script uses several configurable settings:

- Google Sheet Settings
  - SHEET_ID: ID from your Google Sheets URL
  - WORKSHEET_NAME: Name of the specific worksheet/tab
  
- Data Location Settings
  - ASIN_COLUMN: Column containing ASINs (e.g., 3 for Column C)
  - START_ROW: First row containing actual data
  - RESULT_COLUMN: Column where results will be written
  
- Processing Settings
  - CHUNK_SIZE: Number of ASINs to process in one batch
  - PAGE_LOAD_DELAY: Delay between requests in seconds

## Usage

```bash
python3 scraper.py
```

The script will:
1. Authenticate with Google Sheets
2. Load ASINs from the specified column
3. Process ASINs in chunks to avoid rate limiting
4. Save progress after each chunk
5. Write results back to the Google Sheet

## Security Notes

- Never commit `client_secrets.json` or `token.pickle` to version control
- Review Amazon's Terms of Service and rate limiting guidelines
- Use appropriate delays between requests
- The script includes basic rate limiting and CAPTCHA detection

## Dependencies

- gspread: Google Sheets API wrapper
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- google-oauth-oauthlib: Google authentication
- google-auth: Google authentication
- google-auth-oauthlib: Google authentication

## License

MIT