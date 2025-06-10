.PHONY: help install test lint format type-check quality-check run clean pre-commit docker-build-crawler docker-run-crawler docker-run-with-output-crawler docker-build-dashboard docker-run-dashboard

help:
	@echo "Available commands:"
	@echo "  install         - Install dependencies"
	@echo "  test            - Run all tests"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  type-check      - Run type checking"
	@echo "  quality-check   - Run all quality checks"
	@echo "  run-crawler     - Run crawler"
	@echo "  run-dashboard   - Run dashboard"
	@echo "  clean           - Clean build artifacts"
	@echo "  pre-commit      - Run pre-commit hooks"
	@echo "  docker-build-crawler    - Build Docker image"
	@echo "  docker-run-crawler      - Run crawler in Docker container"
	@echo "  docker-run-with-output-crawler - Run crawler and save output to data/"
	@echo "  docker-build-dashboard    - Build Docker image"
	@echo "  docker-run-dashboard      - Run dashboard in Docker container"
	@echo "  clean-data        - Clean data directory"

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

run-crawler:
	poetry run python3 src/crawler.py

run-dashboard:
	poetry run python3 src/dashboard/app.py

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

clean-data:
	rm -rf data/*

docker-build-crawler:
	docker build -t company-crawler . -f Dockerfile.crawler

docker-run-crawler:
	mkdir -p data
	docker run --rm company-crawler

docker-run-with-output-crawler:
	mkdir -p data
	docker run --rm -v $(PWD)/data:/app/data company-crawler

docker-build-dashboard:
	docker build -t company-crawler-dashboard . -f Dockerfile.dashboard

docker-run-dashboard:
	docker run -p 5000:5000 -v $(PWD)/data:/app/data --rm company-crawler-dashboard
