"""Unit tests for searchdb data models."""

import pytest

from src.searchdb.data_models import CompanyRecord, aggregate_json_records_by_domain


class TestCompanyRecord:
    """Test cases for CompanyRecord class."""

    def test_company_record_creation(self):
        """Test basic CompanyRecord creation."""
        record = CompanyRecord(domain="example.com")
        assert record.domain == "example.com"
        assert record.company_names == []
        assert record.phones == []
        assert record.social_media == []
        assert record.addresses == []
        assert record.page_types == []
        assert record.urls == []

    def test_company_record_with_initial_data(self):
        """Test CompanyRecord creation with initial data."""
        record = CompanyRecord(
            domain="example.com",
            company_names=["Example Corp", "Example Inc"],
            phones=["+1-555-0101", "+1-555-0102"],
        )
        assert record.domain == "example.com"
        assert len(record.company_names) == 2
        assert len(record.phones) == 2

    def test_make_unique_list(self):
        """Test _make_unique_list static method."""
        # Test with duplicates
        items = ["a", "b", "a", "c", "b"]
        result = CompanyRecord._make_unique_list(items)
        assert result == ["a", "b", "c"]

        # Test with None values
        items = ["a", None, "b", "", "c"]
        result = CompanyRecord._make_unique_list(items)
        assert result == ["a", "b", "c"]

        # Test with empty list
        result = CompanyRecord._make_unique_list([])
        assert result == []

        # Test with whitespace
        items = [" a ", "b", " a", "c "]
        result = CompanyRecord._make_unique_list(items)
        assert result == ["a", "b", "c"]

    def test_add_company_names(self):
        """Test adding company names."""
        record = CompanyRecord(domain="example.com")

        # Add names
        record.add_company_names(["Example Corp", "Example Inc"])
        assert len(record.company_names) == 2
        assert "Example Corp" in record.company_names
        assert "Example Inc" in record.company_names

        # Add more names with duplicates
        record.add_company_names(["Example Corp", "Example LLC"])
        assert len(record.company_names) == 3  # No duplicate "Example Corp"
        assert "Example LLC" in record.company_names

    def test_add_company_names_from_pipe_separated(self):
        """Test adding company names from pipe-separated string."""
        record = CompanyRecord(domain="example.com")

        # Add pipe-separated names
        record.add_company_names_from_pipe_separated(
            "Example Corp|Example Inc|Example LLC"
        )
        assert len(record.company_names) == 3
        assert "Example Corp" in record.company_names
        assert "Example Inc" in record.company_names
        assert "Example LLC" in record.company_names

        # Test with None
        record.add_company_names_from_pipe_separated(None)
        assert len(record.company_names) == 3  # No change

        # Test with empty string
        record.add_company_names_from_pipe_separated("")
        assert len(record.company_names) == 3  # No change

    def test_merge_with(self):
        """Test merging two CompanyRecord instances."""
        record1 = CompanyRecord(
            domain="example.com", company_names=["Example Corp"], phones=["+1-555-0101"]
        )

        record2 = CompanyRecord(
            domain="example.com",
            company_names=["Example Inc"],
            phones=["+1-555-0102"],
            social_media=["https://twitter.com/example"],
        )

        merged = record1.merge_with(record2)

        assert merged.domain == "example.com"
        assert len(merged.company_names) == 2
        assert "Example Corp" in merged.company_names
        assert "Example Inc" in merged.company_names
        assert len(merged.phones) == 2
        assert "+1-555-0101" in merged.phones
        assert "+1-555-0102" in merged.phones
        assert len(merged.social_media) == 1
        assert "https://twitter.com/example" in merged.social_media

    def test_merge_with_different_domains_raises_error(self):
        """Test that merging records with different domains raises ValueError."""
        record1 = CompanyRecord(domain="example.com")
        record2 = CompanyRecord(domain="test.com")

        with pytest.raises(
            ValueError, match="Cannot merge records for different domains"
        ):
            record1.merge_with(record2)

    def test_to_elasticsearch_doc(self):
        """Test converting to Elasticsearch document format."""
        record = CompanyRecord(
            domain="example.com",
            company_names=["Example Corp", "Example Inc"],
            phones=["+1-555-0101"],
            social_media=["https://twitter.com/example"],
        )

        doc = record.to_elasticsearch_doc()

        assert doc["domain"] == "example.com"
        assert doc["company_names"] == ["Example Corp", "Example Inc"]
        assert doc["phones"] == ["+1-555-0101"]
        assert doc["social_media"] == ["https://twitter.com/example"]

        # Empty fields should not be included
        assert "addresses" not in doc
        assert "page_types" not in doc
        assert "urls" not in doc

    def test_from_csv_row(self):
        """Test creating CompanyRecord from CSV row."""
        csv_row = {
            "domain": "example.com",
            "company_commercial_name": "Example Corp",
            "company_legal_name": "Example Corporation Inc",
            "company_all_available_names": "Example Corp|Example Inc|Example Company",
        }

        record = CompanyRecord.from_csv_row(csv_row)

        assert record.domain == "example.com"
        assert len(record.company_names) == 4  # All unique names
        assert "Example Corp" in record.company_names
        assert "Example Corporation Inc" in record.company_names
        assert "Example Inc" in record.company_names
        assert "Example Company" in record.company_names

    def test_from_csv_row_missing_domain_raises_error(self):
        """Test that CSV row without domain raises ValueError."""
        csv_row = {"company_commercial_name": "Example Corp"}

        with pytest.raises(ValueError, match="CSV row must contain 'domain' field"):
            CompanyRecord.from_csv_row(csv_row)

    def test_from_csv_row_empty_domain_raises_error(self):
        """Test that CSV row with empty domain raises ValueError."""
        csv_row = {"domain": "", "company_commercial_name": "Example Corp"}

        with pytest.raises(ValueError, match="CSV row must contain 'domain' field"):
            CompanyRecord.from_csv_row(csv_row)

    def test_from_json_record(self):
        """Test creating CompanyRecord from JSON record."""
        json_record = {
            "domain": "example.com",
            "page_type": "homepage",
            "phone": "+1-555-0101",
            "social_media": [
                "https://twitter.com/example",
                "https://facebook.com/example",
            ],
            "address": "123 Main St, City, State",
            "url": "https://example.com",
        }

        record = CompanyRecord.from_json_record(json_record)

        assert record.domain == "example.com"
        assert record.phones == ["+1-555-0101"]
        assert len(record.social_media) == 2
        assert "https://twitter.com/example" in record.social_media
        assert "https://facebook.com/example" in record.social_media
        assert record.addresses == ["123 Main St, City, State"]
        assert record.page_types == ["homepage"]
        assert record.urls == ["https://example.com"]

    def test_from_json_record_with_string_social_media(self):
        """Test creating CompanyRecord from JSON record with string social media."""
        json_record = {
            "domain": "example.com",
            "social_media": "https://twitter.com/example",  # String instead of list
        }

        record = CompanyRecord.from_json_record(json_record)

        assert record.domain == "example.com"
        assert record.social_media == ["https://twitter.com/example"]

    def test_from_json_record_missing_domain_raises_error(self):
        """Test that JSON record without domain raises ValueError."""
        json_record = {"phone": "+1-555-0101"}

        with pytest.raises(ValueError, match="JSON record must contain 'domain' field"):
            CompanyRecord.from_json_record(json_record)


class TestAggregateJsonRecordsByDomain:
    """Test cases for aggregate_json_records_by_domain function."""

    def test_aggregate_single_domain_multiple_records(self):
        """Test aggregating multiple records for the same domain."""
        json_records = [
            {
                "domain": "example.com",
                "page_type": "homepage",
                "phone": "+1-555-0101",
                "social_media": ["https://twitter.com/example"],
            },
            {
                "domain": "example.com",
                "page_type": "contact",
                "phone": "+1-555-0102",
                "social_media": [
                    "https://facebook.com/example",
                    "https://twitter.com/example",
                ],
            },
        ]

        result = aggregate_json_records_by_domain(json_records)

        assert len(result) == 1
        assert "example.com" in result

        record = result["example.com"]
        assert record.domain == "example.com"
        assert len(record.phones) == 2
        assert "+1-555-0101" in record.phones
        assert "+1-555-0102" in record.phones
        assert len(record.social_media) == 2  # Duplicates removed
        assert "https://twitter.com/example" in record.social_media
        assert "https://facebook.com/example" in record.social_media
        assert len(record.page_types) == 2
        assert "homepage" in record.page_types
        assert "contact" in record.page_types

    def test_aggregate_multiple_domains(self):
        """Test aggregating records for multiple domains."""
        json_records = [
            {"domain": "example.com", "phone": "+1-555-0101"},
            {"domain": "test.com", "phone": "+1-555-0201"},
            {"domain": "example.com", "phone": "+1-555-0102"},
        ]

        result = aggregate_json_records_by_domain(json_records)

        assert len(result) == 2
        assert "example.com" in result
        assert "test.com" in result

        # example.com should have 2 phones
        example_record = result["example.com"]
        assert len(example_record.phones) == 2

        # test.com should have 1 phone
        test_record = result["test.com"]
        assert len(test_record.phones) == 1

    def test_aggregate_skip_invalid_records(self):
        """Test that invalid records (missing domain) are skipped."""
        json_records = [
            {"domain": "example.com", "phone": "+1-555-0101"},
            {"phone": "+1-555-0201"},  # Missing domain
            {"domain": "", "phone": "+1-555-0202"},  # Empty domain
        ]

        result = aggregate_json_records_by_domain(json_records)

        assert len(result) == 1
        assert "example.com" in result

    def test_aggregate_empty_list(self):
        """Test aggregating empty list of records."""
        result = aggregate_json_records_by_domain([])
        assert result == {}

    def test_aggregate_preserves_all_data_types(self):
        """Test that aggregation preserves all types of data."""
        json_records = [
            {
                "domain": "example.com",
                "page_type": "homepage",
                "phone": "+1-555-0101",
                "social_media": ["https://twitter.com/example"],
                "address": "123 Main St",
                "url": "https://example.com",
            },
            {
                "domain": "example.com",
                "page_type": "contact",
                "phone": "+1-555-0102",
                "social_media": ["https://facebook.com/example"],
                "address": "456 Oak Ave",
                "url": "https://example.com/contact",
            },
        ]

        result = aggregate_json_records_by_domain(json_records)
        record = result["example.com"]

        # Should have consolidated all data
        assert len(record.phones) == 2
        assert len(record.social_media) == 2
        assert len(record.addresses) == 2
        assert len(record.page_types) == 2
        assert len(record.urls) == 2
