from typing import Any, Dict, Iterator, List, Optional

import scrapy


class CompanySpider(scrapy.Spider):
    name = "company_spider"
    allowed_domains: List[str] = []

    def __init__(
        self, target_url: Optional[str] = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.start_urls = [target_url] if target_url else ["https://example.com"]
        self.logger.info(f"Starting spider with URLs: {self.start_urls}")

    def parse(self, response: scrapy.http.Response) -> Iterator[Dict[str, Any]]:
        """Parse response and extract company data."""
        self.logger.info(f"Crawling: {response.url}")

        # Extract page title as company name (basic example)
        title = response.css("title::text").get()

        # Extract all links as potential social media
        social_links = response.css(
            "a[href*='facebook.com'], "
            "a[href*='twitter.com'], "
            "a[href*='linkedin.com'], "
            "a[href*='instagram.com']::attr(href)"
        ).getall()

        # Extract potential phone numbers (simple regex pattern)
        phones = response.css("body ::text").re(r"\+?[\d\s\(\)-]{10,20}")

        # Look for potential address information
        address = response.css("address ::text").getall()
        if not address:
            # Try to find something that might look like an address
            address = response.css(
                "footer p::text, .contact ::text, .address ::text"
            ).re(r"[\d]+\s+[\w\s]+,\s+[\w\s]+,?\s+[\w\s]+")

        yield {
            "url": response.url,
            "company_name": title,
            "social_media": social_links,
            "phone": phones[:1] if phones else None,  # Just take the first one if found
            "address": address[0] if address else None,
        }
