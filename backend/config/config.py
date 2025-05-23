import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:miciamoluca@localhost:5432/postgres")  # Ensure this is correct
    SQLALCHEMY_TRACK_MODIFICATIONS = False
