from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List, Optional
from database import chats_collection, messages_collection
from services.auth_service import get_current_user
from pydantic import BaseModel, ConfigDict
from bson import ObjectId

router = APIRouter()

class ChatListResponse(BaseModel):
    id: str
    name: str
    initials: str
    lastMessage: str
    time: str
    unread: int
    online: bool
    
class MessageSend(BaseModel):
    text: str

class MessageResponse(BaseModel):
    id: str
    sender: str
    text: str
    time: str

@router.get("/api/v1/chat/conversations", response_model=List[ChatListResponse])
async def get_conversations(current_user: dict = Depends(get_current_user)):
    # Simple global chat mock strategy for MVP
    # Ideally, search chats where user_id is in members
    chat_rooms = await chats_collection.find({}).to_list(100)
    
    # If no rooms exist, populate the default ones from the frontend mock
    if not chat_rooms:
        defaults = [
            {"name": "SLSL Beginners Group", "initials": "SG", "online": True},
            {"name": "General Practice", "initials": "GP", "online": True}
        ]
        await chats_collection.insert_many(defaults)
        chat_rooms = await chats_collection.find({}).to_list(100)

    results = []
    for c in chat_rooms:
        # Get last message
        last_msg = await messages_collection.find_one(
            {"chat_id": str(c["_id"])},
            sort=[("timestamp", -1)]
        )
        
        last_str = last_msg["text"] if last_msg else "Tap to start chatting..."
        t_str = "Just now"
        
        if last_msg:
            h = last_msg["timestamp"].hour
            m = last_msg["timestamp"].minute
            t_str = f"{h:02d}:{m:02d}"

        results.append(ChatListResponse(
            id=str(c["_id"]),
            name=c["name"],
            initials=c["initials"],
            lastMessage=last_str,
            time=t_str,
            unread=0,
            online=c.get("online", False)
        ))
        
    return results

@router.get("/api/v1/chat/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: str, current_user: dict = Depends(get_current_user)):
    msgs = await messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1).to_list(100)
    
    res = []
    for m in msgs:
        sender_type = "me" if m["user_id"] == current_user["id"] else "them"
        h = m["timestamp"].hour
        min = m["timestamp"].minute
        t_str = f"{h:02d}:{min:02d}"
        
        res.append(MessageResponse(
            id=str(m["_id"]),
            sender=sender_type,
            text=m["text"],
            time=t_str
        ))
    return res

@router.post("/api/v1/chat/{chat_id}/send")
async def send_message(chat_id: str, msg: MessageSend, current_user: dict = Depends(get_current_user)):
    new_message = {
        "chat_id": chat_id,
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "text": msg.text,
        "timestamp": datetime.utcnow()
    }
    await messages_collection.insert_one(new_message)
    return {"status": "success"}
