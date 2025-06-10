"""
Statistics computation module for crawler results.

This module provides functions to analyze crawler output and generate
comprehensive statistics about the crawling process.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.company_data.domain_loader import DomainLoader

logger = logging.getLogger(__name__)


def compute_crawling_statistics(
    output_filename: str,
    domains_file: str = "configs/companies-domains.csv",
    domain_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Compute comprehensive statistics from crawler output files.

    Args:
        output_filename: Path to the main crawler output JSON file
        domains_file: Path to CSV file containing domains to crawl
        domain_limit: Maximum number of domains that were processed

    Returns:
        Dictionary containing all computed statistics
    """
    company_data = _load_json_file(output_filename)

    # Load the original domains from CSV to calculate true success rate
    domain_loader = DomainLoader()
    all_input_domains = domain_loader.load_domains(domains_file)
    if domain_limit:
        all_input_domains = all_input_domains[:domain_limit]

    # Get domains from successful attempts
    successful_domains = {
        record.get("domain") for record in company_data if record.get("domain")
    }

    # Calculate success rates relative to input domains
    total_input_domains = len(all_input_domains)
    domain_success_rate = (
        (len(successful_domains) / total_input_domains * 100)
        if total_input_domains > 0
        else 0
    )
    page_success_rate = 100.0 if company_data else 0

    # Calculate fill rates aggregated by domain
    fill_rates = _calculate_domain_fill_rates(company_data)

    # Count contact pages
    contact_domains = len(
        {
            record.get("domain")
            for record in company_data
            if record.get("page_type") == "contact"
        }
    )

    return {
        "metadata": {
            "computation_timestamp": datetime.now().isoformat(),
            "output_file": output_filename,
            "total_records": len(company_data),
        },
        "domain_statistics": {
            "total_domains_attempted": total_input_domains,
            "domains_successfully_scraped": len(successful_domains),
        },
        "page_statistics": {
            "total_pages_attempted": len(company_data),
            "pages_successfully_scraped": len(company_data),
        },
        "success_rates": {
            "domain_success_rate": round(domain_success_rate, 2),
            "page_success_rate": round(page_success_rate, 2),
        },
        "data_fill_rates": fill_rates,
        "page_type_analysis": {
            "domains_with_contact_page": contact_domains,
        },
    }


def save_statistics_to_file(stats: Dict[str, Any], output_filename: str) -> str:
    """Save computed statistics to a JSON file with timestamp matching output file."""
    output_path = Path(output_filename)
    base_name = output_path.stem

    if "_" in base_name:
        timestamp_part = "_".join(base_name.split("_")[1:])
        stats_filename = f"data/crawler_stats_{timestamp_part}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_filename = f"data/crawler_stats_{timestamp}.json"

    stats_path = Path(stats_filename)
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    with open(stats_filename, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return stats_filename


def _load_json_file(filename: Optional[str]) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    if not filename or not Path(filename).exists():
        return []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def _has_value(value: Any) -> bool:
    """Check if a value is non-empty."""
    if value is None or value == "" or value == []:
        return False
    if isinstance(value, list):
        return len(value) > 0 and any(item for item in value if item)
    return bool(str(value).strip())


def _calculate_domain_fill_rates(
    company_data: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Calculate fill rates aggregated by domain.

    A domain is considered to have a field filled if at least one record
    for that domain has a non-empty value for that field.
    """
    if not company_data:
        return {}

    # Group data by domain
    domain_data: Dict[str, List[Dict[str, Any]]] = {}
    for record in company_data:
        domain = record.get("domain")
        if domain:
            if domain not in domain_data:
                domain_data[domain] = []
            domain_data[domain].append(record)

    if not domain_data:
        return {}

    # Calculate fill rates by domain
    core_fields = ["name", "phone", "social_media", "address"]
    field_counts = {field: 0 for field in core_fields}

    for domain, records in domain_data.items():
        for field in core_fields:
            # Check if this domain has this field filled in any record
            domain_has_field = any(_has_value(record.get(field)) for record in records)
            if domain_has_field:
                field_counts[field] += 1

    # Calculate percentages
    total_domains = len(domain_data)
    fill_rates = {}
    for field in core_fields:
        fill_rate = (field_counts[field] / total_domains) * 100
        fill_rates[field] = round(fill_rate, 2)

    return fill_rates
