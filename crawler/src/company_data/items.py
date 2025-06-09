"""
Scrapy items for storing extracted company data.

This module defines the structure of items that will be extracted by the crawler.
"""

import scrapy


class CompanyItem(scrapy.Item):
    """Item for storing company data."""

    name = scrapy.Field()
    phone = scrapy.Field()
    social_media = scrapy.Field()
    address = scrapy.Field()
