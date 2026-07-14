#!/usr/bin/env python3
"""
Google search client

Author: Daniel Torres Sandi
"""

import argparse
import os
import random
import re
import sys
import time

# Add the googlesearch module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from googlesearch.googlesearch import SearchClient


BANNER = """
Google search                                                    

Autor: Daniel Torres Sandi
"""

GOOGLE_URL = "https://google.com"
DEBUG = False


def usage():
    """Print usage information"""
    print(BANNER)
    print("Usage:")
    print("-t : Search term")
    print("-o : Output file")
    print("-h : Help")
    print("-d : Date")
    print("-l : Log file")
    print("-c : Cookie string")
    print("Example: googlesearch-client.py -t 'site:gob.bo' -l google2.html -o lista.txt")


def append_to_file(filename: str, urls: list):
    """Append URLs to a file"""
    with open(filename, 'a', encoding='utf-8') as f:
        for url in urls:
            url = url.strip()
            if url:
                f.write(url + '\n')


def check_next_page(log_file: str) -> bool:
    """Check if there is a next page in the results"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for next page indicators (including Spanish and aria-labels)
        pattern = re.compile(r'(?i)Next &gt;|Siguiente &gt;|More results|>&gt;</|aria-label="Página siguiente"|aria-label="Next page"')
        matches = pattern.findall(content)
        
        if DEBUG:
            print(f"next_link count: {len(matches)}")
        
        return len(matches) > 0
    except Exception as e:
        print(f"Error reading log file: {e}")
        return False



def main():
    parser = argparse.ArgumentParser(
        description="Google Search Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: googlesearch-client.py -t 'site:gob.bo' -l google2.html -o lista.txt"
    )
    
    parser.add_argument('-t', '--term', type=str, default='', help='Search term')
    parser.add_argument('-o', '--output', type=str, default='', help='Output file')
    parser.add_argument('-l', '--log', type=str, default='', help='Log file')
    parser.add_argument('-d', '--date', type=str, default='', help='Date filter')
    parser.add_argument('-c', '--cookie', type=str, default='', help='Cookie string')
    
    args = parser.parse_args()
    
    if not args.term:
        print(BANNER)
        parser.print_help()
        return
    
    # Color output using ANSI codes
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    print(f"{YELLOW}\t[+] Search term: {args.term}{RESET}")
    print(f"{BLUE}\t[+] Searching on Google{RESET}")
    
    client = SearchClient()
    client.google_url = GOOGLE_URL
    
    all_unique_urls = []
    seen_urls = set()
    
    page = 0
    try:
        while len(all_unique_urls) < 100:
            print_page = page + 1
            print(f"\t\t[+] page: {print_page} (URLs found: {len(all_unique_urls)})")
            
            # Format unique log filename for this page to avoid cache conflict
            if args.log:
                base, ext = os.path.splitext(args.log)
                page_log_file = f"{base}_{print_page}{ext}"
                is_temp_log = False
            else:
                page_log_file = f"temp_search_log_{print_page}.html"
                is_temp_log = True
            
            # Perform search with dynamic start offset based on current unique URLs found
            start = str(len(all_unique_urls))
            urls_str = client.search(
                keyword=args.term,
                start=start,
                log_file=page_log_file,
                date=args.date,
                cookie=args.cookie
            )
            
            if not urls_str:
                print("\t\t[-] No URLs returned on this page.")
                break
                
            # Process and save results
            urls = urls_str.split(';')
            new_urls_on_page = []
            for url in urls:
                url = url.strip()
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_unique_urls.append(url)
                    new_urls_on_page.append(url)
            
            if not new_urls_on_page:
                print("\t\t[-] No new unique URLs found on this page. Stopping.")
                break
                
            if args.output:
                append_to_file(args.output, new_urls_on_page)
            
            for url in new_urls_on_page:
                print(url)
            
            # Check for next page
            has_next_page = check_next_page(page_log_file)
            
            # Clean up temp file immediately after checking if it was a temp log
            if is_temp_log and os.path.exists(page_log_file):
                try:
                    os.remove(page_log_file)
                except Exception:
                    pass
                    
            if not has_next_page:
                print("\t\t[-] No next page indicator found.")
                break
            
            page += 1
            # Random sleep delay (5-10 seconds) to appear more human-like and avoid CAPTCHAs
            wait_time = random.uniform(5.0, 10.0)
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error performing search: {e}")
        sys.exit(1)
    finally:
        # Clean up any leftover temp files
        if not args.log:
            for p in range(1, page + 2):
                temp_file = f"temp_search_log_{p}.html"
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass
        # Clean up client
        client.close()


if __name__ == "__main__":
    main()
