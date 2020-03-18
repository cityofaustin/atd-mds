# ATD-MDS ETL Unit Tests

In this folder, we place all the unit tests written with pytest.
The aim of the tests is to provide a minimal guidance in terms of
the quality of the code.

The code for the ETL process needs to be modular in order to be
testable, this is the reason most of the code for the ETL process
has been written into different modules (classes) containing
functions that are independently tested.

The general architecture of this project is to write as much as
possible the code into classes, and each class will have its own
test file, and in turn, each test file will provide as many
tests for each function in the class.

The test files also follow a modular style, this is to help group
together all the tests for a specific class. This can help isolate
specific tests in case you only want to run a test for an individual
file.

This is the general pattern to follow:
 
```
├── tests
│   ├── README.md
│   ├── parent_directory.py
│   ├── sample.json
│   ├── test_mds_aws.py
│   ├── test_mds_config.py
│   ├── test_mds_graphql_requests.py
│   ├── test_mds_provider_helpers.py
│   └── test_mds_schedule.py
```

Within a test class:

```python
#!/usr/bin/env python
import pytest

from parent_directory import *

class TestClassExample:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSAWS")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSAWS")

```

The `parent_directory` module provides access to the root folder's
python code and classes.

# Running Tests

### Important: You will need to be on VPN to run tests, this is because the APIs (production or staging) only respond to traffic from CTM's network.
### Follow these steps in order:
1. Make sure you are on CTM's VPN network.
2. Be sure to export both environment variables:
    ```
    export ATD_MDS_BUCKET="the-bucket-name";
    export ATD_MDS_FERNET_KEY="abc123fernet_key="
    ```
    You can find the values in 1Password or in Airflow
3. Make sure you have the requirements by running `pip install -r requirements.txt`, after that you should be able to run:

### Once completed the above steps:
To run all tests with some verbosity:

```
pytest -v
```

For additional verbosity and logging:

```
pytest -v -s
```

To run a specific test (example):

```
pytest -v tests/test_mds_point_in_polygon.py
```

To run a specific test with additional verbosity:

```
pytest -vs tests/test_mds_point_in_polygon.py
```

Tests should be run from the parent directory,
though they can be run within the tests directory as well.

This is a sample output with minimal verbosity (`pytest -v`):

```
tests/test_mds_aws.py::TestMDSAWS::test_constructor PASSED                                                                                                            [  2%]
tests/test_mds_aws.py::TestMDSAWS::test_get_config PASSED                                                                                                             [  5%]
tests/test_mds_aws.py::TestMDSAWS::test_load_valid_json_t1 PASSED                                                                                                     [  7%]
tests/test_mds_aws.py::TestMDSAWS::test_load_valid_json_t2 PASSED                                                                                                     [ 10%]
tests/test_mds_aws.py::TestMDSAWS::test_load_invalid_json_t1 PASSED                                                                                                   [ 13%]
tests/test_mds_aws.py::TestMDSAWS::test_load_invalid_json_t2 PASSED                                                                                                   [ 15%]
tests/test_mds_aws.py::TestMDSAWS::test_load_invalid_json_t3 PASSED                                                                                                   [ 18%]
tests/test_mds_aws.py::TestMDSAWS::test_client_initializer_success_t1 PASSED                                                                                          [ 21%]
tests/test_mds_aws.py::TestMDSAWS::test_save_file_success_t1 PASSED                                                                                                   [ 23%]
tests/test_mds_config.py::TestMDSConfig::test_constructor PASSED                                                                                                      [ 26%]
tests/test_mds_config.py::TestMDSConfig::test_data_path PASSED                                                                                                        [ 28%]
tests/test_mds_config.py::TestMDSConfig::test_provider_config PASSED                                                                                                  [ 31%]
tests/test_mds_graphql_requests.py::TestMDSGraphQLRequests::test_constructor PASSED                                                                                   [ 34%]
tests/test_mds_graphql_requests.py::TestMDSGraphQLRequests::test_configuration_settings PASSED                                                                        [ 36%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_timestamp_bad_t1 PASSED                                                                        [ 39%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_timestamp_bad_t2 PASSED                                                                        [ 42%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_timestamp_good_t1 PASSED                                                                       [ 44%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_timestamp_good_t2 PASSED                                                                       [ 47%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_timestamp_good_t3 PASSED                                                                       [ 50%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_valid_custom_date_time_good_t1 PASSED                                                                [ 52%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_valid_custom_date_time_good_t2 PASSED                                                                [ 55%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_valid_custom_date_time_bad_t1 PASSED                                                                 [ 57%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_valid_custom_date_time_bad_t2 PASSED                                                                 [ 60%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_valid_custom_date_time_bad_t3 PASSED                                                                 [ 63%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_interval_bad_t1 PASSED                                                                         [ 65%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_interval_bad_t2 PASSED                                                                         [ 68%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_interval_good_t1 PASSED                                                                        [ 71%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_interval_good_t2 PASSED                                                                        [ 73%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_parse_interval_good_t3 PASSED                                                                        [ 76%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_load_file_good_t1 PASSED                                                                             [ 78%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_load_file_bad_t1 PASSED                                                                              [ 81%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_load_file_bad_t2 PASSED                                                                              [ 84%]
tests/test_mds_provider_helpers.py::TestMDSProviderHelpers::test_load_file_bad_t3 PASSED                                                                              [ 86%]
tests/test_mds_schedule.py::TestMDSSchedule::test_gql_catches_error PASSED                                                                                            [ 89%]
tests/test_mds_schedule.py::TestMDSSchedule::test_gql_parses_graphql PASSED                                                                                           [ 92%]
tests/test_mds_schedule.py::TestMDSSchedule::test_one_hour_schedule PASSED                                                                                            [ 94%]
tests/test_mds_schedule.py::TestMDSSchedule::test_no_time_min PASSED                                                                                                  [ 97%]
tests/test_mds_schedule.py::TestMDSSchedule::test_schedule_range PASSED                                                                                               [100%]

============================================================================ 38 passed in 2.45s =============================================================================
```
