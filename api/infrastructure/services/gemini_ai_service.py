import httpx
import json
from typing import AsyncGenerator, List, Dict, Any
import structlog

from ...domain.services.ai_service import AIService
from ...infrastructure.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class GeminiAIService(AIService):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_BASE_URL
        self.model = "gemini-pro"
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert OpenAI-style messages to Gemini format"""
        contents = []
        for message in messages:
            if message["role"] == "system":
                # Gemini doesn't have system role, prepend to first user message
                continue
            elif message["role"] == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": message["content"]}]
                })
            elif message["role"] == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": message["content"]}]
                })
        
        return {"contents": contents}
    
    async def generate_response(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a single response using Gemini API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                
                payload = self._convert_messages_to_gemini_format(messages)
                
                response = await client.post(
                    url,
                    json=payload,
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.error("No candidates in Gemini response", result=result)
                    return "I apologize, but I couldn't generate a response at this time."
                    
        except Exception as e:
            logger.error("Error calling Gemini API", error=str(e))
            return "I apologize, but I encountered an error while processing your request."
    
    async def generate_response_stream(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        """Generate streaming response using Gemini API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/models/{self.model}:streamGenerateContent"
                
                payload = self._convert_messages_to_gemini_format(messages)
                
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                # Parse JSON from each line
                                data = json.loads(line)
                                if "candidates" in data and len(data["candidates"]) > 0:
                                    candidate = data["candidates"][0]
                                    if "content" in candidate and "parts" in candidate["content"]:
                                        text = candidate["content"]["parts"][0].get("text", "")
                                        if text:
                                            yield text
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error("Error streaming from Gemini API", error=str(e))
            yield "I apologize, but I encountered an error while processing your request."
