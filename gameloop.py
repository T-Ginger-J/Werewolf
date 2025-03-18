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
        self.roles = ["Werewolf", "Investigator", "Angel", "Villager", "Villager"]
        self.assign_roles()
        self.game_over = False

    def assign_roles(self):
        random.shuffle(self.roles)
        for i, role in enumerate(self.roles):
            self.players.append(Player(f"Player {i+1}", role))

    def night_phase(self):
        print("\n--- Night Phase ---")
        werewolf = next(p for p in self.players if p.role == "Werewolf")
        investigator = next(p for p in self.players if p.role == "Investigator")
        angel = next(p for p in self.players if p.role == "Angel")
        
        target = random.choice([p for p in self.players if p.alive and p != werewolf])
        saved = random.choice([p for p in self.players if p.alive])
        investigated = random.choice([p for p in self.players if p.alive and p != investigator])

        print(f"Werewolf targets {target.name}.")
        print(f"Angel tries to save {saved.name}.")
        print(f"Investigator checks {investigated.name}. They are a {'Werewolf' if investigated.role == 'Werewolf' else 'Villager'}.")
        
        if target != saved:
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

    def check_winner(self):
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
