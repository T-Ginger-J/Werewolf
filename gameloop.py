import random
import time

import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True

    def __repr__(self):
        return f"{self.name} ({'Alive' if self.alive else 'Dead'}) - {self.role}"

class WerewolfGame:
    def __init__(self):
        self.players = []
        self.werewolf_role = ["Werewolf"]
        self.good_roles_pool = ["Investigator", "Angel", "Fool", "Villager", "Villager", "Villager"]
        self.player_names = ["Alice", "Bob", "Charlie", "David", "Eve"]
        self.assign_roles()
        self.game_over = False
        self.fool_wins = False
        self.initialize_ai_players()

    def assign_roles(self):
        chosen_good_roles = random.sample(self.good_roles_pool, 4)  # Select 4 random good roles
        all_roles = self.werewolf_role + chosen_good_roles
        random.shuffle(all_roles)
        
        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        print("\n--- Players and Roles ---")
        for player in self.players:
            print(f"{player.name} is a {player.role}")

    def initialize_ai_players(self):
        for player in self.players:
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
        Respond yes if you understand.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            print(f"AI {player.name} initialized: {response.text.strip()}")
        except Exception as e:
            print(f"Error initializing AI for {player.name}: {e}")

    def get_ai_decision(self, player, decision_type, options):
        prompt = f"""
        You are {player.name}, playing as {player.role} in a game of Werewolf.
        The following players are still alive: {', '.join(options)}
        
        Your task is to make a decision: {decision_type}.
        Respond with only the name of the chosen player.
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        choice = response.text.strip()
        if choice in options:
            return choice
        else:
            print("random")
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
            print(f"Investigator {investigator.name} investigates {suspect.name} and learns they are: {result}.")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(result)

    def day_phase(self):
        print("\n--- Day Phase ---")
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) <= 2:
            self.game_over = True
            return
        
        nominated = set()
        while len(nominated) < len(alive_players) - 1:
            nominator = random.choice([p for p in alive_players if p not in nominated])
            nominee = random.choice([p for p in alive_players if p != nominator and p not in nominated])
            nominated.add(nominee)
            print(f"{nominator.name} nominates {nominee.name}")
            
            voters = [p.name for p in alive_players if random.choice([True, False])]
            print(f"{nominee.name} received votes from: {', '.join(voters) if voters else 'No one'}")
            
            if len(voters) >= (len(alive_players) // 2 + 1):
                nominee.alive = False
                print(f"{nominee.name} is executed with {len(voters)} votes!")
                if nominee.role == "Fool":
                    print("\nThe Fool has been executed and wins the game!")
                    self.fool_wins = True
                    self.game_over = True
                return
        
        print("No player reached the majority vote, no execution today.")

    def check_winner(self):
        if self.fool_wins:
            return

        werewolf_alive = any(p.alive and p.role == "Werewolf" for p in self.players)
        villagers_alive = sum(1 for p in self.players if p.alive and p.role != "Werewolf")

        if not werewolf_alive:
            print("\nVillagers win!")
            self.game_over = True
        elif villagers_alive <= 1:
            print("\nWerewolf wins!")
            self.game_over = True

    def play(self):
        while not self.game_over:
            self.night_phase()
            time.sleep(1)
            self.day_phase()
            self.check_winner()
            time.sleep(1)

if __name__ == "__main__":
    game = WerewolfGame()
    game.play()

