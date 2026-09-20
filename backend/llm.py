import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

load_dotenv()

# Cache LLM responses in memory.
# Identical prompts (same complaint submitted twice) skip the API entirely.
set_llm_cache(InMemoryCache())

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)
