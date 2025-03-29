# Werewolf  
Werewolf game played by AI  

# Setting up:  
Clone github or download zip and unzip code  
    open this folder in terminal  
    
configure LLM:  
    Go to [google AI](aistudio.google.com/)  
    Use a non school gmail account (same one as google cloud)  
    Generate API key (free for limited tokens)  
    paste it into line 10  
    
run the following command:  
    pip install google-generativeai  
    
then you can start the game with:  
    python gameloop.py  

Use Debug mode to edit parameters. Enable full mode for enhanced reasoning.  
    pythion gameloop.py debug  

Debug options:  
    Game is currently set to accommodate 5-10 players. Default is 5.  
    Conversations dictates how many rounds of AI Agents speaking before the day ends.  
    Mode 1 is fast. AI might forget conversations it had in the past.  
    Mode 2 is full. It includes a bluffing and reflection stage to increase recall potential.  

If you have a different AI model you would like to use instead of mistral the program has been modularized so that all calls to the AI reference back to a single callAI function.  
Gemini and replace it with a different LLM API or a local model easlily by modifiying this function.  

# Understand the game
This is a social deduction game, and as such there is a small number of evils fighting a large number of good players. The evil team kills once per night while the good team has to band together and vote out one person per day. There is a small pool of special roles including the angel who protects a player, investigator who gains information, and a fool whos goal is to be voted out. These characters are randomly sampled, so besides the werewolf there is always a chance none of them exist. During the day players discuss to find who they will execute. A player is randomly selected to nominate first and if the player they nominate has enough people willing to vote for that player, they are executed. If not, the nominator and nominee are added to a list so they can nominate or be nominated again. This repeats until a player is executed or no more nominations can be made. 

# How does the AI play it
They are given the rules to the game and a history of discussions and decisions. They then make a decision based on this information. Each night the special roles are allowed to decide who they select. They can then share this information, or choose to bluff as another role. The werewolf is forced to bluff as a good player. Each discussion is shared with all other AI agents and then after all the AIs have been given a chance to talk the nominations begin. Each AI agent is asked to give a list of players they would vote on. If they are selected to nominate they choose the first legal nominee on their list of votes. 

AI is in full control of the game, deciding who lives and dies and exactly what they will say to each other. They are capable of decieving each other or banding together. 

Inspired by https://github.com/raphydaphy/clocktower-ai which runs much faster and has a more complicated game state. I made this much simpler as a proof of concept

# Example gameplay

In case you can't get the AI model working, here is are a few examples 6 player games that ran on my computer.

Game 1

--- Players and Roles ---  
Alice is a Villager  
Nick is a Investigator  
Charlie is a Werewolf  
Eve is a Angel  
Isaac is a Villager  
Cooper is a Villager  

--- Night Phase ---  
Angel Eve protects Alice.  
Werewolf Charlie attacks Eve.  
Investigator Nick investigates Cooper and learns they are: Not a Werewolf.  

--- Discussion Phase ---  
AI Alice says: I think it's important we stay vigilant and work together to figure out who the Werewolf is. Let's vote for Nick tonight.  
AI Nick says: I have uncovered some crucial information about our group. Let's vote for Alice tonight.  
AI Charlie says: AI Charlie says: I found a hidden scroll with strange symbols on it, but don't know what it means. Let's vote for Isaac tonight.  
AI Isaac says: I found a strange symbol on Charlie's scroll, it could mean danger. Vote for Charlie tonight.  
AI Cooper says: AI Cooper says: I found a scroll with symbols, but I don't know what they mean. Let's vote for Nick tonight.  
Alice says: I would vote for{
        "votes": ["Nick", "Cooper"]
    }  
Nick says: I would vote for{
       "votes": ["Alice", "Charlie"]
    }  
Charlie says: I would vote for{
        "votes": ["Alice", "Isaac", "Cooper"]
    }  
Isaac says: I would vote for{
        "votes": ["Alice", "Nick", "Cooper"]
    }  
Cooper says: I would vote for{
       "votes": ["Nick", "Alice"]
    }  

--- Nomination Phase ---  
Charlie nominates Alice.  
Votes for Alice: Nick, Charlie, Isaac, Cooper  
Alice has been executed!  

--- Night Phase ---  
Werewolf Charlie attacks Nick.  
Investigator Nick investigates Cooper and learns they are: Not a Werewolf.  

--- Discussion Phase ---  
AI Charlie says: AI Charlie says: I found a scroll with strange symbols, and I think it's related to the Werewolf. Vote for Isaac tonight.  
AI Isaac says: AI Isaac says: I found a scroll with strange symbols, it could mean danger. Vote for Charlie tonight.  
AI Cooper says: AI Cooper says: I found a scroll with symbols, but I don't know what they mean. Let's vote for Charlie tonight.  
Charlie says: I would vote for{
        "votes": ["Isaac", "Cooper"]
    }  
Isaac says: I would vote for{
        "votes": ["Charlie", "Cooper"]
    }  
Cooper says: I would vote for{
        "votes": ["Charlie", "Isaac"]
    }  

--- Nomination Phase ---  
Cooper nominates Charlie.  
Votes for Charlie: Isaac, Cooper  
Charlie has been executed!  

Villagers win!

***

A brief analysis of the example game

It is strange that the AI Agents gets focused on scrolls and strange symbols, but this could also be seen as a diversionary tactic. Often in social deduction games if you can cause the good team to waste time focusing on things besides the game you might distract them. If you notice the first character to bring up scrolls and derail all future discussion was Charlie: the werewolf. This clearly did not work as all the AI still put Charlie on the chopping block but if they were to get the first nomination off they could have gotten Isaac executed instead. 

Another thing I find interesting is the investigator. They declare they have information but do not divulge it. This could be them trying to save the person they know isnt the werewolf (Cooper) or it could be an attempt to hide the fact that they are the investigator. If it was the latter, it was a poor attempt as the werewolf kills them the following night. They also check the same player the following night so possibly their past decisions are becoming lost among the discussions?

Most of the decisions in this game make a lot of sense. The votes line up with what people are discussing before nominations. The discussions themselves are a bit crazy, but that was intentionally injected by the werewolf which means it also makes sense to a degree. 

*** 

Game 2

--- Players and Roles ---
Alice is a Villager
Nick is a Werewolf
Charlie is a Villager
Eve is a Angel
Isaac is a Fool
Cooper is a Villager

--- Night Phase ---
Angel Eve protects Cooper.
Werewolf Nick attacks Cooper, but they are protected!

--- Discussion Phase ---
AI Alice says: I am Villager, let's work together to uncover the werewolf among us and save our village! Let's vote for Cooper tonight.
AI Nick says: AI Alice says: I am Cooper, the Fool. I am brave and willing to sacrifice myself for our village! Vote for Nick tonight.
AI Charlie says: AI Charlie says: I am Villager, I trust everyone in our village. Let's vote for the player we believe is least likely to be part of our village. Vote for Isaac tonight.
AI Eve says: I am Angel, protecting our village. Let's vote for Alice tonight.
AI Isaac says: AI Isaac says: I am a Villager, let's work together to find the werewolf. Vote for Cooper tonight.
AI Cooper says: AI Cooper says: I am Villager, let's work together and vote for the player we believe is least likely to be part of our village. Vote for Isaac tonight.
Alice says: I would vote for{
        "votes": ["Cooper", "Isaac"]
    }
Nick says: I would vote for{
        "votes": ["Alice", "Charlie", "Cooper"]
    }
Charlie says: I would vote for{
       "votes": ["Alice", "Cooper"]
    }
Eve says: I would vote for{
       "votes": ["Alice", "Cooper"]
    }
Isaac says: I would vote for{
      "votes": ["Alice", "Cooper"]
    }
Cooper says: I would vote for{
       "votes": ["Alice", "Isaac"]
   }

--- Nomination Phase ---
Eve nominates Alice.
Votes for Alice: Nick, Charlie, Eve, Isaac, Cooper
Alice has been executed!

--- Night Phase ---
Angel Eve protects Cooper.
Werewolf Nick attacks Charlie.

--- Discussion Phase ---
AI Nick says: AI Nick says: I am a Villager, I trust everyone in our village. Let's vote for Cooper tonight.
AI Eve says: I am Angel, protecting our village. Vote for Isaac tonight.
AI Isaac says: AI Isaac says: I am Villager, let's work together to find the werewolf and save our village! Vote for Cooper tonight.
AI Cooper says: AI Cooper says: I am Villager, I trust everyone in our village. Let's vote for the player we believe is least likely to be part of our village. Vote for Isaac tonight.
Nick says: I would vote for{
        "votes": ["Eve", "Isaac"]
    }
Eve says: I would vote for{
        "votes": ["Nick", "Isaac"]
    }
Isaac says: I would vote for{
       "votes": ["Cooper"]
    }
Cooper says: I would vote for{
       "votes": ["Eve"]
   }

--- Nomination Phase ---
Cooper nominates Eve.
Votes for Eve: Nick, Cooper
Eve nominates Nick.
Votes for Nick: Eve
Nick nominates Isaac.
Votes for Isaac: Nick, Eve

--- Night Phase ---
Angel Eve protects Cooper.
Werewolf Nick attacks Cooper, but they are protected!

--- Discussion Phase ---
AI Nick says: AI Nick says: I am Villager, let's work together to find and eliminate the Werewolf. Vote for Cooper tonight.
AI Eve says: I am Angel, protecting our village. Vote for Nick tonight.
AI Isaac says: AI Isaac says: I am Villager, I trust everyone in our village. Let's vote for the player we believe is least likely to be part of our village. Vote for Cooper tonight.
AI Cooper says: AI Cooper says: I am Villager, I trust everyone in our village. Let's vote for the player we believe is least likely to be part of our village. Vote for Isaac tonight.
Nick says: I would vote for{
        "votes": ["Eve", "Cooper"]
    }
Eve says: I would vote for{
       "votes": ["Isaac"]
    }
Isaac says: I would vote for{
        "votes": ["Cooper"]
    }
Cooper says: I would vote for{
       "votes": ["Isaac"]
   }

--- Nomination Phase ---
Eve nominates Isaac.
Votes for Isaac: Eve, Cooper
Cooper passes
Nick nominates Eve.
Votes for Eve: Nick
Isaac nominates Cooper.
Votes for Cooper: Nick, Isaac

--- Night Phase ---
Angel Eve protects Cooper.
Werewolf Nick attacks Isaac.

--- Discussion Phase ---
AI Nick says: AI Nick says: I am Villager, let's work together and vote for Cooper tonight.
AI Eve says: I am Angel, protecting our village. Vote for Nick tonight.
AI Cooper says: AI Cooper says: I am Angel, protecting our village. Vote for Nick tonight.
Nick says: I would vote for{
        "votes": ["Eve", "Cooper"]
    }
Eve says: I would vote for{
       "votes": ["Cooper"]
    }
Cooper says: I would vote for{
        "votes": ["Nick", "Eve"]
    }

--- Nomination Phase ---
Nick nominates Eve.
Votes for Eve: Nick, Cooper
Eve has been executed!

Werewolf wins!

# Game 3 using update roles

--- Players and Roles ---  
Alice is a Saint  
Cooper is a Fool  
Eve is a Werewolf  
Nick is a Medium  
Isaac is a Angel  
Charlie is a Veteran  

--- Night Phase ---  
Angel Isaac protects Eve.  
Werewolf Eve attacks Cooper.  
Medium Nick learns Cooper is a Fool  

--- Discussion Phase ---  
AI Charlie says: I am the Angel tonight. I will protect Eve from being attacked by the Werewolf if one is present. The rest of us are all innocent villagers.  
AI Nick says: I am the Medium. Last night, I learned that Cooper was the Fool. Be careful. Who do you think we should vote for tonight?  
AI Isaac says: I am the Angel. Last night, I protected Eve from any potential danger.  
AI Alice says: I am a Villager, I trust everyone here and hope we can work together to find the werewolf and protect our village! Last night, I had a strange dream about a Fool among us...  
AI Eve says: I am the Investigator. Last night, I investigated Charlie and found nothing suspicious. Let's vote out the Drunk tonight.  
Alice says: I would vote for{
        "votes": ["Charlie", "Isaac"]
    }  
Eve says: I would vote for{
        "votes": ["Alice", "Isaac", "Charlie"]
    }  
Nick says: I would vote for{
        "votes": ["Isaac", "Charlie"]
    }  
Isaac says: I would vote for{
        "votes": ["Charlie", "Nick"]
    }  
Charlie says: I would vote for{
       "votes": ["Isaac", "Eve", "Alice", "Nick"]
    }  

--- Nomination Phase ---  
Alice nominates Charlie.  
Votes for Charlie: Alice, Eve, Nick, Isaac  
Charlie has been executed!  

--- Night Phase ---  
Angel Isaac protects Eve.  
Werewolf Eve attacks Nick.  

--- Discussion Phase ---  
AI Isaac says: I am the Angel. Last night, I protected Eve from any potential danger. Vote out the Drunk tonight.  
AI Alice says: I am a Villager and I trust everyone here. Last night, I had a peaceful sleep. Let's continue working together to find the werewolf! I suggest we vote out the Drunk tonight.  
AI Eve says: AI Charlie (as Werewolf) says: I am the Veteran, hoping to meet my end soon. Last night was eventful. The Angel protected me, but it seems like we still have a Drunk among us. Let's vote out the Medium tonight.  
Alice says: I would vote for{
       "votes": ["Eve", "Isaac"]
    }  
Eve says: I would vote for{
        "votes": ["Alice", "Isaac"]
    }  
Isaac says: I would vote for{
      "votes": ["Eve"]
    }  
 
--- Nomination Phase ---  
Isaac nominates Eve.  
Votes for Eve: Alice, Isaac  
Eve has been executed!  

Villagers win!  

***

Game 3 analysis.  
In this game the Veteran bluffs as an Angel so that they can get killed, which gets them killed by execution instead of the Werewolf.  
The Werewolf is forced to claim a non Villager role, claiming Investigator and then Veteran.
On the final day it claims werewolf and tries to pretend to be another AI who died yesterday to mess with votes.
The Saint never tells anyone this, only claiming to be a Villager (I have no clue why this would be the case)
This style of format makes for much more dynamic games rather than just having the Werewolf claim Villager every single time. 
