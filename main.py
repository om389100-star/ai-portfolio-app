from fastapi import FastAPI
import numpy as np

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/optimize")
def optimize_portfolio(data: dict):
    stocks = data.get("stocks", [])

    if len(stocks) == 0:
        return {"error": "No stocks provided"}

    weights = np.random.dirichlet(np.ones(len(stocks)))

    return {
        "allocation": dict(zip(stocks, weights.tolist()))
    }