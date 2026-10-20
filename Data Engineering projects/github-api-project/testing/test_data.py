import json
import pandas as pd

from functions import create_df, sort_repos, without_field
from classes import ValidationResult
from config import schema, df_schema, dlq_schema

valid_repo = {
   "name": "test-repo",
   "private": False,
   "language": "Python",
   "has_discussions": True,
   "has_projects": True,
   "has_pages": False,
   "size": 100,
   "forks_count": 10,
   "open_issues_count": 5,
   "stargazers_count": 50,
   "watchers_count": 20
}

transformed_valid_repo = {
   "repo_name": "test-repo",
   "private": False,
   "language": "Python",
   "has_discussions": True,
   "has_projects": True,
   "has_pages": False,
   "size": 100,
   "forks": 10,
   "open_issues": 5,
   "stargazers": 50,
   "watchers": 20
}

test_repos = {
    # 1. Completely valid
    "completely_valid": {
        **valid_repo
    },
    # 2. Optional field missing
    "optional_field_missing": {
        **without_field(
            valid_repo,
            "forks_count"
            ),
            "name": "optional_field_missing"
    },
    # 3. Required field missing
    "required_field_missing": {
        **without_field(
            valid_repo,
            "language"
            ),
            "name": "required_field_missing"
    },
    # 4. Required integer stored as numeric string (not a float)
    "required_int_numeric_string": {
        **valid_repo,
        "name": "required_int_numeric_string",
        "size": "12"
    },
    # 5. Required integer stored as numeric string (a float)
    "required_int_float_string": {
        **valid_repo,
        "name": "required_int_float_string",
        "size": "12.0"
    },
    # 6. Required integer stored as float
    "required_int_float": {
        **valid_repo,
        "name": "required_int_float",
        "size": 12.0
    },
    # 7. Required integer stored as invalid string
    "required_int_invalid_string": {
        **valid_repo,
        "name": "required_int_invalid_string",
        "size": "12abc"
    },
    # 8. Optional integer stored as numeric string (not a float)
    "optional_int_numeric_string": {
        **valid_repo,
        "name": "optional_int_numeric_string",
        "forks_count": "12"
    },
    # 9. Optional integer stored as numeric string (a float)
    "optional_int_float_string": {
        **valid_repo,
        "name": "optional_int_float_string",
        "forks_count": "12.0"
    },
    # 10. Optional integer stored as valid float
    "optional_int_valid_float": {
        **valid_repo,
        "name": "optional_int_valid_float",
        "forks_count": 2.0
    },
    # 11. Optional integer stored as invalid float
    "optional_int_invalid_float": {
        **valid_repo,
        "name": "optional_int_invalid_float",
        "forks_count": 2.6
    },
    # 12. Optional integer stored as invalid string
    "optional_int_invalid_string": {
        **valid_repo,
        "name": "optional_int_invalid_string",
        "forks_count": "12abc"
    },
    # 13. Boolean stored as integer
    "boolean_stored_as_integer": {
        **valid_repo,
        "name": "boolean_stored_as_integer",
        "private": 1
    },
    # 14. Null required field
    "null_required_field": {
        **valid_repo,
        "name": "null_required_field",
        "language": None
    },
    # 15. Null optional field = None
    "null_optional_none": {
        **valid_repo,
        "name": "null_optional_none",
        "forks_count": None
    },
    # 16. Null optional field = empty string
    "null_optional_empty_string": {
        **valid_repo,
        "name": "null_optional_empty_string",
        "forks_count": ""
    },
    # 17. Null optional field = whitespace
    "null_optional_whitespace": {
        **valid_repo,
        "name": "null_optional_whitespace",
        "forks_count": "      "
    },
    # 18. Required 'name' field stored as integer
    "required_name_integer": {
         **valid_repo,
         "name": "required_name_integer",
         "name": 6
    } #,
   #  # 19. Multiple issues
   #  "multiple_issues": {
   #      **valid_repo,
   #      "": "",
   #      "": ""

   #  }
}

expected_validations = {
    # 1. Completely valid
    "completely_valid": ValidationResult("VALID"),
    # 2. Optional field missing
    "optional_field_missing": ValidationResult("VALID_WITH_WARNING", {"forks_count": "MISSING"}),
    # 3. Required field missing
    "required_field_missing": ValidationResult("INVALID", {"language": "MISSING"}),
    # 4. Required integer stored as numeric string (not a float)
    "required_int_numeric_string": ValidationResult("INVALID", {"size": "WRONG_TYPE"}),
    # 5. Required integer stored as numeric string (a float)
    "required_int_float_string": ValidationResult("INVALID", {"size": "WRONG_TYPE"}),
    # 6. Required integer stored as float
    "required_int_float": ValidationResult("INVALID", {"size": "WRONG_TYPE"}),
    # 7. Required integer stored as invalid string
    "required_int_invalid_string": ValidationResult("INVALID", {"size": "WRONG_TYPE"}),
    # 8. Optional integer stored as numeric string (not a float)
    "optional_int_numeric_string": ValidationResult("VALID_WITH_WARNING", {"forks_count": "WRONG_TYPE"}),
    # 9. Optional integer stored as numeric string (a float)
    "optional_int_float_string": ValidationResult("VALID_WITH_WARNING", {"forks_count": "WRONG_TYPE"}),
    # 10. Optional integer stored as valid float
    "optional_int_valid_float": ValidationResult("VALID_WITH_WARNING", {"forks_count": "WRONG_TYPE"}),
    # 11. Optional integer stored as invalid float
    "optional_int_invalid_float": ValidationResult("VALID_WITH_WARNING", {"forks_count": "WRONG_TYPE"}),
    # 12. Optional integer stored as invalid string
    "optional_int_invalid_string": ValidationResult("VALID_WITH_WARNING", {"forks_count": "WRONG_TYPE"}),
    # 13. Boolean stored as integer
    "boolean_stored_as_integer": ValidationResult("VALID_WITH_WARNING", {"private": "WRONG_TYPE"}),
    # 14. Null required field
    "null_required_field": ValidationResult("INVALID", {"language": "IS_NULL"}),
    # 15. Null optional field = None
    "null_optional_none": ValidationResult("VALID_WITH_WARNING", {"forks_count": "IS_NULL"}),
    # 16. Null optional field = empty string
    "null_optional_empty_string": ValidationResult("VALID_WITH_WARNING", {"forks_count": "IS_NULL"}),
    # 17. Null optional field = whitespace
    "null_optional_whitespace": ValidationResult("VALID_WITH_WARNING", {"forks_count": "IS_NULL"}),
    # 18. Required 'name' field stored as integer
    "required_name_integer": ValidationResult("INVALID", {"name": "WRONG_TYPE"})
}

expected_normalisations = {
    # 1. Completely valid
    "completely_valid": ValidationResult("VALID"),
    # 2. Optional field missing
    "optional_field_missing": {"forks_count": None},
    # 8. Optional integer stored as numeric string (not a float)
    "optional_int_numeric_string": {"forks_count": 12},
    # 9. Optional integer stored as numeric string (a float)
    "optional_int_float_string": {"forks_count": 12},
    # 10. Optional integer stored as valid float
    "optional_int_valid_float": {"forks_count": 2},
    # 11. Optional integer stored as invalid float
    "optional_int_invalid_float": ValidationResult(
        "INVALID", {"forks_count": "WRONG_TYPE"}
        ),
    # 12. Optional integer stored as invalid string
    "optional_int_invalid_string": ValidationResult(
        "INVALID", {"forks_count": "WRONG_TYPE"}
        ),
    # 13. Boolean stored as integer
    "boolean_stored_as_integer": ValidationResult(
        "INVALID", {"private": "WRONG_TYPE"}
        ),
    # 15. Null optional field = None
    "null_optional_none": {"forks_count": None},
    # 16. Null optional field = empty string
    "null_optional_empty_string": {"forks_count": None},
    # 17. Null optional field = whitespace
    "null_optional_whitespace": {"forks_count": None}
}

expected_main_transformation = {
    # 1. Completely valid
    "completely_valid": transformed_valid_repo,
    # 2. Optional field missing
    "optional_field_missing": {
        **transformed_valid_repo,
        "repo_name": "optional_field_missing",
        "forks": None
   },
    # 8. Optional integer stored as numeric string (not a float)
    "optional_int_numeric_string": {
        **transformed_valid_repo,
        "repo_name": "optional_int_numeric_string",
        "forks": 12
   },
    # 9. Optional integer stored as numeric string (a float)
    "optional_int_float_string": {
        **transformed_valid_repo,
        "repo_name": "optional_int_float_string",
        "forks": 12
   },
    # 10. Optional integer stored as valid float
    "optional_int_valid_float": {
        **transformed_valid_repo,
        "repo_name": "optional_int_valid_float",
        "forks": 2
   },
    # 15. Null optional field = None
    "null_optional_none": {
        **transformed_valid_repo,
        "repo_name": "null_optional_none",
        "forks": None
    },
    # 16. Null optional field = empty string
    "null_optional_empty_string": {
        **transformed_valid_repo,
        "repo_name": "null_optional_empty_string",
        "forks": None
    },
    # 17. Null optional field = whitespace
    "null_optional_whitespace": {
        **transformed_valid_repo,
        "repo_name": "null_optional_whitespace",
        "forks": None
    }
    
}

expected_main_df = create_df(
    list(expected_main_transformation.values()),
    df_schema
)

expected_main_dtypes = pd.Series(
    {
        col: pd.api.types.pandas_dtype(typ)
        for col, typ in df_schema.items()
      }, name = 'Main'
   )

failed_validation_keys = (
    set(expected_validations)
    - set(expected_normalisations)
)

failed_normalisation_keys = (
    set(expected_normalisations)
    - set(expected_main_transformation)
)

failed_validations = {
    k: expected_validations[k]
    for k in failed_validation_keys
}


failed_normalisations = {
    k: expected_normalisations[k]
    for k in failed_normalisation_keys
}


failed_results = \
    failed_validations | failed_normalisations

expected_dlq = [
    {
        'repo_name': k,
        'raw_data': json.dumps(test_repos[k]),
        'issues': json.dumps(failed_results[k].show_issues())
    }
    for k in failed_results
]

expected_dlq_df = create_df(
    sort_repos(expected_dlq),
    dlq_schema
)

expected_dlq_dtypes = pd.Series(
    {
        col: pd.api.types.pandas_dtype(typ)
        for col, typ in dlq_schema.items()
        }, name = 'DLQ'
)
