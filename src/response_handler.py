import json
import logging
import re
import uuid
import datetime
import traceback

def convert_to_json(content):
    logging.info("Attempting to convert content to JSON")
    try:
        json_content = json.loads(content)
        logging.info("Content was successfully converted to JSON")
    except ValueError as e:
        logging.info("Content is not in valid JSON format, attempting regex extraction: %s", str(e))
        try:
            match = re.search(r'({.*})', content, re.DOTALL)
            if match:
                json_string = match.group(1)
                json_content = json.loads(json_string)
                logging.info("Regex extraction successful, converted to JSON")
            else:
                logging.warning("Regex extraction found no matches, applying default content structure.")
                string_content = {
                    'content': content,
                    'followUpQuestions': ["What regions have seen the highest number of deals.", "Which type of deals (new business vs. renewals) has a higher success rate?", "What percentage of deals required escalations to higher management?"]
                }
                json_content = json.loads(json.dumps(string_content))
        except Exception as ex:
            logging.error("Regex extraction failed with an unexpected error: %s", str(ex))
            # Fallback to a default structured response if regex extraction fails
            string_content = {
                'content': content,
                'followUpQuestions': ["What regions have seen the highest number of deals.", "Which type of deals (new business vs. renewals) has a higher success rate?", "What percentage of deals required escalations to higher management?"]
            }
            json_content = json.loads(json.dumps(string_content))
    except Exception as e:
        logging.error("Unexpected error during JSON conversion: %s. Traceback: %s", str(e), traceback.format_exc())
        # Consider how to handle this scenario; re-throw, return a default structure, etc.
        raise

    return json_content

def handle_response(response, pandas_df, csv_string, user_input, completions_content):
    logging.info("Handling response")
    try:
        print(f"response in response_handler: {type(response)}")
        # completions_content = response.choices[0].message.content
        json_response = convert_to_json(content=completions_content)
        
        pandas_df_json=pandas_df.to_json()
        data = {
            "pandas_df":pandas_df_json,
            "csv_string":csv_string,
            "user_input":user_input
            ### Add SQL Query
          }
        
        json_string=json.dumps(data)    

        # Structured logging of the response handling process
        logging.info(json.dumps({"action": "convert_to_json", "status": "success", "content_length": len(completions_content)}))

        content = json_response.get('content')
        if not content:
            logging.warning("No content found, applying default error message")
            json_response["content"] = [{"value": "The response from the chat plugin was invalid"}]
        else:
            json_response["content"] = [{
                "value": content,
                "type": 1,
                "rawData": json_string,
                "includeHistory": True,
                "guid": str(uuid.uuid4())
            }]

        questions = json_response.get('followUpQuestions')
        try:
            question_count = len(questions)
            if not questions or question_count != 3:
                logging.info("Invalid or incomplete follow-up questions, adjusting")
                json_response["followUpQuestions"] = ["The generated questions were invalid"]
        except TypeError:
            logging.error("Follow-up questions are not a list")
            json_response["followUpQuestions"] = ["The generated questions were invalid"]

        json_response["role"] = {'label': response.choices[0].message.role}
        json_response["usage"] = {
            "completion_tokens": 0,
            "prompt_tokens": 0,
            "total_tokens": 0
        }
        json_response["timestamp"] = datetime.datetime.now().isoformat()

    except Exception as e:
        logging.error("Failed to handle response: %s. Traceback: %s", str(e), traceback.format_exc())
        raise

    return json.dumps(json_response)

def handle_response_string(response):
    logging.info("Handling response as string")
    try:
        json_response = convert_to_json(content=response)

        content = json_response.get('content')
        if not content:
            logging.warning("No content in response string, applying default message")
            json_response["content"] = [{"value": "The response from the chat plugin was invalid"}]
        else:
            json_response["content"] = [{
                "value": content,
                "type": 1,
                "rawData": None,
                "includeHistory": True,
                "guid": str(uuid.uuid4())
            }]

        questions = json_response.get('followUpQuestions')
        try:
            question_count = len(questions)
            if not questions or question_count != 3:
                logging.info("Adjusting invalid or incomplete follow-up questions from string response")
                json_response["followUpQuestions"] = ["The generated questions were invalid"]
        except TypeError:
            logging.error("Follow-up questions are not a list in string response")
            json_response["followUpQuestions"] = ["The generated questions were invalid"]

        json_response["role"] = {'label': 'assistant'}
        json_response["usage"] = {
            "completion_tokens": 0,
            "prompt_tokens": 0,
            "total_tokens": 0
        }
        json_response["timestamp"] = datetime.datetime.now().isoformat()

    except Exception as e:
        logging.error("Failed to handle response string: %s. Traceback: %s", str(e), traceback.format_exc())
        raise

    return json.dumps(json_response)


def handle_response_with_image(encoded_image: str) -> str:
    logging.info("Handling response with an encoded image")
    try:
        # Prepare the content structure for an image response
        content_empty = {
            "value": "Generated Image",
            "type": 1,
            "rawData": None,
            "includeHistory": False,
            "guid": str(uuid.uuid4())
        } 

        content_img = {
            "value": {"image": f"data:image/png;base64,{encoded_image}"},
            "type": 3,  # Assuming type 3 indicates an image/multimedia response
            "rawData": None,
            "includeHistory": False,
            "guid": str(uuid.uuid4())
        }

        # Construct the overall response JSON
        response_json = {
            "content": [content_empty, content_img],
            "followUpQuestions": [
                "1.	What regions have seen the highest number of deals.",
                "Which type of deals (new business vs. renewals) has a higher success rate?",
                "What percentage of deals required escalations to higher management?"
            ],
            "role": {"label": "assistant"},
            "usage": {
                "completion_tokens": 0,  # These might need to be dynamically determined or set to a default
                "prompt_tokens": 0,
                "total_tokens": 0
            },
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Convert the response dictionary to a JSON string
        response_string = json.dumps(response_json)
        logging.info("Image response successfully generated")
    except Exception as e:
        logging.error("Failed to handle image response: %s. Traceback: %s", str(e), traceback.format_exc())
        raise

    return response_string

def handle_response_image_error(iterative_output, pandas_df, csv_string, user_input):
    logging.info("Handling response with an encoded image")

    import pandas as pd 

    try:

        pandas_df_json=pandas_df.to_json()
        data = {
            "pandas_df":pandas_df_json,
            "csv_string":csv_string,
            "user_input":user_input
          }
        
        json_string=json.dumps(data)  

        content_iterative = {
            "value": iterative_output,
            "type": 1,
            "rawData": json_string,
            "includeHistory": False,
            "guid": str(uuid.uuid4())
        } 

        response_json = {
            "content": [content_iterative],
            "followUpQuestions": [
                "What regions have seen the highest number of deals.",
                "Which type of deals (new business vs. renewals) has a higher success rate?",
                "What percentage of deals required escalations to higher management?"
            ],
            "role": {"label": "assistant"},
            "usage": {
                "completion_tokens": 0,  # These might need to be dynamically determined or set to a default
                "prompt_tokens": 0,
                "total_tokens": 0
            },
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Convert the response dictionary to a JSON string
        response_string = json.dumps(response_json)
        logging.info("Image response successfully generated")
    except Exception as e:
        logging.error("Failed to handle image response: %s. Traceback: %s", str(e), traceback.format_exc())
        raise

    return response_string