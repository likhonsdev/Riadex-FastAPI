from motor.motor_asyncio import AsyncIOMotorClient
from infrastructure.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def init_database():
    """Initialize database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise

async def create_indexes():
    """Create database indexes"""
    try:
        # Sessions collection indexes
        await db.database.sessions.create_index("session_id", unique=True)
        await db.database.sessions.create_index("created_at")
        
        # Messages collection indexes
        await db.database.messages.create_index("session_id")
        await db.database.messages.create_index("timestamp")
        
        # Tools collection indexes
        await db.database.tools.create_index("session_id")
        await db.database.tools.create_index("tool_type")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error("Failed to create indexes", error=str(e))

async def get_database():
    return db.database

async def close_database():
    if db.client:
        db.client.close()
