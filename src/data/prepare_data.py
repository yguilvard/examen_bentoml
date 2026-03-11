import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.admission.constants import FEATURE_MAX_VALUES
# from src.data.normalize import normalize_features
from src.data.constants import PROCESSED_DATA_DIRECTORY, RANDOM_STATE, RAW_DATA_LOCAL_FILENAME, TEST_SIZE, USELESS_COLUMNS, TARGET_COLUMN



COLUMN_MAPPINGS = {
    "GRE Score": "gre_score",
    "TOEFL Score": "toefl_score",
    "University Rating": "rating",
    "SOP": "sop",
    "LOR": "lor",
    "CGPA": "cgpa",
    "Research": "research_xp",
    "Chance of Admit": "chances"
}


def load_dataset(file_path: Path = RAW_DATA_LOCAL_FILENAME) -> pd.DataFrame:
    """Load the admissions dataset from disk."""
    return pd.read_csv(file_path)


def process_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and remove rows that cannot be used for training."""
    processed = dataframe.copy()
    processed.columns = processed.columns.str.strip()

    # Remove useless columns, duplicates and rows with missing values.
    processed = processed.drop(columns=USELESS_COLUMNS, errors="ignore")
    processed = processed.drop_duplicates()
    processed = processed.dropna()

    # Rename columns to match the Student dataclass fields.
    processed = processed.rename(columns=COLUMN_MAPPINGS)

    # Apply the normalization function to the features (target column skipped)
    #processed = processed.apply(lambda row: normalize_features(row.to_dict()), axis=1)
    for column, max_value in FEATURE_MAX_VALUES.items():
        processed[column] = processed[column] / max_value
    
    return processed


def save_processed_data(
        x_train: pd.DataFrame,
        x_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        output_dir: Path = PROCESSED_DATA_DIRECTORY,
) -> None:
    """Persist processed datasets to the expected directory as CSV files."""
    # Creates the output directory if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the datasets as CSV files
    x_train.to_csv(output_dir / "X_train.csv", index=False)
    x_test.to_csv(output_dir / "X_test.csv", index=False)
    y_train.to_frame(name=TARGET_COLUMN).to_csv(output_dir / "y_train.csv", index=False)
    y_test.to_frame(name=TARGET_COLUMN).to_csv(output_dir / "y_test.csv", index=False)
    return


def prepare_data(
    input_path: Path = RAW_DATA_LOCAL_FILENAME,
    output_dir: Path = PROCESSED_DATA_DIRECTORY,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> None:
    """End-to-end data preparation pipeline."""
    # Loading the Raw Dataset
    dataset = load_dataset(input_path)

    # Preparing the data
    cleaned_dataset = process_dataset(dataset)

    # Split the dataset into features and target
    y = cleaned_dataset[TARGET_COLUMN]
    X = cleaned_dataset.drop(columns=[TARGET_COLUMN])

    # Split the dataset into training and test sets
    x_train, x_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
    )
    save_processed_data(x_train, x_test, y_train, y_test, output_dir=output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare admissions data for training.")
    parser.add_argument(
        "--input-path",
        type=Path,
        default=RAW_DATA_LOCAL_FILENAME,
        help="Path to the raw admissions CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROCESSED_DATA_DIRECTORY,
        help="Directory where processed datasets will be written.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=TEST_SIZE,
        help="Proportion of rows reserved for the test set.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=RANDOM_STATE,
        help="Seed used to make the train/test split reproducible.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    prepare_data(
        input_path=arguments.input_path,
        output_dir=arguments.output_dir,
        test_size=arguments.test_size,
        random_state=arguments.random_state,
    )
