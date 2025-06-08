# Web Crawler Component Setup Guide

This guide will walk you through initializing the web crawler component from scratch using automated commands and scripts.

**IMPORTANT**: This crawler is one component of a larger multi-component project. All setup and development happens within the `crawler/` subfolder.

## Prerequisites

- Python 3.11 or higher
- Git
- Make (for running Makefile commands)

## Quick Start

Navigate to the crawler component directory and run setup:

```bash
# Navigate to the project root, then to crawler component
cd path/to/your/project/crawler

# Run the complete setup
make setup-component
```

## Manual Step-by-Step Setup

If you prefer to understand each step or need to troubleshoot:

### 1. Create Crawler Component Structure

```bash
# Ensure you're in the crawler/ directory
cd crawler/

# Create directory structure within crawler component
mkdir -p src/spiders features/steps tests/{unit,acceptance} docs

# Create __init__.py files
touch src/__init__.py
touch src/spiders/__init__.py
touch features/__init__.py
touch features/steps/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/acceptance/__init__.py
```

### 2. Initialize Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

1. Put `scrapy behave requests lxml cssselect` into requirements.txt
2. Put `black isort flake8 mypy pylint pre-commit pytest coverage` into requirements-dev.txt
3. Install using pip inside the virtual environment.

### 4. Generate Configuration Files

**IMPORTANT**: Never write config files manually. Use these commands:

#### Black Configuration
```bash
# Generate black configuration in pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
EOF
```

#### isort Configuration
```bash
# Generate isort configuration
python -c "
import configparser
config = configparser.ConfigParser()
config['settings'] = {
    'profile': 'black',
    'multi_line_output': '3',
    'line_length': '88',
    'known_first_party': 'src',
    'known_third_party': 'scrapy,behave,requests,lxml',
    'sections': 'FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER',
    'default_section': 'THIRDPARTY'
}
with open('.isort.cfg', 'w') as f:
    config.write(f)
"
```

#### Flake8 Configuration
```bash
# Generate flake8 configuration
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    build,
    dist,
    *.egg-info
per-file-ignores = 
    __init__.py:F401
EOF
```

#### MyPy Configuration
```bash
# Generate mypy configuration
cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
show_error_codes = True

[mypy-scrapy.*]
ignore_missing_imports = True

[mypy-behave.*]
ignore_missing_imports = True

[mypy-src.*]
disallow_untyped_defs = True
EOF
```

#### Pre-commit Configuration
```bash
# Generate pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
EOF

# Install pre-commit hooks
pre-commit install
```

### 5. Generate Scrapy Project Structure

```bash
# Initialize Scrapy project within src/ directory
cd src/
scrapy startproject company_crawler .
cd ..

# This creates the proper Scrapy structure with:
# - items.py
# - middlewares.py  
# - pipelines.py
# - settings.py
# - spiders/ directory
```

### 6. Create Makefile

```bash
cat > Makefile << 'EOF'
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
	# Use pip and the requirements files here...

test:
	./venv/bin/behave features/
	./venv/bin/pytest tests/

lint:
	./venv/bin/flake8 src/ tests/ features/
	./venv/bin/pylint src/

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
	rm -rf venv/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
EOF
```

### 7. Create Initial Feature File

```bash
cat > features/extract_company_data.feature << 'EOF'
Feature: Extract company data from websites
  As a data analyst
  I want to extract company information from websites
  So that I can build a comprehensive company database

  Background:
    Given the web crawler is initialized
    And the target website is accessible

  Scenario: Extract company name from HTML title
    Given a website with company name "Acme Corporation" in the title tag
    When I crawl the website
    Then the company name "Acme Corporation" should be extracted
    And the extraction should be stored in the database

  Scenario: Extract phone number from contact page
    Given a website with phone number "(555) 123-4567" in the contact section
    When I crawl the website  
    Then the phone number "(555) 123-4567" should be extracted
    And the phone number should be in normalized format

  Scenario: Extract social media links
    Given a website with social media links to "facebook.com/acme" and "twitter.com/acme"
    When I crawl the website
    Then both social media links should be extracted
    And the links should be validated as active social media URLs

  Scenario: Extract company address
    Given a website with address "123 Main St, Anytown, ST 12345"
    When I crawl the website
    Then the address should be extracted
    And the address should be geocoded if possible
EOF
```

### 8. Create Component-Specific Git Configuration

```bash
# Create .gitignore for crawler component
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Crawler component specific
*.log
*.sqlite
scraped_data/
.scrapy/

# Testing
.pytest_cache/
.coverage
htmlcov/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Build
build/
dist/
*.egg-info/
EOF

# Note: Git initialization should be done at project root level
# This .gitignore is for the crawler component only
```

## Verification

After setup, verify everything works:

```bash
# Ensure you're in the crawler/ directory
cd crawler/

# Activate virtual environment
source venv/bin/activate

# Run quality checks
make quality-check

# Check that all tools are working
black --check src/
isort --check-only src/
flake8 src/
mypy src/
behave --dry-run features/
```

## Development Workflow

Once setup is complete, follow this workflow:

1. **Write Feature File**: Start with `.feature` file describing behavior
2. **Run Behave**: `behave features/` (should fail initially)
3. **Implement Step Definitions**: Write step definitions in `features/steps/`
4. **Write Production Code**: Implement minimal code to pass tests
5. **Run Quality Checks**: `make quality-check`
6. **Commit**: Only commit when all checks pass

## Troubleshooting

### Python Version Issues
```bash
# Check Python version
python --version
# Should be 3.11+

# If wrong version, use specific Python
python3.11 -m venv venv
```

### Virtual Environment Issues
```bash
# Deactivate and recreate
deactivate
rm -rf venv/
make install
```

### Configuration Issues
```bash
# Regenerate all configs
make generate-configs

# Test individual tools
./venv/bin/black --check .
./venv/bin/isort --check-only .  
./venv/bin/flake8 .
./venv/bin/mypy src/
```

### Pre-commit Issues
```bash
# Reinstall pre-commit hooks
./venv/bin/pre-commit uninstall
./venv/bin/pre-commit install

# Test pre-commit
./venv/bin/pre-commit run --all-files
```

## Next Steps

After successful setup:

1. Review the generated Scrapy project structure in `src/`
2. Start implementing your first spider following TDD principles
3. Write comprehensive feature files for all extraction scenarios
4. Set up CI/CD pipeline using the same quality checks
5. Coordinate with other project components as needed

**Remember**: 
- All development must follow the ATDD/BDD workflow defined in `.cursorrules`
- Work within the `crawler/` component directory
- This is one component of a larger multi-component project