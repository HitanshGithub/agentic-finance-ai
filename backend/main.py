from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from agents.controller import ControllerAgent
from pdf_parser import parse_bank_pdf
from database import save_analysis, get_all_analyses, get_analysis_by_id

app = FastAPI()

# ✅ CORS (required for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = ControllerAgent()

@app.get("/")
def root():
    return {"status": "Agentic Finance AI Backend Running"}

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

# @app.post("/upload-pdf")
# async def upload_pdf(file: UploadFile):
#     """
#     Returns:
#     {
#       expenses: [{ category, amount }]
#     }
#     """
#     expenses = parse_bank_pdf(file.file)
#     return {"expenses": expenses}



@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    expenses = parse_bank_pdf(file.file)
    return {"expenses": expenses}

