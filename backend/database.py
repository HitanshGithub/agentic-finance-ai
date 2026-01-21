from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional

load_dotenv()

# MongoDB connection with SSL fix for Render
MONGODB_URI = os.getenv("MONGODB_URI")

try:
    import certifi
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsCAFile=certifi.where()
    )
except:
    # Fallback: allow invalid certificates (for platforms with SSL issues)
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        tls=True,
        tlsAllowInvalidCertificates=True
    )

db = client["finance_db"]

# Collections
analyses_collection = db["analyses"]
users_collection = db["users"]
goals_collection = db["savings_goals"]
chat_history_collection = db["chat_history"]


# ===== USER AUTHENTICATION =====

def create_user(email: str, password_hash: str, is_verified: bool = False) -> str:
    """Create a new user and return the user ID."""
    document = {
        "email": email.lower(),
        "password_hash": password_hash,
        "is_verified": is_verified,
        "google_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    inserted = users_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_user_by_email(email: str) -> Optional[dict]:
    """Get a user by email address."""
    doc = users_collection.find_one({"email": email.lower()})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get a user by ID."""
    from bson.objectid import ObjectId
    try:
        doc = users_collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except:
        return None


def verify_user_email(email: str) -> bool:
    """Mark a user's email as verified."""
    print(f"🔍 Verifying email: {email.lower()}")
    result = users_collection.update_one(
        {"email": email.lower()},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )
    print(f"   Matched: {result.matched_count}, Modified: {result.modified_count}")
    # Use matched_count instead of modified_count so it works even if already verified
    return result.matched_count > 0


def get_user_by_google_id(google_id: str) -> Optional[dict]:
    """Get a user by Google ID."""
    doc = users_collection.find_one({"google_id": google_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def create_or_update_google_user(google_id: str, email: str, name: str = "", picture: str = "") -> dict:
    """Create or update a user from Google OAuth."""
    existing = get_user_by_google_id(google_id)
    if existing:
        # Update existing user
        users_collection.update_one(
            {"google_id": google_id},
            {"$set": {"name": name, "picture": picture, "updated_at": datetime.utcnow()}}
        )
        existing["name"] = name
        existing["picture"] = picture
        return existing
    
    # Check if email already exists (user signed up with email first)
    email_user = get_user_by_email(email)
    if email_user:
        # Link Google account to existing email user
        users_collection.update_one(
            {"email": email.lower()},
            {"$set": {
                "google_id": google_id, 
                "is_verified": True,  # Google users are auto-verified
                "name": name,
                "picture": picture,
                "updated_at": datetime.utcnow()
            }}
        )
        email_user["google_id"] = google_id
        email_user["is_verified"] = True
        return email_user
    
    # Create new user
    document = {
        "email": email.lower(),
        "password_hash": None,  # Google users don't have password
        "is_verified": True,  # Google users are auto-verified
        "google_id": google_id,
        "name": name,
        "picture": picture,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    inserted = users_collection.insert_one(document)
    document["_id"] = str(inserted.inserted_id)
    return document


# ===== FINANCE ANALYSIS (Per-User) =====

def save_analysis(user_id: str, income: float, profile: str, expenses: list, result: dict) -> str:
    """Save an analysis to MongoDB and return the inserted ID."""
    document = {
        "user_id": user_id,
        "income": income,
        "profile": profile,
        "expenses": expenses,
        "result": result,
        "created_at": datetime.utcnow()
    }
    inserted = analyses_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_all_analyses(user_id: str, limit: int = 10) -> list:
    """Get recent analyses from MongoDB for a specific user."""
    cursor = analyses_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    analyses = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        analyses.append(doc)
    return analyses


def get_analysis_by_id(user_id: str, analysis_id: str) -> dict:
    """Get a specific analysis by ID (only if owned by user)."""
    from bson.objectid import ObjectId
    doc = analyses_collection.find_one({"_id": ObjectId(analysis_id), "user_id": user_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ===== SAVINGS GOALS (Per-User) =====

def save_goal(user_id: str, name: str, target: float, current: float = 0, deadline: str = None) -> str:
    """Create a new savings goal for a user."""
    document = {
        "user_id": user_id,
        "name": name,
        "target": target,
        "current": current,
        "deadline": deadline,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    inserted = goals_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_all_goals(user_id: str) -> list:
    """Get all savings goals for a specific user."""
    cursor = goals_collection.find({"user_id": user_id}).sort("created_at", -1)
    goals = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        goals.append(doc)
    return goals


def update_goal(user_id: str, goal_id: str, updates: dict) -> bool:
    """Update a savings goal (only if owned by user)."""
    from bson.objectid import ObjectId
    updates["updated_at"] = datetime.utcnow()
    result = goals_collection.update_one(
        {"_id": ObjectId(goal_id), "user_id": user_id},
        {"$set": updates}
    )
    return result.modified_count > 0


def delete_goal(user_id: str, goal_id: str) -> bool:
    """Delete a savings goal (only if owned by user)."""
    from bson.objectid import ObjectId
    result = goals_collection.delete_one({"_id": ObjectId(goal_id), "user_id": user_id})
    return result.deleted_count > 0


def get_goal_by_id(user_id: str, goal_id: str) -> dict:
    """Get a specific goal by ID (only if owned by user)."""
    from bson.objectid import ObjectId
    doc = goals_collection.find_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ===== CHAT HISTORY (Per-User) =====

def save_chat_message(user_id: str, role: str, content: str) -> str:
    """Save a chat message for a user."""
    document = {
        "user_id": user_id,
        "role": role,  # "user" or "assistant"
        "content": content,
        "created_at": datetime.utcnow()
    }
    inserted = chat_history_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_chat_history(user_id: str, limit: int = 50) -> list:
    """Get chat history for a user."""
    cursor = chat_history_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    messages = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        messages.append(doc)
    return list(reversed(messages))  # Return in chronological order


def clear_chat_history(user_id: str) -> bool:
    """Clear all chat history for a user."""
    result = chat_history_collection.delete_many({"user_id": user_id})
    return result.deleted_count > 0


# ===== TRENDS & ANALYTICS (Per-User) =====

def get_monthly_trends(user_id: str, months: int = 6) -> list:
    """Get monthly spending trends from analysis history for a specific user."""
    from datetime import timedelta
    
    # Get analyses from the last N months
    cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
    cursor = analyses_collection.find(
        {"user_id": user_id, "created_at": {"$gte": cutoff_date}}
    ).sort("created_at", 1)
    
    monthly_data = {}
    
    for doc in cursor:
        date = doc.get("created_at", datetime.utcnow())
        month_key = date.strftime("%Y-%m")
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_key,
                "total_income": 0,
                "total_expenses": 0,
                "analyses_count": 0,
                "categories": {}
            }
        
        monthly_data[month_key]["total_income"] += doc.get("income", 0)
        monthly_data[month_key]["analyses_count"] += 1
        
        for exp in doc.get("expenses", []):
            cat = exp.get("category", "Other")
            amt = exp.get("amount", 0)
            monthly_data[month_key]["total_expenses"] += amt
            
            if cat not in monthly_data[month_key]["categories"]:
                monthly_data[month_key]["categories"][cat] = 0
            monthly_data[month_key]["categories"][cat] += amt
    
    return list(monthly_data.values())


def get_category_trends(user_id: str, months: int = 6) -> dict:
    """Get spending by category over time for a specific user."""
    trends = get_monthly_trends(user_id, months)
    
    category_totals = {}
    for month in trends:
        for cat, amount in month.get("categories", {}).items():
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += amount
    
    # Sort by total spending
    sorted_categories = sorted(
        category_totals.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    return {
        "categories": dict(sorted_categories),
        "monthly_breakdown": trends
    }
