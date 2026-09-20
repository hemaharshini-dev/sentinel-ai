import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.globals import set_llm_cache
from utils.cache import SQLitePersistentCache

load_dotenv()

# Persistent SQLite cache — identical prompts skip the Groq API entirely,
# even across server restarts. Cache stored in backend/.llm_cache.db
set_llm_cache(SQLitePersistentCache())

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)
