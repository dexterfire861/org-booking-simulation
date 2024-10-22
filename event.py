class Event:
    def __init__(self, organization, venue, day, timeslot):
        self.organization = organization
        self.venue = venue
        self.day = day
        self.timeslot = timeslot
        self.attendance = 0
        self.new_students = 0
        self.utilization = 0.0