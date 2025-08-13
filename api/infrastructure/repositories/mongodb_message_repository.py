from typing import List, Optional
from domain.entities.message import MessageEntity
from domain.repositories.message_repository import MessageRepository
from infrastructure.database import get_database

class MongoDBMessageRepository(MessageRepository):
    def __init__(self):
        self.collection_name = "messages"
    
    async def create(self, message: MessageEntity) -> MessageEntity:
        db = await get_database()
        collection = db[self.collection_name]
        
        message_dict = message.dict()
        message_dict["_id"] = message.message_id
        
        await collection.insert_one(message_dict)
        return message
    
    async def get_by_session_id(self, session_id: str) -> List[MessageEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        cursor = collection.find({"session_id": session_id}).sort("timestamp", 1)
        messages = []
        async for doc in cursor:
            doc["message_id"] = doc.pop("_id")
            messages.append(MessageEntity(**doc))
        return messages
    
    async def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        doc = await collection.find_one({"_id": message_id})
        if doc:
            doc["message_id"] = doc.pop("_id")
            return MessageEntity(**doc)
        return None
    
    async def delete_by_session_id(self, session_id: str) -> bool:
        db = await get_database()
        collection = db[self.collection_name]
        
        result = await collection.delete_many({"session_id": session_id})
        return result.deleted_count > 0
