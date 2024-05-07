import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle
import json
import requests

from keyvaultsecrets import initialize_secrets

class OpenAIEmbeddingsRetriever:
    def __init__(self, model_name, api_key):
        """
        Initializes the retriever with the specified OpenAI embeddings model.
        
        :param model_name: The name of the model to use for embeddings.
        :param api_key: The API key for the OpenAI API.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.api_base_url = "https://api.openai.com/v1/engines/" + self.model_name + "/completions"

    def get_embeddings(self, text):
        """
        Retrieves embeddings for the given text using the initialized model.
        
        :param text: The text to embed.
        :return: The embeddings for the given text.
        """
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "prompt": text,
            "max_tokens": 100
        }
        response = requests.post(self.api_base_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            return "Error: " + str(response.status_code)


class EmbeddingSimilaritySelector:
    def __init__(self, embeddings_file_path, original_strings_file_path, openai_retriever):
        """
        Initializes the selector by loading embeddings from a pickle file and reading the
        original strings from a text file. It uses an instance of OpenAIEmbeddingsRetriever
        for embedding generation.
        
        :param embeddings_file_path: Path to the pickle file containing embeddings.
        :param original_strings_file_path: Path to the file containing original strings.
        :param openai_retriever: An instance of OpenAIEmbeddingsRetriever for generating embeddings.
        """
        self.embeddings = self.load_from_file(embeddings_file_path)
        self.original_strings_file_path = original_strings_file_path
        self.openai_retriever = openai_retriever

    @staticmethod
    def load_from_file(file_path):
        """
        Loads embeddings from a pickle file.
        """
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"An error occurred while loading embeddings: {str(e)}")
            return None

    def encode_string(self, string):
        """
        Encodes a string into an embedding using the OpenAIEmbeddingsRetriever.
        
        :param string: The string to encode.
        :return: The embedding vector of the string.
        """
        embedding_json = self.openai_retriever.get_embeddings(string)
        # Assuming the returned JSON contains an embedding vector in a specific key.
        # You may need to adjust the parsing depending on the actual response structure.
        embedding_vector = json.loads(embedding_json)
        return np.array(embedding_vector)

    def get_top_matches(self, target_string, num_matches=10):
        """
        Finds and returns the top matching text strings to the target string based on cosine similarity.
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            print("No embeddings loaded.")
            return []

        target_embedding = self.encode_string(target_string).reshape(1, -1)
        similarities = cosine_similarity(target_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:num_matches]

        top_matches = []
        with open(self.original_strings_file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]

        for index in top_indices:
            if index < len(lines):
                top_matches.append(lines[index])

        return top_matches


