# test/test_server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# Store active sessions
sessions: Dict[int, Dict] = {}

class StartSessionRequest(BaseModel):
    pc_id: int
    duration: int
    user_id: str
    booking_id: str

class ExtendSessionRequest(BaseModel):
    pc_id: int
    extra_minutes: int

@app.get("/")
async def root():
    return {"message": "Gaming Cafe Test Server", "status": "running"}

@app.post("/api/session/start")
async def start_session(request: StartSessionRequest):
    sessions[request.pc_id] = {
        "user_id": request.user_id,
        "duration": request.duration,
        "start_time": asyncio.get_event_loop().time(),
        "booking_id": request.booking_id
    }
    return {"status": "started", "pc_id": request.pc_id, "duration": request.duration}

@app.post("/api/session/extend")
async def extend_session(request: ExtendSessionRequest):
    if request.pc_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # In real app, you'd update database
    return {"status": "extended", "pc_id": request.pc_id, "extra_minutes": request.extra_minutes}

@app.post("/api/session/end")
async def end_session(pc_id: int):
    if pc_id in sessions:
        del sessions[pc_id]
    return {"status": "ended", "pc_id": pc_id}

@app.get("/api/pcs/status")
async def get_all_status():
    # Simulate PC status
    return {
        1: {"pc_id": 1, "status": "available", "type": "PC"},
        2: {"pc_id": 2, "status": "in_use", "type": "PC", "time_remaining": 25},
        3: {"pc_id": 3, "status": "available", "type": "PC"},
        4: {"pc_id": 4, "status": "in_use", "type": "PS", "time_remaining": 10},
        5: {"pc_id": 5, "status": "available", "type": "PS"},
    }

if __name__ == "__main__":
    print("🚀 Test Server starting on http://localhost:8000")
    print("📡 API endpoints:")
    print("   GET  /api/pcs/status")
    print("   POST /api/session/start")
    print("   POST /api/session/extend")
    print("   POST /api/session/end")
    uvicorn.run(app, host="0.0.0.0", port=8000)