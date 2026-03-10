from pathlib import Path

MODEL_DIRECTORY = Path(__file__).parent.parent.parent / "models"
MODEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
BENTOML_MODEL_TAG = "admission_ridge"
BENTOML_MODEL_VERSION = "latest"
