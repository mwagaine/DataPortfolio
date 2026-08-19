import logging
import sqlite3
import pandas as pd

from config import *
from functions import *

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)

# Attempt GET API request
response = get_request_from_api(
     api_credentials['url'],
     api_credentials['token']
)

# Process API responses
valid_repos = []
dead_letter_queue = []

for repo in response.json():
    validation_result = validate_repo(repo, schema, required_results)

    if not validation_result.is_valid():
        logging.warning(
            f"'{repo['name']}' repository is invalid, adding to dead letter queue..."
        )
        dead_letter_queue = update_dlq(
            dead_letter_queue,
            repo['name'],
            repo,
            validation_result
        )
    else:
        repo, validation_result = normalise_repo(
            repo,
            validation_result,
            schema,
            type_policy
        )
        if not validation_result.is_valid():
            logging.warning(
                f"'{repo['name']}' repository is invalid, adding to dead letter queue..."
            )
            dead_letter_queue = update_dlq(
                dead_letter_queue,
                repo['name'],
                repo,
                validation_result
            )
        else:
            logging.info(
                f"'{repo['name']}' repository is valid, preparing for business transformation..."
            )
            valid_repos.append(transform_repo(repo, schema))

main_df = create_df(valid_repos, df_schema)
dlq_df = create_df(dead_letter_queue, dlq_schema)

print(f"PRE-LOAD MAIN:\n{main_df}\n\n")
print(f"PRE-LOAD DLQ:\n{dlq_df}\n\n")

load_to_database(main_df, 'github_api.db', 'repositories')
load_to_database(dlq_df, 'github_api.db', 'dead_letter_queue')

with sqlite3.connect('github_api.db') as connection:
    loaded_dfs = [
        pd.read_sql(f"SELECT * FROM {table}", connection)
        for table in ['repositories', 'dead_letter_queue']
    ]

loaded_main, loaded_dlq = loaded_dfs

for df, schema in zip([loaded_main, loaded_dlq], [df_schema, dlq_schema]):
    df = enforce_df_types(df, schema)

print(f"POST-LOAD MAIN:\n{loaded_main}\n\n")
print(f"POST-LOAD DLQ:\n{loaded_dlq}\n\n")
