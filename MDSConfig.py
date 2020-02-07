import os
import boto3
import json

import logging

class MDSConfig:
    __slots__ = [
        "ATD_MDS_REGION",
        "ATD_ETL_MDS_CONFIG",
        "ATD_MDS_ACCESS_KEY",
        "ATD_MDS_SECRET_ACCESS_KEY",
        "ATD_MDS_BUCKET",
        "ATD_MDS_STAGE",
        "ATD_MDS_PROVIDERS",
        "ATD_MDS_SETTINGS",
        "_MDS_SETTINGS",
        "_MDS_PROVIDERS",
    ]

    def __init__(self):
        logging.debug("MDSConfig::__init__() Initializing configuration")
        self.ATD_MDS_REGION = os.getenv("AWS_DEFALUT_REGION", None)
        self.ATD_MDS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", None)
        self.ATD_MDS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
        self.ATD_MDS_BUCKET = os.getenv("ATD_MDS_BUCKET", None)
        self.ATD_MDS_STAGE = os.getenv("ATD_MDS_RUN_MODE", "STAGING")
        self.ATD_MDS_PROVIDERS = os.getenv("ATD_MDS_PROVIDERS", "config/providers.json")
        self.ATD_MDS_SETTINGS = os.getenv("ATD_MDS_PROVIDERS", f"config/settings_{self.ATD_MDS_STAGE.lower()}.json")
        # Internal
        self._MDS_PROVIDERS = self._load_json_file_s3(key=self.ATD_MDS_PROVIDERS)
        self._MDS_SETTINGS = self._load_json_file_s3(key=self.ATD_MDS_SETTINGS)

    def show_config(self):
        logging.debug("MDSConfig::print() printing configuration...")
        print(
            json.dumps(
                {
                    "ATD_MDS_REGION": self.ATD_MDS_REGION,
                    "ATD_MDS_ACCESS_KEY": self.ATD_MDS_ACCESS_KEY,
                    "ATD_MDS_SECRET_ACCESS_KEY": self.ATD_MDS_SECRET_ACCESS_KEY,
                    "ATD_MDS_BUCKET": self.ATD_MDS_BUCKET,
                    "ATD_MDS_STAGE": self.ATD_MDS_STAGE,
                    "ATD_MDS_PROVIDERS": self.ATD_MDS_PROVIDERS,
                    "ATD_MDS_SETTINGS": self.ATD_MDS_SETTINGS,
                    "_MDS_SETTINGS": self._MDS_SETTINGS,
                    "_MDS_PROVIDERS": self._MDS_PROVIDERS,
                }
            )
        )

    def _load_json_file_s3(self, key):
        """
        Downloads a file from S3 based on bucket and key parameters. It requires credentials.
        Returns a populated dict if successful, None if it fails, it may raise an exception
        if no bucket has been defined.
        :param str key: The path to the file in the S3 bucket
        :return: dict
        """
        logging.debug(f"MDSConfig::_load_json_file_s3() loading file from S3: '{key}'")
        if self.ATD_MDS_BUCKET is None:
            raise Exception(
                "MDSConfig::_load_json_file_s3() Missing value for ATD_MDS_BUCKET environment variable"
            )
        if self.ATD_MDS_ACCESS_KEY is None:
            raise Exception(
                "MDSConfig::_load_json_file_s3() Missing value for ATD_MDS_ACCESS_KEY environment variable"
            )
        if self.ATD_MDS_SECRET_ACCESS_KEY is None:
            raise Exception(
                "MDSConfig::_load_json_file_s3() Missing value for ATD_MDS_SECRET_ACCESS_KEY environment variable"
            )

        client = boto3.client(
            "s3",
            aws_access_key_id=self.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=self.ATD_MDS_SECRET_ACCESS_KEY,
        )
        data = client.get_object(Bucket=self.ATD_MDS_BUCKET, Key=key)
        contents = data["Body"].read()
        return json.loads(contents)
