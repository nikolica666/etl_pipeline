"""
main_crawler.py — Entry point for website crawling and HTML text extraction.
"""

import argparse
from crawler.crawler import crawl_domain

def main():

    parser = argparse.ArgumentParser(description="Crawl websites and extract readable text.")
    parser.add_argument("url", help="Base URL to crawl, e.g. https://www.index.hr")
    parser.add_argument("--limit", type=int, default=10, help="Max number of pages to crawl per domain")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--output", default="data", help="Output directory for extracted text")
    
    args = parser.parse_args()

    crawl_domain(args.url, output_dir=args.output, limit=args.limit, delay=args.delay)

if __name__ == "__main__":
    main()
