

class MDSClient030:

    version = "0.3.0"

    def __init__(self, config):
        self.config = config


    def get_trips(self, start_time, end_time):
        print("Getting trips: %s %s " % (start_time, end_time))
        return self.version
