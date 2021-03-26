
from collections import namedtuple
import unittest
import re
from unittest.mock import patch
from fitin import dict_resolver,views_config

ReturnedValue = namedtuple("returned_value",("value"))

class MockConfigClient():
    mock_remote_config = {"app":"config"}

    @classmethod
    def from_connection_string(cls,con_str):
        assert con_str == "pleaselogmein"
        return cls()

    def get_configuration_setting(self,key):
        return ReturnedValue(value=self.mock_remote_config[key])

class MockSecretClient():
    mock_remote_secrets = {
            "super-secret":"secret",
            "appconfig-connection-string":"pleaselogmein"
        }
    def __init__(self,url,creds):
        assert creds is True
        assert re.search(r"https://[a-z\-]+.vault.azure.net",url) is not None
    def get_secret(self,k):
        return ReturnedValue(value=self.mock_remote_secrets[k])

class TestFitin(unittest.TestCase):
    def test_dict_resolver(self):
        resolver = dict_resolver({"foo":"bar"})
        self.assertEqual(resolver("foo"),"bar")

    @patch("fitin.fitin.AzureAppConfigurationClient",MockConfigClient)
    @patch("fitin.fitin.SecretClient",MockSecretClient)
    @patch("fitin.fitin.DefaultAzureCredential",lambda: True)
    def test_views_config(self):
        try:
            views_config("https://mykeyvault.vault.azure.net")
        except Exception as e:
            self.fail(str(e))
