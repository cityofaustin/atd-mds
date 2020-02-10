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
