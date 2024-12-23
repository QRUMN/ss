from app import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())
