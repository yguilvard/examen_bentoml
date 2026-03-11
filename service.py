# Internal imports
from src.data.normalize import normalize_features
from src.api.tokens import APIToken
from src.adapters.users_fs import UsersDB
from src.adapters.tokens_fs import TokensDB
from src.admission.errors import InvalidTokenError, ScoreTooHighError, ScoreTooLowError
from src.models.constants import BENTOML_MODEL_TAG, BENTOML_MODEL_VERSION


# Python
import logging
from typing import Dict

# Third-party libraries
import bentoml
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Application logger
logger = logging.getLogger(__name__)

# Models


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionRequest(BaseModel):
    gre_score: float
    toefl_score: float
    rating: float
    sop: float
    lor: float
    cgpa: float
    research_xp: float


# =============================================== #
#          FASTAPI: AUTHENTICATION                #
# =============================================== #
auth_app = FastAPI(title="Login API")


@auth_app.post("/login", response_model=TokenResponse)
def login(credential: LoginRequest) -> TokenResponse:
    """Issue a JWT token used to call the protected /predict endpoint."""
    userdb = UsersDB()
    tokensdb = TokensDB()
    user = userdb.get_user(credential.username)
    if user is not None:
        if user.check_password(credential.password):
            token = tokensdb.create_token(username=credential.username)
            logger.info("Login succeeded for user=%s", credential.username)
            return TokenResponse(access_token=token.token)
    logger.warning("Login failed for user=%s", credential.username)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials.")


# =============================================== #
#             BENTOML: PREDICTIONS                #
# =============================================== #
@bentoml.asgi_app(auth_app, path="/")
@bentoml.service(name="admission")
class AdmissionService:
    def __init__(self) -> None:
        self.model = bentoml.sklearn.load_model(
            ":".join([BENTOML_MODEL_TAG, BENTOML_MODEL_VERSION]))

    @bentoml.api(route="/predict")
    def predict(self, request: PredictionRequest, ctx: bentoml.Context) -> Dict[str, float | str]:
        """Predict the admission probability for an authenticated request."""
        try:
            payload = authenticate_request(
                ctx.request.headers.get("authorization", ""))
        except InvalidTokenError as exc:
            logger.warning("Prediction rejected: %s", exc)
            ctx.response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"error": str(exc)}

        try:
            features = pd.DataFrame(
                [normalize_features(request.model_dump())])
        except (ScoreTooHighError, ScoreTooLowError) as exc:
            logger.warning("Prediction rejected: %s", exc)
            ctx.response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": str(exc)}

        prediction = float(self.model.predict(features)[0])  # type: ignore
        logger.info("Prediction succeeded for user=%s", payload["sub"])
        return {'prediction': prediction}


def authenticate_request(authorization_header: str) -> dict:
    """Validate the bearer token and ensure it is stored for the expected user."""
    tokensdb = TokensDB()
    # Check the Authorization header is in the expected format and extract the token
    if not len(authorization_header) or not authorization_header.startswith("Bearer "):
        raise InvalidTokenError("Missing or invalid Authorization header.")
    # Extract the token from the Authorization header
    token = APIToken.extract_bearer_token(authorization_header)
    if token is None:
        raise InvalidTokenError("Missing or invalid Authorization header.")
    # Decode the token to get the username and check if the token is active for this user
    payload = APIToken.decode_access_token(token)
    stored_tokens = tokensdb.list_active_tokens()
    for token_record in stored_tokens:
        if token_record["token"] == token and token_record["username"] == payload["sub"]:
            return payload
    raise InvalidTokenError("Unknown or expired token.")
