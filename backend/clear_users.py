"""
Script to clear all user data from the database.
Run this script to reset all users and start fresh.
"""
from database import users_collection, analyses_collection, goals_collection, chat_history_collection

def clear_all_user_data():
    """Clear all user-related data from the database."""
    print("🔥 Clearing all user data...")
    
    # Delete all users
    users_result = users_collection.delete_many({})
    print(f"   - Deleted {users_result.deleted_count} users")
    
    # Delete all analyses
    analyses_result = analyses_collection.delete_many({})
    print(f"   - Deleted {analyses_result.deleted_count} analyses")
    
    # Delete all goals
    goals_result = goals_collection.delete_many({})
    print(f"   - Deleted {goals_result.deleted_count} goals")
    
    # Delete all chat history
    chat_result = chat_history_collection.delete_many({})
    print(f"   - Deleted {chat_result.deleted_count} chat messages")
    
    print("✅ All user data cleared successfully!")

if __name__ == "__main__":
    confirm = input("⚠️ This will DELETE ALL USERS and their data. Type 'yes' to confirm: ")
    if confirm.lower() == 'yes':
        clear_all_user_data()
    else:
        print("❌ Cancelled")
