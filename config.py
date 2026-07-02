import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("gemini_key")
WEATHER_API_KEY = os.getenv("weather_key")

MODEL_NAME = "gemini-3.1-flash-lite"
REQUEST_TIMEOUT = 15
MAX_RETRY = 2