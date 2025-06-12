Feature: Import scraped data into Elasticsearch
  As a data analyst
  I want to import company data from different sources into Elasticsearch
  So that I can search and analyze company information efficiently

  Background:
    Given an Elasticsearch instance is running at localhost:9200
    And I have a clean Elasticsearch index for companies

  Scenario: Import CSV file with company names
    Given I have a CSV file with company data containing domains and company names
    When I import the CSV file into Elasticsearch
    Then the company data should be indexed by domain
    And each record should contain a company_names array with unique names
    And the company_names array should contain names from company_commercial_name, company_legal_name, and company_all_available_names
    And pipe-separated names in company_all_available_names should be split into individual names
    And all names in the company_names array should be unique

  Scenario: Import JSON file with scraped data
    Given I have a JSON file with scraped company data
    When I import the JSON file into Elasticsearch
    Then the scraped data should be aggregated by domain before importing
    And each record should contain consolidated phone numbers
    And each record should contain consolidated social_media links
    And each record should contain consolidated address information
    And each record should contain all page_types found for that domain

  Scenario: Merge data from multiple sources by domain
    Given I have already imported CSV company data for domain "example.com"
    And I have JSON scraped data for the same domain "example.com"
    When I import the JSON data
    Then the existing record for "example.com" should be updated not replaced
    And the record should contain both CSV and JSON data fields merged together
    And no duplicate records should exist for the same domain
    And existing data should be preserved and new data added

  Scenario: Aggregate JSON data efficiently before import
    Given I have a JSON file with multiple records for the same domain
    When I import the JSON file into Elasticsearch
    Then the records should be aggregated by domain before sending to Elasticsearch
    And phone numbers should be consolidated into a unique array
    And social media links should be consolidated into a unique array
    And addresses should be consolidated into a unique array
    And page types should be consolidated into a unique array
    And only one request per domain should be made to Elasticsearch

  Scenario: Handle missing or null values gracefully
    Given I have data files with missing or null values
    When I import the data into Elasticsearch
    Then null values should be ignored
    And empty strings should be ignored
    And only valid data should be indexed
    And the import process should not fail due to missing values

  Scenario: Ensure data uniqueness within records
    Given I have data with duplicate values for the same domain
    When I import the data into Elasticsearch
    Then each array field should contain only unique values
    And duplicate phone numbers should be removed
    And duplicate social media links should be removed
    And duplicate addresses should be removed
    And duplicate company names should be removed
