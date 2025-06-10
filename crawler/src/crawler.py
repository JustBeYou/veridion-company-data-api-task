import logging
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.company_data.statistics import (
    compute_crawling_statistics,
    save_statistics_to_file,
)

logger = logging.getLogger(__name__)


def run_crawler(
    domains_file: str = "configs/companies-domains.csv", domain_limit: int = 5
) -> str:
    """
    Run the web crawler and generate comprehensive statistics.

    Args:
        domains_file: Path to CSV file containing domains to crawl
        domain_limit: Maximum number of domains to process

    Returns:
        Path to the main output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    stats = compute_crawling_statistics(output_filename, domains_file, domain_limit)
    save_statistics_to_file(stats, output_filename)

    return output_filename


if __name__ == "__main__":
    run_crawler()
