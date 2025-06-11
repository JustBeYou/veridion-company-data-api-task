"""
Company spider module.

This module defines a Scrapy spider for crawling company websites.
"""

from typing import Any, Dict, Iterator, List, Optional, Union
from urllib.parse import urlparse

import scrapy
from scrapy.http import Response

from src.company_data.company_data_extractor import CompanyDataExtractor
from src.company_data.domain_loader import DomainLoader
from src.company_data.items import CompanyItem, PageType


class CompanySpider(scrapy.Spider):
    """Spider for crawling company websites and extracting data."""

    name = "company_spider"
    allowed_domains: List[str] = []

    def __init__(
        self,
        domains_file: str = "configs/companies-domains.csv",
        domain_limit: Optional[int | str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the spider.

        Args:
            domains_file: Path to the CSV file with domains
            domain_limit: Limit the number of domains to crawl
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)

        self.logger.info(f"Initializing spider with domains file: {domains_file}")
        self.logger.info(f"Initializing spider with domain limit: {domain_limit}")

        self.extractor = CompanyDataExtractor()

        self.domain_loader = DomainLoader()
        self.domains = self.domain_loader.load_domains(domains_file)

        if not self.domains:
            raise ValueError(f"No valid domains found in {domains_file}")

        if domain_limit:
            self.domains = self.domains[: int(domain_limit)]

        self.start_urls = [f"https://{domain}" for domain in self.domains]
        self.logger.info(f"Loaded {len(self.domains)} domains")

        # Set allowed domains
        self.allowed_domains = self.domains.copy()

    def parse(
        self, response: Response
    ) -> Iterator[Union[Dict[str, Any], CompanyItem, scrapy.Request]]:
        """
        Parse response and extract company data.

        Args:
            response: Scrapy response object

        Yields:
            Union[Dict[str, Any], scrapy.Request]: Extracted company data or requests to follow
        """
        self.logger.info(f"Crawling: {response.url}")

        domain = urlparse(response.url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        html_content = response.text
        company_data = self.extractor.extract(response.url, html_content)

        item = CompanyItem()
        page_type = self._detect_page_type(domain, response.url)

        item["page_type"] = str(page_type)
        item["phone"] = (
            self.extractor.normalize_phone(company_data.phone)
            if company_data.phone
            else None
        )
        item["social_media"] = list(set(company_data.social_media))
        item["address"] = company_data.address
        item["domain"] = domain
        item["url"] = response.url

        # Skip yield if all data fields are empty/None
        if not any(
            [company_data.phone, company_data.social_media, company_data.address]
        ):
            return

        yield item

        # Follow only relevant internal links within the same domain
        for href in response.css("a::attr(href)").getall():
            # Skip fragments, javascript, mailto, tel, and other non-http links
            if (
                not href
                or href.startswith("#")
                or href.startswith("javascript:")
                or href.startswith("mailto:")
                or href.startswith("tel:")
                or href.startswith("sms:")
                or href.startswith("ftp:")
            ):
                continue

            # Only follow links containing common company page keywords
            href_lower = href.lower()
            if any(
                keyword in href_lower
                for keyword in [
                    "home",
                    "about",
                    "contact",
                    "company",
                    "team",
                    "location",
                    "office",
                    "address",
                    "info",
                    "who-we-are",
                    "careers",
                    "jobs",
                    "career",
                    "job",
                    "join-us",
                    "locations",
                    "offices",
                    "global",
                    "worldwide",
                ]
            ):
                # Follow the link, Scrapy will automatically filter based on allowed_domains
                yield response.follow(
                    href,
                    self.parse,
                )

    def start_requests(self) -> Iterator[scrapy.Request]:
        """
        Generate initial requests for the spider.

        Yields:
            scrapy.Request: Initial requests to crawl
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
            )

    def _detect_page_type(self, domain: str, url: str) -> PageType:
        """Detect page type from URL."""
        url_lower = url.lower()
        domain_lower = domain.lower()

        if url_lower.endswith(domain_lower):
            return PageType.HOME
        elif "contact" in url_lower or "about" in url_lower:
            return PageType.CONTACT
        else:
            return PageType.OTHER
