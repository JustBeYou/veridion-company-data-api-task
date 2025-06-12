"""
API endpoints for company data search.
"""

import logging
import os
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from flask import Blueprint, jsonify, request

from ..searchdb.elasticsearch_importer import ElasticsearchImporter

logger = logging.getLogger(__name__)

# Create Flask Blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number format.

    Args:
        phone: Phone number to normalize

    Returns:
        str: Normalized phone number (digits only)
    """
    # Extract digits only
    return "".join(re.findall(r"\d", phone))


def clean_url(url: str) -> str:
    """
    Clean URL by removing protocol, www, and other useless stuff.

    Args:
        url: URL to clean

    Returns:
        str: Cleaned URL (domain only)
    """
    if not url or not url.strip():
        return url.strip() if url else ""

    try:
        # Add protocol if missing (check both lower and upper case)
        url_lower = url.lower()
        if not url_lower.startswith(("http://", "https://")):
            url = f"http://{url}"

        # Parse the URL
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        return domain
    except Exception:
        # If parsing fails, return the original URL stripped
        return url.strip()


@api_bp.route("/search", methods=["POST"])
def search_companies() -> Any:
    """
    Search for companies based on provided fields.

    Expected JSON format:
    {
        "name": ["name1", "name2"] or "single name",
        "phone": ["phone1", "phone2"] or "single phone",
        "urls": ["url1", "url2"] or "single url",
        "address": ["address1", "address2"] or "single address",
        "debug": true/false (optional, returns top 10 results if true)
    }

    Returns:
        JSON response with the best matching company record (or top 10 if debug=true)
    """
    try:
        # Get JSON data from request
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract fields from request
        names = data.get("name", [])
        phones = data.get("phone", [])
        urls = data.get("urls", [])
        addresses = data.get("address", [])
        debug = data.get("debug", False)

        # Normalize inputs to lists
        if isinstance(names, str):
            names = [names] if names.strip() else []
        if isinstance(addresses, str):
            addresses = [addresses] if addresses.strip() else []
        if isinstance(phones, str):
            phones = [phones] if phones.strip() else []
        if isinstance(urls, str):
            urls = [urls] if urls.strip() else []

        # Validate inputs - check if any field has meaningful content
        has_names = names and any(n.strip() for n in names if isinstance(n, str))
        has_phones = phones and any(p.strip() for p in phones if isinstance(p, str))
        has_urls = urls and any(u.strip() for u in urls if isinstance(u, str))
        has_addresses = addresses and any(
            a.strip() for a in addresses if isinstance(a, str)
        )

        if not any([has_names, has_phones, has_urls, has_addresses]):
            return jsonify({"error": "At least one search field must be provided"}), 400

        # Normalize phone numbers
        normalized_phones = [
            normalize_phone(phone) for phone in phones if phone and phone.strip()
        ]

        # Clean URLs
        cleaned_urls = [clean_url(url) for url in urls if url and url.strip()]

        # Clean names (remove extra whitespace)
        cleaned_names = [name.strip() for name in names if name and name.strip()]

        # Clean addresses (remove extra whitespace)
        cleaned_addresses = [
            addr.strip() for addr in addresses if addr and addr.strip()
        ]

        # Initialize Elasticsearch client
        es_importer = ElasticsearchImporter(es_host=os.environ.get("ES_URI"))  # type: ignore

        # Build Elasticsearch query
        search_query = build_search_query(
            cleaned_names, normalized_phones, cleaned_urls, cleaned_addresses
        )

        # Execute search
        search_size = 10 if debug else 1
        results = es_importer.es_client.search(
            index=es_importer.index_name,
            body=search_query,
            size=search_size,
        )

        # Process results
        hits = results.get("hits", {}).get("hits", [])
        if not hits:
            return (
                jsonify(
                    {
                        "found": False,
                        "message": "No matching companies found",
                        "search_criteria": {
                            "names": cleaned_names,
                            "normalized_phones": normalized_phones,
                            "cleaned_urls": cleaned_urls,
                            "addresses": cleaned_addresses,
                        },
                    }
                ),
                404,
            )

        # Return results (single best match or top 10 if debug)
        if debug:
            return jsonify(
                {
                    "found": True,
                    "results": [
                        {"score": hit["_score"], "company": hit["_source"]}
                        for hit in hits
                    ],
                    "search_criteria": {
                        "names": cleaned_names,
                        "normalized_phones": normalized_phones,
                        "cleaned_urls": cleaned_urls,
                        "addresses": cleaned_addresses,
                    },
                }
            )
        else:
            best_match = hits[0]
            return jsonify(
                {
                    "found": True,
                    "score": best_match["_score"],
                    "company": best_match["_source"],
                    "search_criteria": {
                        "names": cleaned_names,
                        "normalized_phones": normalized_phones,
                        "cleaned_urls": cleaned_urls,
                        "addresses": cleaned_addresses,
                    },
                }
            )

    except Exception as e:
        logger.error(f"Error in search_companies: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


def build_search_query(
    names: List[str], phones: List[str], urls: List[str], addresses: List[str]
) -> Dict[str, Any]:
    """
    Build Elasticsearch query based on provided search criteria.

    Args:
        names: List of company names to search for
        phones: List of normalized phone numbers
        urls: List of cleaned URLs/domains
        addresses: List of addresses to search for

    Returns:
        Dict: Elasticsearch query body
    """
    should_clauses = []

    HIGHEST_BOOST = 3.0
    MEDIUM_BOOST = 2.0
    LOWEST_BOOST = 1.0

    # Search in company names
    if names:
        for name in names:
            # Fuzzy match on company names
            should_clauses.append(
                {
                    "match": {
                        "company_names": {
                            "query": name,
                            "fuzziness": "AUTO",
                            "boost": HIGHEST_BOOST,
                        }
                    }
                }
            )
            # Exact match on keyword field
            should_clauses.append(
                {
                    "term": {
                        "company_names.keyword": {"value": name, "boost": HIGHEST_BOOST}
                    }
                }
            )

            # Split name by capital letters and add matching clause, keeping abbreviations together
            name_parts = []
            current_part = ""

            for char in name:
                if char.isupper():
                    if current_part and len(current_part) >= 3:
                        name_parts.append(current_part)
                    current_part = char
                else:
                    current_part += char

            if current_part and len(current_part) >= 3:
                name_parts.append(current_part)

            if name_parts:
                should_clauses.append(
                    {
                        "match": {
                            "company_names": {
                                "query": " ".join(name_parts),
                                "fuzziness": "AUTO",
                                "boost": MEDIUM_BOOST,
                            }
                        }
                    }
                )

    # Search in phone numbers
    if phones:
        for phone in phones:
            should_clauses.append(
                {"term": {"phones": {"value": phone, "boost": MEDIUM_BOOST}}}
            )

    # Search in URLs/domains (medium boost)
    if urls:
        for url in urls:
            should_clauses.append(
                {"term": {"domain": {"value": url, "boost": HIGHEST_BOOST}}}
            )
            should_clauses.append(
                {"term": {"urls": {"value": url, "boost": MEDIUM_BOOST}}}
            )

    # Search in addresses (lower boost but fuzzy)
    if addresses:
        for address in addresses:
            should_clauses.append(
                {
                    "match": {
                        "addresses": {
                            "query": address,
                            "fuzziness": "AUTO",
                            "boost": LOWEST_BOOST,
                        }
                    }
                }
            )

    # If no specific criteria, return empty query
    if not should_clauses:
        return {"query": {"match_all": {}}}

    # Build the main query
    query = {
        "query": {"bool": {"should": should_clauses, "minimum_should_match": 1}},
        "sort": [{"_score": {"order": "desc"}}],
    }

    return query


@api_bp.route("/showcase/export", methods=["GET"])
def export_showcase_data() -> Any:
    """Export the actual showcase results data as downloadable JSON."""
    try:
        import csv
        import json
        import os
        from datetime import datetime

        from flask import make_response

        # Use the same logic as the showcase page to get the actual results
        def load_csv_data() -> List[Dict[str, str]]:
            """Load the API input sample CSV file."""
            csv_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "configs", "API-input-sample.csv"
            )

            data = []
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Skip empty rows
                        if any(v.strip() for v in row.values() if v):
                            data.append(row)
            except FileNotFoundError:
                logger.warning(f"CSV file not found: {csv_path}")
            except Exception as e:
                logger.warning(f"Error reading CSV: {e}")

            return data

        def process_csv_entry(entry: Dict[str, str]) -> Dict[str, Any]:
            """
            Process a single CSV entry and call the search API.

            Args:
                entry: Dictionary containing CSV row data

            Returns:
                Dict containing the search result and metadata
            """
            # Extract data from CSV entry
            name = entry.get("input name", "").strip()
            phone = entry.get("input phone", "").strip()
            website = entry.get("input website", "").strip()
            facebook = entry.get("input_facebook", "").strip()

            # Build URLs list
            urls = []
            if website:
                urls.append(website)
            if facebook:
                urls.append(facebook)

            # Build phone list
            phones = [phone] if phone else []

            # Prepare API request data
            api_data = {
                "name": name,
                "phone": phones,
                "urls": urls,
                "address": "",  # No address in CSV
            }

            # Call the search API directly (internal call, not HTTP)
            try:
                # Use the same search logic as the API endpoint
                names = [name] if name else []
                normalized_phones = [
                    normalize_phone(phone)
                    for phone in phones
                    if phone and phone.strip()
                ]
                cleaned_urls = [clean_url(url) for url in urls if url and url.strip()]
                cleaned_addresses: List[str] = []

                if names or normalized_phones or cleaned_urls:
                    # Initialize Elasticsearch client
                    es_importer = ElasticsearchImporter(
                        es_host=os.environ.get("ES_URI")  # type: ignore
                    )

                    # Build and execute search
                    search_query = build_search_query(
                        names, normalized_phones, cleaned_urls, cleaned_addresses
                    )
                    results = es_importer.es_client.search(
                        index=es_importer.index_name, body=search_query, size=1
                    )

                    hits = results.get("hits", {}).get("hits", [])
                    if hits:
                        result = {
                            "found": True,
                            "score": hits[0]["_score"],
                            "company": hits[0]["_source"],
                            "search_criteria": {
                                "names": names,
                                "normalized_phones": normalized_phones,
                                "cleaned_urls": cleaned_urls,
                                "addresses": cleaned_addresses,
                            },
                        }
                    else:
                        result = {
                            "found": False,
                            "message": "No matching companies found",
                            "search_criteria": {
                                "names": names,
                                "normalized_phones": normalized_phones,
                                "cleaned_urls": cleaned_urls,
                                "addresses": cleaned_addresses,
                            },
                        }
                else:
                    result = {
                        "found": False,
                        "error": "At least one search field must be provided",
                    }

            except Exception as api_error:
                result = {"found": False, "error": f"API call failed: {str(api_error)}"}

            return {
                "input_data": {
                    "name": name,
                    "phone": phone,
                    "website": website,
                    "facebook": facebook,
                },
                "api_request": api_data,
                "api_response": result,
            }

        # Load CSV data and process entries (same as showcase page)
        csv_data = load_csv_data()
        results = []

        # Process each CSV entry
        for entry in csv_data:
            result = process_csv_entry(entry)
            results.append(result)

        # Create export data structure
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "description": "API Search Showcase Results Export",
                "source": "API-input-sample.csv",
                "total_entries": len(results),
                "note": "Contains actual API test results from CSV data displayed on /api-showcase page",
            },
            "results": results,
            "api_documentation": {
                "endpoint": "/api/search",
                "method": "POST",
                "content_type": "application/json",
                "fields": {
                    "name": "Company name(s) - supports multiple variations",
                    "phone": "Phone number(s) - automatically normalized",
                    "urls": "Website URLs - automatically cleaned and normalized",
                    "address": "Company address(es) - supports multiple formats",
                    "debug": "Boolean flag to return top 10 results instead of single best match",
                },
                "features": [
                    "Multiple values: All fields accept both single strings and arrays",
                    "Debug mode: Set debug=true to get top 10 results instead of best match",
                    "Smart matching: Fuzzy search with intelligent scoring",
                    "URL cleaning: Automatically removes protocols, www, and normalizes domains",
                    "Phone normalization: Extracts and normalizes phone numbers to digits-only",
                ],
            },
        }

        # Create response with proper headers for file download
        response_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        response = make_response(response_data)
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Disposition"] = (
            f'attachment; filename=api_showcase_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

        return response

    except Exception as e:
        logger.error(f"Error exporting showcase data: {str(e)}")
        return jsonify({"error": f"Export failed: {str(e)}"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check() -> Dict[str, str]:
    """Health check endpoint for the API."""
    return {"status": "healthy", "service": "company-search-api"}
