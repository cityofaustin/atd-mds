#!/usr/bin/env python
"""
Provider Configuration
Author: Austin Transportation Department, Data & Technology Services
Description: The purpose of this tool is to facilitate the

The application requires the boto3 and atd-mds-client libraries:
    https://pypi.org/project/boto3/
    https://pypi.org/project/atd-mds-client/
"""

"""
Example uses:

    Download settings, or providers file:
        $ ./provider_configuration.py --file settings --download
        $ ./provider_configuration.py --file providers --download
    
    Download any other file specifically by name
        $ ./provider_configuration.py --file "path/to/file.json" --download
    
    Upload a file and encrypt it (default)
        $ ./provider_configuration.py 
            --file sample_file.json                # This is the name of the file locally
            --upload-path "test/sample_file.json"  # The name of the file remotely
            --upload
    
    Upload a file (in plain text)
        $ ./provider_configuration.py 
            --file sample_file.json                # This is the name of the file locally
            --upload-path "test/sample_file.json"  # The name of the file remotely
            --upload
            --plain-text  # Prevents encryption
    
"""

import click
import json
import pdb
import logging
import getpass
import ntpath


from MDSConfig import MDSConfig
from MDSAWS import MDSAWS


logging.disable(logging.DEBUG)

# Let's initialize our configuration class
mds_config = MDSConfig()

# Then we need to initialize our AWS class with our configuration
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    encryption_key=mds_config.ATD_MDS_FERNET_KEY,
    bucket_name=mds_config.ATD_MDS_BUCKET,
)


@click.command()
@click.option(
    "--production",
    is_flag=True,
    help="Signals this is the production configuration.",
)
@click.option(
    "--upload",
    is_flag=True,
    help="Upload action",
)
@click.option(
    "--download",
    is_flag=True,
    help="Download action",
)
@click.option(
    "--file",
    default=None,
    help="The file to upload or download. Shortcuts: 'providers' or 'settings'",
)
@click.option(
    "--plain-text",
    is_flag=True,
    help="The file will be uploaded in plain text",
)
@click.option(
    "--upload-path",
    default="",
    help="Enter PDB pdb mode",
)
@click.option(
    "--pdb",
    is_flag=True,
    help="Enter PDB pdb mode",
)
def run(**kwargs):
    """
    The script will download or upload a configuration file from S3
    :param dict kwargs: The values specified by click decorators.
    :return:
    """
    # The file being downloaded
    file = kwargs.get("file", None)
    download = kwargs.get("download", False)
    upload = kwargs.get("upload", False)
    upload_path = kwargs.get("upload_path", "")
    production = kwargs.get("production", False)
    pdb_mode = kwargs.get("pdb", False)
    plain_text = kwargs.get("plain_text", False)

    if production:
        mds_config.ATD_MDS_STAGE = "PRODUCTION"
    else:
        mds_config.ATD_MDS_STAGE = "STAGING"

    if mds_config.ATD_MDS_FERNET_KEY is None:
        print("A fernet key will need to be provided, check your password vault and paste it here.")
        mds_config.ATD_MDS_FERNET_KEY = getpass.getpass(
            prompt=f"Enter fernet key for '{mds_config.ATD_MDS_STAGE}': "
        )

    # First check if the file is complete
    if str(file).lower() in ["providers", "settings"]:
        file_to_load = (mds_config.ATD_MDS_PROVIDERS, mds_config.ATD_MDS_SETTINGS)[file=="settings"]
    else:
        file_to_load = file

    # Now time to exit, or pdb.
    if pdb_mode:
        print("\n\n\n--------------------------------------------")
        print("You are now in PDB mode, try a line like this: ")
        print("(pdb) mds_aws.load(file_to_load)")
        print("--------------------------------------------\n\n\n")
        pdb.set_trace()

    if download:
        print(f"Downloading file from S3: {file_to_load}")
        json_object = mds_aws.load(file_to_load)
        download_path = f"./{ntpath.basename(file_to_load)}"
        with open(download_path, "w") as json_file_pointer:
            json.dump(json_object, json_file_pointer)
        print(f"File downloaded to: {download_path}")

    if upload:
        print(f"Uploading file from S3: {file_to_load}")
        with open(file_to_load, "r") as json_file_pointer:
            data = json.load(json_file_pointer)
        pdb.set_trace()
        mds_aws.save(
            upload_path,
            json_document=json.dumps(data),
            encrypted=(True, False)[plain_text]
        )
        print(f"Done saving file to '{upload_path}'")


if __name__ == "__main__":
    run()
