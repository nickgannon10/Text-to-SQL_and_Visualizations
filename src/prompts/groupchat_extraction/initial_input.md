# Global User Input Question: {USER_INPUT}

# Global Goal: The ultimate and global goal is to extract relevant metadata and execute a function call that includes the list of the relevant tables in the database.

## Business and Data Context:

You will be genetating a SQL to query a database that was created and is used by <insert users>. <context about user and task>.

With the information in this database you can do the following:

- <list of sorts of things this DB can be used to answer>

## Operational Context:

To achieve this global goal, a team has been assembled. Each member of the team has there own role and their own personal-goal to execute. Each member of the team, should only ever focus on correctly and comprehensively completing their own personal-goal. The members of this team are as follows.

1. user_proxy: this current message is written and sent by the user proxy, the primary role will be to execute python code when it is provided from the coder
2. data_analyst: The data analyst is provided with its own context, concerning metadata and particular instructions. The data analysts role is to extract relevant TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME tuples that can help answer the Global User Input Question
3. coder: The coder, given its own context, concerning relevant code, instructions, and examples, is assigned the personal-goal of constructing a list inside a function call where each element is a string that includes TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME and it is formatted in the following way [TABLE_SCHEMA].[TABLE_NAME].COLUMN_NAME.

The ordering of responses in this team is as follows: user_proxy (current), data_analyst (next), coder. If everything appears to work correctly, TERMINATE. If not the process will loop again from the beginning.

# Data Analysts Response:

{RESPONSE_TEXT}
