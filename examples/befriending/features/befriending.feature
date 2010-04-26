Feature: befriending

    Scenario: befriending
        When user duane befriends user adelaide
        Then user duane should be friends with user adelaide
        And user adelaide should be friends with user duane
    
