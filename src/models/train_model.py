# Internal imports
from src.data.constants import PROCESSED_DATA_DIRECTORY
from src.models.constants import BENTOML_MODEL_TAG, MODEL_DIRECTORY

import argparse
import joblib
import bentoml
from pathlib import Path

import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_OUTPUT_PATH = MODEL_DIRECTORY / "model.pkl"
DEFAULT_X_TRAIN_PATH = PROCESSED_DATA_DIRECTORY / "X_train.csv"
DEFAULT_Y_TRAIN_PATH = PROCESSED_DATA_DIRECTORY / "y_train.csv"
DEFAULT_X_TEST_PATH = PROCESSED_DATA_DIRECTORY / "X_test.csv"
DEFAULT_Y_TEST_PATH = PROCESSED_DATA_DIRECTORY / "y_test.csv"


def load_training_data(
        x_train_path: Path = DEFAULT_X_TRAIN_PATH,
        y_train_path: Path = DEFAULT_Y_TRAIN_PATH,
) -> tuple[pd.DataFrame, pd.Series]:
    """Load prepared training features and target from disk."""
    X_train = pd.read_csv(x_train_path)
    y_train = pd.read_csv(y_train_path).iloc[:, 0]
    return X_train, y_train


def build_model(alpha: float = 1.0) -> Pipeline:
    """Create a simple and robust regression baseline for tabular data."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=alpha)),
        ]
    )


def train_model(x_train: pd.DataFrame, y_train: pd.Series, alpha: float = 1.0) -> Pipeline:
    """Fit the regression pipeline on the training data."""
    model = build_model(alpha=alpha)
    model.fit(x_train, y_train)
    return model


def save_model(model: Pipeline, output_path: Path = MODEL_OUTPUT_PATH) -> None:
    """Persist the trained model to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        joblib.dump(model, file)
    print(f"Model saved to {output_path}")


def register_model(tag: str, model) -> None:
    model_ref = bentoml.sklearn.save_model(tag, model=model)
    print(f"Modèle enregistré sous : {model_ref}")


def main(x_train_path, x_test_path, y_train_path, y_test_path, output_path, alpha=1.0) -> None:
    """Main entry point"""
    # Load training data
    x_train, y_train = load_training_data(x_train_path, y_train_path)

    # Load test data
    x_test, y_test = load_training_data(x_test_path, y_test_path)

    # Train mode
    model = train_model(x_train, y_train, alpha=alpha)
    save_model(model, output_path)
    register_model(BENTOML_MODEL_TAG, model)

    # Make predictions
    y_preds = model.predict(x_test)

    # Get scores
    mae = mean_absolute_error(y_test, y_preds)
    r2 = r2_score(y_test, y_preds)

    print(f"Test MAE: {mae:.4f}")
    print(f"Test R2: {r2:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train an admissions regression model.")
    parser.add_argument(
        "--x-train-path",
        type=Path,
        default=DEFAULT_X_TRAIN_PATH,
        help="Path to the processed training features CSV file.",
    )
    parser.add_argument(
        "--y-train-path",
        type=Path,
        default=DEFAULT_Y_TRAIN_PATH,
        help="Path to the processed training target CSV file.",
    )
    parser.add_argument(
        "--x-test-path",
        type=Path,
        default=DEFAULT_X_TEST_PATH,
        help="Path to the processed test features CSV file.",
    )
    parser.add_argument(
        "--y-test-path",
        type=Path,
        default=DEFAULT_Y_TEST_PATH,
        help="Path to the processed test target CSV file.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=MODEL_OUTPUT_PATH,
        help="Path where the trained model pickle will be saved.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Regularization strength for Ridge regression.",
    )
    args = parser.parse_args()
    main(**vars(args))
