from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from agents.controller import ControllerAgent
from pdf_parser import parse_bank_pdf

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
    return controller.run(data)

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

