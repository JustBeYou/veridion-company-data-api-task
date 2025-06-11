"""
Scrapy settings for the company crawler project.

This module contains the configuration settings for Scrapy,
controlling the behavior of the crawler.
"""

BOT_NAME = "company_crawler"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 0.1

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 1
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
AUTOTHROTTLE_DEBUG = False

# Configure retry settings
RETRY_ENABLED = True
RETRY_TIMES = 1  # Only retry once
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
RETRY_EXCEPTIONS = [
    "twisted.internet.defer.TimeoutError",
    "twisted.internet.error.TimeoutError",
    "twisted.internet.error.DNSLookupError",
    "twisted.internet.error.ConnectionRefusedError",
    "twisted.internet.error.ConnectionDone",
    "twisted.internet.error.ConnectionLost",
    "twisted.internet.error.TCPTimedOutError",
]

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Set timeout settings to 1 second
DOWNLOAD_TIMEOUT = 3
DNS_TIMEOUT = 1

# Limit crawling depth
DEPTH_LIMIT = 1
