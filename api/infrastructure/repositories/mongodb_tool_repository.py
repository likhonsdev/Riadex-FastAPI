from typing import List, Optional
from domain.entities.tool import ToolEntity
from domain.repositories.tool_repository import ToolRepository
from infrastructure.database import get_database

class MongoDBToolRepository(ToolRepository):
    def __init__(self):
        self.collection_name = "tools"
    
    async def create(self, tool: ToolEntity) -> ToolEntity:
        db = await get_database()
        collection = db[self.collection_name]
        
        tool_dict = tool.dict()
        tool_dict["_id"] = tool.tool_id
        
        await collection.insert_one(tool_dict)
        return tool
    
    async def get_by_id(self, tool_id: str) -> Optional[ToolEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        doc = await collection.find_one({"_id": tool_id})
        if doc:
            doc["tool_id"] = doc.pop("_id")
            return ToolEntity(**doc)
        return None
    
    async def get_by_session_id(self, session_id: str) -> List[ToolEntity]:
        db = await get_database()
        collection = db[self.collection_name]
        
        cursor = collection.find({"session_id": session_id}).sort("created_at", 1)
        tools = []
        async for doc in cursor:
            doc["tool_id"] = doc.pop("_id")
            tools.append(ToolEntity(**doc))
        return tools
    
    async def update(self, tool: ToolEntity) -> ToolEntity:
        db = await get_database()
        collection = db[self.collection_name]
        
        tool_dict = tool.dict()
        tool_dict["_id"] = tool_dict.pop("tool_id")
        
        await collection.replace_one({"_id": tool.tool_id}, tool_dict)
        return tool
    
    async def delete(self, tool_id: str) -> bool:
        db = await get_database()
        collection = db[self.collection_name]
        
        result = await collection.delete_one({"_id": tool_id})
        return result.deleted_count > 0
