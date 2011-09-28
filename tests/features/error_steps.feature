Feature: Error steps
    In order to speed up development
    It is useful to see a verbose report of which step has failed
    
    Scenario: Colorized output
      When I run nose -v --tags @one examples/self_test
      Then it should fail with colorized output
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

          [36m@one[0m
          Feature: Sample
              [36m@four[0m
              Scenario: Failing
                  [31mgiven failing                           [0m [2m# examples{sep}self_test{sep}features{sep}sample.feature:19[0m

          ----------------------------------------------------------------------
          Ran 3 tests in {time}

          FAILED (UNDEFINED=1, errors=1)
          """
    