"""
Unit tests for the DomainLoader class.
"""

import os
import tempfile
import unittest
from typing import List

from src.domain_loader import DomainLoader


class TestDomainLoader(unittest.TestCase):
    """Test case for the DomainLoader class."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.domain_loader = DomainLoader()

        # Create a temporary CSV file with valid domains
        self.valid_domains = ["example.com", "test.example.com", "another-example.com"]

        # Create a temporary CSV file with valid and invalid domains
        self.mixed_domains = [
            "example.com",
            "invalid-domain",  # No TLD
            "test.example.com",
            "example..com",  # Double dot
            "-invalid.com",  # Starting with hyphen
            "another-example.com",
        ]

        # Create temporary files
        self.valid_file = self._create_temp_csv(self.valid_domains)
        self.mixed_file = self._create_temp_csv(self.mixed_domains)

    def tearDown(self) -> None:
        """Clean up after the test."""
        # Remove temporary files
        os.unlink(self.valid_file)
        os.unlink(self.mixed_file)

    def _create_temp_csv(self, domains: List[str]) -> str:
        """Create a temporary CSV file with domains."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w") as f:
            f.write("domain\n")  # Header
            for domain in domains:
                f.write(f"{domain}\n")
        return path

    def test_load_valid_domains(self) -> None:
        """Test loading valid domains from a CSV file."""
        loaded_domains = self.domain_loader.load_domains(self.valid_file)

        # Check that all domains were loaded
        self.assertEqual(len(loaded_domains), len(self.valid_domains))

        # Check that the domains are correct
        for domain in self.valid_domains:
            self.assertIn(domain, loaded_domains)

    def test_load_mixed_domains(self) -> None:
        """Test loading mixed valid and invalid domains from a CSV file."""
        loaded_domains = self.domain_loader.load_domains(self.mixed_file)

        # Check that only valid domains were loaded
        expected_valid = [
            d for d in self.mixed_domains if self.domain_loader.is_valid_domain(d)
        ]
        self.assertEqual(len(loaded_domains), len(expected_valid))

        # Check that invalid domains were counted
        self.assertEqual(
            self.domain_loader.invalid_count,
            len(self.mixed_domains) - len(expected_valid),
        )

    def test_is_valid_domain(self) -> None:
        """Test the domain validation function."""
        valid_domains = [
            "example.com",
            "test.example.com",
            "another-example.com",
            "example.co.uk",
        ]

        invalid_domains = [
            "invalid-domain",  # No TLD
            "example..com",  # Double dot
            "-invalid.com",  # Starting with hyphen
            "example-.com",  # Ending with hyphen
            "example.c",  # Single-character TLD
            "exa mple.com",  # Space in domain
        ]

        for domain in valid_domains:
            self.assertTrue(self.domain_loader.is_valid_domain(domain))

        for domain in invalid_domains:
            self.assertFalse(self.domain_loader.is_valid_domain(domain))

    def test_is_ready(self) -> None:
        """Test the is_ready function."""
        # Initially not ready
        self.assertFalse(self.domain_loader.is_ready())

        # Load domains and check again
        self.domain_loader.load_domains(self.valid_file)
        self.assertTrue(self.domain_loader.is_ready())

        # Reset domains and check again
        self.domain_loader.domains = []
        self.assertFalse(self.domain_loader.is_ready())


if __name__ == "__main__":
    unittest.main()
