import random
from organization import Organization
from venue import Venue
import time
import matplotlib.pyplot as plt

class Simulation:
    def __init__(self, num_orgs, num_venues, num_periods, cancellation_rate):
        #create organizations and venues as per the instantiation parameters. 
        self.organizations = [Organization(f"Organization {i}", random.randint(10, 50)) for i in range(num_orgs)]
        self.venues = [Venue(f"Venue {i}", random.randint(1, num_venues)) for i in range(num_venues)]

        #the number of periods/times to run the simulation for
        self.num_periods = num_periods

        #the rate at which bookings are cancelled by the university for their own purposes
        self.cancellation_rate = cancellation_rate

        #reserve venues are randomly selected from the total number of venues. 
        #This represents the venues that the university will book for organizations if the organizations do not cancel their bookings
        self.reserve_venues = random.sample(self.venues, max(1, num_venues // 5))
        for venue in self.reserve_venues:
            self.venues.remove(venue)

        self.score_history = {org.name: [] for org in self.organizations}  # Store scores for each organization

    def run(self):
        for period in range(self.num_periods):

            #Added in time.sleep to actually be able to track what is going on as the simulation is running

            print(f"\n==== Round {period + 1} ====")
            print("Organizations are either overbooking or booking regularly based on their strategy")

            #reset the venues for the current period
            self.reset_venues()
            time.sleep(2)  # Adjust the number of seconds as needed

            #process the bookings for the current period
            self.organization_bookings(period)
            time.sleep(2)

            #cancel the bookings for the current period
            self.university_cancellations()
            time.sleep(2)

            #allocate reserve venues to organizations that have not booked a venue
            self.allocate_reserve_venues(period)
            time.sleep(2)

            #score the organizations based on their bookings
            self.score_organizations(period)
            time.sleep(2)

            #update the reputations and strategies of the organizations
            self.update_reputations()
            time.sleep(2)
            self.update_strategies()
            time.sleep(2)

    #TODO: create some sort of logic for organizations to book multiple venues if they are overbooking
    #TODO: create some sort of logic for implementing penalities and considering budgets more intensely when booking venues
    
    def reset_venues(self):
        print("Resetting venues for the current period")
        for venue in self.venues:
            venue.booked_by = None
            venue.date = None
    
    def organization_bookings(self, date):
        print("Organizations are booking venues")
        booking_limit = 2  # Set a limit on the number of venues an organization can book per period
        available_venues = [v for v in self.venues if v not in self.reserve_venues and v.booked_by is None]

        # Initialize a dictionary to keep track of how many venues each organization has booked
        bookings = {org: 0 for org in self.organizations}

        while available_venues and any(bookings[org] < booking_limit for org in self.organizations):
            for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
                if bookings[org] < booking_limit and available_venues:
                    venue = available_venues.pop(0)
                    venue.booked_by = org
                    venue.date = date
                    bookings[org] += 1
                    print(f"Organization {org.name} has booked venue {venue.name} on {venue.date}")

    def university_cancellations(self):
        print("University is cancelling bookings based on cancellation rate")
        for venue in self.venues:
            if venue.booked_by and random.random() < self.cancellation_rate:
                venue.booked_by = None
                venue.date = None
                print(f"University has cancelled booking for venue {venue.name} on {venue.date}")

    #give the organizations that have not booked a venue a reserve venue so they can still host events
    def allocate_reserve_venues(self, date):
        print("Allocating reserve venues to organizations...")
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            if not any(v.booked_by == org for v in self.venues + self.reserve_venues):
                for venue in self.reserve_venues:
                    if venue.booked_by is None:
                        venue.booked_by = org
                        venue.date = date
                        break

    def score_organizations(self, date):
        print("Scoring organizations...")
        for org in self.organizations:
            successful_bookings = sum(1 for v in self.venues if v.booked_by == org and v.date == date)
            unused_bookings = sum(1 for v in self.venues if v.booked_by == org and v.date != date)
            org.score += successful_bookings - unused_bookings * org.penalty_cost
            self.score_history[org.name].append(org.score)  # Store the score for analysis
            print(f"Organization {org.name} has a score of {org.score} and a reputation of {org.reputation}")

    def update_reputations(self):
        avg_score = sum(org.score for org in self.organizations) / len(self.organizations)
        print(f"Average score is {avg_score}")
        print("Updating reputations...")
        for org in self.organizations:
            reputation_change = org.score - avg_score
            org.reputation = max(0, min(200, org.reputation + reputation_change))
            print(f"Organization {org.name} has a reputation of {org.reputation}")


    def update_strategies(self):
        avg_score = sum(org.score for org in self.organizations) / len(self.organizations)
        for org in self.organizations:
            org.update_strategy(avg_score)
            print(f"Organization {org.name} has a strategy of {org.strategy} after the round")

    
    def print_results(self):
        print("\nSimulation Results:")
        print("-------------------")
        for org in sorted(self.organizations, key=lambda x: x.score, reverse=True):
            successful_bookings = sum(1 for v in self.venues + self.reserve_venues if v.booked_by == org)
            print(f"{org.name}:")
            print(f"  Strategy: {org.strategy}")
            print(f"  Score: {org.score:.2f}")
            print(f"  Reputation: {org.reputation:.2f}")
            print(f"  Successful Bookings: {successful_bookings}")
        
        print("\nStrategy Performance:")
        strategies = set(org.strategy for org in self.organizations)
        for strategy in strategies:
            orgs = [org for org in self.organizations if org.strategy == strategy]
            avg_score = sum(org.score for org in orgs) / len(orgs)
            print(f"  {strategy}: Average Score = {avg_score:.2f}")

    def plot_results(self):
        print("\nPlotting Results...")
        for org_name, scores in self.score_history.items():
            plt.plot(range(1, self.num_periods + 1), scores, label=org_name)

        plt.title("Organization Scores Over Rounds")
        plt.xlabel("Round")
        plt.ylabel("Score")
        plt.legend()
        plt.show()

    #Upon currently running it, overbooking does drastically better than normal, but we are trying to 
    #simulate it such that if they normally booked then it would be beneficial in the long run. 
    #May have to do some sort of setup where there are multiple simulations where all orgs share and all orgs try to overbook
    # to see how it goes. 