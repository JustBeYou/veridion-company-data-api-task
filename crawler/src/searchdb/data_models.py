"""Data models for company information."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class CompanyRecord:
    """Represents a company record with all available information."""

    domain: str
    company_names: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    social_media: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    page_types: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure all lists contain unique values."""
        self.company_names = self._make_unique_list(self.company_names)
        self.phones = self._make_unique_list(self.phones)
        self.social_media = self._make_unique_list(self.social_media)
        self.addresses = self._make_unique_list(self.addresses)
        self.page_types = self._make_unique_list(self.page_types)
        self.urls = self._make_unique_list(self.urls)

    @staticmethod
    def _make_unique_list(items: List[str]) -> List[str]:
        """Make a list contain only unique non-empty strings."""
        if not items:
            return []

        # Filter out None and empty strings, strip whitespace, and make unique
        unique_items = []
        seen: Set[str] = set()

        for item in items:
            if item is not None:
                cleaned_item = str(item).strip()
                if cleaned_item and cleaned_item not in seen:
                    unique_items.append(cleaned_item)
                    seen.add(cleaned_item)

        return unique_items

    def add_company_names(self, names: List[str]) -> None:
        """Add company names and ensure uniqueness."""
        if names:
            all_names = self.company_names + names
            self.company_names = self._make_unique_list(all_names)

    def add_company_names_from_pipe_separated(
        self, pipe_separated: Optional[str]
    ) -> None:
        """Add company names from pipe-separated string."""
        if pipe_separated:
            names = [name.strip() for name in pipe_separated.split("|")]
            self.add_company_names(names)

    def add_phones(self, phones: List[str]) -> None:
        """Add phone numbers and ensure uniqueness."""
        if phones:
            all_phones = self.phones + phones
            self.phones = self._make_unique_list(all_phones)

    def add_social_media(self, links: List[str]) -> None:
        """Add social media links and ensure uniqueness."""
        if links:
            all_links = self.social_media + links
            self.social_media = self._make_unique_list(all_links)

    def add_addresses(self, addresses: List[str]) -> None:
        """Add addresses and ensure uniqueness."""
        if addresses:
            all_addresses = self.addresses + addresses
            self.addresses = self._make_unique_list(all_addresses)

    def add_page_types(self, page_types: List[str]) -> None:
        """Add page types and ensure uniqueness."""
        if page_types:
            all_types = self.page_types + page_types
            self.page_types = self._make_unique_list(all_types)

    def add_urls(self, urls: List[str]) -> None:
        """Add URLs and ensure uniqueness."""
        if urls:
            all_urls = self.urls + urls
            self.urls = self._make_unique_list(all_urls)

    def merge_with(self, other: "CompanyRecord") -> "CompanyRecord":
        """Merge this record with another record for the same domain."""
        if self.domain != other.domain:
            raise ValueError(
                f"Cannot merge records for different domains: {self.domain} != {other.domain}"
            )

        # Create new record with merged data
        merged = CompanyRecord(domain=self.domain)

        # Merge all fields
        merged.add_company_names(self.company_names + other.company_names)
        merged.add_phones(self.phones + other.phones)
        merged.add_social_media(self.social_media + other.social_media)
        merged.add_addresses(self.addresses + other.addresses)
        merged.add_page_types(self.page_types + other.page_types)
        merged.add_urls(self.urls + other.urls)

        return merged

    def to_elasticsearch_doc(self) -> Dict[str, Any]:
        """Convert to Elasticsearch document format."""
        doc: Dict[str, Any] = {"domain": self.domain}

        # Only include non-empty fields
        if self.company_names:
            doc["company_names"] = self.company_names
        if self.phones:
            doc["phones"] = self.phones
        if self.social_media:
            doc["social_media"] = self.social_media
        if self.addresses:
            doc["addresses"] = self.addresses
        if self.page_types:
            doc["page_types"] = self.page_types
        if self.urls:
            doc["urls"] = self.urls

        return doc

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> "CompanyRecord":
        """Create CompanyRecord from CSV row."""
        if "domain" not in row or not row["domain"]:
            raise ValueError("CSV row must contain 'domain' field")

        record = cls(domain=row["domain"])

        # Add company names from various fields
        if row.get("company_commercial_name"):
            record.add_company_names([row["company_commercial_name"]])

        if row.get("company_legal_name"):
            record.add_company_names([row["company_legal_name"]])

        if row.get("company_all_available_names"):
            record.add_company_names_from_pipe_separated(
                row["company_all_available_names"]
            )

        return record

    @classmethod
    def from_json_record(cls, record: Dict[str, Any]) -> "CompanyRecord":
        """Create CompanyRecord from JSON scraped data record."""
        if "domain" not in record or not record["domain"]:
            raise ValueError("JSON record must contain 'domain' field")

        company_record = cls(domain=record["domain"])

        # Add phone if present
        if record.get("phone"):
            company_record.add_phones([record["phone"]])

        # Add social media links
        if record.get("social_media"):
            social_links = record["social_media"]
            if isinstance(social_links, list):
                company_record.add_social_media(social_links)
            elif isinstance(social_links, str):
                company_record.add_social_media([social_links])

        # Add address if present
        if record.get("address"):
            company_record.add_addresses([record["address"]])

        # Add page type if present
        if record.get("page_type"):
            company_record.add_page_types([record["page_type"]])

        # Add URL if present
        if record.get("url"):
            company_record.add_urls([record["url"]])

        return company_record


def aggregate_json_records_by_domain(
    records: List[Dict[str, Any]],
) -> Dict[str, CompanyRecord]:
    """Aggregate multiple JSON records by domain for efficient processing."""
    domain_records: Dict[str, CompanyRecord] = {}

    for record in records:
        if "domain" not in record or not record["domain"]:
            continue  # Skip invalid records

        domain = record["domain"]
        company_record = CompanyRecord.from_json_record(record)

        if domain in domain_records:
            # Merge with existing record
            domain_records[domain] = domain_records[domain].merge_with(company_record)
        else:
            domain_records[domain] = company_record

    return domain_records
