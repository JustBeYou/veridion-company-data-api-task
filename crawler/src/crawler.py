from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawler(
    domains_file: str = "configs/companies-domains.csv", domain_limit: int = 5
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"data/companies_{timestamp}.json"

    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            output_filename: {
                "format": "json",
                "overwrite": True,
            }
        },
    )

    process = CrawlerProcess(settings=settings)

    process.crawl(
        "company_spider", domains_file=domains_file, domain_limit=domain_limit
    )
    process.start()

    return output_filename


if __name__ == "__main__":
    run_crawler()
