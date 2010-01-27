Feature: Tagging
  It is often useful to group scenarios or features by topic, status, etc

  Scenario: Run with a tag that exists on 2 scenarios
    When I run nose -v --tags three features
    Then it should pass with
        """
        Sample: Missing ... UNDEFINED: "missing" # features/sample.feature:7
        Sample: Passing ... ok

        ----------------------------------------------------------------------
        Ran 2 tests in {time}

        OK (UNDEFINED=1)
        """

  Scenario: Run with a tag that exists on 1 feature
    When I run nose -v --tags @one
    Then it should fail with
        """
        Sample: Missing ... UNDEFINED: "missing" # features/sample.feature:7
        Sample: Passing ... ok
        Sample: Failing ... ERROR
         
        ======================================================================
        ERROR: Sample: Failing
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "{cwd}/features/steps.py", line 14, in failing
            flunker(runner)
          File "{cwd}/features/steps.py", line 5, in flunker
            raise Exception("FAIL")
        Exception: FAIL
        
        >> in "failing" # features/sample.feature:18
        
        ----------------------------------------------------------------------
        Ran 3 tests in {time}
        
        FAILED (UNDEFINED=1, errors=1)
        """

  Scenario: Run with a negative tag
    When I run nose -v --tags ~three features/sample.feature
    Then it should fail with
    """
    Sample: Failing ... ERROR
     
    ======================================================================
    ERROR: Sample: Failing
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "{cwd}/features/steps.py", line 14, in failing
        flunker(runner)
      File "{cwd}/features/steps.py", line 5, in flunker
        raise Exception("FAIL")
    Exception: FAIL
    
    >> in "failing" # features/sample.feature:18
    
    ----------------------------------------------------------------------
    Ran 1 test in {time}
    
    FAILED (errors=1)
    """

