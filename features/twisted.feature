Feature: Asynchronous Testing
  In order to test event-based applications with freshen 
  As a developer and freshen user
  I want to be able to execute tests that return their results asynchronously

  # This scenario requires twisted to work correctly
  # otherwise it will (and should) not pass.
  Scenario: Run an async test
    When I run nose examples/twisted/features/async-steps.feature
    Then it should pass with
        """
        .
        ----------------------------------------------------------------------
        Ran 1 test in {time}

        OK
        """
