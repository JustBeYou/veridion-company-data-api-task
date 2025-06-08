import os

from behave import given, then, when

from src.domain_loader import DomainLoader


@given("the web crawler is initialized")
def step_given_crawler_initialized(context) -> None:
    context.domain_loader = DomainLoader()


@given('a CSV file "{file_name}" with domains')
def step_given_csv_file_with_domains(context, file_name: str) -> None:
    # Set the path to the CSV file - assuming it's in the configs directory
    context.csv_file_path = os.path.join("configs", file_name)
    # Check if the file exists
    assert os.path.exists(
        context.csv_file_path
    ), f"CSV file {context.csv_file_path} does not exist"


@given("a CSV file with some invalid domain entries")
def step_given_csv_file_with_invalid_domains(context) -> None:
    # This step would typically create a test CSV file with some invalid domains
    # For now, we'll assume we have a test file with invalid entries
    context.csv_file_path = "test_files/invalid_domains.csv"
    # In a real implementation, you'd create this file or use a mock


@when("I load the domains from the CSV file")
def step_when_load_domains_from_csv(context) -> None:
    context.loaded_domains = context.domain_loader.load_domains(context.csv_file_path)


@then("the domains should be loaded successfully")
def step_then_domains_loaded_successfully(context) -> None:
    assert context.loaded_domains is not None
    assert len(context.loaded_domains) > 0, "No domains were loaded"


@then("the crawler should be ready to process them")
def step_then_crawler_ready_to_process(context) -> None:
    assert (
        context.domain_loader.is_ready()
    ), "Domain loader is not ready to process domains"


@then("only valid domains should be loaded")
def step_then_only_valid_domains_loaded(context) -> None:
    for domain in context.loaded_domains:
        assert context.domain_loader.is_valid_domain(
            domain
        ), f"Invalid domain loaded: {domain}"


@then("invalid entries should be logged")
def step_then_invalid_entries_logged(context) -> None:
    # In a real implementation, we would check logs
    # This is a placeholder assertion for now
    assert context.domain_loader.invalid_count > 0, "No invalid domains were detected"
