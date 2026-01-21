from fastapi import FastAPI, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from finance_agents.controller import ControllerAgent
from finance_agents.savings_agent import SavingsGoalAgent
from finance_agents.chat_agent import ChatAgent
from pdf_parser import parse_bank_pdf
from recurring_detector import detect_recurring_expenses
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

from database import (
    save_analysis, get_all_analyses, get_analysis_by_id,
    save_goal, get_all_goals, update_goal, delete_goal, get_goal_by_id,
    get_monthly_trends, get_category_trends,
    create_user, get_user_by_email, verify_user_email, get_user_by_id,
    create_or_update_google_user, save_chat_message, get_chat_history, clear_chat_history
)

from auth import (
    hash_password, verify_password, create_access_token, decode_access_token,
    create_email_verification_token, verify_email_token, verify_google_token
)

from email_service import send_verification_email

app = FastAPI()

# Security
security = HTTPBearer(auto_error=False)

# ✅ CORS (required for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
controller = ControllerAgent()
savings_agent = SavingsGoalAgent()
chat_agent = ChatAgent()

# Environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


# ===== PYDANTIC MODELS =====

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    token: str


# ===== AUTH DEPENDENCY =====

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate the current user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            return get_user_by_id(user_id)
    except:
        pass
    return None


@app.get("/")
def root():
    return {"status": "Agentic Finance AI Backend Running", "version": "3.0", "auth": "enabled"}


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/auth/signup")
def signup(data: SignupRequest):
    """
    Sign up with email and password.
    Sends verification email to the user.
    """
    # Check if user already exists
    existing_user = get_user_by_email(data.email)
    if existing_user:
        if existing_user.get("is_verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            # Resend verification email
            token = create_email_verification_token(data.email)
            send_verification_email(data.email, token)
            return {"message": "Verification email resent. Please check your inbox."}
    
    # Validate password
    if len(data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Create user
    password_hash = hash_password(data.password)
    user_id = create_user(data.email, password_hash, is_verified=False)
    
    # Send verification email
    token = create_email_verification_token(data.email)
    email_sent = send_verification_email(data.email, token)
    
    return {
        "message": "Account created! Please check your email to verify your account.",
        "user_id": user_id,
        "email_sent": email_sent,
        "verification_token": token if not email_sent else None  # Return token in dev mode
    }


@app.get("/auth/verify/{token}")
def verify_email(token: str):
    """Verify email from the verification link."""
    print(f"📧 Verification request received")
    print(f"   Token (first 50 chars): {token[:50]}...")
    
    email = verify_email_token(token)
    print(f"   Decoded email: {email}")
    
    if not email:
        print(f"   ❌ Token decode failed!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link"
        )
    
    success = verify_user_email(email)
    print(f"   Verification success: {success}")
    
    if not success:
        print(f"   ❌ User not found in database!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    print(f"   ✅ Email verified successfully!")
    return {"message": "Email verified successfully! You can now login.", "email": email}


@app.post("/auth/login")
def login(data: LoginRequest):
    """Login with email and password."""
    print(f"🔐 Login attempt for: {data.email}")
    user = get_user_by_email(data.email)
    
    if not user:
        print(f"❌ User not found: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    print(f"✅ User found: {user.get('email')}, verified: {user.get('is_verified')}")
    
    if not user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email before logging in"
        )
    
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google Sign-In. Please login with Google."
        )
    
    if not verify_password(data.password, user["password_hash"]):
        print(f"❌ Password verification failed for: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    print(f"✅ Password verified for: {data.email}")
    
    # Create JWT token
    token = create_access_token(user["_id"], user["email"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["_id"],
            "email": user["email"],
            "name": user.get("name", "")
        }
    }


@app.post("/auth/google")
def google_login(data: GoogleLoginRequest):
    """Login with Google OAuth token."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    # Verify Google token
    google_user = verify_google_token(data.token, GOOGLE_CLIENT_ID)
    
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Create or update user
    user = create_or_update_google_user(
        google_id=google_user["google_id"],
        email=google_user["email"],
        name=google_user.get("name", ""),
        picture=google_user.get("picture", "")
    )
    
    # Create JWT token
    token = create_access_token(user["_id"], user["email"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["_id"],
            "email": user["email"],
            "name": user.get("name", ""),
            "picture": user.get("picture", "")
        }
    }


@app.get("/auth/me")
def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "id": user["_id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "picture": user.get("picture", ""),
        "is_verified": user.get("is_verified", False)
    }


# ===== FINANCE ANALYSIS (Protected) =====

@app.post("/analyze")
def analyze_finance(data: dict, user: dict = Depends(get_current_user)):
    """
    Expected input:
    {
      income: number,
      profile: string,
      expenses: [{ category, amount }]
    }
    """
    result = controller.run(data)
    
    # 💾 Save to MongoDB with user_id
    try:
        analysis_id = save_analysis(
            user_id=user["_id"],
            income=data.get("income", 0),
            profile=data.get("profile", ""),
            expenses=data.get("expenses", []),
            result=result
        )
        result["_id"] = analysis_id
    except Exception as e:
        result["db_error"] = str(e)
    
    return result


@app.get("/history")
def get_history(limit: int = 10, user: dict = Depends(get_current_user)):
    """Get recent analysis history from MongoDB."""
    try:
        analyses = get_all_analyses(user["_id"], limit)
        return {"history": analyses}
    except Exception as e:
        return {"error": str(e)}


@app.get("/history/{analysis_id}")
def get_single_analysis(analysis_id: str, user: dict = Depends(get_current_user)):
    """Get a specific analysis by ID."""
    try:
        analysis = get_analysis_by_id(user["_id"], analysis_id)
        if analysis:
            return analysis
        return {"error": "Analysis not found"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    expenses = parse_bank_pdf(file.file)
    return {"expenses": expenses}


# ===== SAVINGS GOALS (Protected) =====

@app.post("/goals")
def create_goal(data: dict, user: dict = Depends(get_current_user)):
    """Create a new savings goal."""
    try:
        goal_id = save_goal(
            user_id=user["_id"],
            name=data.get("name", "My Goal"),
            target=data.get("target", 0),
            current=data.get("current", 0),
            deadline=data.get("deadline")
        )
        return {"_id": goal_id, "message": "Goal created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals")
def list_goals(user: dict = Depends(get_current_user)):
    """Get all savings goals for current user."""
    try:
        goals = get_all_goals(user["_id"])
        return {"goals": goals}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals/{goal_id}")
def get_goal(goal_id: str, user: dict = Depends(get_current_user)):
    """Get a specific goal by ID."""
    try:
        goal = get_goal_by_id(user["_id"], goal_id)
        if goal:
            return goal
        return {"error": "Goal not found"}
    except Exception as e:
        return {"error": str(e)}


@app.put("/goals/{goal_id}")
def modify_goal(goal_id: str, data: dict, user: dict = Depends(get_current_user)):
    """Update a savings goal."""
    try:
        success = update_goal(user["_id"], goal_id, data)
        if success:
            return {"message": "Goal updated successfully"}
        return {"error": "Goal not found or no changes made"}
    except Exception as e:
        return {"error": str(e)}


@app.delete("/goals/{goal_id}")
def remove_goal(goal_id: str, user: dict = Depends(get_current_user)):
    """Delete a savings goal."""
    try:
        success = delete_goal(user["_id"], goal_id)
        if success:
            return {"message": "Goal deleted successfully"}
        return {"error": "Goal not found"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals/{goal_id}/suggestions")
def get_goal_suggestions(goal_id: str, income: float = 0, user: dict = Depends(get_current_user)):
    """Get AI suggestions for reaching a savings goal."""
    try:
        goal = get_goal_by_id(user["_id"], goal_id)
        if not goal:
            return {"error": "Goal not found"}
        
        suggestions = savings_agent.get_suggestions(goal, income)
        return {"goal": goal, "suggestions": suggestions}
    except Exception as e:
        return {"error": str(e)}


# ===== AI CHAT ASSISTANT (Protected) =====

@app.post("/chat")
def chat_endpoint(data: dict, user: dict = Depends(get_current_user)):
    """
    Chat with AI assistant.
    Input: { message: string, context?: { income, expenses, goals } }
    """
    try:
        message = data.get("message", "")
        context = data.get("context", {})
        
        if not message:
            return {"error": "Message is required"}
        
        # Save user message
        save_chat_message(user["_id"], "user", message)
        
        response = chat_agent.chat(message, context)
        
        # Save assistant response
        save_chat_message(user["_id"], "assistant", response)
        
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


@app.get("/chat/history")
def get_chat_history_endpoint(limit: int = 50, user: dict = Depends(get_current_user)):
    """Get chat history for current user."""
    try:
        history = get_chat_history(user["_id"], limit)
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat/clear")
def clear_chat(user: dict = Depends(get_current_user)):
    """Clear chat history for current user."""
    chat_agent.clear_history()
    clear_chat_history(user["_id"])
    return {"message": "Chat history cleared"}


# ===== RECURRING EXPENSES =====

@app.post("/detect-recurring")
def detect_recurring(data: dict, user: dict = Depends(get_current_user)):
    """
    Detect recurring expenses from expense list.
    Input: { expenses: [{ category, amount }] }
    """
    try:
        expenses = data.get("expenses", [])
        result = detect_recurring_expenses(expenses)
        return result
    except Exception as e:
        return {"error": str(e)}


# ===== TRENDS & ANALYTICS (Protected) =====

@app.get("/trends/monthly")
def monthly_trends(months: int = 6, user: dict = Depends(get_current_user)):
    """Get monthly spending trends for current user."""
    try:
        trends = get_monthly_trends(user["_id"], months)
        return {"trends": trends}
    except Exception as e:
        return {"error": str(e)}


@app.get("/trends/categories")
def category_trends(months: int = 6, user: dict = Depends(get_current_user)):
    """Get spending by category over time for current user."""
    try:
        trends = get_category_trends(user["_id"], months)
        return trends
    except Exception as e:
        return {"error": str(e)}
