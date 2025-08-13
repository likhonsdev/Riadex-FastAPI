import httpx
import json
from typing import AsyncGenerator, Dict, Any
from infrastructure.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()

class AIService:
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.gemini_api_key = settings.gemini_api_key
    
    async def generate_streaming_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming AI response"""
        try:
            # Use Gemini through OpenAI-compatible API
            if self.gemini_api_key:
                async for chunk in self._generate_gemini_response(message):
                    yield chunk
            elif self.openai_api_key:
                async for chunk in self._generate_openai_response(message):
                    yield chunk
            else:
                # Fallback to mock response
                async for chunk in self._generate_mock_response(message):
                    yield chunk
                    
        except Exception as e:
            logger.error("AI service error", error=str(e))
            yield {"type": "error", "data": {"error": str(e)}}
    
    async def _generate_gemini_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate response using Gemini API"""
        try:
            # Gemini through OpenAI-compatible endpoint
            headers = {
                "Authorization": f"Bearer {self.gemini_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gemini-pro",
                "messages": [{"role": "user", "content": message}],
                "stream": True
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("choices") and chunk["choices"][0].get("delta"):
                                    content = chunk["choices"][0]["delta"].get("content", "")
                                    if content:
                                        yield {"type": "message", "content": content}
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error("Gemini API error", error=str(e))
            yield {"type": "error", "data": {"error": str(e)}}
    
    async def _generate_openai_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate response using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": message}],
                "stream": True
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("choices") and chunk["choices"][0].get("delta"):
                                    content = chunk["choices"][0]["delta"].get("content", "")
                                    if content:
                                        yield {"type": "message", "content": content}
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error("OpenAI API error", error=str(e))
            yield {"type": "error", "data": {"error": str(e)}}
    
    async def _generate_mock_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate mock response for testing"""
        import asyncio
        
        response_text = f"I received your message: '{message}'. This is a mock response from the AI service."
        
        # Simulate streaming by sending chunks
        words = response_text.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.1)  # Simulate delay
            chunk = word + (" " if i < len(words) - 1 else "")
            yield {"type": "message", "content": chunk}
