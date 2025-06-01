from pydantic import BaseModel

class TokenOut(BaseModel):
    """
    Response model for token issuance.

    Used when returning access and refresh tokens to the client after successful authentication.

    Attributes:
    - access_token (str): The JWT access token used for authenticated API access.
    - token_type (str): The type of token issued (typically "bearer").
    - refresh_token (str): The token used to obtain a new access token when the original expires.
    """
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class TokenIn(BaseModel):
    """
    Request model for token-based operations (e.g., login or validation).

    Attributes:
    - token (str): A JWT or similar token sent by the client for authentication or verification.
    - lang (str): Language code (e.g., "en", "hu") indicating the desired response language.
    """
    token: str
    lang: str


class UserData(BaseModel):
    """
    Represents user identity information extracted from a token.

    Typically used after decoding or validating an authentication token.

    Attributes:
    - sub (str): Unique subject identifier (usually user ID or UUID).
    - email (str): The user's email address.
    - name (str): The user's full display name.
    """
    sub: str
    email: str
    name: str


class RefreshTokenRequest(BaseModel):
    """
    Request model for refreshing an access token using a refresh token.

    Attributes:
    - refresh_token (str): A valid refresh token previously issued to the client.
    """
    refresh_token: str
