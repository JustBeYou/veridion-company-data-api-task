"""
Data models for the crawler.

This module defines the data structures used throughout the crawler.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CompanyData:
    """Class for storing company data extracted from websites."""

    url: str
    name: Optional[str] = None
    phone: Optional[str] = None
    social_media: List[str] = field(default_factory=list)
    address: Optional[str] = None
