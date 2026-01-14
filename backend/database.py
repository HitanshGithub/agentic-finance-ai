from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from datetime import datetime

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


# ===== SAVINGS GOALS =====

def save_goal(name: str, target: float, current: float = 0, deadline: str = None) -> str:
    """Create a new savings goal."""
    document = {
        "name": name,
        "target": target,
        "current": current,
        "deadline": deadline,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    inserted = goals_collection.insert_one(document)
    return str(inserted.inserted_id)


def get_all_goals() -> list:
    """Get all savings goals."""
    cursor = goals_collection.find().sort("created_at", -1)
    goals = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        goals.append(doc)
    return goals


def update_goal(goal_id: str, updates: dict) -> bool:
    """Update a savings goal."""
    from bson.objectid import ObjectId
    updates["updated_at"] = datetime.utcnow()
    result = goals_collection.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": updates}
    )
    return result.modified_count > 0


def delete_goal(goal_id: str) -> bool:
    """Delete a savings goal."""
    from bson.objectid import ObjectId
    result = goals_collection.delete_one({"_id": ObjectId(goal_id)})
    return result.deleted_count > 0


def get_goal_by_id(goal_id: str) -> dict:
    """Get a specific goal by ID."""
    from bson.objectid import ObjectId
    doc = goals_collection.find_one({"_id": ObjectId(goal_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ===== TRENDS & ANALYTICS =====

def get_monthly_trends(months: int = 6) -> list:
    """Get monthly spending trends from analysis history."""
    from datetime import timedelta
    
    # Get analyses from the last N months
    cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
    cursor = analyses_collection.find(
        {"created_at": {"$gte": cutoff_date}}
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


def get_category_trends(months: int = 6) -> dict:
    """Get spending by category over time."""
    trends = get_monthly_trends(months)
    
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

