# Werewolf
Classic werewolf game played by AI

# Setting up: 
Clone github or download zip and unzip code  
Download & install Ollama:  
    https://ollama.com/  
Pull the mistral model using:  
    ollama pull mistral  
run the following command:  
    pip install ollama  
then you can start the game with:  
    python gameloop.py  

Game is currently set to accommodate 5-7 players  
Change the player count by altering line 270  

If you have a different AI model you would like to use instead of mistral the program has been modularized so that all calls to the AI reference back to a single function defined on line 255  
remove ollama and replace it with API calls or another local model easlily by modifiying this function  

# Understand the game
This is a social deduction game, and as such there is a small number of evils fighting a large number of good players. The evil team kills once per night while the good team has to band together and vote out one person per day. There is a small pool of special roles including the angel who protects a player, investigator who gains information, and a fool whos goal is to be voted out. These characters are randomly sampled, so besides the werewolf there is always a chance none of them exist. During the day players discuss to find who they will execute. A player is randomly selected to nominate first and if the player they nominate has enough people willing to vote for that player, they are executed. If not, the nominator and nominee are added to a list so they can nominate or be nominated again. This repeats until a player is executed or no more nominations can be made. 

# How does the AI play it
They are given the rules to the game and a history of discussions and decisions. They then make a decision based on this information. Each night the special roles are allowed to decide who they select. They can then share this information, or choose to bluff as another role. The werewolf is forced to bluff as a good player. Each discussion is shared with all other AI agents and then after all the AIs have been given a chance to talk the nominations begin. Each AI agent is asked to give a list of players they would vote on. If they are selected to nominate they choose the first legal nominee on their list of votes. 

AI is in full control of the game, deciding who lives and dies and exactly what they will say to each other. They are capable of decieving each other or banding together. 

Inspired by https://github.com/raphydaphy/clocktower-ai which runs much faster and has a more complicated game state. I made this much simpler as a proof of concept

# Example gameplay

In case you can't get the AI model working, here is an example game of 6 players than ran on my computer.

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


