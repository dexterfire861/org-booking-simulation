import random
from organization import Organization
from venue import Venue

class Simulation:
    def __init__(self, num_orgs, num_venues, num_periods, cancellation_rate):
        self.organizations = [Organization(f"Org{i}") for i in range(num_orgs)]
        self.venues = [Venue(f"Venue{i}") for i in range(num_venues)]
        self.num_periods = num_periods
        self.cancellation_rate = cancellation_rate
        self.reserve_venues = []


    def run(self):
        for period in range(self.num_periods):
            self.reset_venues()
            self.process_bookings(period)
            self.university_cancellations()
            self.allocate_reserve_venues(period)
            self.score_organizations(period)
            self.update_reputations()
            self.update_strategies()
    
    def reset_venues(self):
        for venue in self.venues:
            venue.booked_by = None
            venue.date = None
    
    def process_bookings(self, date):
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            available_venues = [v for v in self.venues if v not in self.reserve_venues and v.booked_by is None]
            #print(available_venues)
            if not available_venues:
                break
            booked_venues = org.book_venue(available_venues, date)
            for venue in booked_venues:
                if venue.booked_by is None:
                    venue.booked_by = org
                    venue.date = date
    
    def university_cancellations(self):
        for venue in self.venues:
            if venue.booked_by and random.random() < self.cancellation_rate:
                venue.booked_by = None
                venue.date = None

    def allocate_reserve_venues(self, date):
        for org in sorted(self.organizations, key=lambda x: x.reputation, reverse=True):
            if not any(v.booked_by == org for v in self.venues):
                for venue in self.reserve_venues:
                    if venue.booked_by is None:
                        venue.booked_by = org
                        venue.date = date
                        break

    def score_organizations(self, date):
        for org in self.organizations:
            successful_bookings = sum(1 for v in self.venues if v.booked_by == org and v.date == date)
            unused_bookings = sum(1 for v in self.venues if v.booked_by == org and v.date != date)
            org.score += successful_bookings - unused_bookings * 0.5  # Penalty for unused bookings

    def update_reputations(self):
        avg_score = sum(org.score for org in self.organizations) / len(self.organizations)
        for org in self.organizations:
            reputation_change = org.score - avg_score
            org.reputation = max(0, min(200, org.reputation + reputation_change))

    def update_strategies(self):
        avg_score = sum(org.score for org in self.organizations) / len(self.organizations)
        for org in self.organizations:
            org.update_strategy(avg_score)

    
    def print_results(self):
        for org in sorted(self.organizations, key=lambda x: x.score, reverse=True):
            print(f"{org.name}: Strategy: {org.strategy}, Score: {org.score}, Reputation: {org.reputation}")