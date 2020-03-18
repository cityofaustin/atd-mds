import json
import logging
import boto3
from cryptography.fernet import Fernet


class MDSAWS:
    __slots__ = [
        "aws_default_region",
        "aws_access_key_id",
        "aws_secret_access_key",
        "cipher_suite",
        "bucket_name",
        "client",
        "json_document",
    ]

    def __init__(
        self,
        aws_default_region,
        aws_access_key_id,
        aws_secret_access_key,
        bucket_name,
        encryption_key=None,
        encryption_enabled=False,
    ):
        """
        Initializes an AWS client that can save a json document on S3
        :param str aws_default_region:
        :param str aws_access_key_id:
        :param str aws_secret_access_key:
        :param str bucket_name: The name of the bucket
        :param str encryption_key: Encryption Key (optional)
        :param bool encryption_enabled: If True, the files will be encrypted/decrypted. (optional)
        """
        self.aws_default_region = aws_default_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.json_document = None
        self.client = None
        # Initialize Encryption Client
        self.cipher_suite = (
            Fernet(encryption_key.encode()) if encryption_key is not None else None
        )
        # Initialize Client and json document
        self.initialize_client()

    def initialize_client(self):
        """
        Initializes the s3 client
        :return:
        """
        logging.debug(f"MDSAWS::initialize_client() Initializing AWS S3 Client")
        if self.bucket_name is None:
            raise Exception(
                "MDSAWS::initialize_client() Missing value for ATD_MDS_BUCKET environment variable"
            )
        if self.aws_access_key_id is None:
            raise Exception(
                "MDSAWS::initialize_client() Missing value for ATD_MDS_ACCESS_KEY environment variable"
            )
        if self.aws_secret_access_key is None:
            raise Exception(
                "MDSAWS::initialize_client() Missing value for ATD_MDS_SECRET_ACCESS_KEY environment variable"
            )

        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
        except:
            self.client = None

    @staticmethod
    def is_json_valid(data) -> bool:
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
        self.json_document = (
            json_document if self.is_json_valid(data=json_document) else None
        )

    def save(self, file_path, json_document=None, encrypted=False) -> dict:
        """
        The directory and file name (s3 key) to be saved on S3
        :param str file_path: The path and file name desired to store in s3
        :param str json_document: A shortcut in case you want to replace the current json_document
        :param bool encrypted: True if the json document needs to be encrypted before saving.
        :return dict: The response from S3
        """
        if json_document:
            self.json_document = json_document

        if self.client is None:
            raise Exception("MDSAWS::save() Client is not initialized")

        if encrypted:
            self.json_document = self.encrypt(self.json_document)

        return self.client.put_object(
            Bucket=self.bucket_name,
            Body=self.json_document,
            Key=file_path,
        )

    def load(self, file_path) -> dict:
        """
        Downloads a file from S3 based on bucket and key parameters. It requires credentials.
        Returns a populated dict if successful, None if it fails, it may raise an exception
        if no bucket has been defined.
        :param str file_path: The path to the file in the S3 bucket
        :return dict:
        """
        if self.client is None:
            raise Exception("MDSAWS::load() Client is not initialized")
        try:
            data = self.client.get_object(Bucket=self.bucket_name, Key=file_path)
            contents = data["Body"].read().decode()

            if self.is_encrypted(contents):
                contents = self.decrypt(contents)

            return json.loads(contents)
        except:
            return {}

    def get_config(self) -> dict:
        """
        Returns a dictionary with the aws client settings
        :return dict: The dictionary with the values in memory
        """
        return {
            "aws_default_region": self.aws_default_region,
            "aws_access_key_id": self.aws_access_key_id[:10],
            "aws_secret_access_key": self.aws_secret_access_key[:10],
            "bucket_name": self.bucket_name,
            "json_document": self.json_document,
        }

    def get_all_versions(self, file_name):
        response = self.client.list_object_versions(
            Bucket=self.bucket_name, Prefix=file_name,
        )

        try:
            return [id["VersionId"] for id in response["Versions"]]
        except:
            return []

    def delete_file(self, file_name):
        for version in self.get_all_versions(file_name=file_name):
            self.client.delete_object(
                Bucket=self.bucket_name, Key=file_name, VersionId=version
            )

    @staticmethod
    def is_encrypted(input_string) -> bool:
        """
        Returns True if the specified string is encrypted, False otherwise.
        :param str input_string: The string to be evaluated...
        :return bool:
        """
        try:
            return input_string[1:6] == "AAAAA"
        except:
            return False

    def encrypt(self, input_string) -> str:
        """
        Encrypts a string based on the provided key and input text.
        :param str string: The string to be encrypted.
        :return str:
        """

        try:
            return str(self.cipher_suite.encrypt(input_string.encode()).decode())
        except:
            return None

    def decrypt(self, input_string) -> str:
        """
        Decrypts a string and returns a plain decoded string.
        :param str input_string: The input string to be decrypted
        :return str:
        """
        try:
            return str(self.cipher_suite.decrypt(input_string.encode()).decode())
        except:
            return None
