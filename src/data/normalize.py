from src.data.constants import TARGET_COLUMN
from src.admission.constants import FEATURE_MAX_VALUES
from src.admission.errors import ScoreTooHighError, ScoreTooLowError


def normalize_features(raw_features: dict[str, float]) -> dict[str, float]:
    """Validate and normalize raw API inputs to the model feature scale."""

    normalized_features: dict[str, float] = {}

    # Validate and normalize each feature value based on the defined maximum values.
    for feature, raw_value in raw_features.items():
        if feature == TARGET_COLUMN:
            # Skip normalization for the target column.
            normalized_features[feature] = raw_value
            continue

        # Check if the raw value is negative, which is invalid for all features.
        if float(raw_value) < 0.0:
            raise ScoreTooLowError(feature, raw_value)

        max_value = FEATURE_MAX_VALUES[feature]
        # Check if the max value for the feature is defined in the constants.
        if max_value is None:
            raise ValueError(f"Missing max value for feature {feature}")

        # Check if the raw value exceeds the maximum allowed value for the feature.
        if raw_value > max_value:
            raise ScoreTooHighError(feature, raw_value, max_value)

        # Normalize the feature value to the range [0, 1] by dividing by the max value.
        normalized_features[feature] = raw_value / max_value

    return normalized_features
