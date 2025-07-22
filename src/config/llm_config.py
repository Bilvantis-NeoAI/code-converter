from src.config.config import settings
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import HTTPException
import os

def get_llm():
    provider = settings.LLM_PROVIDER.lower()
    if provider == 'openai':
        model_name = settings.LLM.OPEN_AI.MODEL
        return ChatOpenAI(model=model_name, temperature=0.1)
    elif provider == 'gemini':
        model_name = settings.LLM.GEMINI.MODEL
        google_api_key = os.getenv("GEMINI_API_KEY")
        if not google_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set.")
        return ChatGoogleGenerativeAI(model=model_name, temperature=0.1, google_api_key=google_api_key)
    else:
        raise HTTPException(status_code=501, detail=f"LLM provider '{provider}' not supported.") 