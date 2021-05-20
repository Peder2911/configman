from functools import lru_cache
from azure.appconfiguration import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from environs import Env,EnvError

def seek_config(resolvers=None):
    if resolvers is None:
        resolvers = list()
    def return_config(key):
        for res in resolvers:
            try:
                return res(key)
            except KeyError:
                continue
        raise KeyError
    return return_config

dict_resolver = lambda dictionary: lambda k: dictionary[k]

def azure_appconfig_resolver(connection_string):

    client = AzureAppConfigurationClient.from_connection_string(connection_string)

    def return_config(k):
        try:
            return client.get_configuration_setting(k).value
        except ResourceNotFoundError as rnfe:
            raise KeyError from rnfe

    return return_config

def azure_keyvault_secret_resolver(keyvault_url,credentials=None):

    if credentials is None:
        credentials = DefaultAzureCredential()

    client = SecretClient(keyvault_url,credentials)

    def return_config(k):
        fixed_key = k.replace("_","-").lower() # keyvault does not allow _
        try:
            return client.get_secret(fixed_key).value
        except ResourceNotFoundError as rnfe:
            raise KeyError from rnfe

    return return_config

def environs_resolver():

    env = Env()
    env.read_env()

    def return_config(k):
        try:
            return env(k)
        except EnvError as ee:
            raise KeyError from ee

    return return_config

def views_config(keyvault_url,credentials=None):
    environs = environs_resolver()
    secrets = azure_keyvault_secret_resolver(keyvault_url,credentials)
    appconfig = azure_appconfig_resolver(secrets("appconfig-connection-string"))
    return lru_cache(maxsize=None)(seek_config([environs,appconfig,secrets]))
