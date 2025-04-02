from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import text # type: ignore


from api.deps import get_db

router = APIRouter()


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database connection
    """
    try:
        # Execute a simple SQL query to check database connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Service is healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
