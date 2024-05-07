import pandas as pd
from io import StringIO
import os, openai, logging
from src.file_operations import read_file, get_full_path
from src.config import load_config, Config
from src.chat import AzureOpenAIChat
from src.parsing import extract_content, convert_string_to_list, extract_matching_rows_v2, find_matching_joins
from src.retrieval_handler import EmbeddingSimilaritySelector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MetadataExtractor:
    def __init__(self, config_path):
        try:
            self.config = load_config(os.path.join(os.path.dirname(__file__), config_path))
            self.configure_openai_api = Config()
            self.client_turbo = openai.AzureOpenAI(
                azure_endpoint=self.configure_openai_api.base_url,
                api_key=self.configure_openai_api.api_key,
                api_version=self.configure_openai_api.turbo_version
            )
            self.chatbot_turbo = AzureOpenAIChat(self.client_turbo, self.configure_openai_api.turbo_name, streaming_enabled=False)
            self.client_35 = openai.AzureOpenAI(
                azure_endpoint=self.configure_openai_api.base_url,
                api_key=self.configure_openai_api.api_key,
                api_version=self.configure_openai_api.gpt35_version
            )
            self.chatbot_35 = AzureOpenAIChat(self.client_35, self.configure_openai_api.gpt35_name, streaming_enabled=False)

            self.selector = EmbeddingSimilaritySelector(embeddings_file_path='./src/embeddings/descriptions_embeddings.pkl',
                                                original_strings_file_path='./src/metadata_strings/descriptions.txt')

            logging.info("MetadataExtractor initialized successfully.")
        except Exception as e:
            logging.error("Error initializing MetadataExtractor: %s", e)
            raise

    def extract_metadata(self, user_input):
        try:
            if not isinstance(user_input, str):
                raise ValueError("User input must be a string.")
            logging.info("Starting metadata extraction.")

            logging.info("Loading configurations and templates.")
            groupchat_extraction = self.config['groupchat_extraction']
            extract_prompt = read_file(get_full_path(groupchat_extraction['RefinerSystem']))
            sql_metadata = read_file(get_full_path(groupchat_extraction['SQLMetadata']))
            join_metadata = read_file(get_full_path(groupchat_extraction['SQLAssistantSystem']))
            coder_system = read_file(get_full_path(groupchat_extraction['CoderSystem']))
            initial_prompt = read_file(get_full_path(groupchat_extraction['initial_input']))

            metadata_strings = self.config['metadata_strings']
            string_samples = read_file(get_full_path(metadata_strings['string_samples']))
            join_samples = read_file(metadata_strings['join_samples'])

            if any(file is None for file in [extract_prompt, sql_metadata, join_metadata, coder_system, initial_prompt, string_samples, join_samples]):
                raise ValueError("One or more required files could not be read.")
            
            top_matches = self.selector.get_top_matches(user_input, num_matches=10)
            flattened_matches = "\n".join(top_matches)

            extraction = extract_prompt.format(USER_INPUT=user_input, METADATA=sql_metadata, JOIN_METADATA=join_metadata, FLATTENED_MATCHES=flattened_matches)
            metadata_extraction_messages = [{"role": "user", "content": extraction}]
            logging.info("Generating extraction response.")
            extraction_response_text = self.chatbot_turbo.generate_response(metadata_extraction_messages, temperature=0.1)
            extraction_response_text = extraction_response_text.choices[0].message.content


            if extraction_response_text is None:
                raise ValueError("Received no response from OpenAI Chatbot.")

            initial_prompt = initial_prompt.format(USER_INPUT=user_input, RESPONSE_TEXT=extraction_response_text)
            cleaning_prep_messages = [
                {"role": "system", "content": coder_system},
                {'role': 'user', 'content': initial_prompt}
            ]
            logging.info("Generating Clean Prep Messages.")
            response = self.chatbot_35.generate_response(cleaning_prep_messages, temperature=0.1)
            parsed_string = extract_content(response.choices[0].message.content)
            cleaned_string = parsed_string.split('=', 1)[1].strip().replace('\\', '') #testing
            schema_tables_columns_list = convert_string_to_list(cleaned_string)

            logging.info("Processing cleaning and preparation messages.")
            data_io = StringIO(string_samples)
            df_string_samples = pd.read_csv(data_io, sep='\t')

            if df_string_samples.empty:
                raise ValueError("String samples DataFrame is empty.")

            last_column = df_string_samples.iloc[:, -1]
            columns_to_add = pd.concat([last_column] * 4, axis=1)
            columns_to_add.columns = [f"SOME_POSSIBLE_VALUES_{i}" for i in range(1, 5)]
            df_string_samples = pd.concat([df_string_samples, columns_to_add], axis=1)

            logging.info("Extracting and transforming data.")
            string_metadata = extract_matching_rows_v2(df_string_samples, schema_tables_columns_list)
            lines = [line.strip() for line in join_samples.strip().split('\n') if line]
            df = pd.DataFrame(lines, columns=['join_query'])
            pd.set_option('display.max_colwidth', None)
            matching_joins_df = find_matching_joins(df, schema_tables_columns_list)
            
            logging.info("Metadata extraction completed successfully.")
            return { 
                'user_input': user_input,
                'extraction_response_text': extraction_response_text,
                'string_metadata': string_metadata,
                'matching_joins_df': matching_joins_df.to_json(orient='split')
            }
        except Exception as e:
            logging.error("Error during metadata extraction: %s", e)
            raise