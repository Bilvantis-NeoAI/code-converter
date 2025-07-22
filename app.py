from fastapi import FastAPI, Body, UploadFile, File, HTTPException
import sys
from pathlib import Path
import os
sys.path.append(str(Path(__file__).parent / "src"))
from src.logger.logger import setup_logger
from src.middleware.request_id import RequestIdMiddleware
from src.middleware.CORS import CORSMiddleware
from src.prompts.prompt_manager import PromptManager
from src.config.config import settings
from langchain_community.chat_models import ChatOpenAI
from jinja2 import Template
import openai
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.llm_config import get_llm
import traceback
import json

BASE_URL = os.getenv("BASE_URL", "/code-conversion")
logger = setup_logger()

app = FastAPI(
    title="Code Conversion API",
    description="API for code conversion",
    docs_url=f"{BASE_URL}/docs",
    redoc_url=f"{BASE_URL}/redoc",  # ReDoc endpoint (alternative docs, default)
    openapi_tags=[
        {
            "name": "Code conversion",
            "description": "Endpoints for different types of code conversions"
        }
    ],
    openapi_security=[{
        "oauth2": {
            "type": "oauth2",
            "flow": "password",
            "tokenUrl": f"{BASE_URL}/auth/login"
        }
    }]
)
app.add_middleware(CORSMiddleware)
app.add_middleware(RequestIdMiddleware)

@app.get(f"{BASE_URL}/touch", tags=["Health check"])
async def touch():
    """
    Endpoint to check if the API is valid and operational.
    """
    return {"message": "API is valid and operational", "status": "success"}


@app.post(f"{BASE_URL}/convert/cobol-to-java", tags=["Code conversion"])
async def convert_cobol_to_java(file: UploadFile = File(...)):
    """
    Accepts a COBOL file, converts its code to Java using LLM and returns the Java code.
    """
    try:
        if not file.filename.endswith('.cob') and not file.filename.endswith('.cbl'):
            raise HTTPException(status_code=400, detail="Only COBOL files (.cob, .cbl) are supported.")
        
        # Read COBOL code from file
        cobol_code = (await file.read()).decode('utf-8')
        
        # Load prompt template
        prompt_manager = PromptManager()
        template_str = prompt_manager.load_cobal_java_template()
        
        # Prepare prompt
        prompt = Template(template_str)
        prompt_str = prompt.render(cobol_code=cobol_code)
        
        # Get LLM instance
        llm = get_llm()
        
        # Call LLM
        response = llm.invoke(prompt_str)
        try:
            # Find the JSON block in the response
            json_str = response.content.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)
        except:
            # If JSON parsing fails, return the raw response
            result = {"error": "Failed to parse JSON", "raw_response": response.content}
        return result
    except Exception as e:
        print('Exception occurred:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error. Please check server logs for details.")

@app.post(f"{BASE_URL}/convert/cobol-to-python", tags=["Code conversion"])
async def convert_cobol_to_python(file: UploadFile = File(...)):
    """
    Accepts a COBOL file, converts its code to python using LLM and returns the Python code.
    """
    try:
        if not file.filename.endswith('.cob') and not file.filename.endswith('.cbl'):
            raise HTTPException(status_code=400, detail="Only COBOL files (.cob, .cbl) are supported.")
        
        # Read COBOL code from file
        cobol_code = (await file.read()).decode('utf-8')
        
        # Load prompt template
        prompt_manager = PromptManager()
        template_str = prompt_manager.load_cobal_python_template()
        
        # Prepare prompt
        prompt = Template(template_str)
        prompt_str = prompt.render(cobol_code=cobol_code)
        
        # Get LLM instance
        llm = get_llm()
        
        # Call LLM
        response = llm.invoke(prompt_str)
        try:
            # Find the JSON block in the response
            json_str = response.content.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)
        except:
            # If JSON parsing fails, return the raw response
            result = {"error": "Failed to parse JSON", "raw_response": response.content}
        return result
    except Exception as e:
        print('Exception occurred:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error. Please check server logs for details.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)


