import random
import time
import json

import ollama

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

    def __repr__(self):
        return f"{self.name} ({'Alive' if self.alive else 'Dead'}) - {self.role}"

class WerewolfGame:
    def __init__(self, playercount):
        self.playercount = playercount
        self.players = []
        self.ai_agents = {}
        self.werewolf_role = ["Werewolf"]
        self.true_roles_pool = ["Investigator", "Angel", "Fool", "Villager", "Veteran", "Drunk", "Medium", "Sage", "Saint", "Immortal"]
        self.player_names = ["Alice", "Nick", "Charlie", "Eve", "Isaac"] 
        if playercount > 5:
            self.true_roles_pool.append("Psycho")
            self.player_names.append("Cooper")
            if playercount > 6:
                self.player_names.append("Alseid")
        self.assign_roles()
        self.game_over = False
        self.night = 1
        self.initialize_ai_players()

    def assign_roles(self):
        random.shuffle(self.player_names)
        chosen_good_roles = random.sample(self.true_roles_pool, self.playercount - 1)  # Select 1 less than playercount random good roles
        all_roles = self.werewolf_role + chosen_good_roles
        random.shuffle(all_roles)
        
        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        print("\n--- Players and Roles ---")
        for player in self.players:
            print(f"{player.name} is a {player.true_role}")

    def initialize_ai_players(self):
        for player in self.players:
            self.ai_agents[player.name] = [
                {"role": "system", "content": f"You are {player.name}, a player in a Werewolf game. Your role is {player.role}."}
            ]
            self.introduce_ai_player(player)
    
    def introduce_ai_player(self, player):
        prompt = f"""
        You are {player.name}, playing a Werewolf game. Your role is {player.role}.
        Here are the rules:
        - The Werewolf eliminates one player per night.
        - The Investigator can check if a player is a Werewolf.
        - The Angel can protect one player per night.
        - The Veteran wants the Werewolf to kill them. They get to kill a player if it happens.
        - The Fool wins if they are executed. Everyone else loses.
        - The Saint causes the good team to lose if they are executed. 
        - The Drunk does not know they are the Drunk, they think they are investigator, but gets false results.
        - The Psycho kills every night but still wins with good.
        - The Sage starts the game knows one player is not the werewolf.
        - The Medium learns the roles of characters who die.
        - The Immortal survives death once
        - Villagers have no special ability. 
        - Any of the roles besides Werewolf could not be in play. 
        
        The goal of the Werewolf is to eliminate all other players.
        The goal of the Villagers (and other good roles) is to find and kill the Werewolf.
        You should be trying to find out what role everyone is, and kill the ones who are most a threat.
        """
        try:
            # response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            self.ai_agents[player.name].append({"role": "user", "content": prompt})
            print(f"AI {player.name} initialized: {response['message']['content']}")
        except Exception as e:
            self.ai_agents[player.name].append({"role": "user", "content": prompt})
            # print(f"Error initializing AI for {player.name}: {e}")


    def get_ai_decision(self, player, decision_type, options):
    
        # Give AI the current circumstances and ask for direction

        prompt = f"""
        it is night {str(self.night)}
        You are {player.name}, playing as {player.role} in a game of Werewolf.
        The following players are still alive: {', '.join(options)}
        
        Your task is to make a decision: {decision_type}.
        Respond with ONLY one name from the list. No explanations.
    
        Answer format: [Exact player name]
        """

        messages = self.ai_agents[player.name]  # Get player's chat history
        
        choice = self.callAI(messages, prompt)

        if choice in options:
            return choice
        else:
            # print("random")
            return random.choice(options) 

    def night_phase(self):
        print("\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        
        angel = next((p for p in self.players if p.role == "Angel"), None)

        veteran = next((p for p in self.players if p.role == "Veteran"), None)

        immortal = next((p for p in self.players if p.true_role == "immortal"), None)

        dead = []

        protected_player = None
        if angel:
            alive_players = [p.name for p in self.players if p.alive and p != angel]
            protected_name = self.get_ai_decision(angel, "choose a player to protect", alive_players)
            protected_player = next(p for p in self.players if p.name == protected_name)
            self.ai_agents[angel.name].append({"role": "assistant", "content": "night " + str(self.night) + " I protected " + protected_name})
            print(f"Angel {angel.name} protects {protected_player.name}.")
        
        if werewolf:
            alive_players = [p.name for p in self.players if p.alive and p != werewolf]
            target_name = self.get_ai_decision(werewolf, "choose a player to attack", alive_players)
            target = next(p for p in self.players if p.name == target_name) 

            
            if target == protected_player or target == immortal:
                print(f"Werewolf {werewolf.name} attacks {target.name}, but they are protected!")
                if target == immortal:
                    print(f"Immortal {immortal.name} becomes mortal")
                    immortal.true_role = "Mortal"
                    immortal = None
            else:
                dead.append(target)
                print(f"Werewolf {werewolf.name} attacks {target.name}.")
                target.alive = False
                if target.role == "Veteran": 
                    target_name = self.get_ai_decision(veteran, "you have died, choose a player to kill", [p.name for p in self.players if p.alive])
                    target = next(p for p in self.players if p.name == target_name)
                    if target == protected_player or target == immortal:
                        print(f"Veteran {veteran.name} attacks {target.name}, but they are protected!")
                        if target == immortal:
                            print(f"Immortal {immortal.name} becomes mortal")
                            immortal.true_role = "Mortal"
                            immortal = None
                    else:
                        print(f"Veteran {veteran.name} attacks {target.name}.")
                        target.alive = False
                        dead.append(target)
                        if target == werewolf:
                            self.check_winner()

        psycho = next((p for p in self.players if p.role == "Psycho" and p.alive), None)

        if psycho:
            alive_players = [p.name for p in self.players if p.alive and p != psycho]
            target_name = self.get_ai_decision(psycho, "choose a player to kill", alive_players)
            target = next(p for p in self.players if p.name == target_name)
            if target == protected_player or target == immortal:
                print(f"Psycho {psycho.name} attacks {target.name}, but they are protected!")
                if target == immortal:
                        print(f"Immortal {immortal.name} becomes mortal")
                        immortal.true_role = "Mortal"
                        immortal = None
            else:
                dead.append(target)
                print(f"Psycho {psycho.name} attacks {target.name}.")
                target.alive = False
                if target == werewolf:
                   self.check_winner()

        investigator = next((p for p in self.players if p.true_role == "Investigator" and p.alive), None)
        drunk = next((p for p in self.players if p.true_role == "Drunk" and p.alive), None)

        if investigator:
            alive_players = [p.name for p in self.players if p.alive and p != investigator]
            suspect_name = self.get_ai_decision(investigator, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if suspect.role == "Werewolf" else "Not a Werewolf"
            self.ai_agents[investigator.name].append({"role": "assistant", "content": "night " + str(self.night) + " I investigated " + suspect_name + " and learned that they are " + result})
            print(f"Investigator {investigator.name} investigates {suspect.name} and learns they are: {result}.")

        if drunk:
            alive_players = [p.name for p in self.players if p.alive and p != drunk]
            suspect_name = self.get_ai_decision(drunk, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if not suspect.role == "Werewolf" else "Not a Werewolf"
            self.ai_agents[drunk.name].append({"role": "assistant", "content": "night " + str(self.night) + " I investigated " + suspect_name + " and learned that they are " + result})
            print(f"Drunk {drunk.name} investigates {suspect.name} and learns they are: {result}.")

        sage = next((p for p in self.players if p.role == "Sage" and p.alive), None)
        medium = next((p for p in self.players if p.role == "Medium" and p.alive), None)
        
        if sage:
            if self.night == 1:
                alive_players = [p.name for p in self.players if p.alive and p != werewolf and p != sage]
                not_WW = random.choice(alive_players)
                self.ai_agents[sage.name].append({"role": "assistant", "content": "night " + str(self.night) + " I learned " + not_WW + " is not a werewolf"})
                print(f"Sage {sage.name} learns {not_WW} is not a werewolf")
        
        if medium:
            seen = dead[0]
            self.ai_agents[medium.name].append({"role": "assistant", "content": "night " + str(self.night) + " I learned " + seen.name + " was the " + seen.true_role})
            print(f"Medium {medium.name} learns {seen.name} is a {seen.true_role}")
        
        message = str(random.shuffle(dead))
        if len(dead) == 0:
            message = "Nobody died last night"
        else:
            message += " ha"
            if len(dead) == 1:
                message += "s died"
            else:
                message += "ve died"

        for player in alive_players:
            self.ai_agents[player].append({"role": "system", "content": message})

    def discussion_phase(self):
        print("\n--- Discussion Phase ---")
        alive_players = [p for p in self.players if p.alive]

        random.shuffle(alive_players)

        for player in alive_players:
            messages = self.ai_agents[player.name] # get chat history
            prompt = "It is day " + str(self.night) + ". you are a " + player.role
            if player.role == "Werewolf":
                prompt += ". You must not tell anyone this, instead you should falsely claim to be a role that you think will not be executed. You CANNOT pretend to be a villager."
            if player.role == "Investigator":
                prompt += ". Remember that you might not actually be an investigator, there is a chance you are the Drunk. If you found a Werewolf you should push for their execution."
            if player.role == "Fool":
                prompt += ". Remember that you are trying to seem like the werewolf, but don't make it too obvious."
            if player.role == "Saint":
                prompt += ". Remember you lose if you are executed. Try really hard to convince players that you are not the Werewolf."
            if player.role == "Veteran" or player.role == "Immortal" :
                prompt += ". Remember you want to get attacked by the Werewolf. You can be truthful but then the Werewolf might not attack you"  
            prompt += f"""
            The following players are still alive: {', '.join(p.name for p in alive_players)}
            What would you like to tell the other players? 
            You should claim to be a role (Villager, Investigator, Angel, Veteran, Sage, Medium, Saint, Immortal)
            You can bluff about what role you are. 
            If you learned something last night, you should tell the other players 
            You can relay false information and should do so if you are bluffing about what role you are

            Remember there can only be one of each role, but there exists a drunk who thinks they are investigator.
            
            Suggest a player for execution if you suspect someone. 

            Please keep your responses to 2-3 short sentences.  
            """
            # append discussion prompt
            
            # Send prompt
            choice = self.callAI(messages, prompt)
            
            # check if response is formatted
            scan = "AI "+player.name 

            if (not choice.startswith(scan)):
                #format if 
                choice = "AI " + player.name + " says: " + choice

            print(choice)

            for p in alive_players:
                # append response to prompt
                self.ai_agents[p.name].append({"role": "assistant", "content": choice})

    def get_noms(self):
        alive_players = [p for p in self.players if p.alive]

        for player in alive_players:
            messages = self.ai_agents[player.name] # get chat history

            prompt = f"""
            you are a {player.role}
            The following players are still alive: {', '.join(p.name for p in alive_players)}
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

            if player.role == "Fool":
                prompt += ". Remember that you want to get executed."
               

            # Send prompt
            choice = self.callAI(messages, prompt)

            messages.append({"role": "assistant", "content": "day " + str(self.night) + " I would vote for: " + choice})
            # print response
            print(player.name + " says: I would vote for" + choice)

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
                print(nominator.name + " passes")
                continue
            print(f"{nominator.name} nominates {nominee_name}.")
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
            print(f"{nominee_name} has been executed!")
            nominee = next(p for p in self.players if p.name == nominee_name)
            if nominee.true_role == "Immortal":
                print("\nBut does not die!")
            else:
                nominee.alive = False
            if nominee.role == "Fool":
                print("\nThe Fool has been executed and wins the game!")
                self.game_over = True
            if nominee.role == "Saint":
                print("\nThe Saint has been executed and the Werewolf the game!")
                self.game_over = True
            return True
        return False

    def check_winner(self):
        if self.game_over == True:
            return

        werewolf_alive = any(p.alive and p.role == "Werewolf" for p in self.players)
        villagers_alive = sum(1 for p in self.players if p.alive and p.role != "Werewolf")

        if not werewolf_alive:
            print("\nVillagers win!")
            self.game_over = True
        elif villagers_alive <= 2:
            print("\nWerewolf wins!")
            self.game_over = True

    def callAI(self, messages, prompt):
        response = ollama.chat(model="mistral", messages=messages + [{"role": "user", "content": prompt}]) # get AI decision
        return response['message']['content'].strip()

    def play(self):
        while not self.game_over:
            self.night_phase()
            time.sleep(1)
            self.discussion_phase()
            self.get_noms()
            self.nomination_phase()
            self.check_winner()
            time.sleep(1)

if __name__ == "__main__":
    playercount = 6
    # works with 5, 6, or 7 players, simply modify playercount
    game = WerewolfGame(playercount)
    game.play()
