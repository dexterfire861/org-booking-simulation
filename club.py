import event
import random


TIMESLOT_APPEAL = {
    'morning': 0.3,
    'afternoon': 0.5,
    'evening': 0.8
}

class Organization:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.reputation = 100  # Starts at 100
        self.score = 0
        self.planned_events = 0
        self.budget = self.calculate_initial_budget()
        self.events = []
        self.performance_history = []

    def calculate_initial_budget(self):
        # Example: Budget = size * 10 + reputation * 2
        return self.size * 10 + self.reputation * 2

    def gain_budget(self):
        # Example: Gain budget based on reputation and size
        self.budget += self.size * 5 + self.reputation

    def decide_strategy(self):
        # Decide to cooperate or overbook based on reputation and performance
        if self.reputation >= 70 and self.score >= 50:
            return 'cooperate'
        elif self.reputation < 50 and self.score >= 50:
            return 'overbook'
        elif self.reputation >= 70 and self.score < 50:
            return 'cooperate'
        else:
            return 'overbook'

    def book_events(self, available_venues, current_day, two_weeks_ahead):
        strategy = self.decide_strategy()
        events_booked = []
        for venue in available_venues:
            if self.budget < venue.price:
                continue  # Not enough budget
            # Choose a timeslot based on appeal
            timeslot = self.choose_timeslot(venue)
            if not venue.is_available(current_day, timeslot):
                continue  # Timeslot not available
            # Book the venue
            success = venue.book(current_day, timeslot, self)
            if success:
                evnt = event.Event(self, venue, current_day, timeslot)
                self.events.append(evnt)
                events_booked.append(evnt)
                self.budget -= venue.price
                self.planned_events += 1
                if strategy == 'overbook':
                    # Optionally book more venues
                    continue
        return events_booked

    def choose_timeslot(self, venue):
        # Prefer higher appeal timeslots
        times = list(TIMESLOT_APPEAL.keys())
        weights = [TIMESLOT_APPEAL[ts] for ts in times]
        return random.choices(times, weights=weights, k=1)[0]

    def evaluate_events(self, cancellation_rate):
        remaining_events = []
        for evnt in self.events:
            if random.random() < cancellation_rate or self.reputation < 50:
                # Cancel the event
                evnt.venue.cancel_booking(evnt.day, evnt.timeslot)
            else:
                remaining_events.append(evnt)
        self.events = remaining_events

    def update_reputation(self, utilization):
        if utilization >= 0.8:
            self.reputation += 2
        elif utilization < 0.5:
            self.reputation -= 3
        else:
            self.reputation += 0  # No change

    def calculate_score(self):
        # Example scoring: students + reputation + events handled
        self.score = self.size + self.reputation + self.planned_events
        self.performance_history.append(self.score)