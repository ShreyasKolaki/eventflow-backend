from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# -------------------------------
# CORS CONFIGURATION
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eventflow-frontend-eta.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# MongoDB connection
# -------------------------------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["users"]
users_collection = db["user"]

# -------------------------------
# Home
# -------------------------------
@app.get("/")
def home():
    return {"message": "Backend is working 🚀"}

# -------------------------------
# Register User
# -------------------------------
@app.post("/register")
def register_user(user: dict):

    email = user.get("email", "").strip()
    username = user.get("username", "").strip()
    password = user.get("password", "").strip()

    if not email or not username or not password:
        return {"message": "All fields required"}

    existing_user = users_collection.find_one({
        "$or": [
            {"email": email},
            {"username": username}
        ]
    })

    if existing_user:
        return {"message": "User already exists"}

    user_data = {
        "email": email,
        "username": username,
        "password": password,
        "registered_events": []
    }

    users_collection.insert_one(user_data)

    return {"message": "User registered successfully"}

# -------------------------------
# Login User
# -------------------------------
@app.post("/login")
def login_user(user: dict):

    email_or_username = user.get("email_or_username", "").strip()
    password = user.get("password", "").strip()

    if not email_or_username or not password:
        return {"message": "All fields required"}

    # find user by email OR username
    existing_user = users_collection.find_one({
        "$or": [
            {"email": email_or_username},
            {"username": email_or_username}
        ]
    })

    if not existing_user:
        return {"message": "Invalid credentials"}

    # check password manually
    if existing_user["password"] != password:
        return {"message": "Invalid credentials"}

    return {
        "message": "Login successful",
        "username": existing_user["username"]
    }

# -------------------------------
# Get All Events
# -------------------------------
@app.get("/events")
def get_events():

    return {
        "sports": ["Cricket", "Football", "Basketball"],
        "cultural": ["Dance", "Drama", "Singing"],
        "tech": ["Hackathon", "Debugging", "Coding Contest"]
    }

# -------------------------------
# Register for Event
# -------------------------------
@app.post("/register-event")
def register_event(data: dict):

    username = data.get("username", "").strip()
    event = data.get("event", "").strip()

    if not username or not event:
        return {"message": "Missing data"}

    user = users_collection.find_one({"username": username})

    if not user:
        return {"message": "User not found"}

    if event in user.get("registered_events", []):
        return {"message": "Already registered for this event"}

    users_collection.update_one(
        {"username": username},
        {"$push": {"registered_events": event}}
    )

    return {"message": f"Registered for {event}"}

# -------------------------------
# Profile Page
# -------------------------------
@app.get("/profile/{username}")
def get_profile(username: str):

    username = username.strip()

    user = users_collection.find_one(
        {"username": username},
        {"_id": 0, "password": 0}
    )

    if not user:
        return {"message": "User not found"}

    return user