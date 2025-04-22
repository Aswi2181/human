from pymongo import MongoClient
from django.conf import settings
import logging
import datetime

logger = logging.getLogger(__name__)

def get_mongodb_client():
    """Get a MongoDB client using the connection information from settings."""
    try:
        # Print connection string for debugging (mask password in logs)
        uri = settings.MONGODB_URI
        masked_uri = uri.replace(settings.MONGODB_URI.split('@')[0], '***:***')
        logger.info(f"Connecting to MongoDB with URI: {masked_uri}")
        
        # Connect with timeout
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful!")
        return client
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        return None

def get_mongodb_database():
    """Get the MongoDB database."""
    client = get_mongodb_client()
    if client:
        try:
            db = client[settings.MONGODB_NAME]
            logger.info(f"Using MongoDB database: {settings.MONGODB_NAME}")
            return db
        except Exception as e:
            logger.error(f"Error accessing MongoDB database: {str(e)}")
            return None
    return None

def save_subscriber_to_mongodb(subscriber):
    """Save a subscriber to MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return False
    
    collection = db.subscribers
    logger.info(f"Attempting to save subscriber {subscriber.email} to MongoDB")
    
    # Convert Django model to dictionary
    try:
        subscriber_data = {
            'email': subscriber.email,
            'is_paid': subscriber.is_paid,
            'payment_id': subscriber.payment_id,
            'created_at': subscriber.created_at,
            'pdf_generated': subscriber.pdf_generated,
            'pdf_path': subscriber.pdf_path,
            'email_sent': subscriber.email_sent,
            'django_id': subscriber.id,  # Reference to Django model
            'updated_at': datetime.datetime.now()
        }
        
        # Check if subscriber already exists
        existing = collection.find_one({'email': subscriber.email})
        
        if existing:
            logger.info(f"Subscriber {subscriber.email} already exists in MongoDB, updating record")
            result = collection.update_one(
                {'email': subscriber.email}, 
                {'$set': subscriber_data}
            )
            logger.info(f"Subscriber updated in MongoDB: {result.modified_count} document(s) modified")
            return True
        else:
            logger.info(f"Subscriber {subscriber.email} is new, creating record in MongoDB")
            result = collection.insert_one(subscriber_data)
            logger.info(f"Subscriber saved to MongoDB with ID: {result.inserted_id}")
            return True
    except Exception as e:
        logger.error(f"Error saving subscriber to MongoDB: {str(e)}")
        return False

def get_subscribers_from_mongodb():
    """Get all subscribers from MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return []
    
    collection = db.subscribers
    
    try:
        subscribers = list(collection.find())
        logger.info(f"Retrieved {len(subscribers)} subscribers from MongoDB")
        return subscribers
    except Exception as e:
        logger.error(f"Error getting subscribers from MongoDB: {str(e)}")
        return []

def get_subscriber_by_email(email):
    """Get a subscriber by email from MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return None
    
    collection = db.subscribers
    
    try:
        subscriber = collection.find_one({'email': email})
        if subscriber:
            logger.info(f"Found subscriber with email {email} in MongoDB")
        else:
            logger.info(f"No subscriber found with email {email} in MongoDB")
        return subscriber
    except Exception as e:
        logger.error(f"Error getting subscriber from MongoDB: {str(e)}")
        return None

def update_subscriber_in_mongodb(email, update_data):
    """Update a subscriber in MongoDB."""
    db = get_mongodb_database()
    if not db:
        logger.error("Failed to connect to MongoDB database")
        return False
    
    collection = db.subscribers
    
    try:
        # Add updated timestamp
        update_data['updated_at'] = datetime.datetime.now()
        
        logger.info(f"Updating MongoDB subscriber with email {email}: {update_data}")
        result = collection.update_one({'email': email}, {'$set': update_data})
        logger.info(f"Subscriber updated in MongoDB: {result.modified_count} document(s) modified")
        
        if result.modified_count == 0:
            # Document might not exist, check if we need to create it
            if collection.count_documents({'email': email}) == 0:
                logger.info(f"Subscriber {email} not found in MongoDB, creating new record")
                update_data['email'] = email
                update_data['created_at'] = datetime.datetime.now()
                collection.insert_one(update_data)
                logger.info(f"New subscriber record created in MongoDB for {email}")
        
        return True
    except Exception as e:
        logger.error(f"Error updating subscriber in MongoDB: {str(e)}")
        return False 