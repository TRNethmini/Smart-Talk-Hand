from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import datetime
from typing import List
from database import posts_collection
from services.auth_service import get_current_user
from pydantic import BaseModel

router = APIRouter()

class PostCreate(BaseModel):
    achievement: str
    badge: str

class PostResponse(BaseModel):
    id: str
    user: str
    initials: str
    achievement: str
    time: str
    likes: int
    comments: int
    badge: str

@router.get("/api/v1/community/posts", response_model=List[PostResponse])
async def get_posts():
    # Fetch latest posts
    cursor = posts_collection.find({}).sort("created_at", -1).limit(50)
    posts = await cursor.to_list(length=50)
    
    formatted_posts = []
    for p in posts:
        # Simple time formatting for mock equivalence
        created_at = p.get("created_at", datetime.utcnow())
        diff = datetime.utcnow() - created_at
        
        if diff.days > 0:
            time_str = f"{diff.days} days ago"
        elif diff.seconds > 3600:
            time_str = f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            time_str = f"{diff.seconds // 60} mins ago"
        else:
            time_str = "Just now"

        formatted_posts.append(
            PostResponse(
                id=str(p["_id"]),
                user=p["user_name"],
                initials=p["user_initials"],
                achievement=p["achievement"],
                time=time_str,
                likes=p.get("likes", 0),
                comments=p.get("comments", 0),
                badge=p.get("badge", "gold")
            )
        )
    return formatted_posts

@router.post("/api/v1/community/share")
async def share_achievement(post: PostCreate, current_user: dict = Depends(get_current_user)):
    new_post = {
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "user_initials": current_user["initials"],
        "achievement": post.achievement,
        "badge": post.badge,
        "likes": 0,
        "comments": 0,
        "created_at": datetime.utcnow()
    }
    
    await posts_collection.insert_one(new_post)
    return {"status": "success"}
