import random
import time
import json
import sys
import threading

import google.generativeai as genai
import google.api_core.exceptions

genai.configure(api_key="Your Gemini Key")

GUIDE = {
        "Investigator": "Investigators gain very powerful information, but they have to struggle with the fact that they could be Drunk getting false results. There could be up to one other Investigator so do not be overly concerned if there is one other Seer claim. Just remember one gets true information and the other gets false info. If there are 3 or more Seer claims than there are definitely liars in that group. If you ever get 2 different players are both Werewolf, that means you are Drunk and actually neither is Werewolf. If you ever choose yourself you can know for sure if you are the Drunk or Investigator. A Drunk will see their own name labelled as Werewolf, which coudlnt be true. A Drunk Investigator must reverse all its information. Leraning Werewolf actually means the player is not a werewolf.", 
        "Monk": "Monks protect others from death at night. If there are no deaths at night they might have saved their target. A target that was attacked by the Werewolf is not the Werewolf, and therefore can be trusted. Not all Monks will claim Monk, as they have an important role and want to survive. They might privately ask if players want to be protected.",
        "Villager": "Villagers Act clueless but logical. Avoid making strong accusations without reason. They might bluff other roles to try and get killed at night. Try not to do more damage than good by spreading false information as you cannot correct it when you are dead. Tell people it is impossible for a Werewolf to claim villager",
        "Saint": "Saints BEG FOR YOUR LIFE! PLEASE DO NOT EXECUTE ME GOOD PEOPLE OF THIS TOWN. Be LOUD. use CAPS LOCK TO INDICATE SHOUTING. At all costs avoid being exected. You want everyone to know you are Saint and that they lose if you are executed. Remind them at every occaison.",
        "Jester": "Get yourself voted. Pretend to be confused or reckless. Push for executions that might seem odd. Make yourself the centre of attention. All the other players will be on the lookout for a Jester so do not be too overt. You can be meta and try and break the rules of the game by claiming to be a different player or spouting nonsense.",
        "Psycho": "Pyschos are forced to kill. If they do not kill their target, they accuse them of being the werewolf. The only players that can survive are Werewolfs, Sailors with immunity and players protected by the Monk. You should be very suspicous of any player that survives your attack. Remember, they are still trying to win with good.",
        "Werewolf": "Werewolfs try to blend in. They don't want to make a big impact. Just blend in with your surroundings. You are given a free role that is out of play. You should probably bluff this. Give out as little information, so your fake results are less likely to be contradictory, or give out a deluge of information to overwhelm people.",
        "Medium": "Mediums learn one role per night and that role can no longer be in play since it is dead. They will accuse players claiming to be the roles they know are dead. They might not share what role died privately so they can bait someone into claiming that role, and then reveal their information publicly.",
        "Fighter": "Fighters are trying to die at night, so you will probably claim something other than Veteran to some people. When you die at night you can try and take the Werewolf down with you so try to avoid getting protected by Monks. You do not want to be killed during the day so try not to lie too much", 
        "Sailor": "You have 2 lives! At some point you'll lose your first life and act scared. You will learn when you are attacked. You can either act immortal, or claim a different role and try and get attacked. When you are attacked there will probably be no deaths at night, so you can claim to be responsible, and confirm yourself as not a Werewolf",
        "Steward": "Stewards learn one piece of information. They know that one player is good and will trust them with absolute certainty. You can share that you trust them, but it might put a target on their back for the Werewolf to kill them. You are fine with getting voted out yourself, but make sure the player you learn is not.",
        "InvestigatorB": "Investigators will claim to have investigated a player and will get either Werewolf or not a Werewolf. Remember that you could be drunk, which means there can be up to 2 good people that think they are investigator.",
        "MonkB": "Monk protect others. They cannot choose themselves. If there are no deaths at night they might have saved their target. Subtly defend an innocent player, making it seem like you know more than you do. Not all Monks will claim Monk at first, you can be coy. ",
        "VillagerB": "Villagers Act clueless but logical. Avoid making strong accusations without reason. They might bluff other roles to try and get killed at night so the roles with special abilities do not die",
        "SaintB": "Saints BEG FOR YOUR LIFE! PLEASE DO NOT EXECUTE ME GOOD PEOPLE OF THIS TOWN",
        "JesterB": "Jesters are on team chaos. Pretend to be confused or reckless. Push for executions that might seem odd. Try not to be too overt to avoid suspicion. Make yourself the centre of attention.",
        "PsychoB": "Pyschos are forced to kill. If they do not kill their target, they accuse them of being the werewolf unless they claim to be . Remember, they are still trying to win with good.",
        "WerewolfB": "Werewolf... Don't bluff as werewolf... its even a little extreme for a fool to claim werewolf.",
        "MediumB": "Mediums learn one role per night and that role can no longer be in play since it is dead. They will accuse players claiming to be the roles they know are dead.",
        "FighterB": "Fighters are trying to die, so you will probably claim something other than Veteran to some people. When you die you can try and take the Werewolf down with you so don't get protected by Monks", 
        "SailorB": "You have 2 lives! At some point you'll lose your first life and act scared. This is usually accompanied by a night of no deaths",
        "StewardB": "Stewards learn one piece of information. They know that one player is good and will trust them with absolute certainty.",
        "DrunkB": "Drunk, oof you got a low role bluff. Claim to be Investigator and give out horribly innaccurate results to make people think you are the drunk. Or give very accurate results and claim you cannot be the Drunk.",
        "InvestigatorC": "Never Investigate a player you've already picked. Your first Priority should be gaining information by selecting as many players that are not yourself and learning their role. If you need to know if you are the drunk, choose yourself.",
        "MonkC": "Protect players that have claimed strong roles. Did anyone else ask for you to protect them? If you know someone isnt the Werewolf either through Investigator or Steward information always prioritize them.",
        "VillagerC": "Villagers Act clueless but logical. Avoid making strong accusations without reason. They might bluff other roles to try and get killed at night so the roles with special abilities do not die",
        "PsychoC": "Everyone you kill is a Werewolf candidate taht you've eliminated. If you killed a player and they survived, you can kill someone else to kill more players or you can try to kill them again",
        "WerewolfC": "Pick players that have claimed strong roles like Investigator or Medium. Also kill players that have accused you or voted for you, as they will probably try again.",
        "FighterC": "You have one chance to pick the werewolf. Choose the player you are most suspicious of."        
} 

def print_system(role, message):
    if role == "PRO":
        print(f"{Colors.BLUE}{message}{Colors.RESET}")
    elif role == "SYS":  # Evil AI
        print(f"{Colors.RED}{message}{Colors.RESET}")
    elif role == "AI":
        print(f"{Colors.GREEN}{message}{Colors.RESET}")
    else:
        print(message)

class Colors:
    RED = "\033[91m"
    RESET = "\033[0m"
    GREEN = "\033[92m" 
    BLUE = "\033[94m"

class Player:
    def __init__(self, name, role):
        self.name = name
        if (role == "Drunk"):
            self.role = "Investigator"
        else:
            self.role = role
        self.alive = True
        self.votes = []
        self.true_role = role
        if role == "Werewolf" or role == "Jester":
            self.colour = "evil"
        else:
            self.color = "good"
        self.bluff = ""
        self.AI = True

    def __repr__(self):
        return f"{self.name} ({'Alive' if self.alive else 'Dead'}) - {self.role}"

class WerewolfGame:
    def __init__(self, debug=False):
        
        self.playercount = 8  # Default player count
        self.convos = 2
        self.speed = 3
        self.mode = 1
        
        print_system("none", "You are playing as an AI Agent in a game of Werewolf. colourless text like this will ask you to input")
        print_system("SYS", "This is the colour of system messages. They will alert you when things happen")
        print_system("PRO", "This is the colour of prompts exacrly as the AI sees them. They contain information about choices")
        print_system("AI", "Hello! This is the colour of when AI is speaking to you")
        self.name = (input ("Enter name: ") or self.name)
        if debug:
            
            self.playercount = int(input("Enter the number of players: (5-10)") or self.playercount)
            self.convos = int(input("Enter the number of coversations on day 1: (1-3)") or self.convos)
            self.mode = int(input("Enter speed: (1 = fast // 2 = full) ") or self.mode)
            if self.mode == 1:
                self.speed = 1
            if self.mode > 2:
                self.speed = 5
            print_system("SYS", "\nDebug Mode: Custom settings applied.\n")
        else:
            print_system("SYS", f"Default settings: {self.playercount} Players, {self.convos} Conversations, Fast mode enabled")
        

        self.players = []
        self.ai_agents = {}
        self.werewolf_role = ["Werewolf"]
        self.true_roles_pool = ["Investigator", "Monk", "Jester", "Villager", "Fighter", "Drunk", "Medium", "Steward", "Saint", "Sailor"]
        self.player_names = ["Ian", "Si Jin", "Jeran", "Malcolm", "Dexter", "Spencer", "Nadia", "John", "Mike", "Anja"] 
        role_expansions = {
            6: lambda: self.true_roles_pool.append("Psycho"),
            8: lambda: self.true_roles_pool.append("Villager"),
        }
        for i, action in role_expansions.items():
            if self.playercount >= i:
                action()
        self.assign_roles()
        self.game_over = False
        self.night = 1
        self.initialize_ai_players()

    def assign_roles(self):

        chosen_good_roles = random.sample(self.true_roles_pool, self.playercount - 1)  # Select 1 less than playercount random good roles
        all_roles = self.werewolf_role + chosen_good_roles
        print_system("SYS", "The following roles could be in play " + str(self.true_roles_pool))
        random.shuffle(all_roles)
        random.shuffle(self.player_names)
        self.player_names[0] = self.name
        AIs = True

        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        human = next(p for p in self.players if p.name == self.name)

        human.AI = False
        
        werewolf = next(p for p in self.players if p.role == "Werewolf")

        bluff = next(r for r in self.true_roles_pool if r not in chosen_good_roles)
        werewolf.bluff = bluff
        
    def initialize_ai_players(self):
        for player in self.players:
            # self.ai_agents[player.name] = [{"role": "user", "content": f"You are {player.name}, a player in a Werewolf game. Your role is {player.role}."} ]
            self.introduce_ai_player(player)
    
    def introduce_ai_player(self, player):
        prompt = f"""
You are {player.name}, playing a Werewolf game. Your role is {player.role}.
There is one human playing, they might talk differently but that doesnt make them more or less suspicious
Here are the evil roles. They have their own win conditions.
- The Werewolf eliminates one player per night. Wins if they kill everyone
- The Jester wants to be voted out by the town. They win if do, everyone else loses.

Here are all the good roles: they all win by executing the Werewolf
- The Investigator checks players, but might be Drunk. They either learn werewolf or not werewolf
- The Drunk has been told they are Investigator, but always get opposite results.
- The Steward starts the game knowing one player is not the werewolf. They learn nothing else but can trust that player.
- The Medium learns the role of the first character that dies each night.
- The Monk protects one player from death per night.  
- The Fighter wants the Werewolf to kill them. They can kill a player if they are killed.
- The Sailor survives death once. They learn if they were attacked at night.
- The Saint must avoid being voted out by the town. Werewolf wins if they are.
- The Psycho kills every night. The werewolf and protected players are immune. 
- Villager is not the werewolf, probably


Any of the roles besides Werewolf could not be in play. 

ALWAYS REFERENCE THESE ROLES WHEN BLUFFING AS CHARACTER

Consistency is really important. Try to always stick to one story.
You are sleuths trying to solve the murders. You should be trying to find out what role everyone is, and kill the ones who are most a threat.
"""
        if player.role == "Werewolf":
            prompt += """"
            """ + player.bluff + " is the Werewolf's bluff. It is not in play and is safe to bluff as over the course of the game. Only you know this information so take advantage of it."
        
        prompt += """"
            """ + f"As a {player.role} This is what I need to know: {GUIDE[player.role]}"

        if player.AI == False:   # response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            print_system("PRO", prompt)

        
        self.ai_agents[player.name] = [{"role": "user", "content": prompt}]
        
            # print(f"Error initializing AI for {player.name}: {e}")

    def get_ai_decision(self, player, decision_type, options):
        
        random.shuffle(options)

        # Give AI the current circumstances and ask for direction

        prompt = f"""
it is night {str(self.night)}
You are {player.name}, playing as {player.role} in a game of Werewolf.
These are your options {', '.join(options)}

Your task is to make a decision: {decision_type}.
Respond with ONLY one item from the list. No explanations.

Answer format: [Exact option from the list]
"""
        choice = ""

        messages = self.ai_agents[player.name]  # Get player's chat history

        if player.role+"C" in GUIDE:
            prompt += "The following is non binding advice for choosing. you do not have to stick to its rules its just a general guide. " + GUIDE.get(player.role+"C")

        if player.AI == False:
            print_system("PRO", prompt)
            choice = input("Choice? ")
        else: 
            choice = self.callAI(messages, prompt)
        if choice.startswith("["):
            choice = choice[1:-1]

        if choice in options:
            return choice
        else:
            choice = random.choice(options)
            if player.AI == False:
                print_system("SYS", "randomly chose " + choice)
            return choice
            
    def night_phase(self):
        print_system("SYS", "\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        
        monk = next((p for p in self.players if p.role == "Monk"), None)

        fighter = next((p for p in self.players if p.role == "Fighter"), None)

        sailor = next((p for p in self.players if p.true_role == "Sailor"), None)

        dead = []

        alive_players = [p.name for p in self.players if p.alive]


        protected_player = None
        if monk:
            target_players = [p.name for p in self.players if p.alive and p != monk]
            protected_name = self.get_ai_decision(monk, "choose a player to protect", target_players)
            protected_player = next(p for p in self.players if p.name == protected_name)
            current_prompt = self.ai_agents[monk.name][0]["content"]
            string = "night " + str(self.night) + " I protected " + protected_name
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
            # Update the first message with the new prompt
            self.ai_agents[monk.name][0]["content"] = updated_prompt
            self.ai_agents[monk.name].append({"role": "assistant", "content": string})
            # print(f"Monk {monk.name} protects {protected_player.name}.")
            time.sleep(self.speed+3)
        
        if werewolf:
            
            target_players = [p.name for p in self.players if p.alive and p != werewolf]
            target_name = self.get_ai_decision(werewolf, "choose a player to attack", target_players)
            target = next(p for p in self.players if p.name == target_name) 
    
            if target == protected_player:
                if werewolf.AI == False:
                    print_system("SYS", f"Werewolf {werewolf.name} attacks {target.name}, but they survived!")
            else:
                if target == sailor:
                    if target.AI == False:
                        print_system("SYS", f"Sailor {sailor.name} becomes mortal")
                    elif werewolf.AI == False:
                        print_system("SYS", f"Werewolf {werewolf.name} attacks {target.name}, but they survived!")
                    current_prompt = self.ai_agents[sailor.name][0]["content"]
                    string = "night " + str(self.night) + " I was attacked and lost my protection"
                    # Append the new critical information to the prompt
                    updated_prompt = current_prompt + "\n" + string
                    # Update the first message with the new prompt
                    self.ai_agents[sailor.name][0]["content"] = updated_prompt
                    self.ai_agents[sailor.name].append({"role": "assistant", "content": string})
                    sailor.true_role = "Mortal"
                    sailor = None
                else:
                    dead.append(target.name)
                    target.alive = False
                    if target.AI ==  False:
                        print_system("SYS", f"{target.name} is attacked and dies.")
                    if target.role == "Fighter": 
                        time.sleep(self.speed+3)
                        target_name = self.get_ai_decision(fighter, "you have died, choose a player to kill", [p.name for p in self.players if p.alive])
                        target = next(p for p in self.players if p.name == target_name)
                        if target == protected_player:
                            if target.AI == False:
                                time.sleep(1)
                            # print(f"Sailor {sailor.name} becomes mortal")
                        else:
                            if target == sailor:
                                if target.AI == False:
                                    print_system("SYS", f"Sailor {sailor.name} becomes mortal")
                                current_prompt = self.ai_agents[sailor.name][0]["content"]
                                string = "night " + str(self.night) + " I was attacked and lost my protection"
                                # Append the new critical information to the prompt
                                updated_prompt = current_prompt + "\n" + string
                                # Update the first message with the new prompt
                                self.ai_agents[sailor.name][0]["content"] = updated_prompt
                                self.ai_agents[sailor.name].append({"role": "assistant", "content": string})
                                sailor.true_role = "Mortal"
                                sailor = None
                            else:
                                if fighter.AI == False:
                                    print_system("SYS", f"You died in a blaze of glory, game over")
                                elif target.AI == False:
                                    print_system("SYS", f"Fighter {fighter.name} has killed you, game over")
                                target.alive = False
                                dead.append(target.name)
                    self.check_winner()
                                    
            time.sleep(self.speed+3)

        psycho = next((p for p in self.players if p.role == "Psycho" and p.alive), None)

        if psycho:
            target_players = [p.name for p in self.players if p.alive and p != psycho]
            target_name = self.get_ai_decision(psycho, "choose a player to kill", target_players)
            target = next(p for p in self.players if p.name == target_name)
            current_prompt = self.ai_agents[psycho.name][0]["content"]
            string = "night " + str(self.night) + " I attacked " + target_name
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[psycho.name][0]["content"] = updated_prompt
            self.ai_agents[psycho.name].append({"role": "assistant", "content": string})
            if target == protected_player or target == werewolf:
                if psycho.AI ==  False:
                    print_system("SYS", f"Psycho {psycho.name} attacks {target.name}, but they are protected!")
            else:
                if target == sailor:
                    if target.AI == False:
                        print_system("SYS", f"Sailor {sailor.name} becomes mortal")
                    if psycho.AI == False:
                        print_system("SYS", f"Psycho {psycho.name} attacks {target.name}, but they are protected!")
                    current_prompt = self.ai_agents[sailor.name][0]["content"]
                    string = "night " + str(self.night) + " I was attacked and lost my protection"
                        # Append the new critical information to the prompt
                    updated_prompt = current_prompt + "\n" + string
                        # Update the first message with the new prompt
                    self.ai_agents[sailor.name][0]["content"] = updated_prompt
                    self.ai_agents[sailor.name].append({"role": "assistant", "content": string})
                    sailor.true_role = "Mortal"
                    sailor = None
                else:
                    dead.append(target.name)
                    # print(f"Psycho {psycho.name} attacks {target.name}.")
                    target.alive = False
            time.sleep(self.speed+3)

        investigator = next((p for p in self.players if p.true_role == "Investigator" and p.alive), None)
        drunk = next((p for p in self.players if p.true_role == "Drunk" and p.alive), None)

        if investigator:
            suspect_name = self.get_ai_decision(investigator, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if suspect.role == "Werewolf" else "Not a Werewolf"
            current_prompt = self.ai_agents[investigator.name][0]["content"]
            string = "night " + str(self.night) + " I investigated " + suspect_name + " and learned that they are " + result
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[investigator.name][0]["content"] = updated_prompt
            self.ai_agents[investigator.name].append({"role": "assistant", "content": string})
            if investigator.AI == False:
                print_system("SYS", f"Investigator {investigator.name} investigates {suspect.name} and learns they are: {result}.")
            time.sleep(self.speed+3)

        if drunk:
            suspect_name = self.get_ai_decision(drunk, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if not suspect.role == "Werewolf" else "Not a Werewolf"
            current_prompt = self.ai_agents[drunk.name][0]["content"]
            string = "night " + str(self.night) + " I investigated " + suspect_name + " and learned that they are " + result
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[drunk.name][0]["content"] = updated_prompt
            self.ai_agents[drunk.name].append({"role": "assistant", "content": string})
            if drunk.AI == False:
                print_system("SYS", f"Investigator {drunk.name} investigates {suspect.name} and learns they are: {result}.")
            time.sleep(self.speed+3)

        steward = next((p for p in self.players if p.role == "Steward" and p.alive), None)
        medium = next((p for p in self.players if p.role == "Medium" and p.alive), None)
        
        if steward:
            if self.night == 1:
                alive_players = [p.name for p in self.players if p.alive and p != werewolf and p != steward]
                not_WW = random.choice(alive_players)
                current_prompt = self.ai_agents[steward.name][0]["content"]
                string = "on the first night I learned " + not_WW + " is not a werewolf. I will learn no further information with my ability"
            # Append the new critical information to the prompt
                updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
                self.ai_agents[steward.name][0]["content"] = updated_prompt
                self.ai_agents[steward.name].append({"primary role": "player", "content": string})
                if steward.AI == False:
                    print_system("SYS", f"Steward {steward.name} learns {not_WW} is not a werewolf")
        
        if medium:
            if len(dead) > 0:
                seen = next((p for p in self.players if p.name == dead[0]), None)
                current_prompt = self.ai_agents[medium.name][0]["content"]
                string = "night " + str(self.night) + " I learned " + seen.name + " was the " + seen.true_role + ". This means no other players can be that role."
            # Append the new critical information to the prompt
                updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
                self.ai_agents[medium.name][0]["content"] = updated_prompt
                self.ai_agents[medium.name].append({"primary role": "player", "content": string})
                if medium.AI == False:
                    print_system("SYS", f"Medium {medium.name} learns {seen.name} is a {seen.true_role}")
        
        random.shuffle(dead)
        message = str(dead)
        if len(dead) == 0:
            message = "Nobody died last night"
        else:
            message += " ha"
            if len(dead) == 1:
                message += "s died"
            else:
                message += "ve died"
        print_system("SYS", message)

        alive_players = [p.name for p in self.players if p.alive]
        print_system("SYS", str(alive_players) + " are alive")
        
        for player in alive_players:
            self.ai_agents[player].append({"role": "user", "content": message})

    def bluffing(self):
        print_system("SYS", "\n--- Bluffs ---")

        alive_players = [p for p in self.players if p.alive and p.AI]
        bluff_options = self.true_roles_pool + ["Werewolf", "None"]

        for p in alive_players:
            prompt = "you are a " + p.role + " bluffing as " + p.bluff + " and you are deciding whether you want to bluff or not. It is best to stick with a role you are already claiming. You should not bluff (pick None) most of the time, but sometimes you might want to bluff to throw off the evil team."
            if p.role == "Werewolf":
                prompt = "You are the Werewolf, and therefore have to bluff as a role. You can not bluff as Villager and you cannot select None as your bluff" 
                if self.night ==1:
                    prompt +=". To help you: the following role is out of play " + p.bluff + ". REMEMBER THIS ROLE. YOU DEFINITELY SHOULD BLUFF AS THIS ROLE AS IT IS THE SAFEST ONE TO DO"
            if p.role == "Veteran" or p.role == "Sailor" or p.role == "Psycho" or p.role == "Villager" or p.role == "Saint" or p.role == "Steward": 
                prompt += ". you may want to bluff another role to try and get killed. You should choose a bluff most of the time. Pick roles like Angel, Psycho, and Investigator or Medium"
            if p.role == "Angel" or p.role == "Investigator" or p.role == "Psycho" or p.role == "Medium":
                prompt += ". you may want to bluff another role to try and avoid getting killed. You should not bluff most of the time but if you do you can pick a character more likely to want to die like Saint, Steward, Villager, Sailor, Veteran, Psycho or Fool"
            prompt += ". If you want to bluff as a specific character, you will be given information on how to play as that character." 

            bluff_role = self.get_ai_decision(p, prompt, bluff_options)
            if p.bluff != bluff_role:
                p.bluff = bluff_role
                bluff_strategy = f"day {str(self.night)} I might claim to be buffing {GUIDE.get(bluff_role + "B", "Nothing. I plan to just tell the truth.")} but that doesnt mean I am locked on this decision"
                self.ai_agents[p.name].append({"role": "assistant", "content": bluff_strategy})
            time.sleep(self.speed+1)

    def converstaions(self, convos):

        print_system("SYS", "\n--- Private Conversation Phase ---")

        alive_players = [p for p in self.players if p.alive]

        num_rounds = max(0, 1 + convos - self.night)

        for _ in range(num_rounds):
            random.shuffle(alive_players)
            conversations = []
            used_conversations = set()

            # Create groups of 2 (one group of 3 if odd number of players)
            i = 0
            attempts = 0
            while i < len(alive_players):
                if i + 4 > len(alive_players):  
                    conversations.append(alive_players[i:])  # Last group (2 or 3)
                    break
                else:
                    group = tuple(sorted(alive_players[i:i+2], key=lambda p: p.name))
                    if group not in used_conversations or attempts > 1:
                        conversations.append(alive_players[i:i+2])  # Pair of 2
                        used_conversations.add(group)
                        i += 2
                    else: 
                        alive_players[i], alive_players[i+2+attempts] = alive_players[i+2+attempts], alive_players[i]
                        # print_system("SYS", "attempt #" + attempts)
                        
            threads = []
            
            # Run each private conversation
            for convo in conversations:
                participant = [p for p in convo]
                human = any(p.alive and p.AI == False for p in convo)
                if human:
                    human = next((p.alive and p.AI == False for p in convo), None)
                    message = f"you are in a private conversation with {', '.join(p.name for p in participant)}. "
                    string = f"""
                    ----------------------------------------------------------------

                    {message}
                    ----------------------------------------------------------------"""
                    if human:
                        print_system("SYS", string) 
                    for p in participant:
                        self.ai_agents[p.name].append({"role": "user", "content": message})

                    for turn in range(1+len(convo)):    # Each player speaks twice
                        prompt = f"""
you are {human.name} and you are a {human.role} bluffing as {human.bluff} in a private conversation with {', '.join(o.name for o in participant if o.name != p.name)}
anything in your message history with your name is something you have said. Try to be consistent with past claims.
You do not have to commit to the role you are bluffing as
Do not say you are the same role as another player unless you are that player or you are the Werewolf
you are now in a private conversation. Feel free to share any information you have. 
Make sure you respond to the messages already in this conversation. DO NOT REPEAT ANY MESSAGES YOU HAVE SEEN.
You should claim to be a role (Villager, Investigator, Monk, Fighter, Steward, Medium, Saint, Sailor, Psycho, Jester)
Some roles might want to lie about what role they are, like Werewolf. 
You can relay false information if you think it will help.
No ability will ever fail, 

Do not introduce yourself. Assume they already know your name. DO NOT SAY YOUR NAME.
Do not assume that you should follow the same format as the message you've seen. 

You should be concered if 2 players are claiming the same role. One of them is lying. 
Therefore do not claim a role that someone else is claiming unless you have reason to believe they are not that role.

Always look at the prior convesations. to see if you have already claimed a role to the people you are in a conversation with. 
Do not gossip about players that you havent talked to or heard about. If a player does not exist in your history you know nothing about them. 
Do not gossip about player roles that no one has claimed. if no one including yourself is claimging to be that role in your history you know nothing about it.


Stick to one bluff at a time. Do not say you are a role that you are not and are not bluffing unless you are the Werewolf or Fool

Keep your conversation brief, 2-3 sentences.
"""
                        speaker = convo[turn % len(convo)]
                        if speaker.role == "Werewolf":
                            prompt += "You cannot claim to be Villager, you must bluff as another role. Give a convincing impression of that role, giving out false information when you can"
                        player_history = self.ai_agents[speaker.name]

                        if speaker.AI:
                            response = self.callAI(player_history, prompt)
                                # check if response is formatted
                            scan = "AI "+speaker.name 
                            if (not response.startswith(scan)):
                                    #format if not formatted
                                response = "AI " + speaker.name + " says: " + response
                        else:
                            print_system("PRO", prompt)
                            response = input("what do you want to say? ")
                            response = "Human " + speaker.name + " says " + response
                            # Append to all players' history in the conversation
                        for p in convo:
                            self.ai_agents[p.name].append({"role": "assistant" if p.name == speaker.name else "user", "content": response})
                            if p.AI == False and speaker.AI == True:
                                print_system("AI", response)
                        time.sleep(self.speed+5)
                else:
                    # Start AI-only conversations in a separate thread
                    thread = threading.Thread(target=self.ai_conversation, args=(convo,))
                    thread.start()
                    threads.append(thread)
                
            for thread in threads:
                thread.join()

            if self.mode > 1:
                self.reflection()
                self.bluffing()
                time.sleep(1)  

    def ai_conversation(self, convo):
    
        participant = [p for p in convo]
        message = f"you are in a private conversation with {', '.join(p.name for p in participant)}. "

        for p in participant:
            self.ai_agents[p.name].append({"role": "user", "content": message})

        for turn in range(1 + len(convo)):  # Each player speaks twice
            speaker = convo[turn % len(convo)]
            if speaker.AI:  # AI only
                prompt = f"""
you are {p.name} and you are a {p.role} bluffing as {p.bluff} in a private conversation with {', '.join(o.name for o in participant if o.name != p.name)}
anything in your message history with your name is something you have said. Try to be consistent with past claims.
You do not have to commit to the role you are bluffing as
Do not say you are the same role as another player unless you are that player or you are the Werewolf
you are now in a private conversation. Feel free to share any information you have. 
Make sure you respond to the messages already in this conversation. DO NOT REPEAT ANY MESSAGES YOU HAVE SEEN.
You should claim to be a role (Villager, Investigator, Monk, Fighter, Steward, Medium, Saint, Sailor, Psycho, Jester)
Some roles might want to lie about what role they are, like Werewolf. 
You can relay false information if you think it will help.
No ability will ever fail, 

Do not introduce yourself. Assume they already know your name. DO NOT SAY YOUR NAME.
Do not assume that you should follow the same format as the message you've seen. 

You should be concered if 2 players are claiming the same role. One of them is lying. 
Therefore do not claim a role that someone else is claiming unless you have reason to believe they are not that role.

Always look at the prior convesations. to see if you have already claimed a role to the people you are in a conversation with. 
Do not gossip about players that you havent talked to or heard about. If a player does not exist in your history you know nothing about them. 
Do not gossip about player roles that no one has claimed. if no one including yourself is claimging to be that role in your history you know nothing about it.


Stick to one bluff at a time. Do not say you are a role that you are not and are not bluffing unless you are the Werewolf or Fool

Keep your conversation brief, 2-3 sentences.
"""
                player_history = self.ai_agents[speaker.name]
                response = self.callAI(player_history, prompt)

                # Ensure proper formatting
                if not response.startswith(f"AI {speaker.name}"):
                    response = f"AI {speaker.name} says: {response}"

                # Append the response to all players in convo
                for p in convo:
                    self.ai_agents[p.name].append({"role": "assistant" if p == speaker else "user", "content": response})

                time.sleep(1)
                    
    def reflection(self):
        print_system("SYS", "\n--- Self Reflection Phase ---")

        alive_players = [p for p in self.players if p.alive]

        for player in alive_players:
            messages = self.ai_agents[player.name]
            prompt = "It is day " + str(self.night) + ". you are a " + player.role + ". "
            prompt += f"""
The following players are still alive: {', '.join(p.name for p in alive_players)}
This is your chance to record everything you know about the game privately, Think of this as an internal monologue.
Every player has a unique role. Have you learned what roles players are claiming?
What role have you been claiming? If this isn't your real role what information have you been giving out?
What is your route to victory? Who do you need to execute to get there?  
Who do you think should not be executed? is it because they are good? or Because you suspect them of being a Jester?
Do you think there is a drunk in play?

Keep your responses brief, summarize the most important points that you want to remember. Maxium number of sentences is {self.convos + 3}
Its ok to not answer every question. 
Focus on remembering what you have claimed and what you want to claim in the future
Also on suspicions: who is the drunk, who is the jester who is the werewolf?
"""
            
            if player.role == "Werewolf":
                prompt += f"""
Who do you think would be a good kill? Are you planning on claiming the same role tomorrow or switching up your role?
Does the information you are giving out make sense given the role descripitions you've been given?
"""
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("here is the chat history: " + str(messages) + "now respond to this prompt: " + prompt)
            response = response.text.strip()
            # print_system("SYS", "On, day" + str(self.night) + ", " + player.name + " thinks that: " + response)
            
            current_prompt = self.ai_agents[player.name][1]["content"]
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + response
                # Update the first message with the new prompt
            self.ai_agents[player.name][1]["content"] = updated_prompt
            messages.append({"role": "assistant", "content": response})
            time.sleep(self.speed+3)

    def discussion(self, repeats):
        print_system("SYS", "\n--- Discussion Phase ---")
        alive_players = [p for p in self.players if p.alive]
        random.shuffle(alive_players)

        repeats = max(1,repeats-1)

        for _ in range(repeats):
            
            for player in alive_players:
                messages = self.ai_agents[player.name] # get chat history
                prompt = "It is day " + str(self.night) + ". you are a " + player.role + " bluffing " + player.bluff
                if player.role == "Werewolf":
                    prompt += ". You must not tell anyone you are werewolf. instead you should falsely claim to be a role that you think will not be executed. You CANNOT pretend to be a villager."
                if player.role == "Investigator":
                    prompt += ". Remember that you might not actually be an investigator, there is a chance you are the Drunk. If you found a Werewolf you should push for their execution."
                if player.role == "Jester":
                    prompt += ". Remember that you are trying to seem like the werewolf, but don't make it too obvious."
                if player.role == "Saint":
                    prompt += ". Remember you lose if you are executed. Try really hard to convince players that you are not the Werewolf."
                if player.role == "Fighter" or player.role == "Sailor" :
                    prompt += ". Remember you want to get attacked by the Werewolf. The Werewolf might not attack you if you are truthful about your role." 
                prompt += f"""
The following players are still alive: {', '.join(p.name for p in alive_players)}
What would you like to tell the other players? 
You should claim to be a role (Villager, Investigator, Monk, Fighter, Steward, Medium, Saint, Sailor, Pyscho, Jester)
You can bluff about what role you are. Try to be consistent with your past role claims, or give justification for why you are chainging your claim. 
You should not bluff unless you have to.
If you learned something last night, you should tell the other players 
You can relay false information and should do so if you are bluffing about what role you are. You should not do this often. unless you are bluffing a character
A character that you have no spoken to has not been silent, they just haven't had a chance to speak yet. 

Remember there can only be one of each role. You should question anybody claiming the same role as yourself or someone else.

There is a jester and werewolf lying about their role. Avoid executing the jester.

There also could be a drunk who thinks they are investigator. 

Suggest a player for execution if you suspect someone. 

Please keep your responses to 1-2 short sentences.  
"""
                if player.AI == True:
                # Send prompt
                    choice = self.callAI(messages, prompt)
                
                # check if response is formatted
                    scan = "AI "+player.name 

                    if (not choice.startswith(scan)):
                    #format if 
                        choice = "AI " + player.name + " says: " + choice
                    print_system("AI", choice)
                else:
                    print_system("PRO", prompt)
                    choice = input("what do you want to say? ")
                time.sleep(self.speed+5)

                for p in alive_players:
                    # append response to prompt
                    self.ai_agents[p.name].append({"role": "assistant" if p.name == player.name else "user", "content": choice})

    def get_noms(self):
        alive_players = [p for p in self.players if p.alive and p.AI == True]
        human = next((p for p in self.players if p.AI == False and p.alive), None)
        
        threads = []

        for player in alive_players:

            thread = threading.Thread(target=self.ai_get_noms, args=(player,))
            thread.start()
            threads.append(thread)

        if human:
            prompt = f"""
you are {human.name}, a {human.role}
The following players are still alive: {', '.join(p.name for p in alive_players)}
Remember to look at the role that you are and that you believe other players are. 
Based on the current game state, return a JSON object with a list of players you would nominate.
Do not add any explinations, just say which players you think are potentially the werewolf.
You should name at least one player. You can name as many as you like.
The more players you name the more likely an execution is to occur.
The first name should be the player you most want to execute (if any).
Only respond with the JSON object and no other words.
You must follow this Example format: 
{{
    "votes": ["Player1", "Player2", "Player3"]
}}
"""

            if human.role == "Jester":
                prompt += ". Remember that you want to get executed."
               
            
            # print response
            print_system("PRO", prompt)
            user_input = input("Enter a list of items (comma-separated): ")

                # Split the input string into a list using the comma as a delimiter
            human.votes = [item.strip() for item in user_input.split(",")]
            time.sleep(self.speed)

        for thread in threads:
            thread.join()
    
    def ai_get_noms(self, player):
        """Handles AI player nominations in the background"""
        messages = self.ai_agents[player.name]  # Get chat history
        alive_players = [p for p in self.players if p.alive]

        prompt = f"""
you are {player.name}, a {player.role}
The following players are still alive: {', '.join(p.name for p in alive_players)}
Remember to look at the role that you are and that you believe other players are. 
Based on the current game state, return a JSON object with a list of players you would nominate.
Do not add any explanations, just say which players you think are potentially the werewolf.
You should name at least one player. You can name as many as you like.
The more players you name the more likely an execution is to occur.
The first name should be the player you most want to execute (if any).
Only respond with the JSON object and no other words.
You must follow this Example format: 
{{
    "votes": ["Player1", "Player2", "Player3"]
}}
"""

        if player.role == "Jester":
            prompt += ". Remember that you want to get executed. You should always be your first vote."

        
        choice = self.callAI(messages, prompt)

        # Clean response
        choice = choice[7:-3]

        current_prompt = self.ai_agents[player.name][1]["content"]
        string = "day " + str(self.night) + " I have voted for: " + choice

        # Update AI memory
        updated_prompt = current_prompt + "\n" + string
        self.ai_agents[player.name][1]["content"] = updated_prompt
        messages.append({"role": "assistant", "content": string})
        try: 
            vote_data = json.loads(choice)
            player.votes = vote_data.get("votes", [])
        except json.JSONDecodeError:
            player.votes = []

    def nomination_phase(self):
        print_system("SYS", "\n--- Nomination Phase ---")

        
        nominations = set()
        alive_players = [p for p in self.players if p.alive]
        nominators = alive_players
        
        while len(nominations) < len(alive_players) - 1 and nominators:
            if self.game_over:
                break
            nominator = random.choice(nominators)
            available_nominations = [p.name for p in alive_players if p.name not in nominations and p.name != nominator.name]
            nominators = [p for p in nominators if  p.name != nominator.name]
            if not available_nominations:
                print_system("SYS", "Nominations are closed. No one is executed.")
                break
            nominee_name = next((vote for vote in nominator.votes if vote in available_nominations), None)
            if not nominee_name:
                print_system("SYS", nominator.name + " passes")
                continue
            print_system("SYS", f"{nominator.name} nominates {nominee_name}.")
            nominations.add(nominee_name)
            if self.voting_phase(nominee_name):
                break
        
        self.night+=1
    
    def voting_phase(self, nominee_name):
        votes = []
        alive_players = [p.name for p in self.players if p.alive]
        
        for voter_name in alive_players:
            voter = next(p for p in self.players if p.name == voter_name)
            if nominee_name in voter.votes:
                votes.append(voter_name)
        
        message = f"Votes for {nominee_name}: {', '.join(votes)}"
        for p in alive_players:
            current_prompt = self.ai_agents[p.name][0]["content"]
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + message
            # Update the first message with the new prompt
            self.ai_agents[p.name][0]["content"] = updated_prompt
            self.ai_agents[p.name].append({"role": "assistant", "content": message})
        print_system("SYS", message)
        if len(votes) > len(alive_players) / 2:
            message = f"Day {self.night}, {nominee_name} has been executed!"
            print_system("SYS", message)
            nominee = next(p for p in self.players if p.name == nominee_name)
            if nominee.true_role == "Sailor":
                message += " But does not die!"
            else:
                nominee.alive = False
            print_system("SYS", message)
            for p in alive_players:
                current_prompt = self.ai_agents[p.name][0]["content"]
                # Append the new critical information to the prompt
                updated_prompt = current_prompt + "\n" + message
                # Update the first message with the new prompt
                self.ai_agents[p.name][0]["content"] = updated_prompt
                self.ai_agents[p.name].append({"role": "assistant", "content": message})
            if nominee.role == "Jester":
                print_system("SYS", "\nThe Jester has been executed and wins the game!")
                self.game_over = True
                return
            if nominee.role == "Saint":
                print_system("SYS", "\nThe Saint has been executed and the Werewolf the game!")
                self.game_over = True
                return
            return True
        return False

    def check_winner(self):
        werewolf_alive = any(p.alive and p.role == "Werewolf" for p in self.players)
        villagers_alive = sum(1 for p in self.players if p.alive and p.role != "Werewolf")
        playerdead = next((p for p in self.players if p.AI == False and not p.alive), None)

        if not werewolf_alive:
            print_system("SYS", "\nVillagers win!")
            self.game_over = True
        elif villagers_alive < 2:
            print_system("SYS", "\nWerewolf wins!")
            self.game_over = True
        if playerdead:
            print_system("SYS", "\nYou died, so sad! the game is over for you, but you can still spectate public converstaions")
            playerdead.AI = True

    def callAI(self, messages, prompt):
        while True:
            try:
                temp_history = messages[:3] + messages[-self.playercount:]
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content("here is the chat history: " + str(temp_history) + "now respond to this prompt: " + prompt)
                return response.text.strip()
            except google.api_core.exceptions.ResourceExhausted:
                self.speed += 1
                if self.speed > 3:
                    return "Error"
                time.sleep(self.speed)
            
    def play(self):
        while not self.game_over:
            self.night_phase()
            self.check_winner()
            if self.game_over:
                break
            time.sleep(1)
            if self.mode > 1:
                self.bluffing()
                time.sleep(1)
            time.sleep(1)
            self.converstaions(self.convos)
            time.sleep(1)
            self.discussion(self.convos)
            time.sleep(1)
            self.get_noms()
            time.sleep(1)
            self.nomination_phase()
            self.check_winner()
            time.sleep(1)
        print_system("SYS", "\n--- Players and Roles ---")
        for player in self.players:
            print_system("SYS", player.name + " was the " + player.true_role)

if __name__ == "__main__":
    debug_mode = "debug" in sys.argv
    # works with 5 through 10, simply modify playercount
    game = WerewolfGame(debug_mode)
    game.play()
