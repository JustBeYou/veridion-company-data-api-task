# Web Crawler Component

This is a web crawler component for extracting company data points (name, phone, social media links, address) from websites.

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-dir>/crawler
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Running Tests

To run all tests and quality checks:

```bash
make quality-check
```

This will run:
- Code formatting with black and isort
- Linting with flake8
- Type checking with mypy
- BDD tests with behave
- Unit tests with pytest

To run specific checks:

- `make test`: Run all tests
- `make lint`: Run linters
- `make format`: Format code
- `make type-check`: Check types

## Project Structure

- `src/`: Source code
  - `spiders/`: Scrapy spiders
  - `items.py`: Scrapy item definitions
  - `pipelines.py`: Item processing pipelines
  - `middlewares.py`: Scrapy middlewares
  - `settings.py`: Scrapy settings
- `features/`: BDD feature files and step definitions
- `tests/`: Test files
  - `unit/`: Unit tests
  - `acceptance/`: Acceptance tests
- `docs/`: Documentation

## Development Workflow

1. Write feature files in `features/`
2. Implement step definitions in `features/steps/`
3. Write minimal production code in `src/`
4. Run `make quality-check` to verify everything works
5. Refactor if needed

## License

[Your license information]
