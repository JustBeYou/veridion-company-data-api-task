"""
Unit tests for the CompanyDataExtractor class.
"""

import unittest

import lxml.html

from src.company_data.company_data_extractor import CompanyDataExtractor


class TestCompanyDataExtractor(unittest.TestCase):
    """Test case for the CompanyDataExtractor class."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.extractor = CompanyDataExtractor()

        # Test URL
        self.test_url = "https://example.com"

        # Test HTML with phone number
        self.html_with_phone = """
        <html>
            <body>
                <div class="contact">
                    <p>Phone: (555) 123-4567</p>
                </div>
            </body>
        </html>
        """

        # Test HTML with social media links
        self.html_with_social = """
        <html>
            <body>
                <div class="social-links">
                    <a href="https://facebook.com/acme">Facebook</a>
                    <a href="https://twitter.com/acme">Twitter</a>
                    <a href="https://linkedin.com/company/acme">LinkedIn</a>
                </div>
            </body>
        </html>
        """

        # Test HTML with address
        self.html_with_address = """
        <html>
            <body>
                <div class="address">
                    123 Main St, Anytown, ST 12345
                </div>
            </body>
        </html>
        """

        # Test HTML with all data
        self.html_with_all = """
        <html>
            <head>
                <title>Acme Corporation - Home</title>
            </head>
            <body>
                <h1>Welcome to Acme Corporation</h1>
                <div class="contact">
                    <p>Phone: (555) 123-4567</p>
                </div>
                <div class="social-links">
                    <a href="https://facebook.com/acme">Facebook</a>
                    <a href="https://twitter.com/acme">Twitter</a>
                    <a href="https://linkedin.com/company/acme">LinkedIn</a>
                </div>
                <div class="address">
                    123 Main St, Anytown, ST 12345
                </div>
            </body>
        </html>
        """

    def test_extract_phone(self) -> None:
        """Test extracting phone number from HTML."""
        # Parse HTML
        html = self._parse_html(self.html_with_phone)

        # Extract phone number
        phone = self.extractor.extract_phone(html)

        # Check that the phone number was extracted correctly
        self.assertEqual(phone, "(555) 123-4567")

    def test_extract_social_media(self) -> None:
        """Test extracting social media links from HTML."""
        # Parse HTML
        html = self._parse_html(self.html_with_social)

        # Extract social media links
        social_media = self.extractor.extract_social_media(html)

        # Check that all social media links were extracted
        self.assertEqual(len(social_media), 3)
        self.assertIn("https://facebook.com/acme", social_media)
        self.assertIn("https://twitter.com/acme", social_media)
        self.assertIn("https://linkedin.com/company/acme", social_media)

    def test_extract_address(self) -> None:
        """Test extracting address from HTML."""
        # Parse HTML
        html = self._parse_html(self.html_with_address)

        # Extract address
        address = self.extractor.extract_address(html)

        # Check that the address was extracted correctly
        self.assertEqual(address, "123 Main St, Anytown, ST 12345")

    def test_extract_all(self) -> None:
        """Test extracting all data from HTML."""
        # Extract all data
        company_data = self.extractor.extract(self.test_url, self.html_with_all)

        # Check that all data was extracted correctly
        self.assertEqual(company_data.phone, "(555) 123-4567")
        self.assertEqual(len(company_data.social_media), 3)
        self.assertEqual(company_data.address, "123 Main St, Anytown, ST 12345")

    def test_normalize_phone(self) -> None:
        """Test normalizing phone numbers."""
        test_cases = [
            ("(555) 123-4567", "+15551234567"),
            ("555-123-4567", "+15551234567"),
            ("+1 (555) 123-4567", "+15551234567"),
            ("+44 20 1234 5678", "+442012345678"),
        ]

        for phone, expected in test_cases:
            normalized = self.extractor.normalize_phone(phone)
            self.assertEqual(normalized, expected)

    def test_is_valid_social_media_url(self) -> None:
        """Test validating social media URLs."""
        valid_urls = [
            "https://facebook.com/acme",
            "https://www.facebook.com/acme",
            "https://twitter.com/acme",
            "https://linkedin.com/company/acme",
            "https://instagram.com/acme",
            "https://youtube.com/channel/123",
            "https://pinterest.com/acme",
        ]

        invalid_urls = [
            "https://example.com",
            "https://facebook.example.com",
            "facebook.com/acme",  # Missing scheme
            "https://fakebook.com/acme",
            "https://nefsvt.com/equipment-lines",
        ]

        for url in valid_urls:
            self.assertTrue(self.extractor.is_valid_social_media_url(url), url)

        for url in invalid_urls:
            self.assertFalse(self.extractor.is_valid_social_media_url(url), url)

    def test_has_data(self) -> None:
        """Test checking if data has been extracted for a URL."""
        # Initially no data
        self.assertFalse(self.extractor.has_data(self.test_url))

        # Extract data
        self.extractor.extract(self.test_url, self.html_with_all)

        # Check that data exists
        self.assertTrue(self.extractor.has_data(self.test_url))

    def _parse_html(self, html_content: str) -> lxml.html.HtmlElement:
        """Parse HTML content."""
        return lxml.html.fromstring(html_content)


if __name__ == "__main__":
    unittest.main()
