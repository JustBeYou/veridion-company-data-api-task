import csv
import glob
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

import requests
from flask import Flask, render_template

from src.dashboard.api import api_bp

app = Flask(__name__)

# Register API Blueprint
app.register_blueprint(api_bp)


def load_crawler_stats() -> List[Dict[str, Any]]:
    """Load all crawler stats files from the data directory."""
    stats_files = []
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")

    # Find all crawler_stats_*.json files
    pattern = os.path.join(data_dir, "crawler_stats_*.json")
    files = glob.glob(pattern)

    for file_path in files:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Extract timestamp from filename for sorting
            filename = os.path.basename(file_path)
            # Format: crawler_stats_YYYYMMDD_HHMMSS.json
            timestamp_str = filename.replace("crawler_stats_", "").replace(".json", "")

            # Parse timestamp for sorting
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                data["file_timestamp"] = timestamp
                data["filename"] = filename
                stats_files.append(data)
            except ValueError:
                # If timestamp parsing fails, use file modification time
                mtime = os.path.getmtime(file_path)
                data["file_timestamp"] = datetime.fromtimestamp(mtime)
                data["filename"] = filename
                stats_files.append(data)

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}")
            continue

    # Sort by timestamp, newest first
    stats_files.sort(key=lambda x: x["file_timestamp"], reverse=True)
    return stats_files


@app.route("/")
def dashboard() -> str:
    """Main dashboard page showing all crawler runs."""
    crawler_runs = load_crawler_stats()
    return render_template("dashboard.html", crawler_runs=crawler_runs)


@app.route("/run/<filename>")
def run_details(filename: str) -> Union[str, Tuple[str, int]]:
    """Detailed view of a specific crawler run."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    file_path = os.path.join(data_dir, filename)

    try:
        with open(file_path, "r") as f:
            stats = json.load(f)
        return render_template("run_details.html", stats=stats, filename=filename)
    except (json.JSONDecodeError, FileNotFoundError):
        return "Stats file not found", 404


@app.route("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def process_csv_entry(entry: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a single CSV entry and call the search API.

    Args:
        entry: Dictionary containing CSV row data

    Returns:
        Dict containing the search result and metadata
    """
    # Extract data from CSV entry
    name = entry.get("input name", "").strip()
    phone = entry.get("input phone", "").strip()
    website = entry.get("input website", "").strip()
    facebook = entry.get("input_facebook", "").strip()

    # Build URLs list
    urls = []
    if website:
        urls.append(website)
    if facebook:
        urls.append(facebook)

    # Build phone list
    phones = [phone] if phone else []

    # Prepare API request data
    api_data = {
        "name": name,
        "phone": phones,
        "urls": urls,
        "address": "",  # No address in CSV
    }

    # Call the local API
    try:
        response = requests.post(
            "http://localhost:5000/api/search", json=api_data, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
        else:
            result = {
                "found": False,
                "error": f"API returned status {response.status_code}",
                "message": response.text,
            }
    except requests.exceptions.RequestException as e:
        result = {"found": False, "error": "Request failed", "message": str(e)}

    return {
        "input_data": {
            "name": name,
            "phone": phone,
            "website": website,
            "facebook": facebook,
        },
        "api_request": api_data,
        "api_response": result,
    }


def load_csv_data() -> List[Dict[str, str]]:
    """Load the API input sample CSV file."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "configs", "API-input-sample.csv"
    )

    data = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows
                if any(v.strip() for v in row.values() if v):
                    data.append(row)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")

    return data


@app.route("/api-showcase")
def api_showcase() -> str:
    """Showcase API search results for all CSV entries."""
    csv_data = load_csv_data()
    results = []

    # Process each CSV entry
    for entry in csv_data:
        result = process_csv_entry(entry)
        results.append(result)

    # Generate curl example for the first valid entry
    curl_example = generate_curl_example(csv_data)

    return render_template(
        "api_showcase.html",
        results=results,
        curl_example=curl_example,
        total_entries=len(results),
    )


def generate_curl_example(csv_data: List[Dict[str, str]]) -> str:
    """Generate a curl command example from the first valid CSV entry."""
    if not csv_data:
        return ""

    # Find first entry with some data
    example_entry = None
    for entry in csv_data:
        if any(v.strip() for v in entry.values() if v):
            example_entry = entry
            break

    if not example_entry:
        return ""

    # Build example API data
    name = example_entry.get("input name", "").strip()
    phone = example_entry.get("input phone", "").strip()
    website = example_entry.get("input website", "").strip()
    facebook = example_entry.get("input_facebook", "").strip()

    urls = []
    if website:
        urls.append(website)
    if facebook:
        urls.append(facebook)

    phones = [phone] if phone else []

    api_data = {"name": name, "phone": phones, "urls": urls, "address": ""}

    # Generate curl command
    json_data = json.dumps(api_data, indent=2)
    curl_command = f"""curl -X POST http://localhost:5000/api/search \\
  -H "Content-Type: application/json" \\
  -d '{json_data}'"""

    return curl_command


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
