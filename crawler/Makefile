.PHONY: help install test lint format type-check quality-check run clean pre-commit

help:
	@echo "Available commands:"
	@echo "  install         - Install dependencies"
	@echo "  test            - Run all tests"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  type-check      - Run type checking"
	@echo "  quality-check   - Run all quality checks"
	@echo "  run             - Run crawler"
	@echo "  clean           - Clean build artifacts"
	@echo "  pre-commit      - Run pre-commit hooks"

install:
	poetry install

test:
	poetry run behave features/
	poetry run pytest tests/

lint:
	poetry run flake8 src/ tests/ features/

format:
	poetry run black src/ tests/ features/
	poetry run isort src/ tests/ features/

type-check:
	poetry run mypy src/

quality-check: format lint type-check test
	@echo "All quality checks passed!"

pre-commit:
	poetry run pre-commit run

run:
	poetry run scrapy crawl company_spider

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
