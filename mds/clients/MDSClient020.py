

class MDSClient020:

    version = "0.2.0"

    def __init__(self, config):
        self.config = config

    def __request(self, **kwargs):
        return kwargs["hello"]

    def get_trips(self, start_time, end_time):
        print("Getting trips: %s %s " % (start_time, end_time))
        print("request.get")
        return self.version
