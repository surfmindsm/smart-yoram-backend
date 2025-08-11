#\!/usr/bin/env python3
"""
Set GPT API key for church
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Church
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_church_gpt_key():
    db = SessionLocal()
    
    try:
        # Get church ID 1
        church = db.query(Church).filter(Church.id == 1).first()
        if church:
            print(f"Church: {church.name} (ID: {church.id})")
            
            # Set GPT API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                church.gpt_api_key = api_key
                church.gpt_model = "gpt-4o-mini"
                church.max_tokens = 4000
                church.temperature = 0.7
                db.commit()
                print(f"Set GPT API key for church: {api_key[:10]}...")
                print(f"Model: {church.gpt_model}")
            else:
                print("No OPENAI_API_KEY found in environment")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_church_gpt_key()
