import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class KeyVaultSecrets:
    def __init__(self, vault_url):
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def get_secret(self, secret_name):
        secret = self.secret_client.get_secret(secret_name)
        return secret.value

    def set_environment_variables(self, secrets):
        for secret_name, secret_value in secrets.items():
            os.environ[secret_name] = secret_value

import os
import logging
from dotenv import load_dotenv

load_dotenv()
kv_name = os.getenv("KEY_VAULT_NAME")

kv_vault_url = f"<{kv_name} >"

kv = KeyVaultSecrets(
    vault_url=kv_vault_url
)

def initialize_secrets():

    logging.info("Acquiring replay secrets")
    # Fetch the secrets
    secrets = {
        'AZURE_Resouces': kv.get_secret('AZURE-Resource'),
        # continues ...
    }

    # Set the fetched secrets as environment variables
    kv.set_environment_variables(secrets)
