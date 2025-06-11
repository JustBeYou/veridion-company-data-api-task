Feature: End-to-end spider evaluation
  As a data analyst
  I want to run the spider on a small set of domains
  So that I can validate the complete extraction pipeline

  Scenario: Run spider on 5 domains and validate output
    Given the crawler is configured to process 5 domains
    When I run the spider end-to-end
    Then a JSON output file should be created
    And the JSON file should contain exactly 8 company records
    And each record should have the required company data fields
    And the output should be valid JSON format
