#!/usr/bin/env python3
"""
Google search client

Author: Daniel Torres Sandi
"""

import argparse
import os
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
        
        # Check for next page indicators
        pattern = re.compile(r'(?i)Next &gt;|More results|>&gt;</')
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
    
    page = 0
    try:
        while True:
            print_page = page + 1
            print(f"\t\t[+] page: {print_page}")
            
            # Perform search
            start = str(page * 100)
            urls_str = client.search(
                keyword=args.term,
                start=start,
                log_file=args.log,
                date=args.date,
                cookie=args.cookie
            )
            
            # Process and save results
            urls = urls_str.split(';')
            if args.output:
                append_to_file(args.output, urls)
            
            for url in urls:
                print(url)
            
            # Check for next page
            if args.log:
                has_next_page = check_next_page(args.log)
                if not has_next_page:
                    break
            else:
                # If no log file, just do one page
                break
            
            page += 1
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error performing search: {e}")
        sys.exit(1)
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
