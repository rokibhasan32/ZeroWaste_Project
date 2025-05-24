from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import base64, requests, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

def analyze_with_groq(image_bytes):
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "groq-vision",
        "image_base64": encoded,
        "prompt": "Classify this waste image. What type of waste and estimated weight?"
    }

    response = requests.post("https://api.groq.com/v1/vision/analyze", headers=headers, json=data)
    if response.status_code != 200:
        return {
            "waste_type": "Unknown",
            "confidence": 0,
            "estimated_amount": "Unknown"
        }

    result = response.json()
    return {
        "waste_type": result.get("waste_type", "Plastic"),
        "confidence": result.get("confidence", 80),
        "estimated_amount": result.get("estimated_amount", "50-100 kg")
    }

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = analyze_with_groq(image_bytes)
    return JSONResponse({
        "waste_type": result["waste_type"],
        "confidence": result["confidence"],
        "amount": result["estimated_amount"],
        "lat": 23.8103,
        "lon": 90.4125,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    })
