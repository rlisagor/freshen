Feature: Freshen command line
  In order to write better software
  Developers should be able to execute requirements as tests

  Scenario: Run single scenario with missing step definition
    When I run nose features/sample.feature:1
    Then it should pass with
      """
        U
        ----------------------------------------------------------------------
        Ran 1 test in 0.001s

        OK (UNDEFINED=1)
      """

