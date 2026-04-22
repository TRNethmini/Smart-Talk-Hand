from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.ridmi_db

# Collections
users_collection = db.get_collection("users")
posts_collection = db.get_collection("posts")
chats_collection = db.get_collection("chats")
messages_collection = db.get_collection("messages")

async def init_db():
    await users_collection.create_index("email", unique=True)
    await posts_collection.create_index([("created_at", -1)])
    await messages_collection.create_index("chat_id")
    await messages_collection.create_index([("timestamp", 1)])
