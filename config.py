import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

dev_env = Path(".dev_env")
# This is commented out to prevent the production environment from running
prod_env = Path(".env_prodx")

if dev_env.is_file():
    print('loading dev')
    config = {
        **dotenv_values(".env"),
        **dotenv_values(".dev_env"),
    }
elif prod_env.is_file():
    print('loading prod')
    config = {
        **dotenv_values(".env"),
        **dotenv_values(".env_prod"),
    }
else:
    load_dotenv()
    config = os.environ


def configure_database_environment_variables(
    old_database_location: str, database_location: str
) -> None:
    """
    configure the database environment variables.

    By default, there is one set of environment variables for the old database as well as for the
    new Ontology Database. This function will prepend old_database_location to the old database
    environment variables and will prepend database location to the database environment variable.

    This enables the code to have multiple set of database variables and to switch between them in the
    code without having to modify .env file.

    This is important for:

    1. Development: The developer needs to frequently switch between localhost and remote database locations
    in order to ensure that the code is working across multiple locations.

    2. Testing: This feature enables the code to test against multiple database dialects, locations, and users.

    3. Administration: The admin will want to run the Ontology Database Tool for configuring databases. Or to run
    backend scripts such as database backup. This feature will enable multiple customer database locations to
    be executed.

    Args:
        old_database_location:
        database_location:

    Returns: None

    """
    old_database_envs = [
        "old_database_user",
        "old_database_password",
        "old_database_host",
        "old_database_port",
        "old_database_name",
        "old_database_schema_name",
    ]

    for env in old_database_envs:
        config[env] = config[old_database_location + env]

    database_envs = [
        "database_user",
        "database_password",
        "database_host",
        "database_port",
        "database_name",
        "database_schema_name",
    ]

    for env in database_envs:
        config[env] = config[database_location + env]


configure_database_environment_variables(
    config["old_database_location"], config["database_location"]
)

ENTITY_LIST = [
    "actor",
    "app",
    "artist",
    "brand",
    "category",
    "category_hierarchy",
    "company",
    "division",
    "education_level",
    "entity_type",
    "ethnicity",
    "franchise",
    "gender",
    "generation",
    "genre",
    "has_children",
    "household_size",
    "marital_status",
    "political_affiliation",
    "product",
    "property_value",
    "region",
    "residence",
    "space",
    "sport",
    "sport_league",
    "sport_team",
    "sport_team_league",
    "state",
    "theatre_title",
    "ticker",
    "time",
    "time_table",
    "time_type",
    "title",
    "venue",
    "yearly_income",
]

DATASET_LIST = [
    "alligator",
    "android",
    "brand",
    "ios",
    "cheetah",
    "ferret",
    "ferret_retailer",
    "genre",
    "koala",
    "mockingbird",
    "monkey",
    "moose",
    "natterjack",
    "panther",
    "peacock",
    "platypus",
    "porcupine",
    "stork",
    "stork_ios_android",
    "swan",
    "tapir",
    "value_koala",
    "concert_venue",
]
ACTION_LIST = ["map", "fuzzymatch", "import", "exp", "history"]
