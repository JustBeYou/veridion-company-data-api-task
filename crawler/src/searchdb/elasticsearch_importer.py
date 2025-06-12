"""Elasticsearch importer for company data."""

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from elasticsearch import ConnectionError as ESConnectionError
from elasticsearch import (
    Elasticsearch,
    NotFoundError,
)
from elasticsearch.helpers import bulk

from .data_models import CompanyRecord, aggregate_json_records_by_domain

logger = logging.getLogger(__name__)


class ElasticsearchImporter:
    """Handles importing company data into Elasticsearch."""

    def __init__(
        self, es_host: str = "localhost:9200", index_name: str = "companies"
    ) -> None:
        """Initialize the Elasticsearch importer.

        Args:
            es_host: Elasticsearch host and port
            index_name: Name of the Elasticsearch index
        """
        self.es_host = es_host
        self.index_name = index_name

        # Ensure proper URL format
        if not es_host.startswith(("http://", "https://")):
            es_host = f"http://{es_host}"

        self.es_client = Elasticsearch([es_host])

        # Test connection
        try:
            if not self.es_client.ping():
                raise ESConnectionError(f"Cannot connect to Elasticsearch at {es_host}")
        except Exception as e:
            raise ESConnectionError(f"Failed to connect to Elasticsearch: {e}")

    def create_index_if_not_exists(self) -> None:
        """Create the companies index with proper mapping if it doesn't exist."""
        if not self.es_client.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "domain": {"type": "keyword"},
                        "company_names": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {"keyword": {"type": "keyword"}},
                        },
                        "phones": {"type": "keyword"},
                        "social_media": {"type": "keyword"},
                        "addresses": {"type": "text", "analyzer": "standard"},
                        "page_types": {"type": "keyword"},
                        "urls": {"type": "keyword"},
                    }
                }
            }

            self.es_client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created Elasticsearch index: {self.index_name}")

    def import_csv_file(self, file_path: Union[str, Path]) -> int:
        """Import company data from CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Number of records imported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        self.create_index_if_not_exists()

        records: List[CompanyRecord] = []

        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    record = CompanyRecord.from_csv_row(row)
                    records.append(record)
                except ValueError as e:
                    logger.warning(f"Skipping invalid CSV row: {e}")
                    continue

        return self._bulk_import_records(records)

    def import_json_file(self, file_path: Union[str, Path]) -> int:
        """Import company data from JSON file with pre-aggregation by domain.

        Args:
            file_path: Path to the JSON file

        Returns:
            Number of records imported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        self.create_index_if_not_exists()

        with open(file_path, "r", encoding="utf-8") as jsonfile:
            json_records = json.load(jsonfile)

        if not isinstance(json_records, list):
            raise ValueError("JSON file must contain a list of records")

        # Aggregate records by domain for efficient processing
        logger.info(f"Aggregating {len(json_records)} JSON records by domain...")
        domain_records = aggregate_json_records_by_domain(json_records)
        logger.info(f"Aggregated into {len(domain_records)} unique domains")

        records = list(domain_records.values())
        return self._bulk_import_records(records)

    def _bulk_import_records(self, records: List[CompanyRecord]) -> int:
        """Import multiple records using bulk API with upsert semantics.

        Args:
            records: List of CompanyRecord objects to import

        Returns:
            Number of records successfully imported
        """
        if not records:
            logger.info("No records to import")
            return 0

        # Prepare bulk operations for upsert (update or insert)
        actions = []
        for record in records:
            # First, try to get existing record
            existing_doc = self._get_existing_record(record.domain)

            if existing_doc:
                # Merge with existing record
                existing_record = self._doc_to_company_record(
                    existing_doc, record.domain
                )
                merged_record = existing_record.merge_with(record)
                doc = merged_record.to_elasticsearch_doc()
            else:
                # New record
                doc = record.to_elasticsearch_doc()

            action = {
                "_index": self.index_name,
                "_id": record.domain,  # Use domain as document ID
                "_source": doc,
            }
            actions.append(action)

        # Execute bulk import
        try:
            result = bulk(
                self.es_client,
                actions,
                index=self.index_name,
                refresh=True,  # Make changes immediately searchable
            )
            success_count = result[0]
            failed_items = result[1]

            if failed_items:
                logger.warning(f"Failed to import {len(failed_items)} records")  # type: ignore
                for item in failed_items:  # type: ignore
                    logger.warning(f"Failed item: {item}")

            logger.info(f"Successfully imported {success_count} records")
            return success_count

        except Exception as e:
            logger.error(f"Bulk import failed: {e}")
            raise

    def _get_existing_record(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get existing record from Elasticsearch by domain.

        Args:
            domain: Domain to search for

        Returns:
            Existing document or None if not found
        """
        try:
            response = self.es_client.get(index=self.index_name, id=domain)
            result: Dict[str, Any] = response["_source"]
            return result
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error retrieving existing record for domain {domain}: {e}")
            return None

    def _doc_to_company_record(self, doc: Dict[str, Any], domain: str) -> CompanyRecord:
        """Convert Elasticsearch document back to CompanyRecord.

        Args:
            doc: Elasticsearch document
            domain: Domain for the record

        Returns:
            CompanyRecord instance
        """
        record = CompanyRecord(domain=domain)

        # Add all fields from document
        if doc.get("company_names"):
            record.add_company_names(doc["company_names"])
        if doc.get("phones"):
            record.add_phones(doc["phones"])
        if doc.get("social_media"):
            record.add_social_media(doc["social_media"])
        if doc.get("addresses"):
            record.add_addresses(doc["addresses"])
        if doc.get("page_types"):
            record.add_page_types(doc["page_types"])
        if doc.get("urls"):
            record.add_urls(doc["urls"])

        return record

    def search_companies(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Search for companies in Elasticsearch.

        Args:
            query: Search query
            size: Maximum number of results to return

        Returns:
            List of matching company records
        """
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["company_names^2", "domain", "addresses"],
                }
            },
            "size": size,
        }

        try:
            response = self.es_client.search(index=self.index_name, body=search_body)
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def get_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get company data by domain.

        Args:
            domain: Domain to search for

        Returns:
            Company record or None if not found
        """
        return self._get_existing_record(domain)

    def delete_index(self) -> None:
        """Delete the companies index. Use with caution!"""
        if self.es_client.indices.exists(index=self.index_name):
            self.es_client.indices.delete(index=self.index_name)
            logger.info(f"Deleted Elasticsearch index: {self.index_name}")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the companies index.

        Returns:
            Index statistics
        """
        if not self.es_client.indices.exists(index=self.index_name):
            return {"exists": False}

        stats = self.es_client.indices.stats(index=self.index_name)
        doc_count = stats["indices"][self.index_name]["total"]["docs"]["count"]

        return {
            "exists": True,
            "document_count": doc_count,
            "index_size": stats["indices"][self.index_name]["total"]["store"][
                "size_in_bytes"
            ],
        }
