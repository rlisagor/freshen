Using step definitions from: 'step/page_steps'

Feature: Navigate through a document
  In order to read a document
  As a reader 
  I want to be able to flip the pages of the document
     
     
  Scenario: Access next page
   Given a document of 5 pages
     And the page is 3
    When I click for the next page
    Then the page is 4
