import os
import sys
import django
from pymongo import MongoClient
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscription_service.settings')
django.setup()

from django.conf import settings

def test_mongodb_connection():
    """Test the MongoDB connection and save a test document."""
    print(f"Attempting to connect to MongoDB using URI: {settings.MONGODB_URI}")
    
    try:
        # Create a connection
        client = MongoClient(settings.MONGODB_URI)
        
        # Test the connection
        client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Get the database
        db_name = settings.MONGODB_NAME
        db = client[db_name]
        print(f"Using database: {db_name}")
        
        # List all collections
        collections = db.list_collection_names()
        print(f"Collections in database: {collections}")
        
        # Get or create the subscribers collection
        subscribers = db.subscribers
        
        # Insert a test document
        test_subscriber = {
            'email': 'test@example.com',
            'is_paid': False,
            'created_at': datetime.datetime.now(),
            'test_flag': True
        }
        
        result = subscribers.insert_one(test_subscriber)
        print(f"Test document inserted with ID: {result.inserted_id}")
        
        # List all documents in the collection
        count = subscribers.count_documents({})
        print(f"Total documents in subscribers collection: {count}")
        
        # Get the test document and print it
        print("\nDocuments in subscribers collection:")
        for document in subscribers.find():
            print(document)
            
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection() 