.PHONY: help install test lint format type-check quality-check run clean

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

install:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pre-commit install

test:
	./venv/bin/behave features/
	./venv/bin/pytest tests/

lint:
	./venv/bin/flake8 src/ tests/ features/

format:
	./venv/bin/black src/ tests/ features/
	./venv/bin/isort src/ tests/ features/

type-check:
	./venv/bin/mypy src/

quality-check: format lint type-check test
	@echo "All quality checks passed!"

run:
	./venv/bin/scrapy crawl company_spider

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
