import os

from databases import DatabaseURL


DEBUG = True

# DATABASE SETTINGS
MONGO_HOST = os.getenv("MONGO_HOST", 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'invest')

MONGODB_URL = DatabaseURL(
    f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}"
)
