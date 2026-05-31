from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
from contextlib import asynccontextmanager

model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    model_path = "model.pkl"

    if not os.path.exists(model_path):
        raise FileNotFoundError("model.pkl not found")

    model = joblib.load(model_path)
    print("✅ Model loaded")

    yield  # app runs here

    print("🛑 App shutting down")

app = FastAPI(lifespan=lifespan)

class InputData(BaseModel):
    attempts: int
    country: int
    device: int
    hour: int
    vpn: int
    

@app.get("/")
def home():
    return {"message": "Cyber Security AI Running 🚀"}

@app.post("/predict")
def predict(data: InputData):
    try:
        input_data = [[
            data.attempts,
            data.country,
            data.device,
            data.hour,
            data.vpn
        ]]

        print("Input:", input_data)

        prob = model.predict_proba(input_data)[0][1]

        return {
            "risk_score": round(float(prob), 2),
            "status": "🚨 Suspicious" if prob > 0.5 else "✅ Normal"
        }

    except Exception as e:
        return {"error": str(e)}