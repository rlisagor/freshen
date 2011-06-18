Feature: Asynchronous Testing
  In order to test event-based applications with freshen 
  As a developer and freshen user
  I want to be able to execute tests that return their results asynchronously

  # This scenario requires twisted to work correctly
  # otherwise it will (and should) not pass.
  Scenario: Event-based testing
    When I implement a step that returns a twisted Deferred object
    Then freshen will wait for the result before executing the next step

