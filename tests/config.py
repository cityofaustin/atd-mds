#!/usr/bin/env python

from parent_directory import *

# Our basic libraries
import json
from datetime import datetime

# Our custom Library
from mds import *

# Our test subject
from MDSConfig import MDSConfig

print("Testing...")

MDS_CONFIG = MDSConfig()

# Build timezone aware interval
logging.debug("Build time-zone aware interval")
tz_time = MDSTimeZone(
    date_time_now=datetime(2020, 1, 1, 17),
    offset=3600,  # One hour
    time_zone="US/Central",  # US/Central
)

data_path = MDS_CONFIG.get_data_path(provider_name="bird", date=tz_time.get_time_end())

print("Printing provider config: ")
veoride_config = MDS_CONFIG.get_provider_config("veoride")
print(json.dumps(veoride_config))

print("Data Path: " + data_path)
