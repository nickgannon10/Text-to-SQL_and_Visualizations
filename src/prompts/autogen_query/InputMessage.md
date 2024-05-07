# Global User Input Question: {USER_INPUT}

# System Goal: Using the context below, generate a SQL Query that will return information that can help in answering the Global User Input Question.

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

### Keep in Mind:

Provided in the Additional Metadata about each column is the element, SOME_POSSIBLE_VALUES, that informs about the sorts of possible values you may find in each column. Pay special attention to this column as it will serve invaluable, if for example you would like to include a where clause in your query. Please keep in my that SOME_POSSIBLE_VALUES is not necessarily an exaustive lists off all possible values, but rather a sample of what sorts of values the given column may include.

### Suggestions: Some helpful information is provided below for constructing this SQL query, please heed it, but impprove upon it if necessary.

{SUGGESTIONS_RESPONSE_TEXT}

## Instructions:

Never lose sight of your System or your instructions. Please provide accurate, factual, thoughtful, and nuanced answers. Take a deep breath, think it through step-by-step and please be sure to be as correct as possible. This is very important for my career. Key off the examples below. Please keep that in mind during SQL construction all queries will be sent to an Azure SQL Server meaning Transact SQL (T-SQL) syntax is necessary for queries to execute properly. Furthermore, please ensure that you include the Database Schema in the query as well. Additionally, do not include a semi-colon, ';', at the end of your generated query. Always, always, always include TOP(<some integer after SELECT>)

## Output Format Example 1:

### Reasoning

<Insert logic for constructing SQL query here>
### SQL Query
```sql
SELECT TOP(100)
<part of Query>
ORDER BY
<end of query>
```

{K-SHOT}
