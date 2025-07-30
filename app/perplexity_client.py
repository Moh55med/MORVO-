import os
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Perplexity client with API key from env or parameter."""
        load_dotenv()
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY must be provided")
        
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make a request to the Perplexity API."""
        data = {
            "model": "sonar",  # Using Sonar model
            "messages": messages
        }
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 200:
                    raise Exception(f"API error (status {response.status_code}): {response.text}")
                
                return response.json()
        except httpx.TimeoutException:
            raise Exception("Request timed out")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    async def test_connection(self) -> dict:
        """Test if the Perplexity API key is valid."""
        try:
            messages = [{"role": "user", "content": "Say hello"}]
            await self._make_request(messages)
            return {"status": "success", "message": "API key is valid"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def chat(self, message: str) -> str:
        """Send a chat message to Perplexity."""
        try:
            messages = [{"role": "user", "content": message}]
            response = await self._make_request(messages)
            
            if not response or "choices" not in response:
                raise Exception("Invalid response format from Perplexity API")
                
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Chat error: {str(e)}")

# Test script
async def test_perplexity_key():
    """Test the Perplexity API key."""
    print("\n🔑 Testing Perplexity API connection...")
    
    try:
        client = PerplexityClient()
        print(f"Using API key: {client.api_key[:10]}...")
        
        print("\n📡 Sending test request...")
        result = await client.test_connection()
        
        if result["status"] == "success":
            print("✅ API key is valid!")
            
            # Try a test message
            print("\n📝 Sending test message...")
            response = await client.chat("Say hello")
            print(f"📥 Response: {response}")
            
            return True
        else:
            print(f"❌ API key test failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_perplexity_key())