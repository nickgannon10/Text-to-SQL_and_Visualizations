# Global User Input Question: {USER_INPUT}

# Global Goal: The ultimate and global goal is to extract relevant metadata. Specifically you must extract the [TABLE_SCHEMA], [TABLE_NAME], and [COLUMN_NAME] information that can be used to comprehensively answer the Global User Input Question.

## Business Context:

You will be genetating a SQL to query a database that was created and is used by <insert users>. <context about user and task>.

With the information in this database you can do the following:

- <list of sorts of things this DB can be used to answer>

## Operational Context:

Below you will be provided with SQL Metadata and instructions for formatting outputs.

## METADATA:

{METADATA}

## JOIN Metadata

{JOIN_METADATA}

## Examples Question Answer Pairs

## Example 1:

{Q-and-A_K-shot}

## Initial Suggestion have been provided from a first pass of the data, it is likely an incomplete list, that will need to be added to, but it can serve as a starting place:

{FLATTENED_MATCHES}

# Instructions:

Never lose sight of your Personal-Goal or your instructions. Please provide accurate, factual, thoughtful, and nuanced answers. Take a deep breath, think the problem through step-by-step, and please be sure to be as correct as possible. This is very important for my career. If, for example a result that includes UserID it should also include information about that user's name. Do not claim that there are no relevant metadata, because there are, but it may require you to be creative and extrapolate about the contents of columns in order to extract the correct information. Remember only extract, please do not generate the relevant SQL query. Under no circumstances should you include a TABLE SCHEMA, TABLE NAME, COLUMN NAME couple that does not appear above. Lastly, in your step-by-step reasoning, please include some thoughts about JOIN Metadata, as these are the only possible joins the database allows, and therefore, columns included in JOIN Metadata may need to be included in your extracted relevant metadata even if the don't at first appear relevant. Meaning if you would like to use columns from more than one table in you query, you must include a some relevant metadata from JOIN Metadata in you extraction. Under no cirmcustances should you hallucinate joins. Lastly always err on the side of including columns rather than not. Meaning, when in doubt, include the column.
