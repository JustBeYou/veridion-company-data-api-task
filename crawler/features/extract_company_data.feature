Feature: Extract company data from websites
  As a data analyst
  I want to extract company information from websites
  So that I can build a comprehensive company database

  Background:
    Given the web crawler is initialized
    And the target website is accessible

  Scenario: Extract company name from HTML title
    Given a website with company name in the title tag
    When I crawl the website
    Then the company name should be extracted
    And the extraction should be stored

  Scenario: Extract phone number from contact page
    Given a website with phone number in the content
    When I crawl the website
    Then the phone number should be extracted
    And the phone number should be in normalized format

  Scenario: Extract social media links
    Given a website with social media links
    When I crawl the website
    Then the social media links should be extracted
    And the links should be validated as active social media URLs

  Scenario: Extract company address
    Given a website with company address
    When I crawl the website
    Then the address should be extracted
    And the address should be in a structured format
