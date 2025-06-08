"""
Scrapy middlewares for the company crawler.

This module contains the spider middleware for the company crawler,
which processes requests and responses to and from the spiders.
"""

from typing import Any, Iterator

from scrapy import signals
from scrapy.http import Response
from scrapy.spiders import Spider


class CompanyCrawlerMiddleware:
    """Spider middleware for the company crawler."""

    @classmethod
    def from_crawler(cls, crawler: Any) -> "CompanyCrawlerMiddleware":
        """Create a new instance from crawler.

        Args:
            crawler: The crawler

        Returns:
            A new middleware instance
        """
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        """Process spider input.

        Args:
            response: The response
            spider: The spider
        """
        return None

    def process_spider_output(self, response: Response, result: Iterator, spider: Spider) -> Iterator:
        """Process spider output.

        Args:
            response: The response
            result: The result
            spider: The spider

        Returns:
            The processed result
        """
        yield from result

    def spider_opened(self, spider: Spider) -> None:
        """Handle spider opened signal.

        Args:
            spider: The spider
        """
        spider.logger.info(f"Spider opened: {spider.name}")
