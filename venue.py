class Venue:
    def __init__(self, name, popularity_level, time_slots):
        self.name = name
        self.popularity_level = popularity_level
        self.time_slots = {slot: [] for slot in time_slots}

    def is_available(self, slot, enable_mechanism=False):
        if enable_mechanism:
            return True
        else:
            return not self.time_slots[slot]

    def book(self, organization, slot, enable_mechanism=False):
        if self.is_available(slot, enable_mechanism):
            self.time_slots[slot].append(organization)
            return True
        else:
            print(f"Venue {self.name} is already booked for time slot {slot}.")
            return False

    def cancel_booking(self, slot):
        if slot in self.time_slots and self.time_slots[slot]:
            self.time_slots[slot] = []
            return True
        else:
            print(f"Venue {self.name} is not booked for this time slot {slot}")
            return False

    def get_available_time_slots(self, enable_mechanism=False):
        if enable_mechanism:
            return list(self.time_slots.keys())
        else:
            return [slot for slot, bookings in self.time_slots.items() if not bookings]

    def reset_venue_bookings(self):
        self.time_slots = {slot: [] for slot in self.time_slots}
