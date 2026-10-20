import logging
import json
import re
import requests
import pandas as pd
import sqlite3

from classes import ValidationResult
from config import *

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)

# Ingestion functions
def get_request_from_api(url: str, token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        url,
        headers = headers
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        logging.exception(f"GitHub API request failed with status code {response.status_code}")
        raise

    if not response.json():
        logging.error("GitHub API returned an empty list of repositories.")
        raise ValueError("GitHub API returned no repositories")
    else:
        logging.info(f"GitHub API returned {len(response.json())} repositories.")
        return response

# Validation functions
def is_null(field: str, repo: dict, missing_vals: list):
    field_val = repo[field].strip() if isinstance(repo[field], str) \
                else repo[field]
    return True if field_val in missing_vals else False

def is_required(field: str, schema: dict):
    return schema[field]['required']

def update_repo_status(field: str, schema: dict, status: str, issues: dict, options: dict, condition: str):
    option = options[is_required(field, schema)]
    issues[field] = condition
    return "INVALID" if status == "INVALID" or option == "Required" else "VALID_WITH_WARNING"

def validate_repo(repo: dict, schema: dict, options: dict):
    status = "VALID"
    issues = dict()

    for field in schema:
        # Check if field exists
        if field in repo:
            # Check if field is null
            if is_null(field, repo, missing_values):
                # Check if field is required
                status = update_repo_status(field, schema, status, issues, options, conditions['null'])
            else:
                # Check data type:
                if isinstance(repo[field], schema[field]['type']):
                    continue
                else:
                    # Check if field is required:
                    status = update_repo_status(field, schema, status, issues, options, conditions['type'])
        else:
            # Check if field is required
            status = update_repo_status(field, schema, status, issues, options, conditions['exists'])
        
    return ValidationResult(status, issues)

def update_dlq(dlq: dict, name: str, repo: dict, result: ValidationResult):
    dlq.append(
        {
            'repo_name': name,
            'raw_data': json.dumps(repo),
            'issues': json.dumps(
                result.show_issues()
                )
        }
    )
    return dlq

# Normalisation functions
def update_field_type(field: str, repo: dict, result: ValidationResult, policy: dict):
    current_type = type(repo[field])
    expected_type = schema[field]['type']

    if current_type not in policy[expected_type]:
        result.invalidate()
    else:
        if current_type == str and expected_type == int:
            if repo[field].isdigit() or re.fullmatch(r"\d+\.0", repo[field]):
                repo[field] = int(float(repo[field]))
            else:
                result.invalidate()
        if current_type == float and expected_type == int:
            if re.fullmatch(r"\d+\.0", str(repo[field])):
                repo[field] = int(repo[field])
            else:
                result.invalidate()
    
    return repo, result

def normalise_repo(repo: dict, result: ValidationResult, schema: dict = schema, policy: dict = type_policy):
    if result.get_status() == "VALID":
        return repo, result
    else:
        issues = result.show_issues()

        if issues:
            for field in issues:
                if issues[field] == "WRONG_TYPE":
                    repo, result = update_field_type(field, repo, result, policy)          
                if issues[field] in ["MISSING", "IS_NULL"]:
                    repo[field] = schema[field]['default']

        return repo, result

# Transformation functions
def rename_fields(repo: dict, schema: dict = schema):
    for field in schema:
        if schema[field]['source_name'] != schema[field]['output_name']:
            repo[schema[field]['output_name']] = repo.pop(field)
    return repo

def transform_repo(repo: dict, schema: dict):
    return {
        k: v for k, v in rename_fields(repo, schema).items() \
        if k in [v['output_name'] for v in schema.values()]
    }

# Loading functions
def enforce_df_types(df: pd.DataFrame, columns: dict):
    for col, dtype in columns.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    return df

def create_df(repos: list, columns: dict):
    df = pd.DataFrame(repos)[list(columns.keys())]
    df = enforce_df_types(df, columns)
    return df

def build_sql_schema(df: pd.DataFrame):
    sql_dtypes = {}
    for col in df.columns:
        if pd.api.types.is_bool_dtype(df[col]):
            sql_dtypes[col] = "BOOLEAN"
        elif pd.api.types.is_integer_dtype(df[col]):
            sql_dtypes[col] = "INTEGER"
        elif pd.api.types.is_string_dtype(df[col]):
            sql_dtypes[col] = "TEXT"
        else:
            raise TypeError(
                f"Unsupported DataFrame dtype for column '{col}': "
                f"{df[col].dtype}"
            )

    return sql_dtypes

def load_to_database(df: pd.DataFrame, database_path: str, table_name: str):
    # Build schema for database
    sql_dtypes = build_sql_schema(df)

    # Load data to database
    with sqlite3.connect(database_path) as connection:
        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
            dtype=sql_dtypes
        )

# Testing functions
def without_field(repo: dict, field: str):
    result = repo.copy()
    result.pop(field)
    return result

def dict_difference(actual: dict, expected: dict):
    differences = {}
    all_keys = actual.keys() | expected.keys()

    for key in all_keys:
        actual_value = actual.get(key)
        expected_value = expected.get(key)

        if actual_value != expected_value:
            differences[key] = {
                "actual": actual_value,
                "expected": expected_value
            }

    return differences

def sort_repos(repo_list: list[dict]):
    return sorted(repo_list, key = lambda repo: repo["repo_name"])

def assert_dataframe(actual: pd.DataFrame, expected: pd.DataFrame, dtypes: pd.Series):
    try:
        if pd.testing.assert_frame_equal(actual, expected) is None:
            logging.info(f"{dtypes.name} DataFrames are equal")
            try:
                actual_dtypes = actual.dtypes
                actual_dtypes.name = dtypes.name
                if pd.testing.assert_series_equal(actual_dtypes, dtypes) is None:
                    logging.info(f"{dtypes.name} DataFrame data types are matched")
            except AssertionError as e:
                logging.error(f"{dtypes.name} DataFrame data types are NOT matched: {e}")
    except AssertionError as e:
        logging.error(f"{dtypes.name} DataFrames are NOT equal: {e}")
