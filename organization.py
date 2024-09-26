import random

#Class instance for the organization with a score, reputation, and strategy
class Organization:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.reputation = 100
        self.strategy = random.choice(["overbook", "normal"])

    def book_venue(self, venues, date):
        if self.strategy == "overbook":
            return random.sample(venues, min(2, len(venues)))
        return [random.choice(venues)]

    def update_strategy(self, avg_score):
        if self.score < avg_score:
            self.strategy = "overbook" if random.random() < 0.7 else "normal"