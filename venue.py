class Venue:
    def __init__(self, name, popularity_level):
        self.name = name
        self.booked_by = None
        self.date = None
        self.popularity_level = popularity_level
    
    def is_available(self):
        return self.booked_by is None
    
    def book(self, organization):
        self.booked_by = organization
        self.date = organization.date

    def cancel_booking(self):
        self.booked_by = None
        self.date = None
    
    #Try to add in some sort of scheduling logic so that organizations
    #can book venues by date and time as well and create more of a calendar to choose from

    

