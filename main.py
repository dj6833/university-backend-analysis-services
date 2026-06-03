import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text


# Load variables from .env into os.environ
load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL == None:
    raise Exception("Missing database connectionstring")

# DATABASE_URL = "postgresql://neondb_owner:npg_XcdAFq9mOg0B@ep-aged-credit-ab5fjad4-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
# Create the database connection engine
engine = create_engine(DATABASE_URL)

# This defines what data we expect Node to send us (like TypeScript types)
class RecommendationRequest(BaseModel):
    api_username: str
    api_password: str
    student_id: str

@app.post("/recommendations")
async def get_live_recommendation(data: RecommendationRequest):
    target_student_id = data.student_id
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
    
    # Fetch enrollment data live from your PostgreSQL database
    # (Note: Update 'enrollments', 'student_id', and 'class_id' to match your actual column names)
    query = text("""
        SELECT student_id, class_id 
        FROM enrollments;
    """)
    
    # 3. Structure the data exactly how our algorithm expects it
    mock_enrollments = {}
    
    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            student = str(row.student_id)
            course = str(row.class_id)
            
            if student not in mock_enrollments:
                mock_enrollments[student] = []
            mock_enrollments[student].append(course)

    # 4. Run the recommendation algorithm logic
    target_classes = set(mock_enrollments.get(target_student_id, []))
    peer_class_counts = {}
    
    for student_id, classes in mock_enrollments.items():
        if student_id == target_student_id:
            continue
            
        peer_classes = set(classes)
        
        if target_classes.intersection(peer_classes):
            recommendations = peer_classes - target_classes
            for course in recommendations:
                peer_class_counts[course] = peer_class_counts.get(course, 0) + 1
                
    sorted_recommendations = sorted(peer_class_counts.items(), key=lambda x: x[1], reverse=True)
    final_suggestions = [course for course, count in sorted_recommendations]
    
    # 5. Return the real results back to Node
    return {
        "status": "success",
        "processed_student": target_student_id,
        "current_enrollments": list(target_classes),
        "recommended_courses": final_suggestions
    }