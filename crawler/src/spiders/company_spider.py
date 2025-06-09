"""
Company spider module.

This module defines a Scrapy spider for crawling company websites.
"""

from typing import Any, Dict, Iterator, List, Optional, Union

import scrapy
from scrapy.http import Response

from src.company_data.company_data_extractor import CompanyDataExtractor
from src.company_data.domain_loader import DomainLoader
from src.company_data.items import CompanyItem


class CompanySpider(scrapy.Spider):
    """Spider for crawling company websites and extracting data."""

    name = "company_spider"
    allowed_domains: List[str] = []

    def __init__(
        self,
        domains_file: str = "configs/companies-domains.csv",
        target_url: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the spider.

        Args:
            domains_file: Path to the CSV file with domains
            target_url: Optional specific URL to crawl
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.extractor = CompanyDataExtractor()

        if target_url:
            self.start_urls = [target_url]
            self.logger.info(f"Starting spider with URL: {target_url}")
        else:
            # Load domains from CSV
            self.domain_loader = DomainLoader()
            self.domains = self.domain_loader.load_domains(domains_file)

            if not self.domains:
                self.logger.error(f"No valid domains found in {domains_file}")
                self.start_urls = ["https://example.com"]  # Fallback
            else:
                self.start_urls = [f"https://{domain}" for domain in self.domains]
                self.logger.info(f"Loaded {len(self.domains)} domains")

                # Set allowed domains
                self.allowed_domains = self.domains.copy()

    def parse(
        self, response: Response
    ) -> Iterator[Union[Dict[str, Any], scrapy.Request]]:
        """
        Parse response and extract company data.

        Args:
            response: Scrapy response object

        Yields:
            Union[Dict[str, Any], scrapy.Request]: Extracted company data or requests to follow
        """
        self.logger.info(f"Crawling: {response.url}")

        try:
            # Extract company data using our extractor
            html_content = response.text
            company_data = self.extractor.extract(response.url, html_content)

            # Create and yield a Scrapy item
            item = CompanyItem()
            item["name"] = company_data.name
            item["phone"] = company_data.phone
            item["social_media"] = company_data.social_media
            item["address"] = company_data.address

            yield dict(item)  # Convert to dictionary to match the expected return type

            # Follow contact and about pages - they often contain company information
            for href in response.css("a::attr(href)").getall():
                lower_href = href.lower()
                if (
                    "contact" in lower_href or "about" in lower_href
                ) and not href.startswith("#"):
                    yield response.follow(href, self.parse)

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")

    def start_requests(self) -> Iterator[scrapy.Request]:
        """
        Generate initial requests for the spider.

        Yields:
            scrapy.Request: Initial requests to crawl
        """
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.errback)

    def errback(self, failure: Any) -> None:
        """
        Handle request failures.

        Args:
            failure: Failure object
        """
        request = failure.request
        self.logger.error(f"Error crawling {request.url}: {failure.value}")
