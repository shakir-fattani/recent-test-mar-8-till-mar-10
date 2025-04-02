#!/usr/bin/env python
import argparse
import os
import sys

# Add parent directory to path to import application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.security import get_password_hash
from models.user import User
from models.base import Base  # Import Base if you have a separate base model file

def create_user(
    username: str, 
    email: str, 
    password: str, 
    first_name: str = None, 
    last_name: str = None, 
    is_superuser: bool = False
):
    """Create a new user in the database."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if user:
            print(f"Error: User with email '{email}' or username '{username}' already exists.")
            return False
        
        # Create new user
        db_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_superuser=is_superuser
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"User created successfully: {username} ({email})")
        if is_superuser:
            print("User has superuser privileges")
        
        return True
    
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user in the database")
    parser.add_argument("--username", required=True, help="Username for the new user")
    parser.add_argument("--email", required=True, help="Email address for the new user")
    parser.add_argument("--password", required=True, help="Password for the new user")
    parser.add_argument("--first-name", help="First name of the user")
    parser.add_argument("--last-name", help="Last name of the user")
    parser.add_argument("--superuser", action="store_true", help="Give the user superuser privileges")
    
    args = parser.parse_args()
    
    create_user(
        username=args.username,
        email=args.email,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name,
        is_superuser=args.superuser
    )
