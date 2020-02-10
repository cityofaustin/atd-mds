# atd-mds

** UNDER CONSTRUCTION / WORK IN PROGRESS **

This is an ETL process for MDS providers, its purpose is to facilitate
the tracking and gathering of data, new or old.

## Getting Started

1. Create a virtual environment:
   
    ```
    virtualenv venv
    ```
    
2. Set up these environment variables in your shell terminal (with proper values):

    ```
    export ATD_MDS_BUCKET="the-mds-bucket-name";
    export AWS_DEFALUT_REGION="us-east-1"
    export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
    export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
    ``` 
3. Run tests:
    
   ```
   pytest -v
   ```

    The tests will indicate any problems you may have in the system,
    in terms of missing libraries or dependencies, etc.
  
  
## Configuration

First, it is recommended you take a look in the `MDSConfig.py` class.
As you will notice, the configuration is downloaded from protected
files in S3. This is to be able to run clusters of this etl process
in the cloud with minimal effort, all that is needed is a valid set
of AWS credentials with S3 permissions.

This architecture allows to run this ETL from anywhere at any scale
in an organized way.

## Organization

The ETL process currently consists of several modules:

1. `provider_extract.py` This file governs the data extraction. First,
it looks at a schedule table in the cloud, where it determines what
time frames it needs to download data for. Then proceeds to download
the data and store it in S3.

2. `provider_validate_data.py` This file makes sure the data is valid
for processing, it simply runs a series of checks and makes sure it is
ready for further processing into the database.

3. `provider_sync_db.py` This file reads the JSON document and inserts
the data into a postgres database, one item at the time. It reports for
any errors and provides a count of all records processed.

4. `provider_sync_socrata.py` This file takes the same JSON data and
transforms it into a socrata dataset and publishes it.

## Testing

The code is highly modular, this is simplify unit-testing patterns. You,
can [read more about these patterns in the tests folder](./tests).

## Modules (Python Classes)

As previously stated, the code is highly modular to simplify testing patters,
on top of that, there are other considerations in terms of the architecture
of this application.

Most code is put into modules that are as thoroughly tested as possible,
this can help with re-usability, especially for multi-stage complex processes.

All of the modules include a `__slots__` which helps speed up class
instantiation, which helps performance and makes testing smoother,
where the same class can be spun up hundreds of times.

The executable scripts include a `#!/usr/bin/env python` header and are given
executable permissions. These are not classes and utilize the Click library
to parse options & flags in the terminal, these do not include class types and
all of its implementation is done with functions.

## ETL Execution

The ETL only requires AWS credentials, it will gather the configuration
from S3. To run any specific script, you would follow this pattern:

```
$ ./provider_extract.py --time_min "yyyy-mm-dd-hh" --time_max "yyyy-mm-dd-hh" --provider "provider_name"
```

#### Parameters

`--provider` (Required, string) Tis is the name of the MDS provider in question (e.g., "bird", "lime", "jump", ...)

`--time-max` (Required, string) This parameter establishes the hour for which this ETL
is gathering data. It must be written in this format: `"yyyy-mm-dd-hh"` The year, month, day
and hour in military format (e.g., `"2020-01-01-23"`) The data output will not exceed (go past)
this date and time.

`--time-min` (Optional, string, default: Empty) When this parameter is provided, it overrides
the `--interval` flag. This parameter marks the beginning hour it needs to gather data for.
For example, if `--time-max` is set to `"2020-01-02-00"` and `--time-min` is set to
`"2020-01-01-00"`, the ETL will gather data for the entire day of January 1st. 

`--interval` (Optional, integer, default: 1) This is an optional parameter. It indicates the offset
in the past in hours from time_max. For example, if interval is set to `1` and time_max
is set to `2020-01-01-23` the ETL will gather data from 10pm to 11pm. If this was set to
`2` with the same time max value, the ETL would gather data from 9pm to 11pm. This flag
is ignored if the flag `--time-min` is provided.

# License
This project is provided under the GPL 3.0 license.
