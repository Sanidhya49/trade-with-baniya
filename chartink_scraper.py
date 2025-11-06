"""
Chartink Screener Automation
Scrapes stock data from Chartink screener with Nifty 100 filter and saves to Excel
"""

import time
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import platform


class ChartinkScraper:
    def __init__(self, headless=False, use_existing_chrome=False, csrf_token=None):
        """
        Initialize the scraper with Chrome WebDriver
        
        Args:
            headless: Run browser in headless mode (default: False)
            use_existing_chrome: Try to connect to existing Chrome instance (default: False)
            csrf_token: CSRF token for API requests (default: None)
        """
        self.driver = None
        self.headless = headless
        self.use_existing_chrome = use_existing_chrome
        self.csrf_token = csrf_token
        self.session = requests.Session()
        # Will fetch CSRF token dynamically if not provided or if it fails
        self._setup_session()
        # Only setup driver if we need Selenium (will be done lazily)
        self.driver_setup = False
    
    def _setup_session(self):
        """Setup requests session with headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://chartink.com/',
            'Origin': 'https://chartink.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        })
    
    def _fetch_csrf_token(self, url):
        """
        Fetch CSRF token from the page (following Chartink's pattern)
        
        Args:
            url: Chartink screener URL
        
        Returns:
            str: CSRF token or None
        """
        try:
            print("Fetching CSRF token from page...")
            # Get the screener page first
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML to find CSRF token from meta tag (Chartink's method)
            soup = BeautifulSoup(response.content, 'lxml')
            meta = soup.find("meta", {"name": "csrf-token"})
            
            if meta and meta.get("content"):
                csrf_token = meta["content"]
                print(f"Found CSRF token in meta tag: {csrf_token[:20]}...")
                self.csrf_token = csrf_token
                # Update session headers with new token (lowercase x-csrf-token as per Chartink)
                self.session.headers.update({
                    'x-csrf-token': csrf_token
                })
                return csrf_token
            else:
                print("Could not find CSRF token in meta tag")
                return None
                
        except Exception as e:
            print(f"Error fetching CSRF token: {e}")
            return None
    
    def _ensure_driver_setup(self):
        """Lazily setup driver only when needed"""
        if not self.driver_setup:
            self.setup_driver()
            self.driver_setup = True
    
    def setup_driver(self):
        """Setup Chrome WebDriver with user's default Chrome profile"""
        chrome_options = Options()
        
        # Get the default Chrome user data directory based on OS
        if platform.system() == "Windows":
            user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
        elif platform.system() == "Darwin":  # macOS
            user_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Google', 'Chrome')
        else:  # Linux
            user_data_dir = os.path.join(os.path.expanduser('~'), '.config', 'google-chrome')
        
        # Use the Default profile
        profile_path = os.path.join(user_data_dir, 'Default')
        
        # Use a completely separate temporary directory for Chrome to avoid conflicts
        # This prevents issues when Chrome is already running
        import tempfile
        temp_chrome_dir = os.path.join(tempfile.gettempdir(), 'chrome_automation_' + str(int(time.time())))
        
        try:
            os.makedirs(temp_chrome_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={temp_chrome_dir}')
            print(f"Using temporary Chrome directory: {temp_chrome_dir}")
        except Exception as e:
            print(f"Warning: Could not create temporary Chrome directory: {e}")
            # Fallback: try to use automation profile in user's Chrome directory
            if os.path.exists(user_data_dir):
                automation_profile = os.path.join(user_data_dir, 'AutomationProfile')
                try:
                    if not os.path.exists(automation_profile):
                        os.makedirs(automation_profile, exist_ok=True)
                    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
                    chrome_options.add_argument('--profile-directory=AutomationProfile')
                    print(f"Using Chrome automation profile: {automation_profile}")
                except:
                    print("Using default Chrome profile (may require Chrome to be closed)")
            else:
                print("Using default Chrome profile...")
        
        # Additional options
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Try to connect to existing Chrome instance if requested
        if self.use_existing_chrome:
            try:
                print("Attempting to connect to existing Chrome instance...")
                # Connect to existing Chrome with remote debugging
                chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✓ Connected to existing Chrome instance")
                return
            except Exception as e:
                print(f"Could not connect to existing Chrome: {e}")
                print("Make sure Chrome is running with: chrome.exe --remote-debugging-port=9222")
                print("Falling back to opening new Chrome window with your profile...")
                # Remove the debugger address option for new instance
                chrome_options = Options()
                if os.path.exists(user_data_dir):
                    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
                    chrome_options.add_argument('--profile-directory=Default')
                if self.headless:
                    chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Using temporary directory, so no need to close Chrome
        if not self.use_existing_chrome:
            print("\n✓ Using temporary Chrome directory - Chrome can remain open.\n")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
        except Exception as e:
            error_msg = str(e).lower()
            if 'user data directory is already in use' in error_msg or 'profile' in error_msg:
                print("\n❌ Error: Chrome is already running with your default profile.")
                print("   Please close all Chrome windows and try again.")
                print("   Or start Chrome manually with: chrome.exe --remote-debugging-port=9222")
                print("   Then run the script with use_existing_chrome=True")
            else:
                print(f"Error setting up Chrome driver: {e}")
            print("\nMake sure ChromeDriver is installed and in your PATH")
            raise
    
    def navigate_to_screener(self, url):
        """
        Navigate to the Chartink screener URL
        
        Args:
            url: The Chartink screener URL
        """
        if not self.driver:
            self._ensure_driver_setup()
        print(f"Loading page: {url}")
        self.driver.get(url)
        time.sleep(3)  # Wait for initial page load
    
    def change_filter_to_nifty100(self):
        """
        Change the filter from 'future' to 'Nifty 100' segment
        """
        try:
            print("Attempting to change filter to Nifty 100...")
            
            # Wait for the page to load completely
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for filter/segment selection elements
            # Chartink typically has segment filters that can be changed
            # We'll look for buttons or dropdowns that might contain "future" or segment options
            
            # Try to find and click on segment/filter buttons
            # Common selectors for Chartink filters
            segment_selectors = [
                "//button[contains(text(), 'Future')]",
                "//button[contains(text(), 'FUTURE')]",
                "//select[contains(@class, 'segment')]",
                "//div[contains(@class, 'segment')]//button",
                "//span[contains(text(), 'Future')]",
                "//a[contains(text(), 'Future')]",
            ]
            
            # Also try to find Nifty 100 option
            nifty100_selectors = [
                "//button[contains(text(), 'Nifty 100')]",
                "//button[contains(text(), 'NIFTY 100')]",
                "//button[contains(text(), 'Nifty100')]",
                "//option[contains(text(), 'Nifty 100')]",
                "//option[contains(text(), 'NIFTY 100')]",
                "//span[contains(text(), 'Nifty 100')]",
                "//a[contains(text(), 'Nifty 100')]",
            ]
            
            # First, try to find and click Nifty 100 directly
            for selector in nifty100_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    print(f"Successfully clicked Nifty 100 using selector: {selector}")
                    time.sleep(2)
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # If direct click didn't work, try to find Future and replace it
            for selector in segment_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    # Click to open dropdown or change filter
                    element.click()
                    time.sleep(1)
                    
                    # Now try to find Nifty 100 option
                    for nifty_selector in nifty100_selectors:
                        try:
                            nifty_element = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, nifty_selector))
                            )
                            nifty_element.click()
                            print(f"Successfully changed filter to Nifty 100")
                            time.sleep(2)
                            return True
                        except (TimeoutException, NoSuchElementException):
                            continue
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # Alternative: Try to modify filter text directly
            # Look for filter input fields or text areas
            filter_input_selectors = [
                "//textarea[contains(@placeholder, 'Scan')]",
                "//textarea[contains(@placeholder, 'filter')]",
                "//textarea",
                "//input[@type='text']",
                "//div[@contenteditable='true']",
                "//div[contains(@class, 'filter')]//textarea",
                "//div[contains(@class, 'magic')]//textarea",
            ]
            
            for selector in filter_input_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        try:
                            text = element.get_attribute('value') or element.text or ""
                            # Check if this looks like a filter input
                            if 'future' in text.lower() or 'segment' in text.lower() or 'nifty' in text.lower() or len(text) > 10:
                                # Clear and set Nifty 100 filter
                                element.clear()
                                time.sleep(0.5)
                                # Use JavaScript to set value for contenteditable divs
                                if element.tag_name == 'div' and element.get_attribute('contenteditable') == 'true':
                                    self.driver.execute_script("arguments[0].innerText = arguments[1];", element, "Stock passes all of the below filters in nifty 100 segment:")
                                else:
                                    element.send_keys("Stock passes all of the below filters in nifty 100 segment:")
                                time.sleep(1)
                                print("Updated filter text to Nifty 100")
                                return True
                        except Exception as e:
                            continue
                except Exception as e:
                    continue
            
            # Try to find and modify existing filter conditions
            try:
                # Look for filter condition text that mentions "future"
                filter_text_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'future') or contains(text(), 'Future') or contains(text(), 'FUTURE')]")
                for element in filter_text_elements:
                    try:
                        parent = element.find_element(By.XPATH, "./..")
                        if parent:
                            # Try to click and modify
                            parent.click()
                            time.sleep(0.5)
                            # Look for edit/change option
                            edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Edit')] | //button[contains(text(), 'Change')] | //a[contains(text(), 'Edit')]")
                            if edit_buttons:
                                edit_buttons[0].click()
                                time.sleep(1)
                    except:
                        continue
            except:
                pass
            
            print("Warning: Could not automatically change filter to Nifty 100.")
            print("Please manually change the filter to 'Nifty 100' segment if needed.")
            return False
            
        except Exception as e:
            print(f"Error changing filter: {e}")
            return False
    
    def run_scan(self):
        """Click the 'Run Scan' button to execute the screener"""
        try:
            print("Running scan...")
            run_scan_selectors = [
                "//button[contains(text(), 'Run Scan')]",
                "//button[contains(text(), 'RUN SCAN')]",
                "//button[contains(@class, 'run-scan')]",
                "//button[contains(@class, 'btn-run')]",
                "//button[.//span[contains(text(), 'Run Scan')]]",
            ]
            
            for selector in run_scan_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    print("Scan started...")
                    time.sleep(5)  # Wait for results to load
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            print("Warning: Could not find Run Scan button. Results may already be displayed.")
            return False
        except Exception as e:
            print(f"Error running scan: {e}")
            return False
    
    def extract_stock_data(self):
        """
        Extract stock data from the table
        
        Returns:
            list: List of dictionaries containing stock data
        """
        stocks_data = []
        
        try:
            print("Extracting stock data from table...")
            
            # Wait for table to load - try multiple selectors
            table = None
            table_selectors = [
                (By.TAG_NAME, "table"),
                (By.CSS_SELECTOR, "table.table"),
                (By.CSS_SELECTOR, "table.dataTable"),
                (By.CSS_SELECTOR, "div[class*='table'] table"),
                (By.XPATH, "//table"),
            ]
            
            for selector_type, selector_value in table_selectors:
                try:
                    table = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    print(f"Found table using selector: {selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if not table:
                print("Table not found. Trying alternative methods...")
                return self.try_csv_export_method()
            
            time.sleep(3)  # Additional wait for data to populate
            
            # Get table headers
            headers = []
            try:
                # Try thead first
                header_row = table.find_element(By.TAG_NAME, "thead")
                header_cells = header_row.find_elements(By.TAG_NAME, "th")
                if header_cells:
                    headers = [cell.text.strip() for cell in header_cells if cell.text.strip()]
            except NoSuchElementException:
                pass
            
            # If no headers from thead, try first row
            if not headers:
                try:
                    tbody = table.find_element(By.TAG_NAME, "tbody")
                    first_row = tbody.find_element(By.TAG_NAME, "tr")
                    header_cells = first_row.find_elements(By.TAG_NAME, "td")
                    if header_cells:
                        headers = [cell.text.strip() for cell in header_cells if cell.text.strip()]
                except:
                    pass
            
            # If still no headers, use common Chartink headers
            if not headers:
                headers = ["Sr.", "Stock Name", "Symbol", "Links", "% Chg", "Price", "Volume"]
                print("Using default headers")
            
            print(f"Found headers: {headers}")
            
            # Get table rows - try multiple methods
            rows = []
            try:
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
            except NoSuchElementException:
                # If no tbody, get rows directly from table
                rows = table.find_elements(By.XPATH, ".//tr[position()>1]")  # Skip header row
            
            # Also try finding rows by data attributes
            if not rows:
                rows = table.find_elements(By.XPATH, ".//tr[td]")
            
            print(f"Found {len(rows)} rows")
            
            # Extract data from each row
            for row_idx, row in enumerate(rows, start=1):
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) == 0:
                        continue
                    
                    row_data = {}
                    for idx, cell in enumerate(cells):
                        header = headers[idx] if idx < len(headers) else f"Column_{idx+1}"
                        cell_text = cell.text.strip()
                        # Skip empty cells or header-like cells
                        if cell_text and cell_text.lower() not in ['sr.', 'stock name', 'symbol', '% chg', 'price', 'volume']:
                            row_data[header] = cell_text
                    
                    # Only add if we have meaningful data (at least 2 columns with data)
                    if row_data and len([v for v in row_data.values() if v]) >= 2:
                        stocks_data.append(row_data)
                        
                except Exception as e:
                    print(f"Error extracting row {row_idx}: {e}")
                    continue
            
            print(f"Successfully extracted {len(stocks_data)} stocks")
            
            # If no data found, try CSV export method
            if not stocks_data:
                print("No data extracted from table. Trying CSV export method...")
                return self.try_csv_export_method()
            
        except TimeoutException:
            print("Timeout: Table not found or not loaded. Trying CSV export method...")
            return self.try_csv_export_method()
        except Exception as e:
            print(f"Error extracting stock data: {e}")
            print("Trying CSV export method as fallback...")
            return self.try_csv_export_method()
        
        return stocks_data
    
    def try_csv_export_method(self):
        """
        Alternative method: Try to download CSV and parse it
        
        Returns:
            list: List of dictionaries containing stock data
        """
        try:
            print("Attempting to use CSV export button...")
            
            # Look for CSV or Excel export buttons
            export_selectors = [
                "//button[contains(text(), 'CSV')]",
                "//button[contains(text(), 'Excel')]",
                "//a[contains(text(), 'CSV')]",
                "//a[contains(text(), 'Excel')]",
                "//button[contains(@class, 'csv')]",
                "//button[contains(@class, 'excel')]",
            ]
            
            for selector in export_selectors:
                try:
                    export_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    # Note: Direct CSV download might require handling file downloads
                    # For now, we'll just click and see if we can get the data
                    print(f"Found export button: {selector}")
                    # We'll skip auto-clicking download buttons as they require file handling
                    break
                except TimeoutException:
                    continue
            
            return []
            
        except Exception as e:
            print(f"CSV export method also failed: {e}")
            return []
    
    def save_to_excel(self, stocks_data, filename="chartink_stocks.xlsx"):
        """
        Save stock data to Excel file
        
        Args:
            stocks_data: List of dictionaries containing stock data
            filename: Output Excel filename
        """
        if not stocks_data:
            print("No data to save!")
            return False
        
        try:
            # Create DataFrame
            df = pd.DataFrame(stocks_data)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Save to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"Data saved successfully to {filename}")
            print(f"Total stocks saved: {len(df)}")
            return True
            
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fetch_data_via_api(self, screener_id="stock-screener-open-high-open-low", filter_condition=None, url=None):
        """
        Fetch stock data via Chartink API
        
        Args:
            screener_id: Screener ID or slug from URL (default: "stock-screener-open-high-open-low")
            filter_condition: Filter condition string (default: None, uses Nifty 100)
            url: Screener URL to fetch CSRF token from (optional)
        
        Returns:
            list: List of dictionaries containing stock data
        """
        # Fetch CSRF token if not available or if previous attempt failed
        if not self.csrf_token and url:
            self._fetch_csrf_token(url)
        
        if not self.csrf_token:
            print("No CSRF token available. Cannot use API.")
            return []
        
        try:
            print("Attempting to fetch data via API...")
            
            # Default filter condition for Nifty 200 with Daily Open = Daily High
            if filter_condition is None:
                # Chartink scan clause format for Nifty 200 with Daily Open = Daily High condition
                filter_condition = "( {nifty200} ( latest open = latest high ) )"
            
            # Chartink API endpoint
            api_url = "https://chartink.com/screener/process"
            
            # Prepare the condition as form data (following Chartink's pattern)
            condition = {"scan_clause": filter_condition}
            
            # Get CSRF token from the page if not already available
            if not self.csrf_token and url:
                self._fetch_csrf_token(url)
            
            if not self.csrf_token:
                print("No CSRF token available. Cannot make API request.")
                return []
            
            # Set header with CSRF token (lowercase x-csrf-token as per Chartink)
            headers = {"x-csrf-token": self.csrf_token}
            
            try:
                print(f"Sending POST request to {api_url}")
                print(f"Scan clause: {filter_condition}")
                
                # Make POST request with data (form-urlencoded) and headers
                response = self.session.post(
                    api_url,
                    headers=headers,
                    data=condition,  # Send as form data
                    timeout=30
                )
                    
                print(f"API returned status code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                        
                        # Chartink typically returns data in 'data' key
                        if isinstance(data, dict) and 'data' in data:
                            stocks_data = data['data']
                            if stocks_data and len(stocks_data) > 0:
                                print(f"Successfully fetched {len(stocks_data)} stocks via API")
                                # Normalize the data
                                normalized_data = self._normalize_stock_data(stocks_data)
                                return normalized_data
                        else:
                            # Try to parse directly
                            stocks_data = self._parse_api_response(data)
                            if stocks_data:
                                print(f"Successfully fetched {len(stocks_data)} stocks via API")
                                return stocks_data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Response text: {response.text[:500]}")
                elif response.status_code == 419:
                    print(f"CSRF token mismatch. Response: {response.text}")
                    # Try to fetch fresh CSRF token and retry once
                    if url:
                        print("Attempting to fetch fresh CSRF token...")
                        new_token = self._fetch_csrf_token(url)
                        if new_token:
                            print(f"Retrying with fresh CSRF token: {new_token[:20]}...")
                            # Retry the request with new token
                            retry_headers = {"x-csrf-token": new_token}
                            retry_response = self.session.post(
                                api_url,
                                headers=retry_headers,
                                data=condition,  # Use condition, not form_data
                                timeout=30
                            )
                            print(f"Retry API returned status code: {retry_response.status_code}")
                            if retry_response.status_code == 200:
                                try:
                                    data = retry_response.json()
                                    print(f"Retry API Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                                    if isinstance(data, dict) and 'data' in data:
                                        stocks_data = data['data']
                                        if stocks_data and len(stocks_data) > 0:
                                            print(f"Successfully fetched {len(stocks_data)} stocks via API (after token refresh)")
                                            normalized_data = self._normalize_stock_data(stocks_data)
                                            return normalized_data
                                    else:
                                        stocks_data = self._parse_api_response(data)
                                        if stocks_data:
                                            print(f"Successfully fetched {len(stocks_data)} stocks via API (after token refresh)")
                                            return stocks_data
                                except Exception as e:
                                    print(f"Error parsing retry response: {e}")
                            else:
                                print(f"Retry also failed with status {retry_response.status_code}: {retry_response.text[:200]}")
                    print("CSRF token refresh failed. Falling back to Selenium...")
                    return []
                else:
                    print(f"API returned error: {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
            
            print("API method failed. Falling back to Selenium...")
            return []
            
        except Exception as e:
            print(f"Error fetching data via API: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _normalize_stock_data(self, stocks_data):
        """
        Normalize stock data from Chartink API response
        
        Args:
            stocks_data: Raw stock data from API
        
        Returns:
            list: List of dictionaries containing normalized stock data
        """
        normalized_data = []
        
        try:
            for item in stocks_data:
                if isinstance(item, dict):
                    normalized_data.append(item)
                elif isinstance(item, (list, tuple)):
                    # If it's a list, convert to dict with default column names
                    row_dict = {}
                    for idx, value in enumerate(item):
                        row_dict[f"Column_{idx+1}"] = value
                    normalized_data.append(row_dict)
            
            return normalized_data
        except Exception as e:
            print(f"Error normalizing stock data: {e}")
            return stocks_data if isinstance(stocks_data, list) else []
    
    def _parse_api_response(self, data):
        """
        Parse API response from Chartink
        
        Args:
            data: JSON response from API
        
        Returns:
            list: List of dictionaries containing stock data
        """
        stocks_data = []
        
        try:
            # Chartink API might return data in different formats
            # Try to extract stock data from various possible structures
            
            # Format 1: Direct data array
            if isinstance(data, list):
                stocks_data = data
            # Format 2: Nested data object
            elif isinstance(data, dict):
                # Try common keys
                if 'data' in data:
                    stocks_data = data['data']
                elif 'stocks' in data:
                    stocks_data = data['stocks']
                elif 'results' in data:
                    stocks_data = data['results']
                elif 'rows' in data:
                    stocks_data = data['rows']
                else:
                    # If it's a dict with numeric keys, it might be the data itself
                    if all(isinstance(k, (int, str)) for k in data.keys()):
                        stocks_data = list(data.values())
            
            # Normalize the data structure
            return self._normalize_stock_data(stocks_data)
            
        except Exception as e:
            print(f"Error parsing API response: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape(self, url, output_file="chartink_stocks.xlsx", change_filter=True):
        """
        Main method to scrape the screener
        
        Args:
            url: Chartink screener URL
            output_file: Output Excel filename
            change_filter: Whether to change filter to Nifty 100 (default: True)
        """
        try:
            # Try API first if CSRF token is available or can be fetched
            print("Trying API method first...")
            # Extract screener identifier from URL
            screener_id = url.split('/')[-1] if '/' in url else "stock-screener-open-high-open-low"
            stocks_data = self.fetch_data_via_api(screener_id, url=url)
            
            if stocks_data:
                # Save to Excel
                self.save_to_excel(stocks_data, output_file)
                return stocks_data
            else:
                print("API method failed. Falling back to Selenium scraping...")
            
            # Fallback to Selenium scraping
            self._ensure_driver_setup()
            
            # Navigate to the page
            self.navigate_to_screener(url)
            
            # Change filter to Nifty 100 if requested
            if change_filter:
                self.change_filter_to_nifty100()
            
            # Run the scan
            self.run_scan()
            
            # Extract data
            stocks_data = self.extract_stock_data()
            
            # Save to Excel
            if stocks_data:
                self.save_to_excel(stocks_data, output_file)
                return stocks_data
            else:
                print("No stock data found!")
                return []
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


def main():
    """Main function to run the scraper"""
    url = "https://chartink.com/screener/stock-screener-open-high-open-low"
    output_file = "chartink_nifty200_stocks.xlsx"
    
    # CSRF token will be fetched automatically from the page
    csrf_token = None
    
    scraper = None
    try:
        # Initialize scraper (CSRF token will be fetched automatically)
        # Set use_existing_chrome=True if you want to use an already running Chrome
        # (Chrome must be started with: chrome.exe --remote-debugging-port=9222)
        scraper = ChartinkScraper(
            headless=False, 
            use_existing_chrome=False,
            csrf_token=csrf_token
        )
        
        # Scrape the data
        stocks_data = scraper.scrape(url, output_file, change_filter=True)
        
        if stocks_data:
            print(f"\n✓ Successfully scraped {len(stocks_data)} stocks")
            print(f"✓ Data saved to {output_file}")
        else:
            print("\n✗ No data was scraped. Please check the website and try again.")
            
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()

