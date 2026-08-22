import asyncio
import sys
import os
import httpx

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.config import get_settings
from app.providers.llm.gemini_provider import GEMINI_MODEL_CANDIDATES

async def check_models():
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY
    print(f"Checking Gemini models with key present: {bool(api_key)}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # First list available models
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = await client.get(list_url)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            print("\nAvailable models in Gemini API:")
            for m in models_data:
                name = m.get("name")
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(f"  - {name}")
        else:
            print(f"Failed to list models: HTTP {res.status_code} {res.text[:200]}")

        print("\nTesting candidates in GEMINI_MODEL_CANDIDATES:")
        for model in GEMINI_MODEL_CANDIDATES:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
            try:
                r = await client.post(url, json=payload)
                print(f"Model '{model}': Status {r.status_code}")
                if r.status_code != 200:
                    print(f"   Response: {r.text[:100]}")
            except Exception as e:
                print(f"Model '{model}': Error {e}")

if __name__ == "__main__":
    asyncio.run(check_models())
