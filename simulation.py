from organization import Organization
from venue import Venue
import random
import time
import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, num_orgs, num_venues, num_periods, cancellation_rate):
        #hardcoded time slots for the simulation
        self.time_slots = [hour for hour in range(8, 24)]

        #create organizations and venues as per the instantiation parameters. 
        self.organizations = [Organization(f"Organization {i}", random.randint(1,5), []) for i in range(num_orgs)]
        self.venues = [Venue(f"Venue {i}", random.randint(1, 5), self.time_slots) for i in range(num_venues)]

        #the number of periods/times to run the simulation for
        self.num_periods = num_periods

        #the rate at which bookings are cancelled by the university for their own purposes
        self.cancellation_rate = cancellation_rate

        #reserve venues are randomly selected from the total number of venues. 
        #This represents the venues that the university will book for organizations if the organizations have not booked a venue
        self.reserve_venues = random.sample(self.venues, max(1, num_venues // 5))
        for venue in self.reserve_venues:
            self.venues.remove(venue)

        self.score_history = {org.name: [] for org in self.organizations}  # Store scores for each organization
        self.strategy_history = {org.name: [] for org in self.organizations}  # Store strategies for each organization


    def generate_schedules(self):

        for organization in self.organizations:
            organization.schedule = set()

            while len(organization.schedule) < organization.num_events:
                slot = random.choice(self.time_slots)
                is_compatible = True
                for booked_slot in organization.schedule:
                    if abs(booked_slot - slot) < 2:
                        is_compatible = False
                        break

                if is_compatible:
                    organization.schedule.add(slot)
            print(f"Organization {organization.name} has a schedule of: {organization.schedule}")

    def reset_venues(self):
        print("Resetting venues for the current period")
        for venue in self.venues + self.reserve_venues:
            venue.reset_venue_bookings()
    
    def organization_bookings(self):
        print("Organizations are booking venues")

        # Sort organizations by reputation (highest first)
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            # For each time slot in the organization's schedule
            for time_slot in org.schedule:
                available_venues = [v for v in self.venues if v.is_available(time_slot)]

                if available_venues:
                    # Delegate the booking logic to the organization
                    org.book_venues(available_venues)
                else:
                    print(f"No available venues for {org.name} in time slot {time_slot}.")
                

    def university_cancellations(self):
        print("University is cancelling bookings based on cancellation rate")
        for venue in self.venues:
            if any(venue.time_slots[slot] is not None for slot in venue.time_slots):
                cancel_slot = random.choice([slot for slot, org in venue.time_slots.items() if org is not None])
                venue.cancel_booking(cancel_slot)
                print(f"University has cancelled booking for venue {venue.name} at time slot {cancel_slot}.")

    #give the organizations that have not booked a venue a reserve venue so they can still host events
    def allocate_reserve_venues(self):
        print("Allocating reserve venues to organizations...")
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            for time_slot in org.schedule:
                booked = any(venue.time_slots.get(time_slot) == org for venue in self.venues + self.reserve_venues)
                if not booked:
                    for reserve_venue in self.reserve_venues:
                        if reserve_venue.is_available(time_slot):
                            reserve_venue.book(org, time_slot)
                            print(f"{org.name} has been allocated reserve venue {reserve_venue.name} for time slot {time_slot}.")
                            break

    def score_organizations(self):
        """
        Score the organizations based on their bookings using the new payoff function:
        Payoff = sum of venue popularity levels from successful bookings - beta * overbooked venues
        """
        print("Scoring organizations...")

        for org in self.organizations:
            successful_bookings_value = 0
            unused_bookings = 0

            # Track the time slots booked by the organization to detect overbookings
            booked_time_slots = {}

            # Count successful and unused bookings
            for venue in self.venues + self.reserve_venues:
                for slot, booked_org in venue.time_slots.items():
                    if booked_org == org:
                        # Check if this time slot is already booked by the organization in another venue
                        if slot not in booked_time_slots:
                            # First booking for the time slot is successful
                            booked_time_slots[slot] = 1
                            successful_bookings_value += venue.popularity_level  # Use the venue's popularity level as reward
                        else:
                            # Overbooked venues are marked as unused
                            unused_bookings += 1

            # Calculate the final payoff
            beta = org.penalty_cost  # Penalty for overbooked venues
            payoff = successful_bookings_value - (beta * unused_bookings)

            # Update organization's score and reputation based on the calculated payoff
            org.score += payoff
            self.score_history[org.name].append(org.score)

            # Output the current state of the organization
            print(f"{org.name}: Successful bookings = {successful_bookings_value} (sum of venue popularity levels), Overbooked = {unused_bookings}")
            print(f"Payoff: {payoff}, Updated score: {org.score}, Reputation: {org.reputation}")

    def get_average_score(self):
        return sum(org.score for org in self.organizations) / len(self.organizations)
    

    def update_reputations(self):
        avg_score = self.get_average_score()
        print(f"Average score is {avg_score}")
        print("Updating reputations...")
        for org in self.organizations:
            org.update_reputation(avg_score)
            print(f"Organization {org.name} has a reputation of {org.reputation}")


    def update_strategies(self):
        avg_score = self.get_average_score()
        for org in self.organizations:
            org.update_strategy(avg_score)
            self.strategy_history[org.name].append(org.strategy)  # Track strategy each round
            print(f"Organization {org.name} has a strategy of {org.strategy} after the round")

    def run(self):
        for period in range(self.num_periods):

            #Added in time.sleep to actually be able to track what is going on as the simulation is running

            print(f"\n==== Round {period + 1} ====")
            print("Organizations are either overbooking or booking regularly based on their strategy")


            self.generate_schedules()
            time.sleep(2)


            self.reset_venues()
            time.sleep(2)  # Adjust the number of seconds as needed

            #process the bookings for the current period
            self.organization_bookings()
            time.sleep(2)

            #cancel the bookings for the current period
            self.university_cancellations()
            time.sleep(2)

            #allocate reserve venues to organizations that have not booked a venue
            self.allocate_reserve_venues()
            time.sleep(2)

            #score the organizations based on their bookings
            self.score_organizations()
            time.sleep(2)

            #update the reputations and strategies of the organizations
            self.update_reputations()
            time.sleep(2)

            self.update_strategies()
            time.sleep(2)
    
    def print_results(self):
        print("\nSimulation Results:")
        print("-------------------")
        for org in sorted(self.organizations, key=lambda x: x.score, reverse=True):
            successful_bookings = sum(1 for v in self.venues + self.reserve_venues if v == org)
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

        # Track the scores based on strategy
        normal_scores = {org_name: [] for org_name in self.strategy_history if 'normal' in self.strategy_history[org_name]}
        overbook_scores = {org_name: [] for org_name in self.strategy_history if 'overbook' in self.strategy_history[org_name]}

        # Plot for each strategy separately
        plt.figure(figsize=(12, 6))

        # Plot for normal strategy
        plt.subplot(1, 2, 1)
        for org_name in normal_scores:
            plt.plot(range(1, self.num_periods + 1), self.score_history[org_name], label=org_name)
        plt.title("Normal Booking Strategy Scores")
        plt.xlabel("Round")
        plt.ylabel("Score")
        plt.legend()

        # Plot for overbooking strategy
        plt.subplot(1, 2, 2)
        for org_name in overbook_scores:
            plt.plot(range(1, self.num_periods + 1), self.score_history[org_name], label=org_name)
        plt.title("Overbooking Strategy Scores")
        plt.xlabel("Round")
        plt.ylabel("Score")
        plt.legend()

        plt.tight_layout()
        plt.show()
    
    def compare_strategy_performance(self):
        normal_scores = [self.score_history[org_name][-1] for org_name in self.strategy_history if 'normal' in self.strategy_history[org_name]]
        overbook_scores = [self.score_history[org_name][-1] for org_name in self.strategy_history if 'overbook' in self.strategy_history[org_name]]

        avg_normal_score = sum(normal_scores) / len(normal_scores) if normal_scores else 0
        avg_overbook_score = sum(overbook_scores) / len(overbook_scores) if overbook_scores else 0

        print(f"Average score for normal booking: {avg_normal_score:.2f}")
        print(f"Average score for overbooking: {avg_overbook_score:.2f}")

        plt.bar(['Normal Booking', 'Overbooking'], [avg_normal_score, avg_overbook_score])
        plt.title("Comparison of Average Scores by Strategy")
        plt.ylabel("Average Score")
        plt.show()

    def track_strategy_changes(self):
        strategy_changes = {org.name: 0 for org in self.organizations}

        for org in self.organizations:
            for i in range(1, len(self.strategy_history[org.name])):
                if self.strategy_history[org.name][i] != self.strategy_history[org.name][i - 1]:
                    strategy_changes[org.name] += 1

        print("Strategy changes over time:")
        for org_name, changes in strategy_changes.items():
            print(f"{org_name}: {changes} changes")

    

    def calculate_gini_coefficient(self):
        scores = [org.score for org in self.organizations]
        scores = np.array(sorted(scores))
        n = len(scores)
        index = np.arange(1, n + 1)
        gini = (2 * np.sum(index * scores) / np.sum(scores)) - (n + 1) / n
        print(f"Gini Coefficient (score inequality): {gini:.2f}")
