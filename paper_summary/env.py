from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULET_MODEL = "gpt-3.5-turbo-16k"
