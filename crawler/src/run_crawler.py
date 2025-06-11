#!/usr/bin/env python3
"""
Command line wrapper for the web crawler.

This script provides a command line interface for running the crawler
with configurable parameters.
"""

import argparse
import logging
import sys

from src.crawler import run_crawler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="Run the web crawler to extract company data"
    )

    parser.add_argument(
        "--domains-file",
        default="configs/companies-domains.csv",
        help="Path to CSV file containing domains to crawl (default: configs/companies-domains.csv)",
    )

    parser.add_argument(
        "--domain-limit",
        type=int,
        default=100,
        help="Maximum number of domains to process (default: 100)",
    )

    args = parser.parse_args()

    try:
        logger.info(f"Starting crawler with domain limit: {args.domain_limit}")
        logger.info(f"Using domains file: {args.domains_file}")

        output_file = run_crawler(
            domains_file=args.domains_file, domain_limit=args.domain_limit
        )

        logger.info(f"Crawler completed successfully. Output saved to: {output_file}")

    except Exception as e:
        logger.error(f"Crawler failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
