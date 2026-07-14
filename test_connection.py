from pymongo import MongoClient

uri = "mongodb+srv://pranavkedu02_db_user:mypass123@cluster0.kuoya5n.mongodb.net/blogdb?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

print(client.list_database_names())