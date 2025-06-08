Feature: Load domains from CSV file
  As a data analyst
  I want to load domains from a CSV file
  So that I can crawl those websites for company data

  Background:
    Given the web crawler is initialized

  Scenario: Load domains from CSV file
    Given a CSV file "companies-domains.csv" with domains
    When I load the domains from the CSV file
    Then the domains should be loaded successfully
    And the crawler should be ready to process them

  Scenario: Skip invalid domains
    Given a CSV file with some invalid domain entries
    When I load the domains from the CSV file
    Then only valid domains should be loaded
    And invalid entries should be logged
