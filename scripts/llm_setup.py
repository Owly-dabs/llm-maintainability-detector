from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

def set_openai(local: bool = False) -> OpenAI:
    
    if local:
        return OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama'  # required, but unused
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        
        return OpenAI(api_key=api_key)