import sys
import logging
from typing import List, Dict

class AzureOpenAIChat:
    """
    A class to interface with the Azure OpenAI Chat API.
    """
    def __init__(self, client, model_name: str, streaming_enabled: bool = True):
        self.client = client
        self.model_name = model_name
        self.streaming_enabled = streaming_enabled

    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> None:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                stream=self.streaming_enabled
            )
            self._process_response(response)
            return response  
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            raise

    def _process_response(self, response) -> None:
        if self.streaming_enabled:
            for chunk in response:
                if len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.role:
                        sys.stdout.write(delta.role + ": ")
                    if delta.content:
                        sys.stdout.write(delta.content)
                    sys.stdout.flush()
            print()
        else:
            pass
            # print(f"{response.choices[0].message.role}: {response.choices[0].message.content}")