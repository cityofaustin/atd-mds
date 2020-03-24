import os
import boto3
import json

import logging
from MDSAWS import MDSAWS


class MDSConfig:
    __slots__ = [
        "ATD_MDS_REGION",
        "ATD_ETL_MDS_CONFIG",
        "ATD_MDS_ACCESS_KEY",
        "ATD_MDS_SECRET_ACCESS_KEY",
        "ATD_MDS_FERNET_KEY",
        "ATD_MDS_BUCKET",
        "ATD_MDS_STAGE",
        "ATD_MDS_MAX_THREADS",
        "ATD_MDS_PROVIDERS",
        "ATD_MDS_SETTINGS",
        "ATD_MDS_CENSUS_GEOJSON",
        "ATD_MDS_DISTRICTS_GEOJSON",
        "ATD_MDS_HEX_GEOJSON",
        "_MDS_SETTINGS",
        "_MDS_PROVIDERS",
        "_MDS_AWS",
    ]

    def __init__(self):
        logging.debug("MDSConfig::__init__() Initializing configuration")
        self.ATD_MDS_REGION = os.getenv("AWS_DEFALUT_REGION", None)
        self.ATD_MDS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", None)
        self.ATD_MDS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
        self.ATD_MDS_FERNET_KEY = os.getenv("ATD_MDS_FERNET_KEY", None)
        self.ATD_MDS_BUCKET = os.getenv("ATD_MDS_BUCKET", None)
        self.ATD_MDS_STAGE = os.getenv("ATD_MDS_RUN_MODE", "STAGING")
        self.ATD_MDS_MAX_THREADS = os.getenv("ATD_MDS_MAX_THREADS", 10)
        self.ATD_MDS_PROVIDERS = os.getenv(
            "ATD_MDS_PROVIDERS", f"config/providers_{self.ATD_MDS_STAGE.lower()}.json"
        )
        self.ATD_MDS_SETTINGS = os.getenv(
            "ATD_MDS_SETTINGS", f"config/settings_{self.ATD_MDS_STAGE.lower()}.json"
        )
        self.ATD_MDS_CENSUS_GEOJSON = os.getenv(
            "ATD_MDS_CENSUS_GEOJSON", "data/census_tracts_2010_simplified_20pct.json"
        )
        self.ATD_MDS_DISTRICTS_GEOJSON = os.getenv(
            "ATD_MDS_DISTRICTS_GEOJSON", "data/council_districts_simplified.json"
        )
        self.ATD_MDS_HEX_GEOJSON = os.getenv("ATD_MDS_HEX_GEOJSON", "data/hex1000.json")
        self._MDS_AWS = self._initialize_aws()
        # Internal
        self._MDS_PROVIDERS = self._load_json_file_s3(key=self.ATD_MDS_PROVIDERS)
        self._MDS_SETTINGS = self._load_json_file_s3(key=self.ATD_MDS_SETTINGS)

    def get_config(self) -> dict:
        """
        Returns a dictionary with the current settings.
        :return dict:
        """
        logging.debug("MDSConfig::print() printing configuration...")
        return {
            "ATD_MDS_REGION": self.ATD_MDS_REGION,
            "ATD_MDS_ACCESS_KEY": self.ATD_MDS_ACCESS_KEY,
            "ATD_MDS_SECRET_ACCESS_KEY": self.ATD_MDS_SECRET_ACCESS_KEY,
            "ATD_MDS_FERNET_KEY": self.ATD_MDS_FERNET_KEY,
            "ATD_MDS_BUCKET": self.ATD_MDS_BUCKET,
            "ATD_MDS_STAGE": self.ATD_MDS_STAGE,
            "ATD_MDS_PROVIDERS": self.ATD_MDS_PROVIDERS,
            "ATD_MDS_SETTINGS": self.ATD_MDS_SETTINGS,
            "_MDS_SETTINGS": self._MDS_SETTINGS,
            "_MDS_PROVIDERS": self._MDS_PROVIDERS,
        }

    def _initialize_aws(self) -> MDSAWS:
        """
        Initializes the MDS AWS Class
        :return MDSAWS:
        """
        return MDSAWS(
            bucket_name=self.ATD_MDS_BUCKET,
            aws_default_region=self.ATD_MDS_REGION,
            aws_access_key_id=self.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=self.ATD_MDS_SECRET_ACCESS_KEY,
            encryption_key=self.ATD_MDS_FERNET_KEY
        )

    @staticmethod
    def read_json(file_path):
        """
        Load JSON into a dictionary object
        :param str file_path:
        :return dict:
        """
        with open(file_path, "r") as fin:
            return json.loads(fin.read())

    def _load_json_file_s3(self, key) -> dict:
        """
        Downloads a file from S3 based on bucket and key parameters. It requires credentials.
        Returns a populated dict if successful, None if it fails, it may raise an exception
        if no bucket has been defined.
        :param str key: The path to the file in the S3 bucket
        :return dict:
        """
        logging.debug(f"MDSConfig::_load_json_file_s3() loading file from S3: '{key}'")
        if self._MDS_AWS is None:
            raise Exception(
                "MDSConfig::_load_json_file_s3() AWS client not initialized"
            )
        return self._MDS_AWS.load(file_path=key)

    def get_provider_config(self, provider_name) -> dict:
        """
        Returns a dictionary with the provider settings (as loaded from S3).
        :param str provider_name: The name of the provider
        :return dict:
        """
        provider_config = self._MDS_PROVIDERS.get(provider_name, None)
        if provider_config is None:
            raise Exception(
                f"MDSConfig::get_provider_config() Unable to find config for provider: provider_name='{provider_name}'"
            )
        else:
            return provider_config

    def get_root_data_path(self, provider_name) -> str:
        """
        Returns the data root path in the S3 bucket for a provider.
        :param str provider_name: The name of the provider
        :return str:
        """
        return f"{self.ATD_MDS_STAGE.lower()}/{provider_name.lower()}"

    def get_data_path(self, provider_name, date) -> str:
        """
        Returns the data path for a provider for a specific date.
        :param str provider_name: The name of the provider
        :param datetime date: A datetime object
        :return str:
        """
        root_path = self.get_root_data_path(provider_name=provider_name)
        date_time_format = f"{date.year}/{date.month}/{date.day}/{date.hour}/"
        return f"{root_path}/{date_time_format}"

    @staticmethod
    def get_file_name(file_name, date) -> str:
        """
        Returns the data path for a provider for a specific date.
        :param str file_name: The name of the file to be saved
        :param datetime date: A datetime object
        :return str:
        """
        return f"{date.year}-{date.month}-{date.day}-{date.hour}-{file_name}"

    def get_setting(self, setting, default) -> str:
        """
        Returns the MDS setting by name from the loaded configuration.
        :param str setting: The name of the setting
        :param * default: The default value you would want it to assume if not found.
        :return str:
        """
        return self._MDS_SETTINGS.get(setting, default)
