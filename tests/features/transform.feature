Feature: Step argument transforms
  
  Scenario: Run an example with step argument transforms
    When I run nose examples/befriending
    Then it should pass with
        """
        .
        ----------------------------------------------------------------------
        Ran 1 test in {time}

        OK
        """
