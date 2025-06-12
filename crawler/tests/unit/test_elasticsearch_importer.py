"""Unit tests for Elasticsearch importer."""

import csv
import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from elasticsearch import ConnectionError as ESConnectionError
from elasticsearch import NotFoundError

from src.searchdb.data_models import CompanyRecord
from src.searchdb.elasticsearch_importer import ElasticsearchImporter


@pytest.fixture
def mock_es_client():
    """Create a mock Elasticsearch client."""
    mock_client = Mock()
    mock_client.ping.return_value = True
    mock_client.indices.exists.return_value = False
    mock_client.indices.create.return_value = {"acknowledged": True}
    mock_client.get.side_effect = NotFoundError()
    return mock_client


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing."""
    csv_data = [
        [
            "domain",
            "company_commercial_name",
            "company_legal_name",
            "company_all_available_names",
        ],
        [
            "example.com",
            "Example Corp",
            "Example Corporation Inc",
            "Example Corp|Example Inc|Example Company",
        ],
        ["test.com", "Test Company", "Test Company LLC", "Test Co|Test LLC"],
    ]

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    writer = csv.writer(temp_file)
    writer.writerows(csv_data)
    temp_file.close()

    yield temp_file.name

    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def sample_json_file():
    """Create a temporary JSON file for testing."""
    json_data = [
        {
            "domain": "example.com",
            "page_type": "homepage",
            "phone": "+1-555-0101",
            "social_media": [
                "https://twitter.com/example",
                "https://facebook.com/example",
            ],
            "address": "123 Main St, City, State",
            "url": "https://example.com",
        },
        {
            "domain": "test.com",
            "page_type": "contact",
            "phone": "+1-555-0102",
            "social_media": ["https://linkedin.com/company/test"],
            "address": "456 Oak Ave, Town, State",
            "url": "https://test.com/contact",
        },
    ]

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(json_data, temp_file, indent=2)
    temp_file.close()

    yield temp_file.name

    # Cleanup
    os.unlink(temp_file.name)


class TestElasticsearchImporter:
    """Test cases for ElasticsearchImporter class."""

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_init_successful_connection(self, mock_es_class):
        """Test successful initialization with working Elasticsearch connection."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter(
            es_host="localhost:9200", index_name="test_companies"
        )

        assert importer.es_host == "localhost:9200"
        assert importer.index_name == "test_companies"
        assert importer.es_client == mock_client
        mock_es_class.assert_called_once_with(["http://localhost:9200"])
        mock_client.ping.assert_called_once()

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_init_connection_failure(self, mock_es_class):
        """Test initialization failure when Elasticsearch is not available."""
        mock_client = Mock()
        mock_client.ping.return_value = False
        mock_es_class.return_value = mock_client

        with pytest.raises(ESConnectionError):
            ElasticsearchImporter(es_host="localhost:9200")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_init_ping_exception(self, mock_es_class):
        """Test initialization failure when ping raises exception."""
        mock_client = Mock()
        mock_client.ping.side_effect = Exception("Connection failed")
        mock_es_class.return_value = mock_client

        with pytest.raises(ESConnectionError):
            ElasticsearchImporter(es_host="localhost:9200")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_create_index_if_not_exists_new_index(self, mock_es_class):
        """Test creating index when it doesn't exist."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = False
        mock_client.indices.create.return_value = {"acknowledged": True}
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        importer.create_index_if_not_exists()

        mock_client.indices.exists.assert_called_once_with(index="companies")
        mock_client.indices.create.assert_called_once()

        # Verify mapping structure
        create_call_args = mock_client.indices.create.call_args
        assert create_call_args[1]["index"] == "companies"
        mapping = create_call_args[1]["body"]
        assert "mappings" in mapping
        assert "properties" in mapping["mappings"]
        assert "domain" in mapping["mappings"]["properties"]

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_create_index_if_not_exists_existing_index(self, mock_es_class):
        """Test skipping index creation when it already exists."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = True
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        importer.create_index_if_not_exists()

        mock_client.indices.exists.assert_called_once_with(index="companies")
        mock_client.indices.create.assert_not_called()

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_import_csv_file_success(self, mock_es_class, sample_csv_file):
        """Test successful CSV file import."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = False
        mock_client.get.side_effect = NotFoundError("Not found", {}, {})
        mock_es_class.return_value = mock_client

        # Mock bulk operation
        with patch("src.searchdb.elasticsearch_importer.bulk") as mock_bulk:
            mock_bulk.return_value = (2, [])  # 2 successful, 0 failed

            importer = ElasticsearchImporter()
            result = importer.import_csv_file(sample_csv_file)

            assert result == 2
            mock_bulk.assert_called_once()

            # Verify bulk actions
            bulk_call_args = mock_bulk.call_args
            actions = bulk_call_args[0][1]  # Second argument is actions list
            assert len(actions) == 2

            # Check first action
            action1 = actions[0]
            assert action1["_index"] == "companies"
            assert action1["_id"] == "example.com"
            assert "company_names" in action1["_source"]
            assert len(action1["_source"]["company_names"]) == 4  # All unique names

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_import_csv_file_not_found(self, mock_es_class):
        """Test CSV import with non-existent file."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()

        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            importer.import_csv_file("nonexistent.csv")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_import_json_file_success(self, mock_es_class, sample_json_file):
        """Test successful JSON file import."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = False
        mock_client.get.side_effect = NotFoundError("Not found", {}, {})
        mock_es_class.return_value = mock_client

        # Mock bulk operation
        with patch("src.searchdb.elasticsearch_importer.bulk") as mock_bulk:
            mock_bulk.return_value = (2, [])  # 2 successful, 0 failed

            importer = ElasticsearchImporter()
            result = importer.import_json_file(sample_json_file)

            assert result == 2
            mock_bulk.assert_called_once()

            # Verify bulk actions
            bulk_call_args = mock_bulk.call_args
            actions = bulk_call_args[0][1]  # Second argument is actions list
            assert len(actions) == 2

            # Check first action
            action1 = actions[0]
            assert action1["_index"] == "companies"
            assert action1["_id"] == "example.com"
            assert "phones" in action1["_source"]
            assert "social_media" in action1["_source"]

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_import_json_file_aggregation(self, mock_es_class):
        """Test JSON import with domain aggregation."""
        # Create JSON with duplicate domains
        json_data = [
            {"domain": "example.com", "phone": "+1-555-0101", "page_type": "homepage"},
            {
                "domain": "example.com",  # Same domain
                "phone": "+1-555-0102",
                "page_type": "contact",
            },
        ]

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(json_data, temp_file, indent=2)
        temp_file.close()

        try:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.indices.exists.return_value = False
            mock_client.get.side_effect = NotFoundError("Not found", {}, {})
            mock_es_class.return_value = mock_client

            # Mock bulk operation
            with patch("src.searchdb.elasticsearch_importer.bulk") as mock_bulk:
                mock_bulk.return_value = (1, [])  # 1 successful (aggregated)

                importer = ElasticsearchImporter()
                result = importer.import_json_file(temp_file.name)

                assert result == 1  # Should be 1 due to aggregation

                # Verify bulk actions - should have only 1 action for aggregated domain
                bulk_call_args = mock_bulk.call_args
                actions = bulk_call_args[0][1]
                assert len(actions) == 1

                # Check aggregated data
                action = actions[0]
                assert action["_id"] == "example.com"
                source = action["_source"]
                assert len(source["phones"]) == 2  # Both phones included
                assert len(source["page_types"]) == 2  # Both page types included

        finally:
            os.unlink(temp_file.name)

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_import_json_file_invalid_format(self, mock_es_class):
        """Test JSON import with invalid JSON format."""
        # Create invalid JSON file (not a list)
        json_data = {"domain": "example.com"}  # Object instead of array

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(json_data, temp_file, indent=2)
        temp_file.close()

        try:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_es_class.return_value = mock_client

            importer = ElasticsearchImporter()

            with pytest.raises(
                ValueError, match="JSON file must contain a list of records"
            ):
                importer.import_json_file(temp_file.name)

        finally:
            os.unlink(temp_file.name)

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_get_existing_record_found(self, mock_es_class):
        """Test getting existing record when it exists."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = {
            "_source": {"domain": "example.com", "company_names": ["Example Corp"]}
        }
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        result = importer._get_existing_record("example.com")

        assert result is not None
        assert result["domain"] == "example.com"
        assert result["company_names"] == ["Example Corp"]
        mock_client.get.assert_called_once_with(index="companies", id="example.com")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_get_existing_record_not_found(self, mock_es_class):
        """Test getting existing record when it doesn't exist."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.side_effect = NotFoundError("Not found", {}, {})
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        result = importer._get_existing_record("example.com")

        assert result is None
        mock_client.get.assert_called_once_with(index="companies", id="example.com")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_search_companies(self, mock_es_class):
        """Test searching for companies."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "domain": "example.com",
                            "company_names": ["Example Corp"],
                        }
                    }
                ]
            }
        }
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        results = importer.search_companies("example", size=5)

        assert len(results) == 1
        assert results[0]["domain"] == "example.com"
        assert results[0]["company_names"] == ["Example Corp"]

        # Verify search query
        search_call_args = mock_client.search.call_args
        assert search_call_args[1]["index"] == "companies"
        search_body = search_call_args[1]["body"]
        assert search_body["size"] == 5
        assert search_body["query"]["multi_match"]["query"] == "example"

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_get_company_by_domain(self, mock_es_class):
        """Test getting company by domain."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = {
            "_source": {"domain": "example.com", "company_names": ["Example Corp"]}
        }
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        result = importer.get_company_by_domain("example.com")

        assert result is not None
        assert result["domain"] == "example.com"
        assert result["company_names"] == ["Example Corp"]

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_delete_index(self, mock_es_class):
        """Test deleting index."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = True
        mock_client.indices.delete.return_value = {"acknowledged": True}
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        importer.delete_index()

        mock_client.indices.exists.assert_called_once_with(index="companies")
        mock_client.indices.delete.assert_called_once_with(index="companies")

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_get_index_stats_existing_index(self, mock_es_class):
        """Test getting index statistics for existing index."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = True
        mock_client.indices.stats.return_value = {
            "indices": {
                "companies": {
                    "total": {"docs": {"count": 100}, "store": {"size_in_bytes": 1024}}
                }
            }
        }
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        stats = importer.get_index_stats()

        assert stats["exists"] is True
        assert stats["document_count"] == 100
        assert stats["index_size"] == 1024

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_get_index_stats_non_existing_index(self, mock_es_class):
        """Test getting index statistics for non-existing index."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.indices.exists.return_value = False
        mock_es_class.return_value = mock_client

        importer = ElasticsearchImporter()
        stats = importer.get_index_stats()

        assert stats["exists"] is False
        mock_client.indices.stats.assert_not_called()

    @patch("src.searchdb.elasticsearch_importer.Elasticsearch")
    def test_bulk_import_with_merge(self, mock_es_class):
        """Test bulk import with record merging."""
        mock_client = Mock()
        mock_client.ping.return_value = True

        # Mock existing record
        def mock_get(index, id):
            if id == "example.com":
                return {
                    "_source": {
                        "domain": "example.com",
                        "company_names": ["Existing Corp"],
                    }
                }
            else:
                raise NotFoundError("Not found", {}, {})

        mock_client.get.side_effect = mock_get
        mock_es_class.return_value = mock_client

        # Create records to import
        new_record = CompanyRecord(domain="example.com", company_names=["New Corp"])

        # Mock bulk operation
        with patch("src.searchdb.elasticsearch_importer.bulk") as mock_bulk:
            mock_bulk.return_value = (1, [])

            importer = ElasticsearchImporter()
            result = importer._bulk_import_records([new_record])

            assert result == 1

            # Verify merged data
            bulk_call_args = mock_bulk.call_args
            actions = bulk_call_args[0][1]
            assert len(actions) == 1

            action = actions[0]
            source = action["_source"]
            assert len(source["company_names"]) == 2  # Merged names
            assert "Existing Corp" in source["company_names"]
            assert "New Corp" in source["company_names"]
