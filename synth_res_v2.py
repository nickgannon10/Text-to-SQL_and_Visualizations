import pandas as pd
import openai, os, logging
import json
from uuid import uuid4

from src.file_operations import read_file
from src.config import Config, load_config
from src.chat import AzureOpenAIChat
from src.parsing import extract_sql_query, format_metadata_to_markdown_improved, parse_column_names
from src.csv_utils import get_csv_string
from src.database import get_database
from src.tiktoken_tools import num_tokens_from_string, clip_tokens
from src.redis_cache import Cache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SynthesizeResponse2:
    def __init__(self, config_path, user_input, extraction_response_text, string_metadata, matching_joins_df):
        logging.info("Initializing SynthesizeResponse class")
        try:
            self.config = load_config(os.path.join(os.path.dirname(__file__), config_path))
            self.user_input = user_input
            self.extraction_response_text = extraction_response_text
            self.string_metadata = string_metadata
            self.matching_joins_df = matching_joins_df
            self.configure_openai_api = Config()
            self.session_id = str(uuid4())
            self.client = openai.AzureOpenAI(
                azure_endpoint=self.configure_openai_api.base_url,
                api_key=self.configure_openai_api.api_key,
                api_version=self.configure_openai_api.turbo_version
            )
            self.chatbot_turbo = AzureOpenAIChat(self.client, self.configure_openai_api.turbo_name, streaming_enabled=False)
            self.client_35 = openai.AzureOpenAI(
                azure_endpoint=self.configure_openai_api.base_url,
                api_key=self.configure_openai_api.api_key,
                api_version=self.configure_openai_api.gpt35_version
            )
            self.chatbot_35 = AzureOpenAIChat(self.client_35, self.configure_openai_api.gpt35_name, streaming_enabled=False)
            self.csv_string = ""
            self.azure_sql_db = get_database("hrdd")
            logging.info("SynthesizeResponse class initialization successful")
        except Exception as e:
            logging.error("Error during initialization: %s", e)
            raise

    def run_synthesis_process(self):
        logging.info("Starting synthesis process")
        tutorial_instructions = read_file(self.config['autogen_query']['Instructions'])
        query_initial_prompt = read_file(self.config['autogen_query']['InputMessage'])
        iterative_output = read_file(self.config['autogen_query']['IterativeOutput'])

        try: 
            tutorial_instructions_input = tutorial_instructions.format(
                USER_INPUT=self.user_input, 
                EXTRACTION_RESPONSE_TEXT=self.extraction_response_text, 
                STRING_METADATA=self.string_metadata, 
                MATCHING_JOINS_DF=self.matching_joins_df,
                FAILED_QUERY="", 
                ERROR_MESSAGE=""
            )

            tutorial_instructions_messages = [{'role': 'user', 'content': tutorial_instructions_input}]
            tutorial_response_text = self.chatbot_35.generate_response(tutorial_instructions_messages, temperature=0)
            tutorial_response_text = tutorial_response_text.choices[0].message.content

            query_initial_prompt_input = query_initial_prompt.format(
                USER_INPUT=self.user_input,
                EXTRACTION_RESPONSE_TEXT=self.extraction_response_text, 
                STRING_METADATA=self.string_metadata, 
                SUGGESTIONS_RESPONSE_TEXT=tutorial_response_text
            )

            query_generation_messages = [{'role': 'user', 'content': query_initial_prompt_input}]

            query_generation_response_text = self.chatbot_turbo.generate_response(query_generation_messages, temperature=0)
            query_generation_response_text = query_generation_response_text.choices[0].message.content

            sql = extract_sql_query(query_generation_response_text)
            logging.info(f"SQL Query: {sql}")

            result_df, error = self.azure_sql_db.execute_query(sql)

            self.csv_string, pandas_df = get_csv_string(result_df)

            csv_token_count = num_tokens_from_string(self.csv_string, "cl100k_base")
            if csv_token_count > 7500:
                self.csv_string = clip_tokens(self.csv_string, "cl100k_base", 7500)
                    # If there are results and no error, proceed to cache the values
            try:
                if not result_df.empty and error is None:
                    # Cache the user input and SQL query
                    cache_key = f"session:{self.session_id}"
                    session_data = {
                        "user_input": self.user_input,
                        "sql_query": sql
                    }
                    Cache().set(cache_key, json.dumps(session_data))
                    logging.info("Stored user_input and sql_query in Redis cache.")
            except Exception as cache_error:
                logging.warning(f"Failed to add user_input and sql_query to Redis cache: {cache_error}")

            if result_df.empty:
                logging.info(f"metadata: {self.string_metadata}")
                logging.info("###########################################################")
                cleaned_string = format_metadata_to_markdown_improved(self.string_metadata)
                cleaned_up_string = parse_column_names(cleaned_string)
                output = iterative_output.format(
                    CLEANED_STRINGS=cleaned_up_string
                )

                completions_content = ""
                logging.info("run_synthesis_process successfully processed. Preparing to return output.")
                return output, pandas_df, self.csv_string, completions_content
            
            else: 
                synthesis_chain = self.config['chain_3']

                synthesis_prompt_template = read_file(synthesis_chain['PromptTemplate'])
                synthesis_input = synthesis_prompt_template.format(
                    USER_INPUT=self.user_input, 
                    CSV_STRING=self.csv_string
                )

                synthesis_messages = [{'role': 'user', 'content': synthesis_input}]
                synthesis_response_text = self.chatbot_35.generate_response(synthesis_messages, temperature=0)

                synth_format = read_file(self.config['autogen_query']['SynthFormat'])

                completions_content = synth_format.format(
                    SYNTH_RES=synthesis_response_text.choices[0].message.content
                )
                logging.info(f"synthesis_response_text type: {type(synthesis_response_text)}")
                logging.info(f"synthesis_response_text: {synthesis_response_text}")

                return synthesis_response_text, pandas_df, self.csv_string, completions_content #,sql  

        except Exception as e:
            print(f"General Synthesize Response failed: {str(e)}") 






