Feature: Hello World
  As a developer
  I want to verify that the project setup is working
  So that I can start implementing the crawler features

  Scenario: Verify basic function
    Given the project is set up
    When I call the hello_world function
    Then it should return "Hello, World!"
