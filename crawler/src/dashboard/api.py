"""
API endpoints for company data search.
"""

import logging
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
        "name": "string",
        "phone": ["phone1", "phone2"],
        "urls": ["url1", "url2"],
        "address": "string"
    }

    Returns:
        JSON response with the best matching company record
    """
    try:
        # Get JSON data from request
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract fields from request
        name = data.get("name", "")
        phones = data.get("phone", [])
        urls = data.get("urls", [])
        address = data.get("address", "")

        # Validate inputs - check if any field has meaningful content
        has_name = name and name.strip()
        has_phones = (
            phones and any(p.strip() for p in phones if isinstance(p, str))
            if isinstance(phones, list)
            else (phones and str(phones).strip())
        )
        has_urls = (
            urls and any(u.strip() for u in urls if isinstance(u, str))
            if isinstance(urls, list)
            else (urls and str(urls).strip())
        )
        has_address = address and address.strip()

        if not any([has_name, has_phones, has_urls, has_address]):
            return jsonify({"error": "At least one search field must be provided"}), 400

        # Normalize phone numbers
        normalized_phones = []
        if phones:
            if isinstance(phones, str):
                phones = [phones]
            normalized_phones = [normalize_phone(phone) for phone in phones if phone]

        # Clean URLs
        cleaned_urls = []
        if urls:
            if isinstance(urls, str):
                urls = [urls]
            cleaned_urls = [clean_url(url) for url in urls if url]

        # Initialize Elasticsearch client
        es_importer = ElasticsearchImporter()

        # Build Elasticsearch query
        search_query = build_search_query(
            name, normalized_phones, cleaned_urls, address
        )

        # Execute search
        results = es_importer.es_client.search(
            index=es_importer.index_name,
            body=search_query,
            size=1,  # Only return the best match
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
                            "name": name,
                            "normalized_phones": normalized_phones,
                            "cleaned_urls": cleaned_urls,
                            "address": address,
                        },
                    }
                ),
                404,
            )

        # Return the best match
        best_match = hits[0]
        return jsonify(
            {
                "found": True,
                "score": best_match["_score"],
                "company": best_match["_source"],
                "search_criteria": {
                    "name": name,
                    "normalized_phones": normalized_phones,
                    "cleaned_urls": cleaned_urls,
                    "address": address,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error in search_companies: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


def build_search_query(
    name: str, phones: List[str], urls: List[str], address: str
) -> Dict[str, Any]:
    """
    Build Elasticsearch query based on provided search criteria.

    Args:
        name: Company name to search for
        phones: List of normalized phone numbers
        urls: List of cleaned URLs/domains
        address: Address to search for

    Returns:
        Dict: Elasticsearch query body
    """
    should_clauses = []

    # Search in company names (highest boost)
    if name:
        should_clauses.append(
            {
                "multi_match": {
                    "query": name,
                    "fields": ["company_names^3", "company_names.keyword^2"],
                    "type": "best_fields",
                    "boost": 3.0,
                }
            }
        )

    # Search in phone numbers (high boost)
    if phones:
        for phone in phones:
            should_clauses.append({"term": {"phones": {"value": phone, "boost": 2.5}}})

    # Search in URLs/domains (medium boost)
    if urls:
        for url in urls:
            should_clauses.append({"term": {"domain": {"value": url, "boost": 2.0}}})
            should_clauses.append({"term": {"urls": {"value": url, "boost": 1.8}}})

    # Search in addresses (lower boost but fuzzy)
    if address:
        should_clauses.append(
            {
                "match": {
                    "addresses": {"query": address, "fuzziness": "AUTO", "boost": 1.5}
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


@api_bp.route("/health", methods=["GET"])
def health_check() -> Dict[str, str]:
    """Health check endpoint for the API."""
    return {"status": "healthy", "service": "company-search-api"}
