from collections import defaultdict

class Venue:
    def __init__(self, name, size, price):
        self.name = name
        self.size = size
        self.price = price
        # Timeslots per day: morning, afternoon, evening
        self.timeslots = ['morning', 'afternoon', 'evening']
        # Availability per day: {day: {timeslot: None or Organization}}
        self.availability = defaultdict(lambda: {ts: None for ts in self.timeslots})

    def is_available(self, day, timeslot):
        return self.availability[day][timeslot] is None

    def book(self, day, timeslot, organization):
        if self.is_available(day, timeslot):
            self.availability[day][timeslot] = organization
            return True
        return False

    def cancel_booking(self, day, timeslot):
        self.availability[day][timeslot] = None
