# Crawler Dashboard

A Flask web application that provides a visual dashboard for monitoring web crawler runs and statistics.

## Features

- **Main Dashboard**: Displays cards showing summary statistics for all crawler runs, sorted from newest to oldest
- **Detailed View**: Click on any run to see comprehensive statistics including success rates, data fill rates, and page type analysis
- **Responsive Design**: Uses Tailwind CSS for modern, mobile-friendly styling
- **Automatic Data Loading**: Reads all `crawler_stats_*.json` files from the `crawler/data/` directory

## Running the Dashboard

### Prerequisites

Make sure you have Poetry installed and dependencies are up to date:

```bash
cd crawler
poetry install
```

### Start the Dashboard

From the `crawler/src/dashboard/` directory:

```bash
cd crawler/src/dashboard/
poetry run python app.py
```

Or from the crawler root directory:

```bash
cd crawler
poetry run python src/dashboard/app.py
```

The dashboard will be available at: http://localhost:5000

### Features Overview

#### Main Dashboard (`/`)
- Shows all crawler runs as cards
- Each card displays:
  - Run date and time
  - Number of companies processed
  - Success rates with color coding (green: good, yellow: fair, red: poor)
  - Data fill rates for names, phones, social media, and addresses
  - Domain statistics

#### Run Details (`/run/<filename>`)
- Comprehensive view of a specific crawler run
- Overview section with computation timestamp and output file
- Visual progress bars for success rates
- Detailed breakdown of domain and page statistics
- Data fill rates with color-coded progress indicators
- Page type analysis

### Data Structure

The dashboard expects stats files in the following format:
```json
{
  "metadata": {
    "computation_timestamp": "2025-06-10T18:36:55.673407",
    "output_file": "data/companies_20250610_183642.json",
    "total_records": 5
  },
  "domain_statistics": {
    "total_domains_attempted": 5,
    "domains_successfully_scraped": 3
  },
  "page_statistics": {
    "total_pages_attempted": 5,
    "pages_successfully_scraped": 5
  },
  "success_rates": {
    "domain_success_rate": 60.0,
    "page_success_rate": 100.0
  },
  "data_fill_rates": {
    "name": 100.0,
    "phone": 33.33,
    "social_media": 0.0,
    "address": 0.0
  },
  "page_type_analysis": {
    "domains_with_contact_page": 2
  }
}
```

### Development

To run in development mode with debug enabled:

```bash
cd crawler/src/dashboard/
FLASK_ENV=development poetry run python app.py
```

This will enable:
- Hot reloading on file changes
- Detailed error messages
- Debug toolbar

### File Structure

```
crawler/src/dashboard/
├── app.py                 # Main Flask application
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # Main dashboard page
│   └── run_details.html  # Detailed run view
└── README.md             # This file
```
