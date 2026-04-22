from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from models.auth_models import UserRegister, Token, UserResponse
from services.auth_service import get_password_hash, verify_password, create_access_token, get_current_user
from database import users_collection
from bson import ObjectId

router = APIRouter()

@router.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user: UserRegister):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    parts = user.name.split(" ")
    initials = "".join([p[0] for p in parts if p]).upper()[:2]
    
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "initials": initials,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(new_user)
    
    return UserResponse(
        id=str(result.inserted_id),
        name=new_user["name"],
        email=new_user["email"],
        initials=new_user["initials"],
        created_at=new_user["created_at"]
    )

@router.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=str(user["_id"]))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/v1/auth/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
