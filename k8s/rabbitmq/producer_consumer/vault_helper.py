import requests
import os
from dotenv import load_dotenv

class VaultHelper:
    def __init__(self):
        load_dotenv('./.env')
        self.__vault_addr = os.getenv('VAULT_ADDR')
        print(self.__vault_addr)
        self.__token = self.__get_client_token()

    def __get_client_token(self):
        resp = requests.post(
            url=f"{self.__vault_addr}/v1/auth/approle/login",
            json={
                "role_id": os.getenv("VAULT_ROLE_ID"),
                "secret_id": os.getenv("VAULT_SECRET_ID"),
            }
        )

        json_data = resp.json()
        return json_data["auth"]["client_token"]
    
    def __get_secrets(self, secret_path):
        resp = requests.get(
            url=f"{self.__vault_addr}/v1/secrets/data/{secret_path}",
            headers={
                'X-Vault-Token': self.__token
            }
        )

        json_data = resp.json()
        data = json_data['data']['data']
        print(data)
        return data
    
    def get_rabbitmq_credentials(self):
        return self.__get_secrets("rabbitmq")
    
    def get_api_key(self, alias):
        api_data = self.__get_secrets("apikeys")
        return api_data[alias]
    

vault_helper = VaultHelper()