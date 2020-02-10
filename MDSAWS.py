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
            bucket_name,
            **kwargs
    ):
        self.aws_default_region = aws_default_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.json_document = None
        self.client = None
        # Initialize Client and json document
        self.set_json_document(kwargs.get("json_document", None))
        self.initialize_client()

    def initialize_client(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def set_json_document(self, json_document):
        self.json_document = json.loads(json_document)
