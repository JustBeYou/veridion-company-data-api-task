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
# Install poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
make install
```

## Usage

```bash
# Run the crawler with default domains from configs/companies-domains.csv
make run

# Run the crawler with a specific URL
make run-specific URL=https://example.com

# Run the crawler using Docker
make docker-run
```

## Development

This project follows Acceptance Test Driven Development (ATDD) with Behavior Driven Development (BDD) principles.

### Running Tests

```bash
# Run all tests
make test

# Run only the behavior tests
poetry run behave tests/acceptance/features/

# Run only the unit tests
poetry run pytest tests/unit
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
├── data/                      # Output data directory
├── src/                       # Source code
│   ├── spiders/               # Scrapy spiders
│   ├── items.py               # Scrapy items
│   ├── models.py              # Data models
│   ├── company_data_extractor.py # Data extraction logic
│   ├── domain_loader.py       # Domain loading functionality
│   ├── pipelines.py           # Scrapy pipelines
│   ├── settings.py            # Scrapy settings
│   └── middlewares.py         # Scrapy middlewares
├── tests/                     # Tests
│   ├── unit/                  # Unit tests
│   └── acceptance/            # Acceptance tests
│       ├── features/          # Gherkin feature files
│       └── steps/             # Step definitions
├── test_files/                # Test fixtures and data
├── Dockerfile                 # Docker configuration
├── pyproject.toml             # Poetry configuration
├── poetry.lock                # Poetry lock file
├── Makefile                   # Make targets
└── scrapy.cfg                 # Scrapy configuration
```

## Docker

The project includes Docker support for containerized execution:

```bash
# Build the Docker image
make docker-build

# Run the crawler in Docker
make docker-run
```

## License

MIT
