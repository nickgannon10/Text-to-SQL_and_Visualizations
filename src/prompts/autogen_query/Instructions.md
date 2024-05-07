# Global User Input Question: {USER_INPUT}

# System Goals: Construct a comprehensive tutorial for generating an SQL query to answer the Global User Input Question.

## Business Context:

You will be genetating a SQL to query a database that was created and is used by <insert users>. <context about user and task>.

With the information in this database you can do the following:

- <list of sorts of things this DB can be used to answer>

## Date Context:

Below you are given the Schema, Table, and Column information to use to construct your SQL query. Do not use any Columns that are not included below.

### Metadata concerning Schema, Table, and Column Selection:

{EXTRACTION_RESPONSE_TEXT}

### Additional Metadata about each Column:

{STRING_METADATA}

### Officially Confirmed Join Options:

{MATCHING_JOINS_DF}

### Keep in Mind:

Provided in the Additional Metadata about each column is the element, SOME_POSSIBLE_VALUES, that informs about the sorts of possible values you may find in each column. Pay special attention to this column as it will serve invaluable, if for example you would like to include a where clause in your query. Please keep in my that SOME_POSSIBLE_VALUES is not necessarily an exaustive lists off all possible values, but rather a sample of what sorts of values the given column may include. Additionally, be cognizant to format data properly

# Instructions:

Never lose sight of your System Goals or your instructions. Please provide accurate, factual, thoughtful, and nuanced answers. Take a deep breath, think the problem through step-by-step, and please be sure to be as correct as possible. This is very important for my career. If, for example a result that includes UserID it should also include information about that user's name. Do not claim that there are no relevant metadata, because there are, but it may require you to be creative and extrapolate about the contents of columns in order to extract the correct information. Additionally, do not include a semi-colon, ';', at the end of your generated query. Also, in the cases you choose to use an ORDER BY clause, the query must always begin SELECT TOP(<some number>), otherwise an error will be thrown at query time, as the API will not allow GROUP BY clause unless this is specified. Furthermore, please note the Officially Confirmed Join Options in your reasoning. Be sure to construct queries such that is de-deplicates repeates row values. Be sure to construct queries such that is de-deplicates repeates row values. Be sure to construct queries such that is de-deplicates repeates row values.

## Possible Error Handling

In the case that there is an error below this, that means you should integrate the information from that error in the construction of your tutorial. Below will be a previously attempted failred query and the corresponding error.

### Failed Query

{FAILED_QUERY}

### Error Message

{ERROR_MESSAGE}

### Example Error re-solution 1: If error includes The ORDER BY clause is invalid in views, inline functions, derived tables, subqueries, and common table expressions, unless TOP, OFFSET or FOR XML is also specified. Do not forget this point under any circumstances.

SELECT TOP (100)
<rest of query contents>
ORDER BY <some table>

### Example Error re-solution 2: If error includes The ORDER BY clause is invalid in views, inline functions, derived tables, subqueries, and common table expressions, unless TOP, OFFSET or FOR XML is also specified. Do not forget this point under any circumstances.

SELECT TOP (100)
<rest of query contents>
ORDER BY <some table>

### Example Error re-solution 3: If error includes The ORDER BY clause is invalid in views, inline functions, derived tables, subqueries, and common table expressions, unless TOP, OFFSET or FOR XML is also specified. Do not forget this point under any circumstances.

SELECT TOP (100)
<rest of query contents>
ORDER BY <some table>

{EXAMPLE_K_SHOT}
