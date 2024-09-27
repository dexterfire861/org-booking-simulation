import random

#Class instance for the organization with a score, reputation, and strategy
class Organization:
    def __init__(self, name, size):
        self.name = name
        #size of the organization
        self.size = size
        #value used each round to determine if the organization is doing well or not
        self.score = 0
        #reputation of the organization that they must maintain if they want to continue booking venues
        self.reputation = 100
        #which strategy the organization uses to book venues
        self.strategy = random.choice(["overbook", "normal"])
        #budget that the organization has to spend on booking venues
        self.budget = 20
        # as organizations overbook and are penalized, the penalty cost will increase
        self.penalty_cost = 1

    def book_venue(self, venues, date):
        
        if self.strategy == "overbook" and self.budget > 10:
            venues_to_book = random.sample(venues, min(self.size+1, len(venues)))
            self.budget -= self.penalty_cost * len(venues_to_book)*2
        elif self.strategy == "normal" and self.budget > 5:
            venues_to_book = [random.choice(venues)]
            self.budget -= self.penalty_cost * len(venues_to_book)
        else:
            venues_to_book = [random.choice(venues)]
        return venues_to_book

    def update_strategy(self, avg_score):

        #Rudimentary logic for switching strategies, need to take into account more values and 
        #experiment with budget, penalty cost, and other factors to see how it impacts the simulation
        if self.score < avg_score and self.reputation < 60:
            self.strategy = "normal"
        elif self.score > avg_score and self.reputation > 60:
            self.strategy = "overbook"
        else:
            self.strategy = random.choice(["overbook", "normal"])
    
    def update_reputation(self, avg_score):
        #Same thing for updating reputation, need to take into account more values and 
        #see how it impacts the simulation
        if self.score > avg_score:
            self.reputation += 20
        else:
            self.reputation -= 20

    #Need to add a function that will update the penality based on the number of venues booked and the score of the organization

    def update_penalty(self, avg_score):
        pass


