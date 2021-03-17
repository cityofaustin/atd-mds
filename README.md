# atd-mds

This is an ETL process for MDS providers, its purpose is to facilitate
the gathering and tracking of MDS data, new or past. This ETL application
consists of several tools that control different stages of the ETL process.
The application is then bundled and published with Docker, and it is run
with Airflow. 

## Getting Started

1. Install binary dependencies:
    You will need to install `libspatialindex`,  follow this link to learn more
    on how to install it on your computer. For a mac, all you need to do
    is to run brew:
    
    ```
    $ brew install spatialindex
    ```

2. Create a virtual environment & run pip:
   
    ```
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```
    
3. For local development, set up these environment variables in your shell terminal (with proper values):

    ```
    $ export AWS_DEFALUT_REGION="us-east-1"
    $ export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
    $ export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
    $ export ATD_MDS_FERNET_KEY="the-mds-fernet-key"
    $ export ATD_MDS_BUCKET="the-mds-bucket-name";
    ``` 
    
    Both the bucket name and the fernet key are present in the password vault.
     
4. Run tests:
    
   ```
   $ pytest -v
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

The files are encrypted, and you will not be able to read them without
the encryption keys. But once provided the keys, you can 

There is a tool called `./provider_configuration.py` which can help you
load and save configuration files, the encryption and decryption is handled automatically
if the fernet keys are provided.


## Organization

The ETL process currently consists of several modules:

1. `provider_extract.py` This file governs the data extraction. First,
it looks at a schedule table in the cloud, where it determines what
time frames it needs to download data for. Then proceeds to download
the data and store it in S3.

2. `provider_sync_db.py` This file reads the JSON document and inserts
the data into a postgres database, one item at the time. It reports for
any errors and provides a count of all records processed.

3. `provider_sync_socrata.py` This file takes the same JSON data and
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

`--force` Both extraction and sync_db allow forcing the process. Sometimes a schedule block
has already run, and the tools will not allow you to run it again. This flag ensures the
block process is executed again and re-updates the block status in the database.

# ETL Flow:

![ETL Process.png](https://images.zenhubusercontent.com/5b7edad7290aac725aec290c/8c61b94f-c3e9-40ac-96d0-a2940925066a)

# ETL Run Tool

There is an included script called `./process_runtool.py`, and its purpose is to run all three ETL
stages in order for a schedule block. The parameters it needs are the same as the other scripts.

This is an example on how to run this tool:

### Run within Python
Run for a single hour block:
```
./provider_runtool.py --provider "super_scooters" --time-min "2020-03-01-01" --interval 1 --dry-run
```

Running a range of dates:
```
./provider_runtool.py --provider "super_scooters" --time-min "2020-03-01-01" --time-max "2020-04-01-00" --dry-run
```

The script above will gather all schedule blocks for the entire month of March, and execute all three ETL stages in order.

### Run using Docker:

```
./provider_runtool.py --docker-mode --env-file ~/path/to/your/file.env --provider "jump" --time-min "2020-03-01-01" --time-max "2020-3-18-20" --dry-run
```

This will require that you create a .env file compatible with docker and that you provide the path to the file.
You can run either a range (as shown above, or use the interval header).

### Available flags:

`--dry-run` This flag makes the run tool only "print" the commands it is going to run. It is a great tool to learn
how to use this script and not make changes to the database.

`--force` When present, this flag will run all three ETL processes in `force` mode.

`--incomplete-only` This flag indicates the run tool to only look for incomplete schedule blocks.

`--no-logs` This flag indicates the run tool to skip the output of logs  

`--docker-mode` When present, this flag indicates the tool to run the scripts with Docker.

`--env-file [file path]` When running on docker, this file provides all the environment variables the container needs to run.

`--no-sync-db` When present, it indicates the run tool to skip syncing the data to the postgres database.

`--no-sync-socrata` When present, it indicates the tool to skip syncing the data to socrata.

`--no-extract` When present, this flag indicates the tool to skip the ETL first step of extraction. The other processes will assume the data is there, or fail otherwise.

`--time-max` The maximum end date for a schedule block.

`--time-min` The minimum end date for a schedule block.

`--interval [integer]` The interval in hours. This flag indicates the number of hours the script needs to go back and retrieve from `--time-max`

# Airflow

When running in Airflow, make sure the image is present
in the authorized image list: https://github.com/cityofaustin/atd-airflow/blob/master/docker-images.json

Wherever Airflow is running, be sure that those images are present, alternatively make sure
they are being built and deployed to the Docker Hub.

# License
This project is provided under the GPL 3.0 license.
