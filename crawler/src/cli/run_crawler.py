#!/usr/bin/env python3
"""
Command line wrapper for the web crawler.

This script provides a command line interface for running the crawler
with configurable parameters.
"""

import argparse
import logging
import sys
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.company_data.statistics import (
    compute_crawling_statistics,
    save_statistics_to_file,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_crawler(
    domains_file: str = "configs/companies-domains.csv", domain_limit: int = 10
) -> str:
    """
    Run the web crawler and generate comprehensive statistics.

    Args:
        domains_file: Path to CSV file containing domains to crawl
        domain_limit: Maximum number of domains to process

    Returns:
        Path to the main output file
    """
    start_time = datetime.now()
    logger.info(f"Starting crawler at {start_time.isoformat()}")

    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"data/companies_{timestamp}.json"

    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            output_filename: {
                "format": "json",
                "overwrite": True,
            },
        },
    )

    process = CrawlerProcess(settings=settings)

    process.crawl(
        "company_spider", domains_file=domains_file, domain_limit=domain_limit
    )
    process.start()

    end_time = datetime.now()
    running_time = (end_time - start_time).total_seconds()
    logger.info(
        f"Crawler finished at {end_time.isoformat()}. Running time: {running_time:.2f} seconds"
    )

    stats = compute_crawling_statistics(
        output_filename, domains_file, domain_limit, start_time, end_time, running_time
    )
    save_statistics_to_file(stats, output_filename)

    return output_filename


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
        default=10,
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
