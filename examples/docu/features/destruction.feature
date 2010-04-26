Using step definitions from: 'step/page_steps'

Feature: Destroy a document
  In order to take out one's anger on a document
  As an unsatisfied reader 
  I want to be able to rip off the pages of the document

    
  Scenario: Rip off a page
   Given a document of 5 pages
     And the page is 3
    When I rip off the current page
    Then the page is 3
     But the document has 4 pages
