import json
import os

from behave import given, then, when

from src.crawler import run_crawler


@given("the crawler is configured to process 5 domains")
def step_given_crawler_configured_for_5_domains(context) -> None:
    """Configure the crawler to process exactly 5 domains."""
    context.domain_limit = 5
    context.domains_file = "configs/companies-domains.csv"
    context.output_file = None


@when("I run the spider end-to-end")
def step_when_run_spider_end_to_end(context) -> None:
    """Run the complete spider pipeline."""
    context.output_file = run_crawler(
        domains_file=context.domains_file, domain_limit=context.domain_limit
    )
    context.crawler_completed = True


@then("a JSON output file should be created")
def step_then_json_file_created(context) -> None:
    """Verify that a JSON output file was created."""
    assert context.output_file is not None, "No output file was returned"
    assert os.path.exists(
        context.output_file
    ), f"Output file {context.output_file} does not exist"
    assert context.output_file.endswith(
        ".json"
    ), f"Output file {context.output_file} is not a JSON file"


@then("the JSON file should contain exactly 5 company records")
def step_then_json_contains_5_records(context) -> None:
    """Verify the JSON file contains exactly 5 company records."""
    with open(context.output_file, "r") as f:
        data = json.load(f)

    assert isinstance(data, list), "JSON data should be a list of records"
    assert len(data) == 5, f"Expected 5 records, got {len(data)}"
    context.company_records = data


@then("each record should have the required company data fields")
def step_then_records_have_required_fields(context) -> None:
    """Verify each record has the required company data fields."""
    required_fields = [
        "phone",
        "social_media",
        "address",
        "domain",
        "page_type",
    ]

    for i, record in enumerate(context.company_records):
        assert isinstance(record, dict), f"Record {i} should be a dictionary"
        for field in required_fields:
            assert field in record, f"Record {i} missing required field: {field}"


@then("the output should be valid JSON format")
def step_then_output_valid_json(context) -> None:
    """Verify the output file is valid JSON format."""
    try:
        with open(context.output_file, "r") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON format: {e}")
