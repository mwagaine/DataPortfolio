import pandas as pd
import sqlite3

from config import *
from functions import *
from testing.test_data import *

dlq = []
final_repos =  []

for name, repo in test_repos.items():
    # Attempt validation
    actual_validation = \
        validate_repo(repo, schema, required_results)
    
    expected_validation = expected_validations[name]

    # Test validation
    if actual_validation != expected_validation:
        print(
            f"'{name}' repo failed validation: got {actual_validation} but expected {expected_validation}"
            )
    else:
        print(f"'{name}' repo passed validation")

        if not actual_validation.is_valid():
            print(f"'{name}' repo is invalid - adding to dead letter queue...")
            dlq = update_dlq(dlq, name, repo, actual_validation)
        else:
            repo, actual_validation = normalise_repo(
                repo, actual_validation, schema, type_policy
            )
            
            # Test normalisation
            issue_fields = actual_validation.show_issues().keys()

            actual_normalisation = actual_validation if actual_validation.get_status() in ['VALID', 'INVALID'] \
            else {
                field: repo[field] for field in issue_fields
            }

            expected_normalisation = expected_normalisations[name]

            if actual_normalisation != expected_normalisation:
                print(
                    f"'{name}' repo failed normalisation: got {actual_normalisation} but expected {expected_normalisation}"
                )
            else:
                print(f"'{name}' repo passed normalisation")
            
                if not actual_validation.is_valid():
                    print(f"'{name}' repo is invalid - adding to dead letter queue...")
                    dlq = update_dlq(dlq, name, repo, actual_validation)
                else:
                    final_repos.append(transform_repo(repo, schema))

# Test final outputs from Python objects
if sort_repos(final_repos) == sort_repos(list(expected_main_transformation.values())):
    print("Final repo is successful")
else:
    differences = dict_difference(final_repos, expected_main_transformation)
    print(f"Final repo failed.\nDifferences found in the following keys:{list(differences.keys())}\nSee differences:\n{differences}")

if sort_repos(dlq) == sort_repos(expected_dlq):
    print("DLQ is successful")
else:
    print(f"\nActual DLQ:\n{dlq}")
    print(f"\nExpected DLQ:\n{expected_dlq}")
    print(
        f"DLQ is unsuccessful:\nExpected {expected_dlq}\nReceived {dlq}\nSee difference{set(expected_dlq).difference(dlq)}")

main_df = create_df(final_repos, df_schema)
dlq_df = create_df(sort_repos(dlq), dlq_schema)

assert_dataframe(main_df, expected_main_df, expected_main_dtypes)
assert_dataframe(dlq_df, expected_dlq_df, expected_dlq_dtypes)

load_to_database(main_df, 'github_api.db', 'repositories')
load_to_database(dlq_df, 'github_api.db', 'dead_letter_queue')

# Test if table data matches with original DataFrame
with sqlite3.connect('github_api.db') as connection:
    loaded_dfs = [
            pd.read_sql(f"SELECT * FROM {table}", connection)
            for table in ['repositories', 'dead_letter_queue']
        ]
    
loaded_main, loaded_dlq = loaded_dfs

for df, schema in zip([loaded_main, loaded_dlq], [df_schema, dlq_schema]):
    df = enforce_df_types(df, schema)

assert_dataframe(loaded_main, main_df, expected_main_dtypes)
assert_dataframe(loaded_dlq, dlq_df, expected_dlq_dtypes)
