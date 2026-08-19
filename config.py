from dotenv import load_dotenv
import os

load_dotenv()

api_credentials = {
    'url': 'https://api.github.com/user/repos',
    'token': os.getenv('GITHUB_TOKEN')
}

schema = {
    'name': {
        'source_name': 'name',
        'output_name': 'repo_name',
        'type': str,
        'default': None,
        'required': True
    },
    'private': {
        'source_name': 'private',
        'output_name': 'private',
        'type': bool,
        'default': None,
        'required': False
    },
    'language': {
        'source_name': 'language',
        'output_name': 'language',
        'type': str,
        'default': None,
        'required': True
    },
    'has_discussions': {
        'source_name': 'has_discussions',
        'output_name': 'has_discussions',
        'type': bool,
        'default': None,
        'required': False
    },
    'has_projects': {
        'source_name': 'has_projects',
        'output_name': 'has_projects',
        'type': bool,
        'default': None,
        'required': False
    },
    'has_pages': {
        'source_name': 'has_pages',
        'output_name': 'has_pages',
        'type': bool,
        'default': None,
        'required': False
    },
    'size': {
        'source_name': 'size',
        'output_name': 'size',
        'type': int,
        'default': None,
        'required': True
    },
    'forks_count': {
        'source_name': 'forks_count',
        'output_name': 'forks',
        'type': int,
        'default': None,
        'required': False # changed from True
    },
    'open_issues_count': {
        'source_name': 'open_issues_count',
        'output_name': 'open_issues',
        'type': int,
        'default': None,
        'required': True
    },
    'stargazers_count': {
        'source_name': 'stargazers_count',
        'output_name': 'stargazers',
        'type': int,
        'default': None,
        'required': True
    },
    'watchers_count': {
        'source_name': 'watchers_count',
        'output_name': 'watchers',
        'type': int,
        'default': None,
        'required': True
    }
}

df_schema = {
    'repo_name': str,
    'language': str,
    'size': int,
    'open_issues': int,
    'stargazers': int,
    'watchers': int,
    'forks': "Int64",
    'private': "boolean",
    'has_projects': "boolean",
    'has_pages': "boolean",
    'has_discussions': "boolean"
}

dlq_schema = {
    'repo_name': str,
    'raw_data': str,
    'issues': str
}

type_policy = {
    int: [int, float, str],
    str: [str],
    bool: [bool]
}

required_results = {
    True: "Required",
    False: "Optional"
}

conditions = {
    "null": "IS_NULL",
    "type": "WRONG_TYPE",
    "exists": "MISSING"
}

invalid_warnings = {
    "Required field is null",
    "Required field is of wrong type",
    "Required field does not exist"
}

valid_warnings = {
    "Optional field is null",
    "Optional field is of wrong type",
    "Optional field does not exist"
}

missing_values = {
    None,
    ""
}