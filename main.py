from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# This defines what data we expect Node to send us (like TypeScript types)
class RecommendationRequest(BaseModel):
    student_id: str

@app.post("/recommendations")
async def get_test_recommendation(data: RecommendationRequest):
    # This is a test response to prove the connection works
    return {
        "status": "success",
        "message": f"Hello from Python! Engine processed data for student: {data.student_id}",
        "recommended_courses": ["Python-101", "Data-Science-202"]
    }
