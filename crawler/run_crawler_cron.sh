#!/bin/bash

# Crawler cron script
# This script runs the crawler in a loop with configurable sleep intervals

set -e

# Default sleep time in minutes if not provided via environment variable
CRAWLER_SLEEP_MINUTES=${CRAWLER_SLEEP_MINUTES:-60}
DOMAIN_LIMIT=${DOMAIN_LIMIT:-10000}

echo "Starting crawler cron with ${CRAWLER_SLEEP_MINUTES} minute intervals..."

# Import sample websites at startup
echo "Importing sample websites..."
python3 src/cli/run_es_import.py --es-host http://elasticsearch:9200 import-csv configs/sample-websites-company-names.csv

while true; do
    echo "Starting crawler..."
    python3 src/cli/run_crawler.py --domains-file configs/companies-domains.csv --domain-limit $DOMAIN_LIMIT || true

    # Import latest companies file after crawler finishes
    echo "Importing latest companies data..."

    # Get the latest JSON file from the crawler
    latest_json_file=$(ls -t data/companies_*.json | head -n 1)
    echo "Importing latest companies data from $latest_json_file..."
    python3 src/cli/run_es_import.py --es-host http://elasticsearch:9200 import-json $latest_json_file

    echo "Crawler finished. Waiting ${CRAWLER_SLEEP_MINUTES} minutes for next run..."
    sleep $((CRAWLER_SLEEP_MINUTES * 60))
done
