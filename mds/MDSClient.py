"""

"""
from .clients import *
from .MDSAuth import MDSAuth


class MDSClient:
    __slots__ = (
        "config",
        "authenticated",
        "mds_headers",
        "auth_headers",
        "version",
        "provider",
        "custom_client",
        "auth_client",
        "mds_client",
        "custom_authentication",
    )

    def __init__(self, config={}, custom_authentication=None, **kwargs):
        """
        Constructor for this class
        :param dict config: A dictionary of properties.
        :param function custom_authentication: A python function to use for authentication
        :param dic kwargs: Any additional parameters passed to subclasses

        Parameters:
            :param str version: The version of the mds library to be loaded.
            :param dict config: The configuration to be passed to the
            :param str provider: The provider name or UUID
        """
        # Merge config and kwargs into a single dictionary
        self.config = {**config, **kwargs}

        # Try to find in the config the MDS version we are working with
        self.provider = self.config.get("provider", None)
        # Tries to find version in the config, or assumes 0.2.0
        self.version = self.config.get("version", "0.2.0")
        # Try to find the default_class (an MDS class override) or assume None
        self.custom_client = self.config.get("custom_client", None)

        # Assume the headers to be empty
        self.mds_headers = None
        self.auth_headers = None
        # Assume authenticated is False
        self.authenticated = False

        # Try to find a custom authentication function, assume None
        self.custom_authentication = custom_authentication

        # Initialize authentication client
        self.auth_client = MDSAuth(
            config=self.config, custom_function=self.custom_authentication
        )

        # Initialize MDS Client
        self.mds_client = self.load_mds_client(
            version=self.version, custom=self.custom_client,
        )(config=self.config)

        self._authenticate()

    @staticmethod
    def load_mds_client(version, custom=None):
        """
        Returns the class reference to be initialized later.
        :param str version: The version of MDS to initialize
        :param object custom: MDS Class override option
        :return object: The MDS class to be used
        """
        # Check for class override
        if custom is not None:
            return custom
        # Proceed with normal version check & load class
        else:
            return {
                "0.2.0": MDSClient020,
                "0.3.0": MDSClient030,
                "0.4.0": MDSClient040,
            }.get(version, custom)

    def get_trips(self, start_time, end_time):
        """
        Returns the trips for the current client
        :param start_time:
        :param end_time:
        :return:
        """
        print(f"MDSClient::get_trips() Getting trips for start_time: {start_time}, end_time: {end_time} ")
        return self.mds_client.get_trips(
            start_time=start_time, end_time=end_time
        )

    def show_config(self):
        """
        Prints the current version & configuration of the client
        :return:
        """
        print(f"MDSClient::show_config() Current MDS version loaded: {self.mds_client.version}")
        print(self.mds_client.config)

    def _authenticate(self):
        """
        It authenticates the client using the provided configuration
        :return:
        """
        print("MDSClient::authenticate() Generating headers...")
        self.auth_headers = self.auth_client.authenticate()
        print("MDSClient::authenticate() Checking headers...")
        if self.auth_headers:
            print("MDSClient::authenticate() Authentication succeeded...")
            self.authenticated = True

            self.mds_client.set_header(
                "Accept", f"application/vnd.mds.provider+json;version={self.version[:3]}"
            )
            self.mds_client.render_settings(headers=self.auth_headers)

            print("MDSClient::authenticate() Final headers: ")
            print(self.mds_client.get_headers())

        else:
            print("MDSClient::authenticate() Authentication failed")
