import os
import re
import time
import random
import tempfile
from typing import List, Optional

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchFrameException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


# Custom exception for CAPTCHA detection
class CaptchaDetectedException(Exception):
    """Raised when Google CAPTCHA is detected"""
    pass



class SearchClient:
    """Google search client using Selenium WebDriver"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0"
    ]

    
    def __init__(self, profile_dir: Optional[str] = None, skip_login_prompt: bool = False):
        self.proxy_host: Optional[str] = None
        self.proxy_port: Optional[str] = None
        self.proxy_user: Optional[str] = None
        self.proxy_pass: Optional[str] = None
        self.google_url: str = "https://google.com"
        self.user_agent: str = self._get_random_user_agent()
        self.driver: Optional[webdriver.Chrome] = None
        self.skip_login_prompt: bool = skip_login_prompt
        
        # Use custom profile dir if provided, otherwise create a persistent one in home directory
        if profile_dir:
            self.profile_dir = profile_dir
        else:
            # Create a persistent profile directory in ~/.chrome_google_search
            home_dir = os.path.expanduser("~")
            self.profile_dir = os.path.join(home_dir, ".chrome_google_search")
            os.makedirs(self.profile_dir, exist_ok=True)
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(self.USER_AGENTS)
    
    def set_proxy(self, host: str, port: str, user: str = "", password: str = ""):
        """Configure proxy settings for the client"""
        self.proxy_host = host
        self.proxy_port = port
        self.proxy_user = user
        self.proxy_pass = password
    
    def _build_driver(self):
        """Initialize the Chrome WebDriver with configured options"""
        if self.driver is not None:
            return
        
        # Create profile directory if it doesn't exist
        os.makedirs(self.profile_dir, exist_ok=True)
        
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={self.user_agent}')
        
        # VISIBLE MODE - Remove headless to allow manual CAPTCHA solving
        options.add_argument('--headless')  # Enabled for headless environment
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use persistent profile to maintain cookies and session
        options.add_argument(f'--user-data-dir={self.profile_dir}')
        
        # Enhanced stealth options to bypass Google login detection
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-save-password-bubble')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
        
        # Set preferences to make browser appear more legitimate
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Randomize window size to appear more human-like
        window_width = random.randint(1200, 1600)
        window_height = random.randint(800, 1000)
        options.add_argument(f'--window-size={window_width},{window_height}')
        
        # Configure proxy if set
        if self.proxy_host and self.proxy_port:
            proxy_url = f"{self.proxy_host}:{self.proxy_port}"
            options.add_argument(f'--proxy-server={proxy_url}')
        
        # Use local ChromeDriver instead of webdriver-manager
        chromedriver_path = '/usr/bin/chromedriver'
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to avoid detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.user_agent
        })
        
        # Enhanced JavaScript to mask automation - execute multiple stealth scripts
        stealth_js = """
        // Overwrite the `navigator.webdriver` property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Overwrite the `navigator.plugins` to appear like a real browser
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Overwrite the `navigator.languages` to appear more realistic
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Mock the permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Remove traces of automation
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
        
        self.driver.execute_script(stealth_js)
        
        # Navigate to Google/Gmail on first launch to allow user to log in
        # This reduces captcha challenges when using a logged-in Google account
        if not self.skip_login_prompt:
            # Check if this is a fresh profile (no login yet)
            profile_first_run = os.path.join(self.profile_dir, "First Run")
            is_first_run = not os.path.exists(profile_first_run)
            
            if is_first_run:
                print("\n" + "="*80)
                print("⚠️  IMPORTANT: Manual Login Required")
                print("="*80)
                print("Google blocks automated browsers from logging in.")
                print("")
                print("SOLUTION: You need to log in manually using a REGULAR Chrome browser.")
                print("")
                print("Follow these steps:")
                print("1. Open a NEW regular Chrome browser window (NOT this automated one)")
                print("2. Use this command in another terminal:")
                print(f"   google-chrome --user-data-dir=\"{self.profile_dir}\"")
                print("3. In that browser, log into your Google account (gmail.com)")
                print("4. Close that browser window")
                print("5. Come back here and press ENTER to continue")
                print("")
                print("This profile will be reused, so you only need to do this ONCE.")
                print("="*80 + "\n")
                
                input("Press ENTER after you've logged in using the regular Chrome browser...")
                print("\nContinuing with search operations...\n")
            else:
                print("\n✓ Using existing Chrome profile (already logged in)\n")
    
    def search(self, keyword: str, date: str = "", lang: str = "", 
               start: str = "0", log_file: str = "", cookie: str = "") -> str:
        """
        Perform a Google search with the specified options
        
        Args:
            keyword: Search term
            date: Date filter (qdr parameter)
            lang: Language filter
            start: Start index for pagination
            log_file: If file exists, read from it; otherwise save HTML to it
            cookie: Cookie string to add to browser
            
        Returns:
            Semicolon-separated list of URLs
        """
        # Check if log_file exists and read from it
        if log_file and os.path.exists(log_file):
            print(f"Reading from existing file: {log_file}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                urls = self._extract_urls(content)
                return ";".join(urls)
            except Exception as e:
                print(f"Error reading log file: {e}")
                raise
        
        # Otherwise, perform live search
        self._build_driver()
        
        # Build search URL
        from urllib.parse import quote_plus
        search_url = (
            f"{self.google_url}/search?q={quote_plus(keyword)}"
            f"&oq={quote_plus(keyword)}&num=100&filter=0"
            f"&sourceid=chrome&client=gws-wiz&xssi=t"
            f"&gs_pcrt=undefined&hl=es-419&authuser=0"
            f"&psi=EOhuaO_wManY5OUP0uzO0Q8.1752098822626&dpr=1"
        )
        
        if start:
            search_url += f"&start={start}"
        if date:
            search_url += f"&tbs=qdr:{date}"
        if lang:
            search_url += f"&hl={lang}"
        
        print(f"searchURL: {search_url}")
        
        max_retries = 7
        for tries in range(max_retries):
            try:
                content = self._make_request(search_url, cookie)
                
                # Check for multiple CAPTCHA indicators
                if ("Our systems have detected unusual traffic from your computer network" in content or
                    "g-recaptcha" in content or 
                    "recaptcha" in content.lower()):
                    print("\n" + "="*80)
                    print("⚠️  CAPTCHA DETECTED!")
                    print("="*80)
                    print("Please solve the CAPTCHA in the Chrome browser window that just opened.")
                    print("Once solved, press ENTER to continue...")
                    print("="*80 + "\n")
                    
                    # Wait for user to solve CAPTCHA
                    input()
                    
                    # Retry the request after CAPTCHA is solved
                    print("Retrying search after CAPTCHA solving...")
                    continue
                
                # Check if no results were found
                if "did not match any documents" in content.lower():
                    # Save content to file
                    with open("google.html", "w", encoding="utf-8") as f:
                        f.write(content)
                    return ""
                
                # Save content to file
                with open("google.html", "w", encoding="utf-8") as f:
                    f.write(content)
                
                urls = self._extract_urls(content)
                
                if log_file:
                    try:
                        os.rename("google.html", log_file)
                    except Exception as e:
                        print(f"Warning: Could not rename log file: {e}")
                
                return ";".join(urls)
                
            except CaptchaDetectedException:
                # This exception shouldn't be raised anymore, but keep for compatibility
                print("\n" + "="*80)
                print("⚠️  CAPTCHA DETECTED!")
                print("="*80)
                print("Please solve the CAPTCHA in the Chrome browser window.")
                print("Once solved, press ENTER to continue...")
                print("="*80 + "\n")
                input()
                continue
            except Exception as e:
                if tries == max_retries - 1:
                    raise e
                time.sleep(5)
                continue
        
        raise Exception("max retries exceeded")
    
    def _make_request(self, url: str, cookie: str = "") -> str:
        """Make a request using Selenium WebDriver with improved wait conditions"""
        try:
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for page to load with explicit conditions
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                print("Warning: Page load timeout, continuing anyway...")
            
            # Add cookie if provided (only needed for first request in session)
            if cookie:
                # Add cookies after page has loaded
                for cookie_item in cookie.split(';'):
                    cookie_item = cookie_item.strip()
                    if '=' in cookie_item:
                        name, value = cookie_item.split('=', 1)
                        try:
                            self.driver.add_cookie({
                                'name': name.strip(), 
                                'value': value.strip(),
                                'domain': '.google.com'
                            })
                        except Exception as e:
                            # Ignore cookie errors and continue
                            pass
                # Reload page with cookies
                self.driver.get(url)
                # Wait for page to load again
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    print("Warning: Page reload timeout, continuing anyway...")
            
            # Small random delay to appear more human-like
            time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll page slightly to mimic human behavior
            try:
                self.driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(random.uniform(0.3, 0.7))
            except Exception:
                pass
            
            # Get page source
            return self.driver.page_source
            
        except TimeoutException as e:
            print(f"Timeout while loading page: {e}")
            # Return whatever we have so far
            return self.driver.page_source if self.driver else ""
        except StaleElementReferenceException:
            # If element goes stale, retry getting page source
            print("Stale element detected, retrying...")
            time.sleep(1)
            return self.driver.page_source if self.driver else ""
    
    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from HTML content - only from href attributes"""
        from urllib.parse import unquote, parse_qs, urlparse
        
        # Pattern to match Google redirect URLs: href="/url?...&url=<actual_url>&..."
        # Handles both & and &amp; (HTML-encoded ampersands)
        redirect_pattern = re.compile(
            r"href=[\"']?/url\?[^\"'>]*?(?:&|&amp;)url=([^&\"'> ;]+)",
            re.IGNORECASE
        )
        
        # Pattern to match direct URLs in href attributes
        # Matches: href="http://example.com" or href='http://example.com'
        direct_pattern = re.compile(
            r"href=[\"']?(https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?)[\"\']?",
            re.IGNORECASE
        )
        
        # Use dict to maintain order while removing duplicates (Python 3.7+)
        unique_urls = {}
        
        # First, extract URLs from Google redirect format
        redirect_matches = redirect_pattern.findall(content)
        for encoded_url in redirect_matches:
            # Decode the URL-encoded string
            url = unquote(encoded_url)
            # Clean up the URL
            url = url.rstrip('.,!?:;\'"&amp')
            
            # Skip unwanted patterns
            if any(unwanted in url for unwanted in [
                'google.com', 'gstatic.com', 'accounts.google',
                'support.google', 'w3.org', 'policies.google'
            ]):
                continue
            
            unique_urls[url] = None
        
        # Then, extract direct URLs (fallback for any non-redirect hrefs)
        direct_matches = direct_pattern.findall(content)
        for url in direct_matches:
            # Clean up the URL
            url = url.rstrip('.,!?:;\'"&amp')
            
            # Skip unwanted patterns
            if any(unwanted in url for unwanted in [
                'google.com', 'gstatic.com', 'accounts.google',
                'support.google', 'w3.org', 'policies.google'
            ]):
                continue
            
            unique_urls[url] = None
        
        return list(unique_urls.keys())
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
