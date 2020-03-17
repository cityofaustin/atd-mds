#!/usr/bin/env python
import pytest
import json

import botocore
from parent_directory import *


from MDSConfig import MDSConfig
from MDSAWS import MDSAWS

mds_config = MDSConfig()
sample_encryption_key = "8zHNiqyI2_1nkt2xHYbJGbEZew2zRDfO1Jgii01jM5g="

mds_aws = MDSAWS(
    bucket_name=mds_config.ATD_MDS_BUCKET,
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    encryption_key=sample_encryption_key,
)


class TestMDSAWS:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSAWS")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSAWS")
        mds_aws.delete_file(file_name="tests/json_save_test1.json")

    def test_constructor(self):
        mds_aws_test = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
        )
        assert isinstance(mds_aws_test, MDSAWS)

    def test_get_config(self):
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
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str)

    def test_load_valid_json_t2(self):
        json_document = "{}"
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str)

    def test_load_invalid_json_t1(self):
        json_document = """
            {
                "This is not a valid json object"
            }
        """
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str) is False

    def test_load_invalid_json_t2(self):
        mds_aws.set_json_document(json_document=None)
        assert isinstance(mds_aws.json_document, str) is False

    def test_load_invalid_json_t3(self):
        json_document = {"valid": "dictionary", "but": "not string"}
        mds_aws.set_json_document(json_document=json_document)
        assert isinstance(mds_aws.json_document, str) is False

    def test_client_initializer_success_t1(self):
        mds_aws_test = MDSAWS(
            bucket_name=mds_config.ATD_MDS_BUCKET,
            aws_default_region=mds_config.ATD_MDS_REGION,
            aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
            aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
        )
        assert mds_aws_test.client is not None

    def test_save_file_success_t1(self):
        file_path = "tests/json_save_test1.json"
        initial_file_content = """
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
        mds_aws.set_json_document(json_document=initial_file_content)
        mds_aws.save(file_path=file_path)
        file_content = mds_aws.load(file_path=file_path)
        assert str(json.loads(initial_file_content)) == str(file_content)

    def test_save_get_versions_success_t1(self):
        file_path = "tests/json_versions_test.json"
        initial_file_content_v1 = """
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
        initial_file_content_v2 = """
        {
            "glossary": {
                "title": "example glossary version 2",
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
        mds_aws.set_json_document(json_document=initial_file_content_v1)
        mds_aws.save(file_path=file_path)
        mds_aws.set_json_document(json_document=initial_file_content_v2)
        mds_aws.save(file_path=file_path)

        versions = mds_aws.get_all_versions(file_name=file_path)
        assert len(versions) == 2

    def test_delete_all_versions_success_t1(self):
        file_name = "tests/json_versions_test.json"
        versions = mds_aws.get_all_versions(file_name=file_name)
        mds_aws.delete_file(file_name=file_name)
        versions_two = mds_aws.get_all_versions(file_name=file_name)
        assert len(versions) == 2 and len(versions_two) == 0

    def test_cipher_suite_success_t1(self):
        assert mds_aws.cipher_suite is not None

    def test_is_encrypted_success_t1(self):
        test_string = "This is a plain-text string."
        encrypted_string = str(mds_aws.encrypt(test_string))
        encrypted = mds_aws.is_encrypted(encrypted_string)
        assert encrypted is True

    def test_is_encrypted_success_t2(self):
        test_string = "-$W[KF_c6u/Ye]Uc%2BfKBn[^!vL93."
        encrypted_string = str(mds_aws.encrypt(test_string))
        encrypted = mds_aws.is_encrypted(encrypted_string)
        assert encrypted is True

    def test_is_encrypted_success_t3(self):
        test_string = "nb8UK]n<V$iQ/]edB7YG2996^K8W94-@HW5EZsZA+%onDNe][9{*8jDf8UG_p#"
        encrypted_string = str(mds_aws.encrypt(test_string))
        encrypted = mds_aws.is_encrypted(encrypted_string)
        assert encrypted is True

    def test_is_encrypted_fail_t1(self):
        assert mds_aws.is_encrypted("This is a plain-text string.") is False

    def test_is_encrypted_fail_t2(self):
        assert mds_aws.is_encrypted("") is False

    def test_is_encrypted_fail_t3(self):
        assert mds_aws.is_encrypted(None) is False

    def test_decrypt_success_t1(self):
        test_string = "This is a plain-text string."
        encrypted_string = mds_aws.encrypt(test_string)
        decrypted = mds_aws.decrypt(encrypted_string)
        assert decrypted == test_string

    def test_decrypt_success_t2(self):
        test_string = "-$W[KF_c6u/Ye]Uc%2BfKBn[^!vL93."
        encrypted_string = mds_aws.encrypt(test_string)
        decrypted = mds_aws.decrypt(encrypted_string)
        assert decrypted == test_string

    def test_decrypt_success_t3(self):
        test_string = "nb8UK]n<V$iQ/]edB7YG2996^K8W94-@HW5EZsZA+%onDNe][9{*8jDf8UG_p#"
        encrypted_string = mds_aws.encrypt(test_string)
        decrypted = mds_aws.decrypt(encrypted_string)
        assert decrypted == test_string

    def test_save_encrypted_success_t1(self):
        file_path = "tests/json_save_test_encrypted.json"
        initial_file_content = """
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
        mds_aws.set_json_document(json_document=initial_file_content)
        mds_aws.save(file_path=file_path, encrypted=True)
        file_content_decrytpted = mds_aws.load(file_path=file_path)
        mds_aws.delete_file(file_name=file_path)
        assert json.dumps(json.loads(initial_file_content)) == (
            json.dumps(file_content_decrytpted)
        )
