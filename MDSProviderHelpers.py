from datetime import datetime
import json


class MDSProviderHelpers:
    @staticmethod
    def parse_timestamp(unix_timestamp):
        """
        Parses a unix epoch timestamp and returns a datetime object
        :param int unix_timestamp: The unix epoch timestamp
        :return datetime:
        """
        try:
            return datetime.fromtimestamp(int(unix_timestamp))
        except:
            return None

    @staticmethod
    def parse_custom_datetime(custom_date_time):
        """
        Parses a string in "yyyy-mm-dd-hh" format into a dict object for easy access.
        Returns None if the string fails to parse.
        :param str custom_date_time: The date time
        :return dict|None:
        """
        try:
            custom_date_components = custom_date_time.split("-")
            return {
                "year": int(custom_date_components[0]),
                "month": int(custom_date_components[1]),
                "day": int(custom_date_components[2]),
                "hour": int(custom_date_components[3]),
            }
        except:
            return None


    @staticmethod
    def parse_interval(interval):
        """
        Tries to parse a string into an int, returns None if it fails.
        :param str interval:
        :return int|None:
        """
        try:
            return int(interval)
        except:
            return None

    @staticmethod
    def load_file(file_name):
        """
        Loads a json file from disk and returns a dictionary, or None if it fails to parse
        :param str file_name: The physical location of the file
        :return dict|None:
        """
        if not isinstance(file_name, str):
            return None

        try:
            with open(file_name) as f:
                return json.load(f)
        except:
            return None