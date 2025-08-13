from typing import List, Optional
from domain.entities.session import SessionEntity, SessionStatus
from domain.repositories.session_repository import SessionRepository
from infrastructure.database import get_database
import uuid
from datetime import datetime

class MongoDBSessionRepository(SessionRepository):
    def __init__(self):
        self.collection_name = "sessions"
    
    async def create(self, session: SessionEntity) -> SessionEntity:
        db = await get_database()
        collection = db[self.collection_name]
        
        session_dict = session.dict()
        session_dict["_id"] = session.session_id
        
        await collection.insert_one(session_dict)
        return session
    
    async def get_by_id(self, session_id: str) -> Optional[SessionEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        doc = await collection.find_one({"_id": session_id})
        if doc:
            doc["session_id"] = doc.pop("_id")
            return SessionEntity(**doc)
        return None
    
    async def get_all(self) -> List[SessionEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        cursor = collection.find().sort("created_at", -1)
        sessions = []
        async for doc in cursor:
            doc["session_id"] = doc.pop("_id")
            sessions.append(SessionEntity(**doc))
        return sessions
    
    async def update(self, session: SessionEntity) -> SessionEntity:
        db = await get_database()
        collection = db[self.collection_name]
        
        session.updated_at = datetime.utcnow()
        session_dict = session.dict()
        session_dict["_id"] = session_dict.pop("session_id")
        
        await collection.replace_one({"_id": session.session_id}, session_dict)
        return session
    
    async def delete(self, session_id: str) -> bool:
        db = await get_database()
        collection = db[self.collection_name]
        
        result = await collection.delete_one({"_id": session_id})
        return result.deleted_count > 0
    
    async def update_status(self, session_id: str, status: str) -> bool:
        db = await get_database()
        collection = db[self.collection_name]
        
        result = await collection.update_one(
            {"_id": session_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
