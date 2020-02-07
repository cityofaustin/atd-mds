from datetime import datetime
import json


def parse_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp)


def load_file(file_name):
    try:
        with open(file_name) as f:
            return json.load(f)
    except:
        return None


def parse_datetime(date_time):
    date_components = date_time.split("-")
    try:
        return {
            "year": int(date_components[0]),
            "month": int(date_components[1]),
            "day": int(date_components[2]),
            "hour": int(date_components[3]),
        }
    except:
        return None


def parse_interval(interval):
    try:
        return int(interval)
    except:
        return None