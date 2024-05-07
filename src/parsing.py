def extract_content(original_string):
    # Define the delimiters
    start_delimiter = '"cell": "'
    end_delimiter = '"\n}'
    
    # Find the start and end
    start_idx = original_string.find(start_delimiter) + len(start_delimiter)
    end_idx = original_string.find(end_delimiter, start_idx)
    
    # Extract and return the content
    return original_string[start_idx:end_idx].strip()

def convert_string_to_list(input_string):
    # Remove the variable assignment part as we are only interested in the list
    import ast
    try:
        # Parse the input string to construct the list variable
        list_variable = ast.literal_eval(input_string)
        
        # Check if the result is indeed a list
        if isinstance(list_variable, list):
            return list_variable
        else:
            raise ValueError("The input string does not contain a list.")
    except (SyntaxError, ValueError) as e:
        # Handle any parsing error
        print(f"An error occurred: {e}")
        return None

def extract_matching_rows_v2(df_string_samples, stuff_list):
    import pandas as pd
    # Check if df_string_samples is a DataFrame and stuff_list is a valid iterable
    if not isinstance(df_string_samples, pd.DataFrame) or stuff_list is None or not hasattr(stuff_list, '__iter__'):
        return ''  # or any suitable default value

    # Desired fields to be extracted from the dataframe
    desired_fields = [
        'TABLE_SCHEMA',
        'TABLE_NAME',
        'COLUMN_NAME',
        'ORDINAL_POSITION',
        'COLUMN_DEFAULT',
        'IS_NULLABLE',
        'DATA_TYPE',
        'CHARACTER_MAXIMUM_LENGTH', 
        'SOME_POSSIBLE_VALUES',
        'SOME_POSSIBLE_VALUES_1',
        'SOME_POSSIBLE_VALUES_2', 
        'SOME_POSSIBLE_VALUES_3', 
        'SOME_POSSIBLE_VALUES_4'    
    ]
    
    matching_rows_reduced = []
    
    for item in stuff_list:
        # Split the string by '.' and remove brackets
        parts = item.replace('[', '').replace(']', '').split('.')
        
        # Check that the split resulted in three parts: schema, table, and column
        if len(parts) == 3:
            schema, table, column = parts
            
            # Check if the schema and table match what we have in the metadata DataFrame
            df_filtered = df_string_samples[
                (df_string_samples['TABLE_SCHEMA'] == schema) & 
                (df_string_samples['TABLE_NAME'] == table)
            ]
            
            # If the column name is in df_filtered, extract the desired fields
            matching_row = df_filtered[df_filtered['COLUMN_NAME'] == column]
            if not matching_row.empty:
                # Extract only the desired fields
                reduced_info = {field: matching_row.iloc[0][field] for field in desired_fields}
                matching_rows_reduced.append(reduced_info)
    
    parsed_output = ''.join(str(e) for e in matching_rows_reduced)
    
    return parsed_output

def find_matching_joins(dataframe, column_list):
    import pandas as pd
    matching_rows = []
    for column_table_string in column_list:
        matches = dataframe['join_query'].apply(lambda x: column_table_string in x)
        matching_rows.extend(dataframe[matches].values.tolist())
    return pd.DataFrame(matching_rows, columns=dataframe.columns)

def extract_sql_query(text):
    """
    This function extracts a SQL query from a given string that contains the query 
    enclosed within triple backticks (```).
    
    Parameters:
    - text (str): The string containing the SQL query.
    
    Returns:
    - str: The extracted SQL query or an empty string if not found.
    """
    # Define the start and end markers for the SQL block
    start_marker = "```sql"
    end_marker = "```"
    
    # Find the index of the start and end markers
    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index + len(start_marker))
    
    # If both markers are found, extract the SQL query
    if start_index != -1 and end_index != -1:
        # Add the length of the start marker to the start index to skip the marker itself
        start_index += len(start_marker)
        # Extract the query
        query = text[start_index:end_index].strip()
        return query
    else:
        # If the SQL query is not found, return an empty string
        return ""

def parse_error_message(error_message):
    # Find the index where the unwanted text starts
    index = error_message.find("at com.microsoft")
    # Extract the part of the error message before that index
    parsed_message = error_message[:index].strip()
    return parsed_message 

import re
import json

def format_metadata_to_markdown_improved(metadata_str):
    """
    Improved version of the function to handle special cases and provide detailed error information.
    """
    # Regular expression to match individual dictionaries
    dict_pattern = r"\{'TABLE_SCHEMA':.*?}(?=\{'TABLE_SCHEMA':|$)"
    dict_matches = re.findall(dict_pattern, metadata_str, re.DOTALL)

    markdown_output = []
    
    for dict_str in dict_matches:
        try:
            # Handling 'nan' values by replacing them with null
            dict_str = dict_str.replace("nan", "null")
            dict_data = json.loads(dict_str.replace("'", '"'))
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}\nProblematic string: {dict_str[:100]}...")
            continue

        table_header = f"### {dict_data.get('TABLE_SCHEMA')}.{dict_data.get('TABLE_NAME')}\n"
        markdown_output.append(table_header)

        for key, value in dict_data.items():
            if key not in ['TABLE_SCHEMA', 'TABLE_NAME']:
                markdown_output.append(f"- **{key}**: {value}\n")

    return ''.join(markdown_output)


# string = """{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDElementDeal', 'COLUMN_NAME': 'createdon', 'ORDINAL_POSITION': 92, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'datetime', 'CHARACTER_MAXIMUM_LENGTH': nan, 'SOME_POSSIBLE_VALUES': 'Oct 10 2023 6:07PM', 'SOME_POSSIBLE_VALUES_1': 'Oct 10 2023 6:07PM', 'SOME_POSSIBLE_VALUES_2': 'Oct 10 2023 6:07PM', 'SOME_POSSIBLE_VALUES_3': 'Oct 10 2023 6:07PM', 'SOME_POSSIBLE_VALUES_4': 'Oct 10 2023 6:07PM'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDElementDeal', 'COLUMN_NAME': 'statuscodename', 'ORDINAL_POSITION': 5, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'nvarchar', 'CHARACTER_MAXIMUM_LENGTH': 1000.0, 'SOME_POSSIBLE_VALUES': 'Canceled', 'SOME_POSSIBLE_VALUES_1': 'Canceled', 'SOME_POSSIBLE_VALUES_2': 'Canceled', 'SOME_POSSIBLE_VALUES_3': 'Canceled', 'SOME_POSSIBLE_VALUES_4': 'Canceled'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDElementDeal', 'COLUMN_NAME': 'hrdd_dealid', 'ORDINAL_POSITION': 69, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'int', 'CHARACTER_MAXIMUM_LENGTH': nan, 'SOME_POSSIBLE_VALUES': nan, 'SOME_POSSIBLE_VALUES_1': nan, 'SOME_POSSIBLE_VALUES_2': nan, 'SOME_POSSIBLE_VALUES_3': nan, 'SOME_POSSIBLE_VALUES_4': nan}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDIncident', 'COLUMN_NAME': 'createdon', 'ORDINAL_POSITION': 278, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'datetime', 'CHARACTER_MAXIMUM_LENGTH': nan, 'SOME_POSSIBLE_VALUES': 'Oct 4 2021 12:55PM', 'SOME_POSSIBLE_VALUES_1': 'Oct 4 2021 12:55PM', 'SOME_POSSIBLE_VALUES_2': 'Oct 4 2021 12:55PM', 'SOME_POSSIBLE_VALUES_3': 'Oct 4 2021 12:55PM', 'SOME_POSSIBLE_VALUES_4': 'Oct 4 2021 12:55PM'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDIncident', 'COLUMN_NAME': 'statuscodename', 'ORDINAL_POSITION': 13, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'nvarchar', 'CHARACTER_MAXIMUM_LENGTH': 1000.0, 'SOME_POSSIBLE_VALUES': 'No Action', 'SOME_POSSIBLE_VALUES_1': 'No Action', 'SOME_POSSIBLE_VALUES_2': 'No Action', 'SOME_POSSIBLE_VALUES_3': 'No Action', 'SOME_POSSIBLE_VALUES_4': 'No Action'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDIncident', 'COLUMN_NAME': 'hrdd_ticketnumber', 'ORDINAL_POSITION': 2, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'nvarchar', 'CHARACTER_MAXIMUM_LENGTH': 400.0, 'SOME_POSSIBLE_VALUES': 'HRDD-CAS-16921-T9S1H6', 'SOME_POSSIBLE_VALUES_1': 'HRDD-CAS-16921-T9S1H6', 'SOME_POSSIBLE_VALUES_2': 'HRDD-CAS-16921-T9S1H6', 'SOME_POSSIBLE_VALUES_3': 'HRDD-CAS-16921-T9S1H6', 'SOME_POSSIBLE_VALUES_4': 'HRDD-CAS-16921-T9S1H6'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDOpportunity', 'COLUMN_NAME': 'estimatedclosedate', 'ORDINAL_POSITION': 8, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'datetime', 'CHARACTER_MAXIMUM_LENGTH': nan, 'SOME_POSSIBLE_VALUES': 'Apr 30 2021 12:00AM', 'SOME_POSSIBLE_VALUES_1': 'Apr 30 2021 12:00AM', 'SOME_POSSIBLE_VALUES_2': 'Apr 30 2021 12:00AM', 'SOME_POSSIBLE_VALUES_3': 'Apr 30 2021 12:00AM', 'SOME_POSSIBLE_VALUES_4': 'Apr 30 2021 12:00AM'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDOpportunity', 'COLUMN_NAME': 'statuscodename', 'ORDINAL_POSITION': 5, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'nvarchar', 'CHARACTER_MAXIMUM_LENGTH': 1000.0, 'SOME_POSSIBLE_VALUES': 'In Progress', 'SOME_POSSIBLE_VALUES_1': 'In Progress', 'SOME_POSSIBLE_VALUES_2': 'In Progress', 'SOME_POSSIBLE_VALUES_3': 'In Progress', 'SOME_POSSIBLE_VALUES_4': 'In Progress'}{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDOpportunity', 'COLUMN_NAME': 'hrdd_ticket', 'ORDINAL_POSITION': 19, 'COLUMN_DEFAULT': nan, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'uniqueidentifier', 'CHARACTER_MAXIMUM_LENGTH': nan, 'SOME_POSSIBLE_VALUES': '197A9967-B0A8-EB11-B1AC-002248089981', 'SOME_POSSIBLE_VALUES_1': '197A9967-B0A8-EB11-B1AC-002248089981', 'SOME_POSSIBLE_VALUES_2': '197A9967-B0A8-EB11-B1AC-002248089981', 'SOME_POSSIBLE_VALUES_3': '197A9967-B0A8-EB11-B1AC-002248089981', 'SOME_POSSIBLE_VALUES_4': '197A9967-B0A8-EB11-B1AC-002248089981'}"""
# test_string = "{'TABLE_SCHEMA': 'HRDD', 'TABLE_NAME': 'vw_HRDDElementDeal', 'COLUMN_NAME': 'createdon', 'DATA_TYPE': 'datetime'}"
# x = format_metadata_to_markdown_improved(string)
# print(x)


def contains_visualization_flag(input_string: str) -> bool:
    """
    Checks if the input string contains any of the specified phrases that indicate a request for visualization.
    
    Args:
    - input_string: The string to search the flags in.
    
    Returns:
    - True if any of the specified phrases is found, False otherwise.
    """
    # Define a list of phrases to look for, including the original flags and new phrases.
    phrases_to_check = ['--v', '--V', 'visualization', 'make a visualization', 'make an insight']
    
    # Convert the input string to lower case to make the search case-insensitive.
    input_string_lower = input_string.lower()
    
    # Use the any() function to check if any of the phrases is in the input string.
    return any(phrase in input_string_lower for phrase in phrases_to_check)

def contains_both_v_and_n_flags(input_string: str) -> bool: 
    """
    Checks if the input string contains both '--v' (or '--V') and '--n' (or '--N').
    
    Args:
    - input_string: The string to search the flags in.
    
    Returns:
    - True if both '--v' (or '--V') and '--n' (or '--N') are found, False otherwise.
    """
    # resolving reversion issue
    input_string_lower = input_string.lower()
    return '--v' in input_string_lower and '--n' in input_string_lower


def format_sql_query_corrected(sql_query: str) -> str:
    # Keywords for line breaks and their indentation levels
    keywords = ["FROM", "WHERE", "ORDER BY", "GROUP BY", "JOIN"]
    # Split the query into lines for better handling
    lines = [sql_query]
    
    for keyword in keywords:
        new_lines = []
        for line in lines:
            # Check if the keyword is in the line and not just a part of another word
            if f" {keyword} " in line.upper():
                # Split the line at the keyword and add the keyword back with proper formatting
                parts = line.split(f" {keyword} ", 1)
                new_lines.append(parts[0].strip())  # Before keyword part
                new_lines.append(f"{keyword}\n    " + parts[1].strip())  # Keyword with new line and indentation
            else:
                new_lines.append(line)
        lines = new_lines
    
    # Combine the lines back into a single string
    formatted_query = "\n".join(lines)
    return formatted_query

def parse_sql_error_revised(error_message: str) -> str:
    # Step 1: Identify the beginning of the SQL query
    start_marker = "[SQL:"
    start_index = error_message.find(start_marker) + len(start_marker)
    
    # Step 2: Accurately locate the end of the SQL query, before the closing ']' that precedes the error URL
    end_marker = "] (Background on this error at:"
    end_index = error_message.find(end_marker)
    
    # If the end marker is not found, try adjusting to find just before the "]" which directly precedes the URL info
    if end_index == -1:
        end_index = error_message.find("]", start_index)
    
    # Step 3: Extract the SQL query using the identified indices, trimming any whitespace
    sql_query = error_message[start_index:end_index].strip()
    formatted_sql_query = format_sql_query_corrected(sql_query)

    return formatted_sql_query

def parse_column_names(input_text):
    import logging
    logging.info("Starting to parse column names from input text.")
    logging.debug(f"Input text for parsing: {input_text}")
    lines = input_text.split('\n')
    formatted_output = ""
    logging.debug(f"Input text for parsing: {input_text}")

    for line in lines:
        if line.startswith("- **COLUMN_NAME**"):  # Adjusted to match the input string format
            # Adjusting the extraction logic to account for the new format
            column_name = line.split("**:")[1].strip()  # Adjusting the split to work with the new format
            if formatted_output:  # Adds <br> only if formatted_output is not empty
                formatted_output += "<br>"
            formatted_output += column_name
    logging.debug(f"Formatted output: {formatted_output}")

    return formatted_output

