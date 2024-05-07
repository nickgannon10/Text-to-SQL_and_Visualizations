# UC-2: Create Trending Identification + Reporting

## Skeleton

1. User submits query then the request is piped to the backend
2. Metadata Extraction

- Begins with a rag of the questions (met_ex.py)
- rag contents along with other contents are placed on CW to get more accurate metadata extraction

3. External Knowledge Construction (met_ex.py)

- Pandas data cleaning occurs to aid with sitatutions such as joins, providing info about column vlaues, and given additional metadata

4. SQL Generation + Execution (synth_res_v2.py)
5. Visual Representation Generation + Execution. (vis_gen.py)

## File Info:

- Embeddings/ holds pickle files containing vector stores
- metadata_strings/
  - metadata_prep, holds the string contents associated with the vector store
  - join samples includes list of all possible joins
  - string_samples hold metadata associated with each column including possible column values
- Prompts, includes all the prompt templates being used, see config.json in the HRDD_TRENDS directory if you're interested in making changes to these prompts.
- adls_v3 is not currently being used, but is being held just in case the pickeled vector stores grow to large
- chat.py hold the OPENAI API generation class object

## Batch Process Data Engine Updates

- Relevant Files
  - data_engine.py
  - src/embedding_handler.py
  - src/retrieval_handler.py
  - src/redis_cache.py

Step 1: When the redis cache is sufficiently full run the data_engine.py script, and it will retrieve all of the stored question answer pairs.

- Ultimatley, this script creates a redis.json file in the metadata_strings director

Step 2: Run the embedding_handler.py script to build the vector embeddings.

- file paths my need to be updates according to you machine
- This output a pickle file, that pickle file is a vector database that can be queried against.

Step 3: Use the retrieval handler class object scripts to test the redis.json pickle embeddings.

- file paths my need to be updates according to you machine
  - this includes update the config.json accordingly

Step 4: Uncomment the in the Integrate Embeddings HERE sections of the synth_res_v2.py file.

Step 5: Repeat the batch processing to grow the size of the dynamic k-shot Q&A pairs.
