import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import asyncio

# Load variables from .env into os.environ
load_dotenv()

app = FastAPI()

# Whitelist your frontend origins explicitly, now they make browser-based requests to "warmup" endpoint which requires them to support CORS
allowed_origins = os.getenv("ALLOWED_CORS_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL == None:
    raise Exception("Missing database connectionstring")

# Create the database connection engine
engine = create_engine(DATABASE_URL)

# This defines what data we expect Node to send us (like TypeScript types)
class RecommendationRequest(BaseModel):
    api_username: str
    api_password: str
    student_id: str
    max_records: int

@app.get("/warmup")
async def health_check():
    #await asyncio.sleep(5)
    return {"status": "ok"}

@app.post("/recommendations")
async def get_live_recommendation(data: RecommendationRequest):
    target_student_id = data.student_id
    req_max_records = data.max_records

    max_records = int(req_max_records) if (req_max_records and req_max_records > 0) else 10
    
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
    query = text("""
        SELECT student_id, class_id 
        FROM enrollments;
    """)
    
    # Structure the data exactly how our algorithm expects it
    mock_enrollments = {}
    
    with engine.connect() as connection:
        result = connection.execute(query)
        for row in result:
            student = str(row.student_id)
            classID = str(row.class_id)
            
            if student not in mock_enrollments:
                mock_enrollments[student] = []
            mock_enrollments[student].append(classID)

    '''
    Run the recommendation algorithm logic
    First, Python looks up the logged-in student (e.g., student_1) and extracts a unique 
    list of classes they have already joined. We convert this list into a Python set()
    '''
    target_classes = set(mock_enrollments.get(target_student_id, []))
    peer_class_counts = {}
    '''
    Loop through every other student in the database.
    For each peer, it turns their classes into a set as well.
    Then, it checks for an overlap using intersection():
    '''
    for student_id, classes in mock_enrollments.items():
        if student_id == target_student_id:
            continue
            
        peer_classes = set(classes)
        '''
        This is a mathematical check.
        If the target student and the peer share at least one class in common, this returns True.
        If they share zero classes, Python ignores this peer and skips to the next one.
        This filters out noise from unrelated departments.
        '''
        if target_classes.intersection(peer_classes):
            '''
            Once Python finds a peer who shares a class, it needs to know:
               "What else is this peer taking that our target student hasn't discovered yet?"
            The minus sign (-) in Python sets performs a set difference.
            It takes the peer's classes and completely subtracts the target student's classes.
            '''
            recommendations = peer_classes - target_classes
            '''
            Python loops through these newly discovered candidate classes and logs them into a tally dictionary of 1..n
            '''
            for classID in recommendations:
                peer_class_counts[classID] = peer_class_counts.get(classID, 0) + 1
                
    # Calculate percentage scores
    final_suggestions = []

    if peer_class_counts:
        # Sort recommendations by the highest count first
        all_sorted_recommendations = sorted(peer_class_counts.items(), key=lambda x: x[1], reverse=True)
    	
        # Identify the highest vote count to use as our 100% baseline
        highest_count = all_sorted_recommendations[0][1]

        topN_sorted_recommendations = all_sorted_recommendations[:max_records]
        
        # Calculate relative percentages for each class
        for classID, count in topN_sorted_recommendations:
            # Formula: (current_count / highest_count) * 100 {round() keeps the decimal clean for the frontend UI}
            percentage_score = round((count / highest_count) * 100)
            
            final_suggestions.append({
                "classId": classID,
                # "match_strength": f"{percentage_score}%"
                "match_strength": percentage_score
            })
    
    # Return the enriched results
    return {
        "status": "success",
        "processed_student": target_student_id,
        # "current_enrollments": list(target_classes),  << currently not required by frontend
        "recommended_classes": final_suggestions
    }