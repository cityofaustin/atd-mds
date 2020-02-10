#!/usr/bin/env python
import pytest


from parent_directory import *


from MDSConfig import MDSConfig
from MDSAWS import MDSAWS

mds_config = MDSConfig()

class TestMDSAWS:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSAWS")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSAWS")

    def test_constructor(self):
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        assert isinstance(mds_aws, MDSAWS)

    def test_get_config(self):
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        aws_config = mds_aws.get_config()
        print(aws_config)
        assert isinstance(aws_config, dict)
