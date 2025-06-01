from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

# Exception handler registration: Attaches custom handlers for various exception types.
def setup_exception_handlers(app):
    """
    Registers custom exception handlers for the FastAPI application.
    
    This includes handlers for HTTP exceptions, validation errors, and uncaught exceptions.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handles HTTP exceptions raised within routes or by the framework.
        Returns a JSON response with the appropriate status code and message.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handles validation errors raised by FastAPI/Pydantic.
        Returns a 422 response with details about the validation issues.
        """
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation failed",
                "details": exc.errors()
            },
        )
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """
        Handles rate limit exceeded errors raised by SlowAPI.
        Returns a user-friendly 429 response with a clear message.
        """
        return JSONResponse(
            status_code=429,
            content={"error": True, "message": "Too many requests. Please try again in a minute."},
        )


    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Handles uncaught exceptions that were not matched by more specific handlers.
        Can be extended to include logging for better observability.
        """
        # Logging could be implemented here for production environments
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "Internal server error"},
        )
