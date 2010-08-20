Feature: befriending many

    Scenario: befriending many people
        When user duane befriends user adelaide
        And user duane befriends user hazel
        And user hazel befriends user adelaide
        Then these users should be friends: duane, hazel, adelaide

    
