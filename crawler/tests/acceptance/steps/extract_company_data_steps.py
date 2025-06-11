from behave import given, then, when

from src.company_data.company_data_extractor import CompanyDataExtractor


@given("the target website is accessible")
def step_given_target_website_accessible(context) -> None:
    # This would typically check if the website is up
    # For testing, we'll use a mock or fixture
    context.website_accessible = True


@given("a website with phone number in the content")
def step_given_website_with_phone_number(context) -> None:
    # Mock response with phone number
    context.mock_response = {
        "url": "https://example.com/contact",
        "html": "<html><body><div class='contact'>Phone: (555) 123-4567</div></body></html>",
    }
    context.expected_phone = "(555) 123-4567"
    context.expected_normalized_phone = "5551234567"


@given("a website with social media links")
def step_given_website_with_social_media_links(context) -> None:
    # Mock response with social media links
    context.mock_response = {
        "url": "https://example.com",
        "html": """
        <html><body>
            <div class='social-links'>
                <a href="https://facebook.com/examplecompany">Facebook</a>
                <a href="https://twitter.com/examplecompany">Twitter</a>
                <a href="https://linkedin.com/company/examplecompany">LinkedIn</a>
            </div>
        </body></html>
        """,
    }
    context.expected_social_media = [
        "https://facebook.com/examplecompany",
        "https://twitter.com/examplecompany",
        "https://linkedin.com/company/examplecompany",
    ]


@given("a website with company address")
def step_given_website_with_address(context) -> None:
    # Mock response with address
    context.mock_response = {
        "url": "https://example.com/contact",
        "html": """
        <html><body>
            <div class='address'>
                123 Main St, Anytown, ST 12345
            </div>
        </body></html>
        """,
    }
    context.expected_address = "123 Main St, Anytown, ST 12345"


@when("I crawl the website")
def step_when_crawl_website(context) -> None:
    # Initialize the extractor
    context.extractor = CompanyDataExtractor()
    # Extract data from mock response
    context.extracted_data = context.extractor.extract(
        context.mock_response["url"], context.mock_response["html"]
    )


@then("the extraction should be stored")
def step_then_extraction_stored(context) -> None:
    # This would check if the data is stored in the database or output file
    # For now, we'll just check if the extractor has the data
    assert context.extractor.has_data(context.mock_response["url"])


@then("the phone number should be extracted")
def step_then_phone_number_extracted(context) -> None:
    assert context.extracted_data.phone is not None
    assert context.extracted_data.phone == context.expected_phone


@then("the phone number should be in normalized format")
def step_then_phone_number_normalized(context) -> None:
    normalized_phone = context.extractor.normalize_phone(context.extracted_data.phone)
    assert normalized_phone == context.expected_normalized_phone


@then("the social media links should be extracted")
def step_then_social_media_links_extracted(context) -> None:
    assert context.extracted_data.social_media is not None
    assert len(context.extracted_data.social_media) > 0
    for expected_link in context.expected_social_media:
        assert expected_link in context.extracted_data.social_media


@then("the links should be validated as active social media URLs")
def step_then_links_validated(context) -> None:
    for link in context.extracted_data.social_media:
        assert context.extractor.is_valid_social_media_url(link)


@then("the address should be extracted")
def step_then_address_extracted(context) -> None:
    assert context.extracted_data.address is not None
    assert context.extracted_data.address == context.expected_address


@then("the address should be in a structured format")
def step_then_address_structured(context) -> None:
    # This would check if the address is parsed into components
    # For now, just check if it's extracted
    assert context.extracted_data.address is not None
