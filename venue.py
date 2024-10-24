class Venue:
    def __init__(self, name, popularity_level, time_slots):
        self.name = name
        self.popularity_level = popularity_level
        self.time_slots = {slot: None for slot in (time_slots)}
    
    def is_available(self, slot):
        if self.time_slots[slot] is None:
            return True
        else:
            return False
         
    
    def book(self, organization, slot):
        if self.is_available(slot):
            self.time_slots[slot] = organization
            return True
        else:
            print("Venue is already booked for this time slot")
            return False

    def cancel_booking(self, slot):
        if slot in self.time_slots:
            self.time_slots[slot] = None
            return True
        else:
            print("Venue is not booked for this time slot")
            return False
    
    def get_available_time_slots(self):
        list_of_available_slots = []
        for slot, org in self.time_slots.items():
            if org is None:
                list_of_available_slots.append(slot)
            
        
        return list_of_available_slots
    
    def reset_venue_bookings(self):
        self.time_slots = {slot: None for slot in self.time_slots}
