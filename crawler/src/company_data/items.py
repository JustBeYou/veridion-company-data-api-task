"""
Scrapy items for storing extracted company data.

This module defines the structure of items that will be extracted by the crawler.
"""

from enum import StrEnum

import scrapy


class PageType(StrEnum):
    HOME = "home"
    CONTACT = "contact"
    OTHER = "other"


class CompanyItem(scrapy.Item):
    """Item for storing company data."""

    # Core company data fields
    name = scrapy.Field()
    phone = scrapy.Field()
    social_media = scrapy.Field()
    address = scrapy.Field()

    # Metadata for statistics and tracking
    domain = scrapy.Field()
    url = scrapy.Field()
    page_type = scrapy.Field()
