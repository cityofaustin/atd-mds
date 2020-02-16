from datetime import datetime
from MDSProviderHelpers import MDSProviderHelpers


class TestMDSProviderHelpers:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSProviderHelpers")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSProviderHelpers")

    #
    # Testing parse_timestamp
    #
    def test_parse_timestamp_bad_t1(self):
        ts = MDSProviderHelpers.parse_timestamp({"not": "an int"})
        assert isinstance(ts, datetime) is False

    def test_parse_timestamp_bad_t2(self):
        ts = MDSProviderHelpers.parse_timestamp("Not a parsable numeric string")
        assert isinstance(ts, datetime) is False

    def test_parse_timestamp_good_t1(self):
        ts = MDSProviderHelpers.parse_timestamp(0)
        assert isinstance(ts, datetime)

    def test_parse_timestamp_good_t2(self):
        ts = MDSProviderHelpers.parse_timestamp("0")
        assert isinstance(ts, datetime)

    def test_parse_timestamp_good_t3(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.parse_timestamp(2.9)
        assert isinstance(ts, datetime)

    #
    # Testing parse_custom_datetime
    #
    @staticmethod
    def is_valid_custom_date_time(custom_dt):
        if not isinstance(custom_dt, dict):
            return False

        if (
            "year" not in custom_dt
            or "month" not in custom_dt
            or "day" not in custom_dt
            or "hour" not in custom_dt
        ):
            return False

        return True

    def test_valid_custom_date_time_good_t1(self):
        cdt = MDSProviderHelpers.parse_custom_datetime("2020-1-1-20")
        assert self.is_valid_custom_date_time(cdt)

    def test_valid_custom_date_time_good_t2(self):
        cdt = MDSProviderHelpers.parse_custom_datetime("9999-99-99-99")
        assert self.is_valid_custom_date_time(cdt)

    def test_valid_custom_date_time_bad_t1(self):
        cdt = MDSProviderHelpers.parse_custom_datetime(0)
        assert self.is_valid_custom_date_time(cdt) is False

    def test_valid_custom_date_time_bad_t2(self):
        cdt = MDSProviderHelpers.parse_custom_datetime({"not": "close"})
        assert self.is_valid_custom_date_time(cdt) is False

    def test_valid_custom_date_time_bad_t3(self):
        cdt = MDSProviderHelpers.parse_custom_datetime("2020*10*10*10")
        assert self.is_valid_custom_date_time(cdt) is False

    #
    # Test parse_interval
    #
    def test_parse_interval_bad_t1(self):
        ts = MDSProviderHelpers.parse_interval({"not": "an int"})
        assert isinstance(ts, int) is False

    def test_parse_interval_bad_t2(self):
        ts = MDSProviderHelpers.parse_interval("Not a parsable numeric string")
        assert isinstance(ts, int) is False

    def test_parse_interval_good_t1(self):
        ts = MDSProviderHelpers.parse_interval(0)
        assert isinstance(ts, int)

    def test_parse_interval_good_t2(self):
        ts = MDSProviderHelpers.parse_interval("0")
        assert isinstance(ts, int)

    def test_parse_interval_good_t3(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.parse_interval(2.9)
        assert isinstance(ts, int)

    #
    # Test load_file
    #

    def test_load_file_good_t1(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.load_file("./tests/sample.json")
        assert isinstance(ts, dict)

    def test_load_file_bad_t1(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.load_file("./sample.json")
        assert isinstance(ts, dict) is False

    def test_load_file_bad_t2(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.load_file(0)
        assert isinstance(ts, dict) is False

    def test_load_file_bad_t3(self):
        # Floating point values are ok, but they are truncated
        ts = MDSProviderHelpers.load_file({"json": "document"})
        assert isinstance(ts, dict) is False
