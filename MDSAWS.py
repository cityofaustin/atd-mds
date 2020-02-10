import json
import logging
import boto3


class MDSAWS:
    __slots__ = [
        "aws_default_region",
        "aws_access_key_id",
        "aws_secret_access_key",
        "bucket_name",
        "client",
        "json_document"
    ]

    def __init__(
            self,
            aws_default_region,
            aws_access_key_id,
            aws_secret_access_key,
            bucket_name
    ):
        """
        Initializes an AWS client that can save a json document on S3
        :param str aws_default_region:
        :param str aws_access_key_id:
        :param str aws_secret_access_key:
        :param str bucket_name: The name of the bucket
        """
        self.aws_default_region = aws_default_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.json_document = None
        self.client = None
        # Initialize Client and json document
        self.initialize_client()

    def initialize_client(self):
        """
        Initializes the s3 client
        :return:
        """
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    @staticmethod
    def is_json_valid(data):
        """
        Returns True if data is a valid json document, otherwise False.
        :param str data: The json string to evaluate
        :return bool:
        """
        try:
            json.loads(data)
            return True
        except:
            return False

    def set_json_document(self, json_document):
        """
        Sets the content of the json document to save on S3
        :param str json_document: A string containing the body of the document in plain text
        """
        self.json_document = json_document if self.is_json_valid(data=json_document) else None

    def save(self, file_path):
        """
        The directory and file name (s3 key) to be saved on S3
        :param str file_path: The path and file name desired to store in s3
        :return dict: The response from S3
        """
        return self.client.put_object(
            Bucket=self.bucket_name,
            Body=self.json_document,
            Key=file_path
        )

    def get_config(self):
        """
        Returns a dictionary with the aws client settings
        :return dict: The dictionary with the values in memory
        """
        return {
            "aws_default_region": self.aws_default_region,
            "aws_access_key_id": self.aws_access_key_id[:10],
            "aws_secret_access_key": self.aws_secret_access_key[:10],
            "bucket_name": self.bucket_name,
            "json_document": self.json_document
        }
