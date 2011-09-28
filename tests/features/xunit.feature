Feature: XUnit output
  In order to report feature/scenario execution to programs such as CI servers
  and reporting tools, they should be provided better output in XUnit format

  Scenario: Run all scenarios in sample feature and ensure xunit report is generated with appropriate contents
    When I run nose --with-xunit --xunit-file=/tmp/nosetests.xml examples/self_test/features/sample.feature
    Then it should fail with xunit file /tmp/nosetests.xml
    And it should report Passing from Sample as passed
    And it should report Failing from Sample as failed
    And it should report Missing from Sample as undefined
