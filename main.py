import os
from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel

# Load variables from .env into os.environ
load_dotenv()

app = FastAPI()

# This defines what data we expect Node to send us (like TypeScript types)
class RecommendationRequest(BaseModel):
    api_username: str
    api_password: str
    student_id: str

@app.post("/recommendations")
async def get_test_recommendation(data: RecommendationRequest):
    # This is a test response to prove the connection works
    # todo: replace temporary user & pwd approach with JWT or similar if not using a private network across hosting platforms
    reqUser = os.getenv("RECOMMEND_ENROLLMENTS_API_USERNAME")
    reqPwd = os.getenv("RECOMMEND_ENROLLMENTS_API_PASSWORD")
    if reqUser == None or reqPwd == None:
        return {
                "status": "fail",
                "message": "Internal error: Unable to validate credentials"
        } 

    if data.api_username != reqUser or data.api_password != reqPwd :
        return {
            "status": "fail",
            "message": "Incorrect username or password"
    }        

    return {
        "status": "success",
        "message": f"Hello from Python! Engine processed data for student: {data.student_id}",
        "recommended_courses": ["Python-101", "Data-Science-202"]
    }
