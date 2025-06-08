# Company Data Crawler

A web crawler component to extract company data points (name, phone, social media links, address) from websites. Built using Python 3, Scrapy, and following Acceptance Test Driven Development (ATDD) with Behavior Driven Development (BDD) principles.

## Features

- Extract company names from website titles and headings
- Extract phone numbers from website content
- Extract social media links from websites
- Extract addresses from website content
- Load domains to crawl from a CSV file

## Installation

```bash
# Install dependencies
make install

# Install development dependencies
make install-dev
```

## Usage

```bash
# Run the crawler with default domains from configs/companies-domains.csv
make run

# Run the crawler with a specific URL
make run-specific URL=https://example.com
```

## Development

This project follows Acceptance Test Driven Development (ATDD) with Behavior Driven Development (BDD) principles.

### Running Tests

```bash
# Run all tests
make test

# Run only the behavior tests
behave features/

# Run only the unit tests
python -m pytest tests/
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run all quality checks
make quality-check
```

## Project Structure

```
crawler/
├── configs/                   # Configuration files
│   └── companies-domains.csv  # List of domains to crawl
├── features/                  # BDD feature files
│   ├── steps/                 # Step definitions
│   └── *.feature              # Feature files
├── src/                       # Source code
│   ├── spiders/               # Scrapy spiders
│   ├── items.py               # Scrapy items
│   ├── pipelines.py           # Scrapy pipelines
│   └── settings.py            # Scrapy settings
├── tests/                     # Tests
│   ├── unit/                  # Unit tests
│   └── acceptance/            # Acceptance tests
├── Makefile                   # Make targets
```

## License

MIT
