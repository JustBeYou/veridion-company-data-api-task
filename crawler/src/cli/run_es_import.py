"""Command line interface for Elasticsearch import functionality."""

import argparse
import logging
import sys
from pathlib import Path

from src.searchdb.elasticsearch_importer import ElasticsearchImporter


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def import_csv_command(args: argparse.Namespace) -> int:
    """Handle CSV import command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        logging.info(f"Importing CSV file: {args.file}")
        count = importer.import_csv_file(args.file)
        logging.info(f"Successfully imported {count} records from CSV")
        return 0

    except Exception as e:
        logging.error(f"Failed to import CSV file: {e}")
        return 1


def import_json_command(args: argparse.Namespace) -> int:
    """Handle JSON import command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        logging.info(f"Importing JSON file: {args.file}")
        count = importer.import_json_file(args.file)
        logging.info(f"Successfully imported {count} records from JSON")
        return 0

    except Exception as e:
        logging.error(f"Failed to import JSON file: {e}")
        return 1


def search_command(args: argparse.Namespace) -> int:
    """Handle search command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        logging.info(f"Searching for: {args.query}")
        results = importer.search_companies(args.query, size=args.size)

        if not results:
            print("No results found.")
            return 0

        print(f"\nFound {len(results)} results:")
        print("-" * 50)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Domain: {result['domain']}")

            if result.get("company_names"):
                print(f"   Company Names: {', '.join(result['company_names'])}")

            if result.get("phones"):
                print(f"   Phones: {', '.join(result['phones'])}")

            if result.get("social_media"):
                print(f"   Social Media: {', '.join(result['social_media'])}")

            if result.get("addresses"):
                print(f"   Addresses: {', '.join(result['addresses'])}")

            if result.get("page_types"):
                print(f"   Page Types: {', '.join(result['page_types'])}")

        return 0

    except Exception as e:
        logging.error(f"Search failed: {e}")
        return 1


def get_company_command(args: argparse.Namespace) -> int:
    """Handle get company by domain command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        logging.info(f"Getting company data for domain: {args.domain}")
        result = importer.get_company_by_domain(args.domain)

        if not result:
            print(f"No company found for domain: {args.domain}")
            return 0

        print(f"\nCompany data for {args.domain}:")
        print("-" * 50)

        if result.get("company_names"):
            print(f"Company Names: {', '.join(result['company_names'])}")

        if result.get("phones"):
            print(f"Phones: {', '.join(result['phones'])}")

        if result.get("social_media"):
            print(f"Social Media: {', '.join(result['social_media'])}")

        if result.get("addresses"):
            print(f"Addresses: {', '.join(result['addresses'])}")

        if result.get("page_types"):
            print(f"Page Types: {', '.join(result['page_types'])}")

        if result.get("urls"):
            print(f"URLs: {', '.join(result['urls'])}")

        return 0

    except Exception as e:
        logging.error(f"Failed to get company data: {e}")
        return 1


def stats_command(args: argparse.Namespace) -> int:
    """Handle index statistics command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        stats = importer.get_index_stats()

        if not stats.get("exists"):
            print(f"Index '{args.index}' does not exist.")
            return 0

        print(f"\nIndex Statistics for '{args.index}':")
        print("-" * 50)
        print(f"Document Count: {stats['document_count']}")
        print(f"Index Size: {stats['index_size']} bytes")

        return 0

    except Exception as e:
        logging.error(f"Failed to get index stats: {e}")
        return 1


def delete_index_command(args: argparse.Namespace) -> int:
    """Handle delete index command."""
    try:
        importer = ElasticsearchImporter(es_host=args.es_host, index_name=args.index)

        if not args.confirm:
            response = input(
                f"Are you sure you want to delete index '{args.index}'? (y/N): "
            )
            if response.lower() != "y":
                print("Operation cancelled.")
                return 0

        importer.delete_index()
        print(f"Index '{args.index}' deleted successfully.")
        return 0

    except Exception as e:
        logging.error(f"Failed to delete index: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Elasticsearch Company Data Import Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import CSV file
  python -m src.searchdb.cli import-csv data/companies.csv

  # Import JSON file
  python -m src.searchdb.cli import-json data/scraped_data.json

  # Search for companies
  python -m src.searchdb.cli search "example"

  # Get specific company by domain
  python -m src.searchdb.cli get example.com

  # View index statistics
  python -m src.searchdb.cli stats

  # Delete index (use with caution!)
  python -m src.searchdb.cli delete-index --confirm
        """,
    )

    # Global arguments
    parser.add_argument(
        "--es-host",
        default="localhost:9200",
        help="Elasticsearch host and port (default: localhost:9200)",
    )
    parser.add_argument(
        "--index",
        default="companies",
        help="Elasticsearch index name (default: companies)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import CSV command
    csv_parser = subparsers.add_parser(
        "import-csv", help="Import company data from CSV file"
    )
    csv_parser.add_argument("file", type=Path, help="Path to CSV file to import")
    csv_parser.set_defaults(func=import_csv_command)

    # Import JSON command
    json_parser = subparsers.add_parser(
        "import-json", help="Import company data from JSON file"
    )
    json_parser.add_argument("file", type=Path, help="Path to JSON file to import")
    json_parser.set_defaults(func=import_json_command)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for companies")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--size", type=int, default=10, help="Maximum number of results (default: 10)"
    )
    search_parser.set_defaults(func=search_command)

    # Get company command
    get_parser = subparsers.add_parser("get", help="Get company data by domain")
    get_parser.add_argument("domain", help="Domain to lookup")
    get_parser.set_defaults(func=get_company_command)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show index statistics")
    stats_parser.set_defaults(func=stats_command)

    # Delete index command
    delete_parser = subparsers.add_parser(
        "delete-index", help="Delete the entire index (use with caution!)"
    )
    delete_parser.add_argument(
        "--confirm", action="store_true", help="Skip confirmation prompt"
    )
    delete_parser.set_defaults(func=delete_index_command)

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        return 1

    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
