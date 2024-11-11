import random

#Class instance for the organization with a score, reputation, and strategy
class Organization:
    def __init__(self, name, events, schedule):
        self.name = name
        #Number of events/time slots that the organization wants to book
        self.num_events = events
        #value used each round to determine if the organization is doing well or not which is calculated by how well they utilized their rooms and if they get penalized by overbooking
        self.score = 0
        #reputation of the organization that they must maintain if they want to continue booking venues
        self.reputation = 100
        #which strategy the organization uses to book venues
        self.strategy = random.choice(["overbook", "normal"])
        # as organizations overbook and are penalized, the penalty cost will increase
        self.penalty_cost = 1
        #budget of the organization
        self.budget = 200
        #schedule of organization
        self.schedule = schedule
        self.round_scores = []
        self.total_successful_bookings = 0
        self.total_unused_bookings = 0

        self.current_round_score = 0

    def book_venues(self, venues, enable_mechanism=False):
        if self.budget <= 5:
            print(f"{self.name} has insufficient budget to book any venue.")
            return False

        for time_slot in self.schedule:
            # Filter venues with the desired time slot available
            available_venues = [venue for venue in venues if venue.is_available(time_slot, enable_mechanism)]
            if not available_venues:
                print(f"{self.name} could not find any available venues for time slot {time_slot}.")
                continue

            venue = random.choice(available_venues)
            cost = venue.popularity_level * 5

            if self.budget >= cost:
                self.budget -= cost
                if venue.book(self, time_slot, enable_mechanism=enable_mechanism):
                    print(f"{self.name} successfully booked {venue.name} at time slot {time_slot}.")

                    # If overbooking, attempt to book an additional venue for the same time slot
                    if self.strategy == "overbook" and self.budget >= cost:
                        additional_venues = [v for v in available_venues if v != venue]
                        if additional_venues:
                            additional_venue = random.choice(additional_venues)
                            additional_cost = additional_venue.popularity_level * 5
                            if self.budget >= additional_cost:
                                self.budget -= additional_cost
                                if additional_venue.book(self, time_slot, enable_mechanism=enable_mechanism):
                                    print(f"{self.name} also overbooked {additional_venue.name} at time slot {time_slot}.")
            else:
                print(f"{self.name} does not have enough budget to book {venue.name}.")
                continue

        return True

    def update_strategy(self, avg_round_score):
        if self.budget < 10:
            self.strategy = "normal"
            print(f"{self.name} has switched to normal strategy due to low budget.")
        elif self.reputation < 60 and self.current_round_score < avg_round_score:
            self.strategy = "normal"
            print(f"{self.name} has switched to normal strategy due to low score and reputation.")
        elif self.current_round_score > avg_round_score and self.reputation >= 60:
            self.strategy = "overbook"
            print(f"{self.name} has switched to overbook strategy due to high score and reputation.")
        else:
            self.strategy = random.choice(["overbook", "normal"])
            print(f"{self.name} has randomly switched strategies due to average performance.")
        return True


    def update_reputation(self, avg_round_score):
        score_diff = self.current_round_score - avg_round_score
        # Adjust reputation change rate as needed
        reputation_change = score_diff * 0.5  # 0.5 is a scaling factor
        max_change = 20  # Maximum reputation change per round
        
        # Ensure the reputation change doesn't exceed the maximum allowed change
        reputation_change = max(-max_change, min(max_change, reputation_change))
        
        self.reputation += reputation_change
        if reputation_change > 0:
            print(f"{self.name} has gained {reputation_change:.2f} reputation due to high score.")
        elif reputation_change < 0:
            print(f"{self.name} has lost {abs(reputation_change):.2f} reputation due to low score.")
        else:
            print(f"{self.name}'s reputation remains the same.")
        
        self.reputation = max(0, min(200, self.reputation))
        return True


    def calculate_payoff(self, successful_bookings, unused_bookings):
        # Constants for reward and penalty
        REWARD_MULTIPLIER = 5  # Increased to boost rewards
        PENALTY_PER_UNUSED = self.penalty_cost   # Reduced to lower penalties

        # Total reward is based on the sum of venue popularity levels
        total_reward = sum([venue.popularity_level * REWARD_MULTIPLIER for venue, _ in successful_bookings])

        # Total penalty is based on unused bookings
        total_penalty = unused_bookings * PENALTY_PER_UNUSED

        # Calculate payoff and ensure it's non-negative
        payoff = max(0, total_reward - total_penalty)

        return payoff


    def update_penalty(self, unused_venues):
        self.penalty_cost += unused_venues * 0.5
        self.penalty_cost = min(10, self.penalty_cost)
        print(f"{self.name} has a penalty cost of {self.penalty_cost} due to {unused_venues} unused venues.")
        return True