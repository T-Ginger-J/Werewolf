import random
import time
import json

import ollama

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True
        self.votes = []

    def __repr__(self):
        return f"{self.name} ({'Alive' if self.alive else 'Dead'}) - {self.role}"

class WerewolfGame:
    def __init__(self, playercount):
        self.playercount = playercount
        self.players = []
        self.ai_agents = {}
        self.werewolf_role = ["Werewolf"]
        self.good_roles_pool = ["Investigator", "Angel", "Fool", "Villager", "Villager", "Villager"]
        self.player_names = ["Alice", "Nick", "Charlie", "Eve", "Isaac"] 
        if playercount > 5:
            self.good_roles_pool.append("Villager")
            self.player_names.append("Cooper")
            if playercount > 6:
                self.player_names.append("Alseid")
        self.assign_roles()
        self.game_over = False
        self.fool_wins = False
        self.initialize_ai_players()

    def assign_roles(self):
        chosen_good_roles = random.sample(self.good_roles_pool, self.playercount - 1)  # Select 1 less than playercount random good roles
        all_roles = self.werewolf_role + chosen_good_roles
        random.shuffle(all_roles)
        
        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        print("\n--- Players and Roles ---")
        for player in self.players:
            print(f"{player.name} is a {player.role}")

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
        - The Fool wins if they are executed.
        - Villagers have no special ability.
        - There can be at most one of each non Villager role. 
        - Any of the roles besides Werewolf could not be in play. 
        
        The goal of the Werewolf is to eliminate all other players.
        The goal of the Villagers (and other good roles) is to find and execute the Werewolf.
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
        You are {player.name}, playing as {player.role} in a game of Werewolf.
        The following players are still alive: {', '.join(options)}
        
        Your task is to make a decision: {decision_type}.
        Respond with ONLY one name from the list. No explanations.
    
        Answer format: [Exact player name]
        """

        messages = self.ai_agents[player.name]  # Get player's chat history
        
        response = ollama.chat(model="mistral", messages=messages + [{"role": "user", "content": prompt}]) # get AI decision

        choice = response['message']['content'].strip() #get the text from the response

        if choice in options:
            return choice
        else:
            # print("random")
            return random.choice(options) 

    def night_phase(self):
        print("\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        investigator = next((p for p in self.players if p.role == "Investigator" and p.alive), None)
        angel = next((p for p in self.players if p.role == "Angel" and p.alive), None)

        protected_player = None
        if angel:
            alive_players = [p.name for p in self.players if p.alive and p != angel]
            protected_name = self.get_ai_decision(angel, "choose a player to protect", alive_players)
            protected_player = next(p for p in self.players if p.name == protected_name)
            self.ai_agents[angel.name].append({"role": "assistant", "content": "I protected " + protected_name})
            print(f"Angel {angel.name} protects {protected_player.name}.")
        
        if werewolf:
            alive_players = [p.name for p in self.players if p.alive and p != werewolf]
            target_name = self.get_ai_decision(werewolf, "choose a player to attack", alive_players)
            target = next(p for p in self.players if p.name == target_name)
            if target == protected_player:
                print(f"Werewolf {werewolf.name} attacks {target.name}, but they are protected!")
            else:
                print(f"Werewolf {werewolf.name} attacks {target.name}.")
                target.alive = False

        if investigator:
            alive_players = [p.name for p in self.players if p.alive and p != investigator]
            suspect_name = self.get_ai_decision(investigator, "choose a player to investigate", alive_players)
            suspect = next(p for p in self.players if p.name == suspect_name)
            result = "Werewolf" if suspect.role == "Werewolf" else "Not a Werewolf"
            self.ai_agents[investigator.name].append({"role": "assistant", "content": "I investigated " + suspect_name + " and learned that they are " + result})
            print(f"Investigator {investigator.name} investigates {suspect.name} and learns they are: {result}.")
        

    def discussion_phase(self):
        print("\n--- Discussion Phase ---")
        alive_players = [p for p in self.players if p.alive]

        for player in alive_players:
            messages = self.ai_agents[player.name] # get chat history

            prompt = f"""
            The following players are still alive: {', '.join(p.name for p in alive_players)}
            What would you like to tell the other players? 
            You can tell them any information you know.
            You can relay false information if you think it is beneficial. 
            You can bluff about what role you are. 
            You should definetly do this if you are the Werewolf.
            Remember there can only be one of each role.
            
            Suggest a player for execution if you suspect someone. 

            Please keep your responses to only 2 sentences. 
            """
            # append discussion prompt
            
            # Send prompt
            response = ollama.chat(model="mistral", messages=messages + [{"role": "user", "content": prompt}]) # get AI decision

            choice = response['message']['content'].strip()

            # print response
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
            The following players are still alive: {', '.join(p.name for p in alive_players)}
            Based on the current game state, return a JSON object with a list of players you would nominate.
            Do not add any explinations, just say which players you think are potentially the werewolf.
            You should name at least one player. 
            You must follow this Example format:
            {{
                "votes": ["Player1", "Player2", "Player3"]
            }}
            """

            #instead of appending this message to the chat history, make a temporary

            
            # Send prompt
            response = ollama.chat(model="mistral", messages=messages + [{"role": "user", "content": prompt}]) # get AI decision

            choice = response['message']['content'].strip()

            messages.append({"role": "assistant", "content": "I would vote for: " + choice})
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
                break
            nominee_name = next((vote for vote in nominator.votes if vote in available_nominations), None)
            if not nominee_name:
                print(nominator.name + " passes")
                continue
            print(f"{nominator.name} nominates {nominee_name}.")
            nominations.add(nominee_name)
            if self.voting_phase(nominee_name):
                break
    
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
            if next(p for p in self.players if p.name == nominee_name).role == "Fool":
                print("\nThe Fool has been executed and wins the game!")
                self.game_over = True
            next(p for p in self.players if p.name == nominee_name).alive = False
            return True
        return False

    def check_winner(self):

        werewolf_alive = any(p.alive and p.role == "Werewolf" for p in self.players)
        villagers_alive = sum(1 for p in self.players if p.alive and p.role != "Werewolf")

        if not werewolf_alive:
            print("\nVillagers win!")
            self.game_over = True
        elif villagers_alive <= 2:
            print("\nWerewolf wins!")
            self.game_over = True

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
    playercount = 7
    # works with 5, 6, or 7 players, simply modify playercount
    game = WerewolfGame(playercount)
    game.play()
