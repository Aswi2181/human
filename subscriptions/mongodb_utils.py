from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_mongodb_client():
    """Get a MongoDB client using the connection information from settings."""
    try:
        client = MongoClient(settings.MONGODB_URI)
        # Test connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return client
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return None

def get_mongodb_database():
    """Get the MongoDB database."""
    client = get_mongodb_client()
    if client:
        return client[settings.MONGODB_NAME]
    return None

def save_subscriber_to_mongodb(subscriber):
    """Save a subscriber to MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return False
    
    collection = db.subscribers
    
    # Convert Django model to dictionary
    subscriber_data = {
        'email': subscriber.email,
        'is_paid': subscriber.is_paid,
        'payment_id': subscriber.payment_id,
        'created_at': subscriber.created_at,
        'pdf_generated': subscriber.pdf_generated,
        'pdf_path': subscriber.pdf_path,
        'email_sent': subscriber.email_sent,
        'django_id': subscriber.id  # Reference to Django model
    }
    
    try:
        result = collection.insert_one(subscriber_data)
        logger.info(f"Subscriber saved to MongoDB with ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving subscriber to MongoDB: {e}")
        return False

def get_subscribers_from_mongodb():
    """Get all subscribers from MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return []
    
    collection = db.subscribers
    
    try:
        return list(collection.find())
    except Exception as e:
        logger.error(f"Error getting subscribers from MongoDB: {e}")
        return []

def get_subscriber_by_email(email):
    """Get a subscriber by email from MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return None
    
    collection = db.subscribers
    
    try:
        return collection.find_one({'email': email})
    except Exception as e:
        logger.error(f"Error getting subscriber from MongoDB: {e}")
        return None

def update_subscriber_in_mongodb(email, update_data):
    """Update a subscriber in MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return False
    
    collection = db.subscribers
    
    try:
        result = collection.update_one({'email': email}, {'$set': update_data})
        logger.info(f"Subscriber updated in MongoDB: {result.modified_count} document(s) modified")
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating subscriber in MongoDB: {e}")
        return False 