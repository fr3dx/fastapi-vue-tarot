from fastapi import FastAPI, HTTPException

# Root endpoint definition.
# This route is useful for simple health checks or confirming the API is online.
@app.get("/")
async def read_root():
    """
    Basic root endpoint that returns a simple message to confirm the API service is operational.
    """
    return {"message": "Tarot API is running."}

# Note:
# To run this FastAPI application:
# - Save the relevant code to 'main.py' and supporting modules accordingly.
# - Ensure a '.env' file exists with your environment variables (e.g., database credentials).
# - Run the app using Uvicorn in your terminal:
#     uvicorn main:app --reload
# Make sure your working directory and virtual environment are correctly set.
