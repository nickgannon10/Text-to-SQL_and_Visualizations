import os
import pickle
from sentence_transformers import SentenceTransformer

class BERTEncoder:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2", device="cpu"):
        """
        Initializes the BERTEncoder with a specified model and device.

        :param model_name: The model to use for encoding.
        :param device: The device to run the model on ('cpu' or 'cuda').
        """
        self.model = SentenceTransformer(model_name, device=device)
    
    def read_and_encode(self, file_path):
        """
        Reads lines from a file and encodes each line using the BERT model.

        :param file_path: Path to the file containing the descriptions to encode.
        :return: A list of embeddings, one for each line in the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines and strip whitespace
            
        # Encode the lines using the BERT model
        embeddings = self.model.encode(lines)
        return embeddings

    @staticmethod
    def save_embeddings_to_file(file_path, embeddings):
        """
        Saves embeddings to a file using pickle.

        :param file_path: The file path where embeddings should be saved.
        :param embeddings: The embeddings to save.
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                pickle.dump(embeddings, f)
            print(f"Embeddings successfully saved to {file_path}")
        except Exception as e:
            print(f"An error occurred while saving embeddings: {str(e)}")

# Usage example
if __name__ == "__main__":
    encoder = BERTEncoder()  # Initialize the encoder with the default model
    file_path = './src/metadata_strings/descriptions.txt'
    embeddings = encoder.read_and_encode(file_path)
    
    # Specify the path for the pickle file to save embeddings
    pickle_file_path = './src/embeddings/descriptions_embeddings.pkl'
    BERTEncoder.save_embeddings_to_file(pickle_file_path, embeddings)

