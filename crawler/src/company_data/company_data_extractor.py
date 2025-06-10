"""
Company data extractor module.

This module provides functionality to extract company data from HTML content.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import lxml.html


@dataclass
class CompanyData:
    """Class for storing company data extracted from websites."""

    url: str
    name: Optional[str] = None
    phone: Optional[str] = None
    social_media: List[str] = field(default_factory=list)
    address: Optional[str] = None


class CompanyDataExtractor:
    """Class for extracting company data from website HTML."""

    def __init__(self) -> None:
        """Initialize the company data extractor."""
        self.logger = logging.getLogger(__name__)
        self.extracted_data: Dict[str, CompanyData] = {}
        self.social_media_domains: Set[str] = {
            "facebook.com",
            "twitter.com",
            "linkedin.com",
            "instagram.com",
            "youtube.com",
            "pinterest.com",
        }

    def extract(self, url: str, html_content: str) -> CompanyData:
        """
        Extract company data from HTML content.

        Args:
            url: URL of the website
            html_content: HTML content of the website

        Returns:
            CompanyData: Extracted company data
        """
        company_data = CompanyData(url=url)

        try:
            html = lxml.html.fromstring(html_content)

            company_data.name = self.extract_company_name(html)
            company_data.phone = self.extract_phone(html)
            company_data.social_media = self.extract_social_media(html)
            company_data.address = self.extract_address(html)

            self.extracted_data[url] = company_data

        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {str(e)}")

        return company_data

    def extract_company_name(self, html: lxml.html.HtmlElement) -> Optional[str]:
        """
        Extract company name from HTML.

        Args:
            html: Parsed HTML

        Returns:
            Optional[str]: Company name if found, None otherwise
        """
        # Try to extract from title
        title_elements = html.xpath("//title/text()")
        if title_elements and len(title_elements) > 0:
            # Clean up the title - common patterns like "Company Name - Home"
            name = str(title_elements[0]).strip()
            name = re.sub(r"\s*-\s*.*$", "", name)  # Remove everything after the dash
            return name

        # Try to extract from h1
        h1_elements = html.xpath("//h1/text()")
        if h1_elements and len(h1_elements) > 0:
            return str(h1_elements[0]).strip()

        return None

    def extract_phone(self, html: lxml.html.HtmlElement) -> Optional[str]:
        """
        Extract phone number from HTML.

        Args:
            html: Parsed HTML

        Returns:
            Optional[str]: Phone number if found, None otherwise
        """
        # Look for phone patterns in text
        text_elements = html.xpath("//text()")
        text_content = " ".join(str(text) for text in text_elements)

        phone_patterns = [
            r"\(\d{3}\)\s*\d{3}-\d{4}",  # (555) 123-4567
            r"\d{3}-\d{3}-\d{4}",  # 555-123-4567
            r"\+\d{1,3}\s*\(\d{3}\)\s*\d{3}-\d{4}",  # +1 (555) 123-4567
            r"\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{4}",  # +1 555 123 4567
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text_content)
            if matches and len(matches) > 0:
                return str(matches[0])

        return None

    def extract_social_media(self, html: lxml.html.HtmlElement) -> List[str]:
        """
        Extract social media links from HTML.

        Args:
            html: Parsed HTML

        Returns:
            List[str]: List of social media links
        """
        social_links: List[str] = []
        link_elements = html.xpath("//a/@href")

        for link in link_elements:
            link_str = str(link)
            if self.is_valid_social_media_url(link_str):
                social_links.append(link_str)

        return social_links

    def extract_address(self, html: lxml.html.HtmlElement) -> Optional[str]:
        """
        Extract address from HTML.

        Args:
            html: Parsed HTML

        Returns:
            Optional[str]: Address if found, None otherwise
        """
        # Look for common address containers
        address_elements = html.xpath('//div[contains(@class, "address")]')
        if address_elements and len(address_elements) > 0:
            text_elements = address_elements[0].xpath(".//text()")
            address = " ".join(str(text) for text in text_elements).strip()
            if address:
                return address

        # Look for address patterns
        text_elements = html.xpath("//text()")
        text_content = " ".join(str(text) for text in text_elements)

        # Simple US address pattern
        address_pattern = r"\d+\s+[\w\s]+,\s+[\w\s]+,\s+[A-Z]{2}\s+\d{5}"
        matches = re.findall(address_pattern, text_content)

        if matches and len(matches) > 0:
            return str(matches[0])

        return None

    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number format.

        Args:
            phone: Phone number to normalize

        Returns:
            str: Normalized phone number (E.164 format)
        """
        # Extract digits only
        digits = "".join(re.findall(r"\d", phone))

        # Assume US number if 10 digits
        if len(digits) == 10:
            return f"+1{digits}"
        # If already has country code
        elif len(digits) > 10:
            return f"+{digits}"

        return phone

    def is_valid_social_media_url(self, url: str) -> bool:
        """
        Check if a URL is a valid social media link.

        Args:
            url: URL to check

        Returns:
            bool: True if it's a valid social media URL, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Handle cases where domain starts with www.
            if domain.startswith("www."):
                domain = domain[4:]

            return any(sm_domain in domain for sm_domain in self.social_media_domains)
        except Exception:
            return False

    def has_data(self, url: str) -> bool:
        """
        Check if data has been extracted for a URL.

        Args:
            url: URL to check

        Returns:
            bool: True if data exists, False otherwise
        """
        return url in self.extracted_data
