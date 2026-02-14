from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyze import analyze

app = FastAPI(title="TradeMind API")

# --- FIX 1: ADD CORS MIDDLEWARE ---
# This allows your browser/frontend to talk to this backend without the 405 Error.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any website (change this to your specific URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

class AnalyzeRequest(BaseModel):
    ticker: str

@app.get("/")
def health():
    return {"status": "TradeMind API is running"}

# --- FIX 2: HANDLE POST REQUESTS AT THE ROOT ---
# Your JS fetches "https://...app", so we need a POST handler at "/"
@app.post("/")
def analyze_stock_root(request: AnalyzeRequest):
    try:
        result = analyze(request.ticker)
        return result
    except Exception as e:
        return {"error": str(e)}

# (Optional) Keeping this if you ever want to use /analyze explicitly
@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    try:
        result = analyze(request.ticker)
        return result
    except Exception as e:
        return {"error": str(e)}
