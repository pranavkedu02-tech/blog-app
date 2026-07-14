"""
MongoDB connection setup using PyMongo.
Open MongoDB Compass and connect to mongodb://localhost:27017
to watch the 'blog_app_db' database and its collections appear
as you use the app.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["blog_app_db"]

# Collections
users_collection = db["users"]
posts_collection = db["posts"]