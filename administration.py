import organization

class Administration:
    def __init__(self):
        pass

    def distribute_budget(self, organizations):
        for org in organizations:
            org.gain_budget()
