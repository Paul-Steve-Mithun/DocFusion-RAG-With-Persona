from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from ..db.mongo import get_db
from ..core.security import get_password_hash, verify_password, create_access_token, decode_token
from ..models import UserCreate, UserLogin, TokenResponse
from bson import ObjectId

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user_id(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    db = await get_db()
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(payload.password)
    res = await db.users.insert_one({"email": payload.email, "password": hashed})
    token = create_access_token(str(res.inserted_id))
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    db = await get_db()
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return TokenResponse(access_token=token)

@router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    db = await get_db()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user id")
    user = await db.users.find_one({"_id": oid}, {"email": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"_id": str(user["_id"]), "email": user["email"]}


