from organization import Organization
from venue import Venue
import random
import time
import matplotlib.pyplot as plt

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
        """Score the organizations based on their bookings, accounting for overbooked venues."""
        print("Scoring organizations...")
        
        for org in self.organizations:
            successful_bookings = 0
            unused_bookings = 0

            # Track the time slots booked by the organization to detect overbookings
            booked_time_slots = {}

            # Count successful and unused bookings
            for venue in self.venues + self.reserve_venues:
                for slot, booked_org in venue.time_slots.items():
                    if booked_org == org:
                        # Check if this time slot is already booked by the organization in another venue
                        if slot not in booked_time_slots:
                            booked_time_slots[slot] = 1  # Mark the first booking as successful
                            successful_bookings += 1
                        else:
                            # If the organization has already booked a venue for this time slot, count it as overbooking
                            booked_time_slots[slot] += 1
                            unused_bookings += 1

            # Apply penalties based on the unused bookings (overbooked venues)
            penalty = unused_bookings * org.penalty_cost

            # Update organization's score
            org.score += successful_bookings - penalty
            self.score_history[org.name].append(org.score)  # Store the score for analysis


            # Output the current state of the organization
            print(f"{org.name} has {successful_bookings} successful bookings and {unused_bookings} overbooked (unused) venues.")
            print(f"Penalty applied: {penalty}, Updated score: {org.score}, Reputation: {org.reputation}")

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
        for org_name, scores in self.score_history.items():
            plt.plot(range(1, self.num_periods + 1), scores, label=org_name)

        plt.title("Organization Scores Over Rounds")
        plt.xlabel("Round")
        plt.ylabel("Score")
        plt.legend()
        plt.show()