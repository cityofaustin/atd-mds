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

    def test_load_valid_json_t1(self):
        json_document = """
        {
            "glossary": {
                "title": "example glossary",
                "GlossDiv": {
                    "title": "S",
                    "GlossList": {
                        "GlossEntry": {
                            "ID": "SGML",
                            "SortAs": "SGML",
                            "GlossTerm": "Standard Generalized Markup Language",
                            "Acronym": "SGML",
                            "Abbrev": "ISO 8879:1986",
                            "GlossDef": {
                                "para": "A meta-markup language, used to create markup languages such as DocBook.",
                                "GlossSeeAlso": ["GML", "XML"]
                            },
                            "GlossSee": "markup"
                        }
                    }
                }
            }
        }
        """
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )

        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str)

    def test_load_valid_json_t2(self):
        json_document = "{}"
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str)

    def test_load_invalid_json_t1(self):
        json_document = """
            {
                "This is not a valid json object"
            }
        """
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str) is False

    def test_load_invalid_json_t2(self):
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        mds_aws.set_json_document(json_document=None)
        assert isinstance(mds_aws.json_document, str) is False

    def test_load_invalid_json_t3(self):
        json_document = {
            "valid": "dictionary",
            "but": "not string"
        }
        mds_aws = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY
        )
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str) is False
