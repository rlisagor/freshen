Feature: Freshen core
  In order to write better software
  Developers should be able to execute requirements as tests

  Scenario: Run single scenario with missing step definition
    When I run nose examples/self_test/features/sample.feature:1
    Then it should pass with
        """
        U
        ----------------------------------------------------------------------
        Ran 1 test in {time}

        OK (UNDEFINED=1)
        """

  Scenario: Specify the 1-based index of a scenario
    When I run nose examples/self_test/features/sample.feature:2
    Then it should pass with
        """
        .
        ----------------------------------------------------------------------
        Ran 1 test in {time}

        OK
        """

  Scenario: Run all with verbose formatter
    When I run nose -v examples/self_test/features/sample.feature
    Then it should fail with
        """
        Sample: Missing ... UNDEFINED: "missing" # examples{sep}self_test{sep}features{sep}sample.feature:7
        Sample: Passing ... ok
        Sample: Failing ... ERROR

        ======================================================================
        ERROR: Sample: Failing
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "{cwd}{sep}examples{sep}self_test{sep}features{sep}steps.py", line 14, in failing
            flunker()
          File "{cwd}{sep}examples{sep}self_test{sep}features{sep}steps.py", line 5, in flunker
            raise Exception("FAIL")
        Exception: FAIL

        >> in "failing" # examples{sep}self_test{sep}features{sep}sample.feature:18

        ----------------------------------------------------------------------
        Ran 3 tests in {time}
        
        FAILED (UNDEFINED=1, errors=1)
        """
  
  Scenario: Run scenario outline steps only
    When I run nose -v examples/self_test/features/outline_sample.feature:2:3:4:5
    Then it should fail with
        """
        Outline Sample: Test state ... UNDEFINED: "missing without a table" # examples{sep}self_test{sep}features{sep}outline_sample.feature:6
        Outline Sample: Test state ... ok
        Outline Sample: Test state ... ERROR
        Outline Sample: Test state ... ok

        ======================================================================
        ERROR: Outline Sample: Test state
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "{cwd}{sep}examples{sep}self_test{sep}features{sep}steps.py", line 22, in fail_without_table
            flunker()
          File "{cwd}{sep}examples{sep}self_test{sep}features{sep}steps.py", line 5, in flunker
            raise Exception("FAIL")
        Exception: FAIL

        >> in "failing without a table" # examples{sep}self_test{sep}features{sep}outline_sample.feature:6

        ----------------------------------------------------------------------
        Ran 4 tests in {time}

        FAILED (UNDEFINED=1, errors=1)
        """

  Scenario: Find feature files in nested directories
    When I run nose -v --tags nested examples/self_test/features
    Then it should pass with
        """
        A feature in a subdirectory: Passing ... ok
        A feature in a subdirectory (indirect import): Passing ... ok
        A feature in a subdirectory (undefined): Passing ... UNDEFINED: "passing without a table" # examples{sep}self_test{sep}features{sep}nested_two{sep}nested.feature:4
        
        ----------------------------------------------------------------------
        Ran 3 tests in {time}

        OK (UNDEFINED=1)
        """


