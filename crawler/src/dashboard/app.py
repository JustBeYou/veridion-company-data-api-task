import glob
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

from flask import Flask, render_template

from .api import api_bp

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
