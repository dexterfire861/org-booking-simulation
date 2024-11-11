from organization import Organization
from venue import Venue
import random
import time
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.cm as cm
import numpy as np

class Simulation:
    def __init__(self, num_orgs, num_venues, num_periods, cancellation_rate, enable_mechanism=True):
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

        self.enable_mechanism = enable_mechanism  #for the venue sharing mechanism that is toggled for comparison


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
            org.book_venues(self.venues, enable_mechanism=self.enable_mechanism)
                

    def university_cancellations(self):
        print("University is cancelling bookings based on cancellation rate")
        for venue in self.venues:
            for slot in venue.time_slots:
                if venue.time_slots[slot] and random.random() < self.cancellation_rate:
                    venue.cancel_booking(slot)
                    print(f"University has cancelled booking for venue {venue.name} at time slot {slot}.")

    #give the organizations that have not booked a venue a reserve venue so they can still host events
    def allocate_reserve_venues(self):
        print("Allocating reserve venues to organizations...")
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            for time_slot in org.schedule:
                booked = any(org in venue.time_slots.get(time_slot, []) for venue in self.venues + self.reserve_venues)
                if not booked:
                    for reserve_venue in self.reserve_venues:
                        if reserve_venue.is_available(time_slot):
                            reserve_venue.book(org, time_slot)
                            print(f"{org.name} has been allocated reserve venue {reserve_venue.name} for time slot {time_slot}.")
                            break
    
    def apply_mechanism(self):
        if self.enable_mechanism:
            for org in self.organizations:
                for time_slot in org.schedule:
                    # Check if the organization already has a booking for this time slot
                    has_booking = any(
                        org in venue.time_slots.get(time_slot, []) for venue in self.venues + self.reserve_venues
                    )
                    if has_booking:
                        continue  # Skip, already has a booking for this time slot

                    # If not, try to book an available venue
                    available_venues = [v for v in self.venues if v.is_available(time_slot, enable_mechanism=True)]
                    if available_venues:
                        chosen_venue = random.choice(available_venues)
                        chosen_venue.book(org, time_slot, enable_mechanism=True)
                        print(f"{org.name} shared venue {chosen_venue.name} for time slot {time_slot} under the mechanism.")



    def check_nash_equilibrium(self):
        print("Checking for Nash Equilibrium...")
        equilibrium = True
        for org in self.organizations:
            original_strategy = org.strategy
            original_score = org.score
            # Hypothetical switch
            org.strategy = "overbook" if original_strategy == "normal" else "normal"
            org.score = 0  # Reset score for hypothetical scenario
            self.reset_venues()
            org.book_venues(self.venues, enable_mechanism=self.enable_mechanism)
            hypothetical_score = org.score
            # Compare scores
            if hypothetical_score > original_score:
                equilibrium = False
                print(f"{org.name} has an incentive to deviate from {original_strategy}.")
            # Revert changes
            org.strategy = original_strategy
            org.score = original_score
        if equilibrium:
            print("Nash Equilibrium found: No organization has an incentive to deviate.")
        else:
            print("Current profile is not a Nash Equilibrium.")

    def score_organizations(self):
        print("Scoring organizations...")

        for org in self.organizations:
            bookings_per_time_slot = {}
            for venue in self.venues + self.reserve_venues:
                for slot, booked_orgs in venue.time_slots.items():
                    if org in booked_orgs:
                        if slot in bookings_per_time_slot:
                            bookings_per_time_slot[slot].append(venue)
                        else:
                            bookings_per_time_slot[slot] = [venue]

            unused_bookings = 0
            successful_bookings = []

            for slot in org.schedule:
                if slot in bookings_per_time_slot:
                    venues_booked = bookings_per_time_slot[slot]
                    # Choose one venue as the utilized booking (e.g., the one with highest popularity)
                    utilized_venue = max(venues_booked, key=lambda v: v.popularity_level)
                    successful_bookings.append((utilized_venue, slot))
                    # The rest are unused overbooked venues
                    unused_overbooked = len(venues_booked) - 1
                    unused_bookings += unused_overbooked
                else:
                    # No booking made for this scheduled event
                    unused_bookings += 1

            # Increment total counts
            org.total_unused_bookings += unused_bookings
            org.total_successful_bookings += len(successful_bookings)

            org.update_penalty(unused_bookings)
            payoff = org.calculate_payoff(successful_bookings, unused_bookings)
            org.current_round_score = payoff

            org.score += payoff

            revenue = sum(v.popularity_level * 5 for v, _ in successful_bookings)
            org.budget += revenue

            org.round_scores.append((org.strategy, payoff))  # Store strategy and payoff for this round

            self.score_history[org.name].append(org.score)
            print(f"{org.name}: Successful bookings = {len(successful_bookings)}, Unused bookings = {unused_bookings}")
            print(f"Payoff: {payoff}, Updated score: {org.score}, Reputation: {org.reputation:.2f}")


    def get_average_score(self):
        return sum(org.current_round_score for org in self.organizations) / len(self.organizations)
    

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
            self.strategy_history[org.name].append(org.strategy)  # Track strategy each round
            org.update_strategy(avg_score)
            print(f"Organization {org.name} has a strategy of {org.strategy} after the round")

    def run(self):
        for period in range(self.num_periods):

            #Added in time.sleep to actually be able to track what is going on as the simulation is running

            print(f"\n==== Round {period + 1} ====")
            print("Organizations are either overbooking or booking regularly based on their strategy")


            self.generate_schedules()


            self.reset_venues()

            #process the bookings for the current period
            self.organization_bookings()

            #cancel the bookings for the current period
            self.university_cancellations()

            #allocate reserve venues to organizations that have not booked a venue
            self.allocate_reserve_venues()

            self.apply_mechanism()

            #score the organizations based on their bookings
            self.score_organizations()

            #update the reputations and strategies of the organizations
            self.update_reputations()

            self.update_strategies()

            self.check_nash_equilibrium()
    
    def print_results(self):
        print("\nSimulation Results:")
        print("-------------------")
        for org in sorted(self.organizations, key=lambda x: x.score, reverse=True):
            successful_bookings = org.total_successful_bookings
            unused_bookings = org.total_unused_bookings

            print(f"{org.name}:")
            print(f"  Strategy: {org.strategy}")
            print(f"  Score: {org.score:.2f}")
            print(f"  Reputation: {org.reputation:.2f}")
            print(f"  Successful Bookings: {successful_bookings}")
            print(f"  Unused Bookings: {unused_bookings}")
        print("\nStrategy Performance:")

    def plot_results(self):

        print("\nPlotting Results...")

        rounds = range(1, self.num_periods + 1)
        org_names = [org.name for org in self.organizations]
        num_orgs = len(org_names)
        colors = cm.get_cmap('tab10', num_orgs)  # Get a color map with enough colors

        # Define markers for strategies
        strategy_markers = {"normal": "o", "overbook": "s"}  # Circle for normal, square for overbook

        plt.figure(figsize=(12, 6))

        for idx, org in enumerate(self.organizations):
            scores = self.score_history[org.name]
            strategies = self.strategy_history[org.name]
            color = colors(idx)
            marker_style = [strategy_markers[strat] for strat in strategies]

            # Plot the score over rounds with markers indicating strategy
            for i in range(len(scores)):
                plt.plot(rounds[i], scores[i], marker=marker_style[i], color=color, markersize=8, linestyle='-')
                if i > 0:
                    plt.plot(rounds[i-1:i+1], scores[i-1:i+1], color=color, linestyle='-')

        # Create custom legend entries for organizations
        org_legend = [Line2D([0], [0], color=colors(idx), lw=2, label=org.name) for idx, org in enumerate(self.organizations)]

        # Create custom legend entries for strategies
        strategy_legend = [Line2D([0], [0], marker=marker, color='w', label=label,
                                markerfacecolor='black', markersize=8) for label, marker in strategy_markers.items()]

        plt.title("Organization Scores Over Time with Strategies")
        plt.xlabel("Round")
        plt.ylabel("Score")
        plt.legend(handles=org_legend + strategy_legend, loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.show()


    
    def compare_strategy_performance(self):
        normal_scores = []
        overbook_scores = []

        for org in self.organizations:
            for (strategy, score) in org.round_scores:
                if strategy == 'normal':
                    normal_scores.append(score)
                elif strategy == 'overbook':
                    overbook_scores.append(score)

        avg_normal_score = sum(normal_scores) / len(normal_scores) if normal_scores else 0
        avg_overbook_score = sum(overbook_scores) / len(overbook_scores) if overbook_scores else 0

        print(f"Average score for normal booking: {avg_normal_score:.2f}")
        print(f"Average score for overbooking: {avg_overbook_score:.2f}")

        plt.bar(['Normal Booking', 'Overbooking'], [avg_normal_score, avg_overbook_score])
        plt.title("Comparison of Average Scores by Strategy")
        plt.ylabel("Average Score")
        plt.show()

    def analyze_comparison(self, results_without, results_with):
        print("\nComparing Results:")
        avg_score_without = sum(results_without['scores'].values()) / len(self.organizations)
        avg_score_with = sum(results_with['scores'].values()) / len(self.organizations)

        print(f"Average Score without Mechanism: {avg_score_without:.2f}")
        print(f"Average Score with Mechanism: {avg_score_with:.2f}")

        # Compare total successful bookings
        total_bookings_without = sum(results_without['successful_bookings'].values())
        total_bookings_with = sum(results_with['successful_bookings'].values())

        print(f"Total Successful Bookings without Mechanism: {total_bookings_without}")
        print(f"Total Successful Bookings with Mechanism: {total_bookings_with}")

        total_unused_without = sum(results_without['unused_bookings'].values())
        total_unused_with = sum(results_with['unused_bookings'].values())

        print(f"Total Unused Bookings without Mechanism: {total_unused_without}")
        print(f"Total Unused Bookings with Mechanism: {total_unused_with}")

        # Additional analyses can be added here, such as comparing Gini coefficients
        gini_without = self.calculate_gini_coefficient_from_scores(list(results_without['scores'].values()))
        gini_with = self.calculate_gini_coefficient_from_scores(list(results_with['scores'].values()))

        print(f"Gini Coefficient without Mechanism: {gini_without:.2f}")
        print(f"Gini Coefficient with Mechanism: {gini_with:.2f}")


    def analyze_strategy_impact(self):
        print("\nAnalyzing Strategy Impact:")
        for org in self.organizations:
            scores = self.score_history[org.name]
            strategies = self.strategy_history[org.name]
            strategy_changes = 0
            for i in range(1, len(strategies)):
                if strategies[i] != strategies[i - 1]:
                    strategy_changes += 1

            total_overbook_score = sum([scores[i] - scores[i - 1] for i in range(1, len(scores)) if strategies[i] == 'overbook'])
            total_normal_score = sum([scores[i] - scores[i - 1] for i in range(1, len(scores)) if strategies[i] == 'normal'])

            print(f"{org.name}:")
            print(f"  Strategy Changes: {strategy_changes}")
            print(f"  Total Score Gain during Overbooking: {total_overbook_score}")
            print(f"  Total Score Gain during Normal Booking: {total_normal_score}")


    def track_strategy_changes(self):
        strategy_changes = {org.name: 0 for org in self.organizations}

        for org in self.organizations:
            for i in range(1, len(self.strategy_history[org.name])):
                if self.strategy_history[org.name][i] != self.strategy_history[org.name][i - 1]:
                    strategy_changes[org.name] += 1

        print("Strategy changes over time:")
        for org_name, changes in strategy_changes.items():
            print(f"{org_name}: {changes} changes")

    

    def calculate_gini_coefficient_from_scores(self, scores_list):
        scores = np.array(sorted(scores_list))
        if np.all(scores == 0):
            return 0.0  # All scores are zero, indicating perfect equality
        else:
            n = len(scores)
            sum_scores = np.sum(scores)
            index = np.arange(1, n + 1)  # Indices from 1 to n
            # Apply the simplified Gini coefficient formula
            gini = (2 * np.sum(index * scores)) / (n * sum_scores) - (n + 1) / n
            return gini

    
    def run_simulations(self):
        # Run simulation without mechanism
        print("\nRunning simulation without venue sharing mechanism...")
        self.enable_mechanism = False
        self.reset_simulation()
        self.run()
        results_without_mechanism = self.collect_results()
        self.print_results()
        self.plot_results()
        self.compare_strategy_performance()
        self.analyze_strategy_impact()
        self.print_results()



        # Run simulation with mechanism
        print("\nRunning simulation with venue sharing mechanism...")
        self.enable_mechanism = True
        self.reset_simulation()
        self.run()
        results_with_mechanism = self.collect_results()
        self.print_results()
        self.plot_results()
        self.compare_strategy_performance()
        self.analyze_strategy_impact()

        # Analyze and compare the results
        self.analyze_comparison(results_without_mechanism, results_with_mechanism)

    def reset_simulation(self):
        # Reset organizations
        for org in self.organizations:
            org.score = 0
            org.current_round_score = 0
            org.reputation = 100
            org.budget = 200
            org.penalty_cost = 1
            org.round_scores = []
            org.total_successful_bookings = 0
            org.total_unused_bookings = 0
            self.score_history[org.name] = []
            self.strategy_history[org.name] = []
            

        # Reset venues
        self.reset_venues()
        self.generate_schedules()

    def collect_results(self):
        # Collect results after simulation run
        results = {
            'scores': {org.name: org.score for org in self.organizations},
            'reputations': {org.name: org.reputation for org in self.organizations},
            'strategies': {org.name: self.strategy_history[org.name] for org in self.organizations},
            'successful_bookings': {org.name: org.total_successful_bookings for org in self.organizations},
            'unused_bookings': {org.name: org.total_unused_bookings for org in self.organizations}
        }
        return results


