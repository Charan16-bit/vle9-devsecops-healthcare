import os
import secrets
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(
    title="Secure Healthcare API",
    description="DevSecOps Healthcare Demonstration",
    version="1.0.0"
)

API_KEY = os.getenv("DEMO_API_KEY")

@app.get("/")
def home():
    return {
        "message": "Secure Healthcare API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/patients")
def get_patients(x_api_key: str = Header(default="")):
    if not API_KEY or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized access")

    return {
        "patients": [
            {"id": 101, "name": "Demo Patient A",
             "condition": "General Checkup"},
            {"id": 102, "name": "Demo Patient B",
             "condition": "Routine Follow-up"}
        ]
    }
