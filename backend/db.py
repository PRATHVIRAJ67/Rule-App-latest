from pymongo import MongoClient
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

def get_db():
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is not defined in the environment variables.")

    print(f"MongoDB URI: {MONGODB_URI}")  

    try:
        parsed_uri = urlparse(MONGODB_URI)
        path = parsed_uri.path  
        db_name = path.lstrip('/')  
        print(f"Extracted Database Name: '{db_name}'") 

        if not db_name:
            raise ValueError("No database name found in MongoDB URI.")

        client = MongoClient(MONGODB_URI)
        db = client[db_name]
        print(f"Connected to MongoDB database: '{db_name}'") 
        return db
    except Exception as e:
        raise ValueError(f"Error parsing MongoDB URI: {e}")

if __name__ == "__main__":
    db = get_db()
