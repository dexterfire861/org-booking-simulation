import random
import venue
import administration
import organization
from datetime import datetime, timedelta

class Simulation:
    def __init__(self, num_rounds, round_length, cancellation_rate, num_organizations, num_venues):
        self.num_rounds = num_rounds
        self.round_length = round_length  # Number of days per round
        self.cancellation_rate = cancellation_rate
        self.num_organizations = num_organizations
        self.num_venues = num_venues
        self.organizations = []
        self.venues = []
        self.administration = administration.Administration()
        self.current_day = 0
        self.initialize_entities()

    def initialize_entities(self):
        # Initialize Venues
        for i in range(1, self.num_venues + 1):
            name = f"Venue_{i}"
            size = random.randint(50, 200)
            price = random.randint(100, 500)
            venue = venue.Venue(name, size, price)
            self.venues.append(venue)
        # Initialize Organizations
        for i in range(1, self.num_organizations + 1):
            name = f"Organization_{i}"
            size = random.randint(20, 100)
            org = organization.Organization(name, size)
            self.organizations.append(org)

    def run_simulation(self):
        for round_num in range(1, self.num_rounds + 1):
            print(f"\n--- Round {round_num} ---")
            self.administration.distribute_budget(self.organizations)
            for day in range(1, self.round_length + 1):
                self.current_day += 1
                print(f"\nDay {self.current_day}")
                # Evaluate and cancel events
                for org in self.organizations:
                    org.evaluate_events(self.cancellation_rate)
                # Shuffle organizations for random booking order
                random.shuffle(self.organizations)
                # Available venues for the day
                available_venues = [venue for venue in self.venues]
                # Organizations attempt to book venues
                for org in self.organizations:
                    booked_events = org.book_events(available_venues, self.current_day, two_weeks_ahead=True)
                    for event in booked_events:
                        print(f"{org.name} booked {event.venue.name} at {event.timeslot}")
                # Process events for the day
                for venue in self.venues:
                    for ts in venue.timeslots:
                        org = venue.availability[self.current_day][ts]
                        if org:
                            attendance = self.calculate_attendance(org, venue, ts)
                            new_students = self.calculate_new_students(org, attendance, venue)
                            utilization = attendance / venue.size
                            org.size += new_students
                            org.budget += attendance * 2  # Example: income from attendance
                            org.update_reputation(utilization)
                            print(f"Event at {venue.name} during {ts}: {attendance} attended, {new_students} new students, Utilization: {utilization:.2f}")
                # End of day updates
                for org in self.organizations:
                    org.calculate_score()
                    print(f"{org.name}: Reputation={org.reputation}, Size={org.size}, Budget={org.budget}, Score={org.score}")
            # End of round summary
            self.round_summary(round_num)
        # End of simulation summary
        self.simulation_summary()

    def calculate_attendance(self, org, venue, timeslot):
        appeal = organization.TIMESLOT_APPEAL.get(timeslot, 0.5)
        base_attendance = int(org.size * 0.1 * appeal)
        # Limit attendance to venue size
        attendance = min(base_attendance, venue.size)
        return attendance

    def calculate_new_students(self, org, attendance, venue):
        # Example: 10% of attendance join
        return int(attendance * 0.1)

    def round_summary(self, round_num):
        print(f"\n--- End of Round {round_num} Summary ---")
        for org in self.organizations:
            print(f"{org.name}: Reputation={org.reputation}, Size={org.size}, Budget={org.budget}, Score={org.score}")

    def simulation_summary(self):
        print(f"\n=== Simulation Completed ===")
        for org in self.organizations:
            print(f"{org.name}: Final Reputation={org.reputation}, Final Size={org.size}, Final Budget={org.budget}, Total Score={org.score}")
