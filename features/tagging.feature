Feature: Tagging
  It is often useful to group scenarios or features by topic, status, etc

  Scenario: Run with a tag that exists on 2 scenarios
    When I run nose -v --tags three examples/self_test/features
    Then it should pass with
        """
        Sample: Missing ... UNDEFINED: "missing" # examples{sep}self_test{sep}features{sep}sample.feature:7
        Sample: Passing ... ok

        ----------------------------------------------------------------------
        Ran 2 tests in {time}

        OK (UNDEFINED=1)
        """

  Scenario: Run with a tag that exists on 3 feature
    When I run nose -v --tags @one examples/self_test
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

  Scenario: Run with a negative tag
    When I run nose -v --tags ~three examples/self_test/features/sample.feature
    Then it should fail with
    """
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
    Ran 1 test in {time}
    
    FAILED (errors=1)
    """


  Scenario: Run with a negative feature tag
    When I run nose -v --tags ~pending examples/counter_independence/features/independent_four.feature
    Then it should pass with
    """
    
    ----------------------------------------------------------------------
    Ran 0 tests in {time}

    OK
    """
