.PHONY: help install test lint format type-check quality-check run clean pre-commit docker-build docker-run docker-run-with-output

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
	@echo "  docker-build    - Build Docker image"
	@echo "  docker-run      - Run crawler in Docker container"
	@echo "  docker-run-with-output - Run crawler and save output to data/"

install:
	poetry install

test:
	poetry run pytest tests/unit
	poetry run behave tests/acceptance/

lint:
	poetry run flake8 src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

type-check:
	poetry run mypy src/

quality-check: format lint type-check test
	@echo "All quality checks passed!"

pre-commit:
	poetry run pre-commit run

run:
	poetry run python3 src/crawler.py

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

docker-build:
	docker build -t company-crawler .

docker-run:
	mkdir -p data
	docker run --rm company-crawler

docker-run-with-output:
	mkdir -p data
	docker run --rm -v $(PWD)/data:/app/data
