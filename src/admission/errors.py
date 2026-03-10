class AdmissionError(Exception):
    """Base class for exceptions in this module."""
    pass

class AuthenticationError(AdmissionError):
    """Exception raised for authentication failures."""
    pass

class PredictionError(AdmissionError):
    """Exception raised for errors during prediction."""
    pass

class ScoreTooHighError(AdmissionError):
    """Exception raised for errors in the input data."""
    def __init__(self, field_name: str, value: float, max_value: float):
        self.field_name = field_name
        self.value = value
        self.max_value = max_value
        super().__init__(f"Invalid value received for field {field_name}: {value} > {max_value}")

class ScoreTooLowError(AdmissionError):
    """Exception raised for errors in the input data."""
    def __init__(self, field_name: str, value: float):
        self.field_name = field_name
        self.value = value
        super().__init__(f"Invalid value received for field {field_name}: {value} < 0")

class InvalidTokenError(AuthenticationError):
    """Exception raised for invalid JWT tokens."""
    pass
