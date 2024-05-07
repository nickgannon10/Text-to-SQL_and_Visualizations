import azure.functions as func
import json, os, logging
from met_ex import MetadataExtractor
from vis_gen import VisualizationGenerator
from synth_res_v2 import SynthesizeResponse2
from src.parsing import contains_visualization_flag
from src.config import Config
from src.response_handler import handle_response, handle_response_string, handle_response_with_image, handle_response_image_error
import pandas as pd

def check_environment():
    if 'FUNCTIONS_WORKER_RUNTIME' in os.environ:
        azure_env = True
        print('azure env true')
    else:
        azure_env = False
        print('azure env false')

    return azure_env

app = func.FunctionApp()

@app.route(route="hrdd_trends")
def hrdd_trends(req: func.HttpRequest) -> func.HttpResponse:
    configure_openai_api = Config()
    logging.info('Python HTTP trigger function processed a request.')

    try:
        try:
            req_body = req.get_json()

            messages = req_body.get("messages")
            if not messages:
                return func.HttpResponse("Missing 'messages' in JSON", status_code=400)

            last_message = messages[-1]
            content = last_message.get("Content")  # Capitalized 'Content'
            if not content:
                return func.HttpResponse("Missing 'Content' in last message", status_code=400)

            user_input = content[0].get("Value")  # Capitalized 'Value'
            if not user_input:
                return func.HttpResponse("Missing 'Value' in Content", status_code=400)

        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)
        except KeyError as e:
            return func.HttpResponse(f"KeyError: {str(e)}", status_code=400)

        is_azure_env = check_environment()

        if contains_visualization_flag(user_input): 
            try:
                if 'messages' in req_body and len(req_body['messages']) >= 2 and req_body['messages'][-2]:
                    if 'Content' in req_body['messages'][-2] and req_body['messages'][-2]['Content']:
                        raw_data = req_body['messages'][-2]['Content'][0].get('RawData')
                        if raw_data is not None:
                            data = json.loads(raw_data)
                            pandas_df_json = data.get("pandas_df")
                            if pandas_df_json:
                                pandas_df = pd.read_json(pandas_df_json)
                                csv_string = data.get("csv_string")
                                user_input = data.get("user_input")
                                logging.info("Data retrieval and processing successful.")
                            else:
                                logging.error("'pandas_df_json' is missing in the data.")
                        else:
                            logging.warning("'RawData' is None in the second-to-last message.")
                    else:
                        logging.error("'Content' is missing in the second-to-last message.")
                else:
                    logging.warning("Not enough messages or 'messages' key is missing.")

                vis_gen = VisualizationGenerator("config.json", pandas_df, csv_string, user_input)
                encoded_image, iterative_output = vis_gen.generate_visualization()
                if encoded_image not in ['error_state_placeholder', 'default_placeholder_or_error_message']:
                    logging.info(f"ENCODED IMAGE: {encoded_image}")
                    response = handle_response_with_image(encoded_image)
                    logging.info(f" RESPONSE: {response}")
                    return func.HttpResponse(response)
                else:
                    response = handle_response_image_error(iterative_output, pandas_df, csv_string, user_input)
                    return func.HttpResponse(response)

            except Exception as e:
                logging.error("Failed to run VisualizationGenerator: %s", e)
                return func.HttpResponse("Error in VisualizationGenerator", status_code=500)

        else:
            try:
                extractor = MetadataExtractor('config.json')
                metadata = extractor.extract_metadata(user_input)
            except Exception as e:
                logging.error("Failed to run MetadataExtractor: %s", e)
                return func.HttpResponse("Error in Metadata Extraction", status_code=500)

            try:
                extraction_response_text = metadata['extraction_response_text']
                string_metadata = metadata['string_metadata']
                matching_joins_df = metadata['matching_joins_df']

                synthesize_response = SynthesizeResponse2('config.json', user_input, extraction_response_text, string_metadata, matching_joins_df)
                synthesis_response_text, pandas_df, csv_string, completions_content = synthesize_response.run_synthesis_process()
                if isinstance(synthesis_response_text, str):
                    logging.info("running handle response string")
                    response = handle_response_string(synthesis_response_text)
                    return func.HttpResponse(response)
                else:
                    logging.info("running handle response original")
                    response = handle_response(synthesis_response_text, pandas_df, csv_string, user_input, completions_content)
                    return func.HttpResponse(response)
            except Exception as e:
                logging.error("Failed to run SynthesizeResponse: %s", e)
                return func.HttpResponse("Error in SynthesizeResponse", status_code=500)

    except ValueError:
        print(f'Function failed  {ValueError}')
