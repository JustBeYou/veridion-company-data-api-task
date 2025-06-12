#!/bin/bash

# Crawler cron script
# This script runs the crawler in a loop with configurable sleep intervals

set -e

# Default sleep time in minutes if not provided via environment variable
CRAWLER_SLEEP_MINUTES=${CRAWLER_SLEEP_MINUTES:-60}
DOMAIN_LIMIT=${DOMAIN_LIMIT:-10000}

echo "Starting crawler cron with ${CRAWLER_SLEEP_MINUTES} minute intervals..."

while true; do
    echo "Starting crawler..."
    python3 src/cli/run_crawler.py --domains-file configs/companies-domains.csv --domain-limit $DOMAIN_LIMIT || true
    echo "Crawler finished. Waiting ${CRAWLER_SLEEP_MINUTES} minutes for next run..."
    sleep $((CRAWLER_SLEEP_MINUTES * 60))
done
