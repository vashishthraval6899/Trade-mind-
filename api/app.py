from fastapi import FastAPI
from pydantic import BaseModel
from analyze import analyze

app = FastAPI(title="TradeMind API")


class AnalyzeRequest(BaseModel):
    ticker: str


@app.get("/")
def health():
    return {"status": "TradeMind API is running"}


@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    try:
        result = analyze(request.ticker)
        return result
    except Exception as e:
        return {"error": str(e)}
