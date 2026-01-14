from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from datetime import datetime
import certifi

load_dotenv()

# MongoDB connection with SSL certificate fix
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    tls=True,
    tlsCAFile=certifi.where()
)
db = client["finance_db"]

# Collections
analyses_collection = db["analyses"]
users_collection = db["users"]


def save_analysis(income: float, profile: str, expenses: list, result: dict) -> str:
    """Save an analysis to MongoDB and return the inserted ID."""
    document = {
        "income": income,
        "profile": profile,
        "expenses": expenses,
        "result": result,
        "created_at": datetime.utcnow()
    }
    inserted = analyses_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_all_analyses(limit: int = 10) -> list:
    """Get recent analyses from MongoDB."""
    cursor = analyses_collection.find().sort("created_at", -1).limit(limit)
    analyses = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        analyses.append(doc)
    return analyses


def get_analysis_by_id(analysis_id: str) -> dict:
    """Get a specific analysis by ID."""
    from bson.objectid import ObjectId
    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc
