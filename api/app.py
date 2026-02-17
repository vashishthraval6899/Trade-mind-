from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyze import analyze

app = FastAPI(title="TradeMind API")

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request Model
# -------------------------------
class AnalyzeRequest(BaseModel):
    ticker: str

# -------------------------------
# Health Check
# -------------------------------
@app.get("/")
def health():
    return {"status": "TradeMind API is running"}

# -------------------------------
# Analyze Endpoint
# -------------------------------
@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    try:
        result = analyze(request.ticker)

        if not isinstance(result, dict):
            raise ValueError("Analyze function did not return JSON.")

        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )
