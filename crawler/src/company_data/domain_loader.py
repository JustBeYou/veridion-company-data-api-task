"""
Domain loader module for the crawler.

This module provides functionality to load domains from a CSV file.
"""

import csv
import logging
import re
from typing import List


class DomainLoader:
    """Class for loading and validating domains from a CSV file."""

    def __init__(self) -> None:
        """Initialize the domain loader."""
        self.domains: List[str] = []
        self.invalid_count: int = 0
        self.logger = logging.getLogger(__name__)

    def load_domains(self, csv_file_path: str) -> List[str]:
        """
        Load domains from a CSV file.

        Args:
            csv_file_path: Path to the CSV file containing domains

        Returns:
            List[str]: List of valid domains
        """
        self.domains = []
        self.invalid_count = 0

        try:
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if "domain" in row:
                        domain = row["domain"].strip()
                        if self.is_valid_domain(domain):
                            self.domains.append(domain)
                        else:
                            self.invalid_count += 1
                            self.logger.warning(f"Invalid domain: {domain}")
                    else:
                        self.logger.error("CSV file does not have a 'domain' column")
                        break
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file_path}")
        except Exception as e:
            self.logger.error(f"Error loading domains: {str(e)}")

        return self.domains

    def is_valid_domain(self, domain: str) -> bool:
        """
        Check if a domain is valid.

        Args:
            domain: Domain to validate

        Returns:
            bool: True if the domain is valid, False otherwise
        """
        # Simple domain validation regex
        domain_pattern = (
            r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        )
        return bool(re.match(domain_pattern, domain))

    def is_ready(self) -> bool:
        """
        Check if the domain loader is ready to process domains.

        Returns:
            bool: True if domains are loaded, False otherwise
        """
        return len(self.domains) > 0
