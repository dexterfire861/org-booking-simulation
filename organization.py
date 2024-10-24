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

    def book_venues(self, venues):
        venues_to_book = []
        number_of_needed_venues = self.num_events

        if self.strategy == "overbook" and self.budget > 10:
            # If overbooking, the organization books more venues for the same time slots as backups
            while number_of_needed_venues > 0:
                # Pick a random venue that has available slots
                venue = random.choice([venue for venue in venues if venue.get_available_time_slots() != []])
                available_time_slots = venue.get_available_time_slots()

                # Ensure that the time slot does not conflict with the organization's existing schedule
                compatible_time_slots = [time_slot for time_slot in available_time_slots if time_slot in [s for s in self.schedule]]

                if compatible_time_slots:
                    time_slot = random.choice(compatible_time_slots)
                    cost = venue.popularity_level * 5  # Overbooking costs more
                    if self.budget >= cost:
                        self.budget -= cost
                        venues_to_book.append((venue, time_slot))
                        number_of_needed_venues -= 1

                        # Overbook by booking additional venues for the same time slot
                        additional_venue = random.choice([v for v in venues if v.get_available_time_slots() != [] and v != venue])
                        additional_time_slot = time_slot  # Overbook for the same time slot
                        additional_cost = additional_venue.popularity_level * 5
                        if self.budget >= additional_cost:
                            self.budget -= additional_cost
                            venues_to_book.append((additional_venue, additional_time_slot))
                        else:
                            print("Organization does not have enough budget to overbook additional venue.")
                        number_of_needed_venues -= 1
                    else:
                        print("Organization does not have enough budget to book venue.")
                        break
                else:
                    print("No compatible time slots available for overbooking.")
                    continue

        elif self.strategy == "normal" and self.budget > 10:
            # Normal booking: Book only the required number of venues with no overbooking
            while number_of_needed_venues > 0:
                venue = random.choice([venue for venue in venues if venue.get_available_time_slots() != []])
                available_time_slots = venue.get_available_time_slots()

                # Ensure that the time slot does not conflict with the organization's existing schedule
                compatible_time_slots = [time_slot for time_slot in available_time_slots if time_slot in [s for s in self.schedule]]

                if compatible_time_slots:
                    time_slot = random.choice(compatible_time_slots)
                    cost = venue.popularity_level * 5  # Normal booking cost
                    if self.budget >= cost:
                        self.budget -= cost
                        venues_to_book.append((venue, time_slot))
                        number_of_needed_venues -= 1
                    else:
                        print("Organization does not have enough budget to book venue.")
                        break
                else:
                    print("No compatible time slots available for normal booking.")
                    continue

        for venue, slot in venues_to_book:
            venue.book(self,slot)
            print(f"{self.name} has booked {venue.name} for time slot {slot}.")
        return venues_to_book



    def update_strategy(self, avg_score):
        if self.budget < 10:
            self.strategy = "normal"
            print(f"{self.name} has switched to normal strategy due to low budget.")
        elif self.reputation < 60 and self.score < avg_score:
            # Low reputation and low score force normal booking
            self.strategy = "normal"
            print(f"{self.name} has switched to normal strategy due to low score and reputation.")
        elif self.score > avg_score and self.reputation >= 60:
            self.strategy = "overbook"
            print(f"{self.name} has switched to overbook strategy due to high score and reputation.")
        else:
            self.strategy = random.choice(["overbook", "normal"])
            print(f"{self.name} has randomly switched strategies due to average performance.")
        
        return True

        
    
    def update_reputation(self, avg_score):
        
        if self.score < avg_score:
            self.reputation -= 20
            print(f"{self.name} has lost reputation due to low score and high penalty.")
        elif self.score > avg_score and self.reputation < 90:
            self.reputation += 15
            print(f"{self.name} has gained reputation due to high score.")
        elif self.score > avg_score and self.penalty_cost <= 2:
            self.reputation += 10
            print(f"{self.name} has gained reputation due to low penalty and good performance.")
        
        self.reputation = max(0, min(200, self.reputation))
        return True


    #Need to add a function that will update the penalty based on the number of venues booked and the score of the organization

    def update_penalty(self, unused_venues):
        
        self.penalty_cost += unused_venues*2

        self.penalty_cost = min(10, self.penalty_cost)
        print(f"{self.name} has a penalty cost of {self.penalty_cost} due to {unused_venues} unused venues.")
        return True
