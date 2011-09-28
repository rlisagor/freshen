Feature: Befriending
  In order to have some friends
  As a Facebook user
  I want to be able to manage my list of friends
  
  
  Background: User Ken has two friends
    Given I am the user Ken
    And I have friends Barbie, Cloe


  @new_friend
  Scenario: Adding a new friend
    When I add a new friend named Jade
    Then I should have friends Barbie, Cloe, Jade


  Scenario: Removing a friend
    When I remove my friend Cloe
    Then I should have friends Barbie
