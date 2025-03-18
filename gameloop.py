import random
import time

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

    def assign_roles(self):
        chosen_good_roles = random.sample(self.good_roles_pool, 4)  # Select 4 random good roles
        all_roles = self.werewolf_role + chosen_good_roles
        random.shuffle(all_roles)
        
        for i, role in enumerate(all_roles):
            self.players.append(Player(self.player_names[i], role))
        
        print("\n--- Players and Roles ---")
        for player in self.players:
            print(f"{player.name} is a {player.role}")

    def night_phase(self):
        print("\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        investigator = next((p for p in self.players if p.role == "Investigator" and p.alive), None)
        angel = next((p for p in self.players if p.role == "Angel" and p.alive), None)
        
        target = random.choice([p for p in self.players if p.alive and p != werewolf])
        saved = random.choice([p for p in self.players if p.alive]) if angel else None
        investigated = random.choice([p for p in self.players if p.alive and p != investigator]) if investigator else None

        print(f"Werewolf targets {target.name}.")
        if angel:
            print(f"Angel tries to save {saved.name}.")
        if investigator:
            print(f"Investigator checks {investigated.name}. They are a {'Werewolf' if investigated.role == 'Werewolf' else 'Villager'}.")
        
        if not angel or target != saved:
            target.alive = False
            print(f"{target.name} was killed!")
        else:
            print(f"{target.name} was saved!")

    def day_phase(self):
        print("\n--- Day Phase ---")
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) <= 2:
            self.game_over = True
            return

        vote_target = random.choice(alive_players)
        vote_target.alive = False
        print(f"Players vote to eliminate {vote_target.name}!")

        if vote_target.role == "Fool":
            print("\nThe Fool has been eliminated and wins the game!")
            self.fool_wins = True
            self.game_over = True

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
