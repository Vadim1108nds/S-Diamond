import os
from getpass import getpass
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/sdiamond")
client = MongoClient(MONGO_URI)
db = client.get_default_database()

username = input("Admin username [admin]: ").strip() or "admin"
email = input("Admin email [admin@gmail.com]: ").strip() or "admin@gmail.com"
password = getpass("Admin password [admin]: ") or "admin"

if db.users.find_one({"username": username}):
    print("Користувач з таким username вже є.")
else:
    db.users.insert_one({
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "admin"
    })
    print("Admin створено.")

