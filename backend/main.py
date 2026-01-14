from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from finance_agents.controller import ControllerAgent
from finance_agents.savings_agent import SavingsGoalAgent
from finance_agents.chat_agent import ChatAgent
from pdf_parser import parse_bank_pdf
from recurring_detector import detect_recurring_expenses
from database import (
    save_analysis, get_all_analyses, get_analysis_by_id,
    save_goal, get_all_goals, update_goal, delete_goal, get_goal_by_id,
    get_monthly_trends, get_category_trends
)

app = FastAPI()

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


@app.get("/")
def root():
    return {"status": "Agentic Finance AI Backend Running", "version": "2.0"}


# ===== FINANCE ANALYSIS =====

@app.post("/analyze")
def analyze_finance(data: dict):
    """
    Expected input:
    {
      income: number,
      profile: string,
      expenses: [{ category, amount }]
    }
    """
    result = controller.run(data)
    
    # 💾 Save to MongoDB
    try:
        analysis_id = save_analysis(
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
def get_history(limit: int = 10):
    """Get recent analysis history from MongoDB."""
    try:
        analyses = get_all_analyses(limit)
        return {"history": analyses}
    except Exception as e:
        return {"error": str(e)}


@app.get("/history/{analysis_id}")
def get_single_analysis(analysis_id: str):
    """Get a specific analysis by ID."""
    try:
        analysis = get_analysis_by_id(analysis_id)
        if analysis:
            return analysis
        return {"error": "Analysis not found"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    expenses = parse_bank_pdf(file.file)
    return {"expenses": expenses}


# ===== SAVINGS GOALS =====

@app.post("/goals")
def create_goal(data: dict):
    """Create a new savings goal."""
    try:
        goal_id = save_goal(
            name=data.get("name", "My Goal"),
            target=data.get("target", 0),
            current=data.get("current", 0),
            deadline=data.get("deadline")
        )
        return {"_id": goal_id, "message": "Goal created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals")
def list_goals():
    """Get all savings goals."""
    try:
        goals = get_all_goals()
        return {"goals": goals}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals/{goal_id}")
def get_goal(goal_id: str):
    """Get a specific goal by ID."""
    try:
        goal = get_goal_by_id(goal_id)
        if goal:
            return goal
        return {"error": "Goal not found"}
    except Exception as e:
        return {"error": str(e)}


@app.put("/goals/{goal_id}")
def modify_goal(goal_id: str, data: dict):
    """Update a savings goal."""
    try:
        success = update_goal(goal_id, data)
        if success:
            return {"message": "Goal updated successfully"}
        return {"error": "Goal not found or no changes made"}
    except Exception as e:
        return {"error": str(e)}


@app.delete("/goals/{goal_id}")
def remove_goal(goal_id: str):
    """Delete a savings goal."""
    try:
        success = delete_goal(goal_id)
        if success:
            return {"message": "Goal deleted successfully"}
        return {"error": "Goal not found"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/goals/{goal_id}/suggestions")
def get_goal_suggestions(goal_id: str, income: float = 0):
    """Get AI suggestions for reaching a savings goal."""
    try:
        goal = get_goal_by_id(goal_id)
        if not goal:
            return {"error": "Goal not found"}
        
        suggestions = savings_agent.get_suggestions(goal, income)
        return {"goal": goal, "suggestions": suggestions}
    except Exception as e:
        return {"error": str(e)}


# ===== AI CHAT ASSISTANT =====

@app.post("/chat")
def chat_endpoint(data: dict):
    """
    Chat with AI assistant.
    Input: { message: string, context?: { income, expenses, goals } }
    """
    try:
        message = data.get("message", "")
        context = data.get("context", {})
        
        if not message:
            return {"error": "Message is required"}
        
        response = chat_agent.chat(message, context)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat/clear")
def clear_chat():
    """Clear chat history."""
    chat_agent.clear_history()
    return {"message": "Chat history cleared"}


# ===== RECURRING EXPENSES =====

@app.post("/detect-recurring")
def detect_recurring(data: dict):
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


# ===== TRENDS & ANALYTICS =====

@app.get("/trends/monthly")
def monthly_trends(months: int = 6):
    """Get monthly spending trends."""
    try:
        trends = get_monthly_trends(months)
        return {"trends": trends}
    except Exception as e:
        return {"error": str(e)}


@app.get("/trends/categories")
def category_trends(months: int = 6):
    """Get spending by category over time."""
    try:
        trends = get_category_trends(months)
        return trends
    except Exception as e:
        return {"error": str(e)}
