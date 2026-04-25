from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os

port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "Stock Dashboard API is running"}

# 🔥 NEW API
@app.get("/data/{symbol}")
def get_data(symbol: str):
    df = yf.download(symbol + ".NS", period="30d")

    if df.empty:
        return {"error": "Invalid symbol or no data"}

    # 🔥 FIX 1: flatten columns if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # 🔥 calculations
    df['Daily Return'] = (df['Close'] - df['Open']) / df['Open']
    df['7MA'] = df['Close'].rolling(window=7).mean()

    df = df.fillna(0)

    # 🔥 reset index
    df = df.reset_index()

    # 🔥 convert date to string
    df['Date'] = df['Date'].astype(str)

    # 🔥 FINAL SAFE RETURN
    return df.to_dict(orient="records")
@app.get("/companies")
def get_companies():
    return [
        "INFY", "TCS", "RELIANCE", "HDFCBANK",
        "ICICIBANK", "SBIN", "WIPRO", "HCLTECH",
        "AXISBANK", "KOTAKBANK", "LT", "ITC"
    ]
@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    df = yf.download(symbol + ".NS", period="1y")

    if df.empty:
        return {"error": "Invalid symbol"}

    # Fix multi-index again (important)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    return {
        "52_week_high": float(df["Close"].max()),
        "52_week_low": float(df["Close"].min()),
        "average_close": float(df["Close"].mean())
    }
    
@app.get("/compare")
def compare(symbol1: str, symbol2: str):
    df1 = yf.download(symbol1 + ".NS", period="30d")
    df2 = yf.download(symbol2 + ".NS", period="30d")
    if isinstance(df1.columns, pd.MultiIndex):
        df1.columns = [col[0] for col in df1.columns]
    if isinstance(df2.columns, pd.MultiIndex):
        df2.columns = [col[0] for col in df2.columns]

    df1 = df1.reset_index()
    df2 = df2.reset_index()

    df1['Date'] = df1['Date'].astype(str)
    df2['Date'] = df2['Date'].astype(str)

    return {
        "dates": df1["Date"].tolist(),
        symbol1: df1["Close"].fillna(0).tolist(),
        symbol2: df2["Close"].fillna(0).tolist()
    }
