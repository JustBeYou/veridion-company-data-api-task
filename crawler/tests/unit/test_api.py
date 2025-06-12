"""Unit tests for the API module."""

import json
import unittest
from unittest.mock import MagicMock, patch

from src.dashboard.api import clean_url, normalize_phone


class TestAPIUtilities(unittest.TestCase):
    """Test utility functions in the API module."""

    def test_normalize_phone(self) -> None:
        """Test phone number normalization."""
        test_cases = [
            ("(555) 123-4567", "5551234567"),
            ("555-123-4567", "5551234567"),
            ("+1 (555) 123-4567", "15551234567"),
            ("555.123.4567", "5551234567"),
            ("555 123 4567", "5551234567"),
            ("abc555def123ghi4567", "5551234567"),
            ("", ""),
            ("no digits here", ""),
        ]

        for input_phone, expected in test_cases:
            with self.subTest(input_phone=input_phone):
                result = normalize_phone(input_phone)
                self.assertEqual(result, expected)

    def test_clean_url(self) -> None:
        """Test URL cleaning functionality."""
        test_cases = [
            ("https://www.example.com", "example.com"),
            ("http://www.example.com", "example.com"),
            ("https://example.com", "example.com"),
            ("http://example.com", "example.com"),
            ("www.example.com", "example.com"),
            ("example.com", "example.com"),
            ("HTTPS://WWW.EXAMPLE.COM", "example.com"),
            ("https://subdomain.example.com", "subdomain.example.com"),
            ("", ""),
            ("not-a-url", "not-a-url"),
        ]

        for input_url, expected in test_cases:
            with self.subTest(input_url=input_url):
                result = clean_url(input_url)
                self.assertEqual(result, expected)


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        from src.dashboard.app import app

        app.config["TESTING"] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.app_context.pop()

    def test_health_endpoint(self) -> None:
        """Test the health check endpoint."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "company-search-api")

    def test_search_endpoint_no_json(self) -> None:
        """Test search endpoint with no JSON data."""
        response = self.client.post("/api/search", content_type="application/json")
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("No JSON data provided", data["error"])

    def test_search_endpoint_empty_data(self) -> None:
        """Test search endpoint with empty search criteria."""
        payload = {}
        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("At least one search field must be provided", data["error"])

    @patch("src.dashboard.api.ElasticsearchImporter")
    def test_search_endpoint_no_results(
        self, mock_es_importer_class: MagicMock
    ) -> None:
        """Test search endpoint when no results are found."""
        # Mock Elasticsearch response with no hits
        mock_es_instance = MagicMock()
        mock_es_importer_class.return_value = mock_es_instance
        mock_es_instance.es_client.search.return_value = {"hits": {"hits": []}}

        payload = {
            "name": "Acme Corp",
            "phone": ["555-123-4567"],
            "urls": ["https://www.example.com"],
            "address": "123 Main St",
        }

        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertFalse(data["found"])
        self.assertIn("No matching companies found", data["message"])
        self.assertIn("search_criteria", data)

    @patch("src.dashboard.api.ElasticsearchImporter")
    def test_search_endpoint_with_results(
        self, mock_es_importer_class: MagicMock
    ) -> None:
        """Test search endpoint with successful results."""
        # Mock Elasticsearch response with a hit
        mock_es_instance = MagicMock()
        mock_es_importer_class.return_value = mock_es_instance
        mock_es_instance.es_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_score": 2.5,
                        "_source": {
                            "domain": "example.com",
                            "company_names": ["Acme Corp"],
                            "phones": ["5551234567"],
                            "addresses": ["123 Main St, Anytown, USA"],
                        },
                    }
                ]
            }
        }

        payload = {
            "name": "Acme Corp",
            "phone": ["555-123-4567"],
            "urls": ["https://www.example.com"],
            "address": "123 Main St",
        }

        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["found"])
        self.assertEqual(data["score"], 2.5)
        self.assertIn("company", data)
        self.assertEqual(data["company"]["domain"], "example.com")
        self.assertIn("search_criteria", data)

        # Verify search criteria processing
        search_criteria = data["search_criteria"]
        self.assertEqual(search_criteria["names"], ["Acme Corp"])
        self.assertEqual(search_criteria["normalized_phones"], ["5551234567"])
        self.assertEqual(search_criteria["cleaned_urls"], ["example.com"])
        self.assertEqual(search_criteria["addresses"], ["123 Main St"])

    @patch("src.dashboard.api.ElasticsearchImporter")
    def test_search_endpoint_string_inputs(
        self, mock_es_importer_class: MagicMock
    ) -> None:
        """Test search endpoint with string inputs instead of arrays."""
        mock_es_instance = MagicMock()
        mock_es_importer_class.return_value = mock_es_instance
        mock_es_instance.es_client.search.return_value = {"hits": {"hits": []}}

        payload = {
            "name": "Acme Corp",
            "phone": "555-123-4567",  # String instead of array
            "urls": "https://www.example.com",  # String instead of array
            "address": "123 Main St",
        }

        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )

        # Should not fail due to string inputs
        self.assertIn(response.status_code, [200, 404])  # Either result or no result

    @patch("src.dashboard.api.ElasticsearchImporter")
    def test_search_endpoint_elasticsearch_error(
        self, mock_es_importer_class: MagicMock
    ) -> None:
        """Test search endpoint when Elasticsearch raises an error."""
        mock_es_instance = MagicMock()
        mock_es_importer_class.return_value = mock_es_instance
        mock_es_instance.es_client.search.side_effect = Exception(
            "Elasticsearch connection failed"
        )

        payload = {
            "name": "Acme Corp",
            "phone": ["555-123-4567"],
            "urls": ["https://www.example.com"],
            "address": "123 Main St",
        }

        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)

        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Internal server error", data["error"])

    @patch("src.dashboard.api.ElasticsearchImporter")
    def test_search_endpoint_debug_mode(
        self, mock_es_importer_class: MagicMock
    ) -> None:
        """Test search endpoint with debug=true returns top 10 results."""
        mock_es_instance = MagicMock()
        mock_es_importer_class.return_value = mock_es_instance
        mock_es_instance.es_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_score": 2.5,
                        "_source": {
                            "domain": "example1.com",
                            "company_names": ["Company 1"],
                        },
                    },
                    {
                        "_score": 2.0,
                        "_source": {
                            "domain": "example2.com",
                            "company_names": ["Company 2"],
                        },
                    },
                ]
            }
        }

        payload = {
            "name": ["Test Company"],
            "debug": True,
        }

        response = self.client.post(
            "/api/search", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data["found"])
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["score"], 2.5)
        self.assertEqual(data["results"][1]["score"], 2.0)

        # Verify the search was called with size=10
        mock_es_instance.es_client.search.assert_called_once()
        call_args = mock_es_instance.es_client.search.call_args
        self.assertEqual(call_args.kwargs["size"], 10)


if __name__ == "__main__":
    unittest.main()
