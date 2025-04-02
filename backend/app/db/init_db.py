import logging
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta

from core.database import engine
from models import Base
# Import all models to ensure they're registered with SQLAlchemy
from models.user import User
from models.chat import Chat, ChatHistory
from models.file import FileList

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database by creating all tables if they don't exist."""
    try:
        # Get existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Get all models defined in our Base
        models = [cls for cls in Base.__subclasses__()]
        model_tables = [model.__tablename__ for model in models if hasattr(model, '__tablename__')]
        
        # Log the tables we're going to create
        tables_to_create = set(model_tables) - set(existing_tables)
        if tables_to_create:
            logger.info(f"Creating tables: {', '.join(tables_to_create)}")
        else:
            logger.info("All tables already exist")
        
        # Create tables that don't exist
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        after_tables = inspect(engine).get_table_names()
        logger.info(f"Database initialized with tables: {', '.join(after_tables)}")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
