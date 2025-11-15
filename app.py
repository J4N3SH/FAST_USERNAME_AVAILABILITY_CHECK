from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from service.bloom_service import BloomService
from service.user_store import init_db, save_new_user
from service.redis_lock import RedisLock  # New import for race fix
import time  # For backoff sleep

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup_event():
    init_db()

bloom = BloomService()
lock = RedisLock()  # New: Lock instance

class RegisterRequest(BaseModel):
    username: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "", "last": ""})

@app.post("/check", response_class=HTMLResponse)
def check_username(request: Request, username: str = Form(...)):
    available = bloom.is_definitely_absent(username)
    if available:
        msg = f"✅ '{username}' is available."
    else:
        msg = f"❌ '{username}' appears taken or cannot be guaranteed free."
    return templates.TemplateResponse("index.html", {"request": request, "message": msg, "last": username})

@app.post("/register_from_ui", response_class=HTMLResponse)
def register_from_ui(request: Request, username: str = Form(...)):
    if bloom.is_definitely_absent(username):  # Bloom check first (safe, fast)
        retries = 1  # Single retry for middle approach
        while retries > 0:
            result = lock.atomic_register(username, ttl=0.1)  # Atomic lock attempt
            if result == 1:  # Lock acquired
                try:
                    save_new_user(username)  # DB insert
                    bloom.add_username(username)  # Update Bloom
                    msg = f"🎉 '{username}' successfully registered."
                    break  # Success - TTL handles unlock
                except Exception as e:
                    lock.r.delete(f"lock:{username}")  # Unlock on failure
                    msg = f"⚠️ Registration failed: {e}"
                    retries -= 1
            else:  # Lock held
                if retries == 1:  # First fail - quick backoff for retry
                    time.sleep(0.01)  # 10ms wait
                retries -= 1
        if retries == 0:  # Exhausted (after retry)
            msg = f"⚠️ '{username}' is busy—try another name."
    else:
        msg = f"❌ '{username}' appears taken—cannot register."
    return templates.TemplateResponse("index.html", {"request": request, "message": msg, "last": username})

@app.get("/username_available")
def api_check(username: str):
    available = bloom.is_definitely_absent(username)
    return {"available": available}

@app.post("/register")
def api_register(req: RegisterRequest):
    username = req.username
    if bloom.is_definitely_absent(username):
        retries = 1  # Single retry
        while retries > 0:
            result = lock.atomic_register(username, ttl=0.1)
            if result == 1:
                try:
                    save_new_user(username)
                    bloom.add_username(username)
                    return {"status": "registered", "username": username}
                except Exception:
                    lock.r.delete(f"lock:{username}")
                    retries -= 1
            else:
                if retries == 1:
                    time.sleep(0.01)  # Backoff
                retries -= 1
        raise HTTPException(status_code=429, detail=f"'{username}' is busy—try another")
    else:
        raise HTTPException(status_code=400, detail="Username appears taken")