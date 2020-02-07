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
