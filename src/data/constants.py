import os
from pathlib import Path

# Dataset paths and URLs
DATA_DIRECTORY = Path(os.environ.get('ADMISSION_DATA_DIRECTORY', Path(__file__).parent.parent.parent / "data"))
RAW_DATA_LOCAL_DIRECTORY = DATA_DIRECTORY / 'raw'
RAW_DATA_LOCAL_FILENAME = RAW_DATA_LOCAL_DIRECTORY / 'admissions.csv'
RAW_DATA_URL = "https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv"

# PROCESSED DATA
PROCESSED_DATA_DIRECTORY = DATA_DIRECTORY / 'processed'

# Data sets
TEST_SIZE = 0.2
RANDOM_STATE = 42
