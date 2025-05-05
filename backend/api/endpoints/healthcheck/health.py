from fastapi import APIRouter

router = APIRouter(tags=["health"])
# Healthcheck endpoint definition.
@router.get("/health")
async def health():
    """
    Basic root endpoint that returns a simple message to confirm the API service is operational.
    """
    return {"message": "running."}

# Note:
# To run this FastAPI application:
# - Save the relevant code to 'main.py' and supporting modules accordingly.
# - Ensure a '.env' file exists with your environment variables (e.g., database credentials).
# - Run the app using Uvicorn in your terminal:
#     uvicorn main:app --reload
# Make sure your working directory and virtual environment are correctly set.
