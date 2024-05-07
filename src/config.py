import json
import os  
import logging

def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

class Config:
    """
    Configuration class to manage environment variables.
    """
    def __init__(self):
        self.validate_env_variables()

    def validate_env_variables(self):
        pass

    def _get_env_variable(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable {var_name} not found")
        return value
    
    def autogen_load_environment_variables(self):
        self.env_vars = [{
            'model': self.turbo_name, 
            'api_key': self.api_key,
            'base_url': self.base_url,
            'api_type': "azure",        
            'api_version': "2023-12-01-preview",
        }]

        return self.env_vars
