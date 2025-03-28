import random
import time
import json
import sys

import google.generativeai as genai
import google.api_core.exceptions

genai.configure(api_key="Your Gemini Key")

BLUFF_GUIDE = {
        "Seer": "Seers will claim to have investigated a player and will get either Werewolf or not a Werewolf. Remember that you could be drunk, which means there can be up to 2 good people that think they are seer.",
        "Angel": "Angels protect others. If there are no deaths at night they might have saved their target. Subtly defend an innocent player, making it seem like you know more than you do. Not all Angels will claim Angel at first, you can be coy. ",
        "Villager": "Villagers Act clueless but logical. Avoid making strong accusations without reason. They might bluff other roles to try and get killed at night so the roles with special abilities do not die",
        "Saint": "Saints BEG FOR YOUR LIFE! PLEASE DO NOT EXECUTE ME GOOD PEOPLE OF THIS TOWN",
        "Jester": "Jesters are on team chaos. Pretend to be confused or reckless. Push for executions that might seem odd. Try not to be too overt to avoid suspicion. Make yourself the centre of attention.",
        "Psycho": "Pyschos are forced to kill. If they do not kill their target, they accuse them of being the werewolf unless they claim to be . Remember, they are still trying to win with good.",
        "Werewolf": "Werewolf... Don't bluff as werewolf... its even a little extreme for a fool to claim werewolf.",
        "Medium": "Mediums learn one role per night and that role can no longer be in play since it is dead. They will accuse players claiming to be the roles they know are dead.",
        "Veteran": "Veterans are trying to die, so you will probably claim something other than Veteran to some people. When you die you can try and take the Werewolf down with you so don't get protected by Angels", 
        "Sailor": "You have 2 lives! At some point you'll lose your first life and act scared. This is usually accompanied by a night of no deaths",
        "Steward": "Stewards learn one piece of information. They know that one player is good and will trust them with absolute certainty.",
        "Drunk": "Drunk, oof you got a low role bluff. Claim to be Seer and give out horribly innaccurate results to make people think you are the drunk. Or give very accurate results and claim you cannot be the Drunk."
} 


def print_colored(role, message):
    if role == "good": # Good AI
        print(f"{Colors.GREEN}{message}{Colors.RESET}")
    elif role == "evil":  # Evil AI
        print(f"{Colors.RED}{message}{Colors.RESET}")
    elif role == "bluff":
        print(f"{Colors.BLUE}{message}{Colors.RESET}")
    else:
        print(message)

class Colors:
    RED = "\033[91m"  # Evil roles (Werewolf)
    GREEN = "\033[92m"  # Good roles (Villager, Investigator, Angel, etc.)
    BLUE = "\033[94m"  # System messages
    RESET = "\033[0m"  # Reset to default color

class Player:
    def __init__(self, name, role):
        self.name = name
        if (role == "Drunk"):
            self.role = "Seer"
        else:
            self.role = role
        self.alive = True
        self.votes = []
        self.true_role = role
        if role == "Werewolf" or role == "Jester":
            self.color = "evil"
        else:
            self.color = "good"
        self.bluff = "None"

    def __repr__(self):
        return f"{self.name} ({'Alive' if self.alive else 'Dead'}) - {self.role}"

class WerewolfGame:
    def __init__(self, debug=False):
        
        self.playercount = 5  # Default player count
        self.convos = 2
        self.speed = 2
        self.mode = 1
        if debug:
            self.playercount = int(input("Enter the number of players: (5-10)") or self.playercount)
            self.convos = int(input("Enter the number of coversations on day 1: (1-3)") or self.convos)
            self.mode = int(input("Enter speed: (1 = fast // 2 = full) ") or self.mode)
            if self.mode == 1:
                self.speed = 0
            if self.mode > 2:
                self.speed = 5
            print(f"\nDebug Mode: Custom settings applied.\n")
        else:
            print(f"Default settings")
        

        self.players = []
        self.ai_agents = {}
        self.werewolf_role = ["Werewolf"]
        self.true_roles_pool = ["Seer", "Monk", "Jester", "Villager", "Fighter", "Drunk", "Medium", "Steward", "Saint", "Sailor"]
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
        print("The following roles are in play: " + str(self.true_roles_pool))
        random.shuffle(all_roles)
        random.shuffle(self.player_names)

        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        print("\n--- Players and Roles ---")
        for player in self.players:
            print_colored(player.color ,f"{player.name} is a {player.true_role}")

        werewolf = next(p for p in self.players if p.role == "Werewolf")

        bluff = next(r for r in self.true_roles_pool if r not in chosen_good_roles)
        werewolf.bluff = bluff
        string = bluff + " is the Werewolf's bluff. It is not in play and is safe to bluff as over the course of the game"
        print_colored(werewolf.color,string)

    def initialize_ai_players(self):
        for player in self.players:
            # self.ai_agents[player.name] = [{"role": "user", "content": f"You are {player.name}, a player in a Werewolf game. Your role is {player.role}."} ]
            self.introduce_ai_player(player)
    
    def introduce_ai_player(self, player):
        prompt = f"""
You are {player.name}, playing a Werewolf game. Your role is {player.role}.
Here are the evil roles. They have their own win conditions.
- The Werewolf eliminates one player per night. Wins if they kill everyone
- The Jester wants to be voted out by the town. They win if do, everyone else loses.

Here are all the good roles: they all win by executing the Werewolf
- The Seer checks players, but might be Drunk. They either learn werewolf or not werewolf
- The Drunk has been told they are Seer, but always get opposite results.
- The Steward starts the game knowing one player is not the werewolf. They learn nothing else but can trust that player.
- The Medium learns the role of the first character that dies each night. If no one dies they learn nothing.
- The Monk protects one player from death per night. If no deaths occur they can probably trust that player.
- The Fighter wants the Werewolf to kill them. They can kill a player if they are killed.
- The Sailor survives death once. They learn if they were attacked at night.
- The Saint must avoid being voted out by the town. Werewolf wins if they are.
- The Psycho kills every night. The werewolf and protected players are immune. 
- Villager is not the werewolf, probably


Any of the roles besides Werewolf could not be in play. 

ALWAYS REFERENCE THESE ROLES WHEN BLUFFING AS CHARACTER

Consistency is really important. Try to always stick to one story.
You are sleuths trying to solve the murders. You should be trying to find out what role everyone is, and kill the ones who are most a threat.
Be aggressive and suspicious to anyone you think is a Werewolf candidate. Trust the players you know are not Werewolf candidates.
        """
        if player.role == "Werewolf":
            prompt += "/n " + player.bluff + " is the Werewolf's bluff. It is not in play and is safe to bluff as over the course of the game. Only you know this information so take advantage of it."
        
            # response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        self.ai_agents[player.name] = [{"role": "user", "content": prompt}]
            
        
            # print(f"Error initializing AI for {player.name}: {e}")

    def get_ai_decision(self, player, decision_type, options):
    
        # Give AI the current circumstances and ask for direction

        prompt = f"""
it is night {str(self.night)}
You are {player.name}, playing as {player.role} in a game of Werewolf.
These are your options {', '.join(options)}

Your task is to make a decision: {decision_type}.
Respond with ONLY one item from the list. No explanations.

Answer format: [Exact option from the list]
        """

        messages = self.ai_agents[player.name]  # Get player's chat history
        
        choice = self.callAI(messages, prompt)
        if choice.startswith("["):
            choice = choice[1:-1]

        if choice in options:
            return choice
        else:
            print_colored(player.color,choice)
            return random.choice(options) 

    def night_phase(self):
        print("\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        
        monk = next((p for p in self.players if p.role == "Monk"), None)

        fighter = next((p for p in self.players if p.role == "Fighter"), None)

        sailor = next((p for p in self.players if p.true_role == "Sailor"), None)

        dead = []

        alive_players = [p.name for p in self.players if p.alive]

        protected_player = None
        if monk:
            alive_players = [p.name for p in self.players if p.alive and p != monk]
            protected_name = self.get_ai_decision(monk, "choose a player to protect", alive_players)
            protected_player = next(p for p in self.players if p.name == protected_name)
            current_prompt = self.ai_agents[monk.name][0]["content"]
            string = "night " + str(self.night) + " I protected " + protected_name
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
            # Update the first message with the new prompt
            self.ai_agents[monk.name][0]["content"] = updated_prompt
            self.ai_agents[monk.name].append({"role": "assistant", "content": string})
            print_colored(monk.color,f"Monk {monk.name} protects {protected_player.name}.")
            time.sleep(self.speed+3)
        
        if werewolf:
            
            alive_players = [p.name for p in self.players if p.alive and p != werewolf]
            target_name = self.get_ai_decision(werewolf, "choose a player to attack", alive_players)
            target = next(p for p in self.players if p.name == target_name) 
    
            if target == protected_player:
                print_colored(werewolf.color,f"Werewolf {werewolf.name} attacks {target.name}, but they are protected!")
            else:
                if target == sailor:
                    print_colored(werewolf.color,f"Werewolf {werewolf.name} attacks {target.name}, but they are protected!")
                    print_colored(sailor.color,f"Sailor {sailor.name} becomes mortal")
                    
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
                    print_colored(werewolf.color,f"Werewolf {werewolf.name} attacks {target.name}.")
                    target.alive = False
                    if target.role == "Fighter": 
                        time.sleep(self.speed+3)
                        target_name = self.get_ai_decision(fighter, "you have died, choose a player to kill", [p.name for p in self.players if p.alive])
                        target = next(p for p in self.players if p.name == target_name)
                        if target == protected_player:
                            print_colored(fighter.color,f"Fighter {fighter.name} attacks {target.name}, but they are protected!")
                        else:
                            if target == sailor:
                                print_colored(fighter.color,f"Fighter {fighter.name} attacks {target.name}, but they are protected!")
                                print_colored(sailor.color,f"Sailor {sailor.name} becomes mortal")
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
                                print_colored(fighter.color,f"Fighter {fighter.name} attacks {target.name}.")
                                target.alive = False
                                dead.append(target.name)
                                if target == werewolf:
                                    self.check_winner()
            time.sleep(self.speed+3)

        psycho = next((p for p in self.players if p.role == "Psycho" and p.alive), None)

        if psycho:
            alive_players = [p.name for p in self.players if p.alive and p != psycho]
            target_name = self.get_ai_decision(psycho, "choose a player to kill", alive_players)
            target = next(p for p in self.players if p.name == target_name)
            current_prompt = self.ai_agents[psycho.name][0]["content"]
            string = "night " + str(self.night) + " I attacked " + target_name
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[psycho.name][0]["content"] = updated_prompt
            self.ai_agents[psycho.name].append({"role": "assistant", "content": string})
            if target == protected_player or target == werewolf:
                if target == werewolf:
                    print_colored(psycho.color,f"Psycho {psycho.name} attacks {target.name}, but they are the werewolf!")
                else:
                    print_colored(psycho.color,f"Psycho {psycho.name} attacks {target.name}, but they are protected!")
            else:
                if target == sailor:
                    print_colored(psycho.color,f"Psycho {psycho.name} attacks {target.name}, but they are protected!")
                    print_colored(sailor.color,f"Sailor {sailor.name} becomes mortal")
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
                    print_colored(psycho.color,f"Psycho {psycho.name} attacks {target.name}.")
                    target.alive = False
            time.sleep(self.speed+3)

        seer = next((p for p in self.players if p.true_role == "Seer" and p.alive), None)
        drunk = next((p for p in self.players if p.true_role == "Drunk" and p.alive), None)

        if seer:
            suspect_name = self.get_ai_decision(seer, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if suspect.role == "Werewolf" else "Not a Werewolf"
            current_prompt = self.ai_agents[seer.name][0]["content"]
            string = "night " + str(self.night) + " I investigated " + suspect_name + " and learned that they are " + result
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[seer.name][0]["content"] = updated_prompt
            self.ai_agents[seer.name].append({"role": "assistant", "content": string})
            print_colored(seer.color,f"Seer {seer.name} investigates {suspect.name} and learns they are: {result}.")
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
            print_colored(drunk.color,f"Drunk {drunk.name} investigates {suspect.name} and learns they are: {result}.")
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
                print_colored(steward.color,f"Steward {steward.name} learns {not_WW} is not a werewolf")
        
        if medium:
            string = "night "+ str(self.night) + "no one died"
            current_prompt = self.ai_agents[medium.name][0]["content"]
            if len(dead) > 0:
                seen = next((p for p in self.players if p.name == dead[0] ), None)
                string = "night " + str(self.night) + " I learned " + seen.name + " was the " + seen.true_role + ". This means no other players can be that role."
                # Append the new critical information to the prompt
                print_colored(medium.color,f"Medium {medium.name} learns {seen.name} is a {seen.true_role}")
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[medium.name][0]["content"] = updated_prompt
            self.ai_agents[medium.name].append({"primary role": "player", "content": string})
            
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
        
        print(message)

        for player in alive_players:
            self.ai_agents[player].append({"role": "user", "content": message})

    def bluffing(self):
        print("\n--- Bluffs ---")

        alive_players = [p for p in self.players if p.alive]
        bluff_options = self.true_roles_pool + ["Werewolf", "None"]

        for p in alive_players:
            prompt = "you are a " + p.role + " bluffing as " + p.bluff + " and you are deciding whether you want to bluff or not. Is it time to come clean and reveal the truth? It is best to stick with a role you are already claiming. You should not bluff (pick None) most of the time, but sometimes you might want to bluff to throw off the evil team."
            if p.role == "Werewolf":
                prompt = "You are the Werewolf, and therefore have to bluff as a role. You can not bluff as Villager and you cannot select None as your bluff" 
                if self.night ==1:
                    prompt +=". To help you: the following role is out of play " + p.bluff + ". REMEMBER THIS ROLE. YOU DEFINITELY SHOULD BLUFF AS THIS ROLE AS IT IS THE SAFEST ONE TO DO"
            if p.role == "Veteran" or p.role == "Sailor" or p.role == "Psycho" or p.role == "Villager" or p.role == "Saint" or p.role == "Steward": 
                prompt += ". you may want to bluff another role to try and get killed. You should choose a bluff most of the time. Pick roles like Angel, Psycho, and Seer or Medium"
            if p.role == "Angel" or p.role == "Seer" or p.role == "Psycho" or p.role == "Medium":
                prompt += ". you may want to bluff another role to try and avoid getting killed. You should not bluff most of the time but if you do you can pick a character more likely to want to die like Saint, Steward, Villager, Sailor, Veteran, Psycho or Fool"
            prompt += ". If you want to bluff as a specific character, you will be given information on how to play as that character." 

            bluff_role = self.get_ai_decision(p, prompt, bluff_options)

            if p.color == "good":
                if bluff_role != p.role and bluff_role !="None":
                    p.color = "bluff"
            if p.color == "bluff":
                if bluff_role == p.role or bluff_role == "None":
                    p.color = "good"
            if p.bluff != bluff_role:
                p.bluff = bluff_role
                bluff_strategy = "I might claim to be buffing" + BLUFF_GUIDE.get(bluff_role, "Nothing. I plan to just tell the truth") + "but that doesnt mean I am locked on this decision"
                self.ai_agents[p.name].append({"role": "assistant", "content": bluff_strategy})
                print_colored(p.color,p.name + " the " + p.role + " is bluffing as: " + bluff_role)
            time.sleep(self.speed+1)

    def converstaions(self, convos):
        if self.mode > 1:
                self.bluffing()
                time.sleep(1)

        print("\n--- Private Conversation Phase ---")

        alive_players = [p for p in self.players if p.alive]

        num_rounds = max(0, 1 + convos - self.night)
        used_conversations = set()

        for _ in range(num_rounds):
            
            random.shuffle(alive_players)
            conversations = []
            

            # Create groups of 2 (one group of 3 if odd number of players)
            i = 0
            attempts = 0
            while i < len(alive_players):
                
                if i + 4 > len(alive_players): 
                    group = tuple(sorted(alive_players[i:], key=lambda p: p.name))
                    used_conversations.add(group)
                    conversations.append(alive_players[i:])  # Last group (2 or 3)
                    break
                else:
                    group = tuple(sorted(alive_players[i:i+2], key=lambda p: p.name))
                    if group not in used_conversations or attempts > 1:
                        conversations.append(alive_players[i:i+2])  # Pair of 2
                        used_conversations.add(group)
                        i += 2
                    else: 
                        attempts +=1
                        alive_players[i], alive_players[i+2+attempts] = alive_players[i+2+attempts], alive_players[i]
                        print("attempt #" + str(attempts))
                        
                    
            
            # Run each private conversation
            for convo in conversations:
                participant = [p for p in convo]
                message = f"you are in a private conversation with {', '.join(p.name for p in participant)}. "
                string = f"""
                ----------------------------------------------------------------

                {message}
                ----------------------------------------------------------------"""
                print(string) 
                for p in participant:
                    self.ai_agents[p.name].append({"role": "user", "content": message})

                for turn in range(1+len(convo)):    # Each player speaks twice
                    speaker = convo[turn % len(convo)]
                    prompt = f"""
you are {speaker.name} and you know for a fact that you are a {speaker.role} bluffing as {speaker.bluff} in a private conversation with {', '.join(o.name for o in participant if o.name != p.name)}
You do not have to commit to the role you are bluffing as
Do not say you are the same role as another player unless you are that role or you are the Werewolf
you are now in a private conversation. Feel free to share any information you have. 
Make sure you respond to the messages already in this conversation. DO NOT REPEAT ANY MESSAGES YOU HAVE SEEN.
You should claim to be a role (Villager, Seer, Monk, Fighter, Steward, Medium, Saint, Sailor, Psycho, Jester)
Some roles might want to lie about what role they are, like Werewolf. 
You can relay false information if you think it will help.
No ability will ever fail, never claim that you don't know who you chose last night or that you don't know the outcome. 
Either you learned something or you did not. No claiming that results were inconclusive or anything like that.
No saying Vague or Inconclusive. You need to be precise.
Do not say you don't know something about your role. - Instead say you do not want to reveal that information yet.
Do not say you know someone is the werewolf unless you have a piece of evidence. - Instead say there are a Werewolf candidate.
If you do not want to claim your role you can offer up two roles offering a "2 for 2". - You suggest 2 roles you might be and the other might do the same. I am either the X or Y. 
Do not say you are learning towards something. Instead say I am claiming this or that. 
Keep your conversation brief, 2-3 sentences.
Do not introduce yourself. Assume they already know your name. DO NOT SAY YOUR NAME.
Do not assume that you should follow the same format as the message you've seen. 
Do not comment on emotions. you shouldnt act scared or worried. You should act skeptical and inquisitve.
Death does not concern you.

Do not comment about a players death unless you know something about them like their role. 
Your talk should soley revolve around the game you are playing. 
Do not comment on who died unless you have infromation regarding it. 

You should be concered if 2 players are claiming the same role. One of them is lying. 
Therefore do not claim a role that someone else is claiming unless you have reason to believe they are not that role.

Always look at the prior convesations. to see if you have already claimed a role to the people you are in a conversation with. 
Do not gossip about players that you havent talked to or heard about. If a player does not exist in your history you know nothing about them. 
Do not gossip about player roles that no one has claimed. if no one including yourself is claimging to be that role in your history you know nothing about it.
You should have absoulte certainty about the things you know and no knowledge of the things that are not in your history.

Stick to one bluff at a time. Do not say you are a role that you are not and are not bluffing unless you are the Werewolf or Fool 
            """
                    speaker = convo[turn % len(convo)]
                    if speaker.role == "Werewolf":
                        prompt += "You cannot claim to be Villager, you must bluff as another role. Give a convincing impression of that role, giving out false information when you can"
                    player_history = self.ai_agents[speaker.name]
                    response = self.callAI(player_history, prompt)
                        # check if response is formatted
                    scan = "AI "+speaker.name 
                    if (not response.startswith(scan)):
                            #format if not formatted
                        response = "AI " + speaker.name + " says: " + response

                    print_colored(speaker.color,response)
                        # Append to all players' history in the conversation
                    for p in convo:
                        self.ai_agents[p.name].append({"role": "assistant" if p.name == speaker.name else "user", "content": response})
                    time.sleep(self.speed+5)
            if self.mode > 1:
                self.reflection()
                self.bluffing()
                time.sleep(1)    
                    
    def reflection(self, ):
        print("\n--- Self Reflection Phase ---")

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
List all the players and the roles they have claimed so you can reference it in case they change their claim
            """
            
            if player.role == "Werewolf":
                prompt += f"""
Who do you think would be a good kill? Are you planning on claiming the same role tomorrow or switching up your role?
Does the information you are giving out make sense given the role descripitions you've been given?
Has anyone given out information that you know to be false?
List all the players and the roles they have claimed so you can reference it in case they change their claim
            """
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("here is the chat history: " + str(messages) + "now respond to this prompt: " + prompt)
            response = response.text.strip()
            print_colored(player.color,"On, day" + str(self.night) + ", " + player.name + " thinks that: " + response)
            
            current_prompt = self.ai_agents[player.name][1]["content"]
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + response
                # Update the first message with the new prompt
            self.ai_agents[player.name][1]["content"] = updated_prompt
            messages.append({"role": "assistant", "content": response})
            time.sleep(self.speed+5)

    def discussion(self, repeats):
        print("\n--- Discussion Phase ---")
        alive_players = [p for p in self.players if p.alive]
        random.shuffle(alive_players)

        repeats = max(1, repeats)

        for _ in range(repeats):
            
            for player in alive_players:
                messages = self.ai_agents[player.name] # get chat history
                prompt = "It is day " + str(self.night) + ". you are a " + player.role + ". In the past you have bluffed as a  " + player.bluff 
                if player.role == "Werewolf":
                    prompt += ". You must not tell anyone this, instead you should falsely claim to be a role that you think will not be executed. You CANNOT pretend to be a villager."
                if player.role == "Seer":
                    prompt += ". Remember that you might not actually be an seer, there is a chance you are the Drunk. If you found a Werewolf you should push for their execution."
                if player.role == "Jester":
                    prompt += ". Remember that you are trying to seem like the werewolf, but don't make it too obvious."
                if player.role == "Saint":
                    prompt += ". Remember you lose if you are executed. Try really hard to convince players that you are not the Werewolf."
                if player.role == "Fighter" or player.role == "Sailor" :
                    prompt += ". Remember you want to get attacked by the Werewolf. The Werewolf might not attack you if you are truthful about your role." 
                prompt += f"""
The following players are still alive: {', '.join(p.name for p in alive_players)}
What would you like to tell the other players? 
You should claim to be a role 
(Villager, Seer, Monk, Fighter, Steward, Medium, Saint, Sailor, Pyscho, Jester)
You can bluff about what role you are. 
Try to be consistent with your past role claims
give justification for why you are chainging your claim. 
You should not lie about your role unless you have to.
If you learned something last night, you should tell the other players.
Do not say you don't know something about your role. - Instead say you do not want to reveal that information yet.
Do not say you know someone is the werewolf unless you have a piece of evidence. - Instead say there are a Werewolf candidate.
No saying Vague or Inconclusive. You need to be precise.
Do not assume that you should follow the same format as the message you've seen. 
Do not comment on emotions. you shouldnt act scared or worried. You should act skeptical and inquisitve.
Death does not concern you.
You can relay false information and should do so if you are bluffing about what role you are. You should not do this often. unless you are bluffing a character

Remember there can only be one of each role. You should question anybody claiming the same role as yourself or someone else.

There is a jester and werewolf lying about their role. Avoid executing the jester.

There also could be a drunk who thinks they are seer. 

Suggest a player for execution if you suspect someone. 

Please keep your responses to 1-2 short sentences.  
                """
                
                # Send prompt
                choice = self.callAI(messages, prompt)
                
                # check if response is formatted
                scan = "AI "+player.name 

                if (not choice.startswith(scan)):
                    #format if 
                    choice = "AI " + player.name + " says: " + choice

                print_colored(player.color,choice)
                time.sleep(self.speed+5)

                for p in alive_players:
                    # append response to prompt
                    self.ai_agents[p.name].append({"role": "assistant" if p.name == player.name else "user", "content": choice})

    def get_noms(self):
        alive_players = [p for p in self.players if p.alive]

        for player in alive_players:
            messages = self.ai_agents[player.name] # get chat history

            prompt = f"""
you are {player.name}, a {player.role}
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

            if player.role == "Jester":
                prompt += ". Remember that you want to get executed."
               

            # Send prompt
            choice = self.callAI(messages, prompt)

            # clearn response
            choice = choice[7:-3]

            current_prompt = self.ai_agents[player.name][1]["content"]
            string = "day " + str(self.night) + " I have voted for vote for: " + choice
            # Append the new critical information to the prompt
            updated_prompt = current_prompt + "\n" + string
                # Update the first message with the new prompt
            self.ai_agents[player.name][1]["content"] = updated_prompt
            messages.append({"role": "assistant", "content": string})
            # print response
            print_colored(player.color,player.name + " says " + string)
            time.sleep(self.speed+7)

            try: 
                vote_data = json.loads(choice)
                player.votes = vote_data.get("votes", [])
            except json.JSONDecodeError:
                player.votes = []

    def nomination_phase(self):
        print("\n--- Nomination Phase ---")

        
        nominations = set()
        alive_players = [p for p in self.players if p.alive]
        nominators = alive_players
        
        while len(nominations) < len(alive_players) - 1 and nominators:
            nominator = random.choice(nominators)
            available_nominations = [p.name for p in alive_players if p.name not in nominations and p.name != nominator.name]
            nominators = [p for p in nominators if  p.name != nominator.name]
            if not available_nominations:
                print("Nominations are closed. No one is executed.")
                break
            nominee_name = next((vote for vote in nominator.votes if vote in available_nominations), None)
            if not nominee_name:
                print_colored(nominator.color,nominator.name + " passes")
                continue
            print_colored(nominator.color,f"{nominator.name} nominates {nominee_name}.")
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
        
        print(f"Votes for {nominee_name}: {', '.join(votes)}")
        if len(votes) > len(alive_players) / 2:
            nominee = next(p for p in self.players if p.name == nominee_name)
            print_colored(nominee.color,f"{nominee_name} has been executed!")
            if nominee.true_role == "Sailor":
                print_colored(nominee.color,"\nBut does not die!")
            else:
                nominee.alive = False
            if nominee.role == "Jester":
                print_colored(nominee.color,"\nThe Jester has been executed and wins the game!")
                self.game_over = True
                return
            if nominee.role == "Saint":
                print_colored("evil","\nThe Saint has been executed and the Werewolf the game!")
                self.game_over = True
                return
            return True
        return False

    def check_winner(self):
        werewolf_alive = any(p.alive and p.role == "Werewolf" for p in self.players)
        villagers_alive = sum(1 for p in self.players if p.alive and p.role != "Werewolf")

        if not werewolf_alive:
            print_colored("good","\nVillagers win!")
            self.game_over = True
        elif villagers_alive < 2:
            print_colored("evil","\nWerewolf wins!")
            self.game_over = True

    def callAI(self, messages, prompt):
        while True:
            try:
                temp_history = messages[:3] + messages[-5:]
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
            if self.mode < 1:
                self.bluffing()
                time.sleep(1)
            time.sleep(1)
            self.converstaions(self.convos)
            time.sleep(1)
            self.discussion(self.convos-1)
            time.sleep(1)
            self.get_noms()
            time.sleep(1)
            self.nomination_phase()
            self.check_winner()
            time.sleep(1) 

if __name__ == "__main__":
    debug_mode = "debug" in sys.argv
    # works with 5 through 10, simply modify playercount
    game = WerewolfGame(debug_mode)
    game.play()
