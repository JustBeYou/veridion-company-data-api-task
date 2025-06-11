#!/bin/bash

# Filter alive domains from companies-domains.csv
# Usage: ./filter_alive_domains.sh [--verbose]

set -euo pipefail

# Configuration
INPUT_FILE="configs/companies-domains.csv"
OUTPUT_FILE="configs/alive-domains.csv"
TEMP_DIR=$(mktemp -d)
PARALLEL_JOBS=20
TIMEOUT=5
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log verbose messages
log_verbose() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}[DEBUG] $1${NC}" >&2
    fi
}

# Function to check if a domain is alive
check_domain() {
    local domain="$1"
    # Clean up domain (remove any whitespace, carriage returns)
    domain=$(echo "$domain" | tr -d '\r\n' | xargs)

    # Skip empty domains
    if [[ -z "$domain" ]]; then
        return 1
    fi

    local protocols=("https" "http")

    for protocol in "${protocols[@]}"; do
        local url="${protocol}://${domain}"

        log_verbose "Checking $url"

        # Use curl to check if domain responds
        local http_code
        http_code=$(curl -s -L --max-time "$TIMEOUT" --max-redirs 3 \
           --user-agent "Mozilla/5.0 (compatible; DomainChecker/1.0)" \
           -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")

        log_verbose "HTTP code for $url: $http_code"

        # Check for successful HTTP codes
        if [[ "$http_code" =~ ^(200|201|202|301|302|303|307|308|400|401|403|405|410|429|500|502|503)$ ]]; then
            echo "$domain"
            log_verbose "✓ $domain is alive (code: $http_code)"
            return 0
        fi
    done

    log_verbose "✗ $domain appears to be dead"
    return 1
}

# Export function and variables so parallel can use them
export -f check_domain log_verbose
export TIMEOUT VERBOSE BLUE NC

# Function to test a few domains manually for debugging
test_sample_domains() {
    echo -e "${YELLOW}Testing a few sample domains manually...${NC}"
    local sample_domains=("google.com" "github.com" "stackoverflow.com")

    for domain in "${sample_domains[@]}"; do
        echo -n "Testing $domain... "
        if check_domain "$domain" >/dev/null; then
            echo -e "${GREEN}ALIVE${NC}"
        else
            echo -e "${RED}DEAD${NC}"
        fi
    done
}

# Main script
main() {
    echo -e "${YELLOW}Starting domain filtering process...${NC}"

    # Check if input file exists
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo -e "${RED}Error: Input file $INPUT_FILE not found!${NC}" >&2
        exit 1
    fi

    # Check if parallel is installed
    if ! command -v parallel >/dev/null 2>&1; then
        echo -e "${RED}Error: GNU parallel is not installed. Please install it first.${NC}" >&2
        echo "On Ubuntu/Debian: sudo apt-get install parallel"
        echo "On macOS: brew install parallel"
        exit 1
    fi

    # Run test if verbose mode is enabled
    if [[ "$VERBOSE" == true ]]; then
        test_sample_domains
        echo ""
    fi

    # Count total domains (excluding header)
    local total_domains=$(tail -n +2 "$INPUT_FILE" | wc -l)
    echo -e "${YELLOW}Total domains to check: $total_domains${NC}"
    echo -e "${YELLOW}Using $PARALLEL_JOBS parallel jobs with ${TIMEOUT}s timeout${NC}"

    # Create output file with header
    echo "domain" > "$OUTPUT_FILE"

    # Process domains in parallel
    echo -e "${YELLOW}Checking domains...${NC}"

    # Skip header line, clean up line endings, and process domains
    tail -n +2 "$INPUT_FILE" | \
    tr -d '\r' | \
    parallel -j "$PARALLEL_JOBS" --bar --line-buffer check_domain {} >> "$OUTPUT_FILE"

    # Count results
    local alive_domains=$(tail -n +2 "$OUTPUT_FILE" | wc -l)
    local dead_domains=$((total_domains - alive_domains))

    echo -e "${GREEN}✓ Processing complete!${NC}"
    echo -e "${GREEN}Alive domains: $alive_domains${NC}"
    echo -e "${RED}Dead domains: $dead_domains${NC}"
    echo -e "${GREEN}Results saved to: $OUTPUT_FILE${NC}"

    # Show first few alive domains if any were found
    if [[ $alive_domains -gt 0 ]]; then
        echo -e "${YELLOW}First few alive domains:${NC}"
        head -6 "$OUTPUT_FILE"
    fi

    # Cleanup
    rm -rf "$TEMP_DIR"
}

# Trap to cleanup on exit
trap 'rm -rf "$TEMP_DIR"' EXIT

# Check if script is being run from the correct directory
if [[ ! -f "$INPUT_FILE" ]]; then
    echo -e "${RED}Error: Please run this script from the crawler directory${NC}" >&2
    echo "cd to the directory containing configs/companies-domains.csv"
    exit 1
fi

# Run main function
main "$@"
