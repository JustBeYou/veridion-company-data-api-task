"""
Scrapy pipelines for processing items extracted by spiders.

This module contains the pipelines that process items after they have been
extracted by spiders and before they are stored or exported.
"""

from typing import Any, Dict


class CompanyPipeline:
    """Pipeline for processing company items."""

    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        """
        Process the company item.

        Args:
            item: The scraped item
            spider: The spider that scraped the item (unused but required by Scrapy)

        Returns:
            The processed item
        """
        return item
