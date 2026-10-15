from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def get_embedding(text: str) -> list[float]:
    """Converts a string of text into a 768-dimensional vector."""
    
    response = client.models.embed_content(
        model='models/gemini-embedding-2',
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    
    if not response.embeddings or not response.embeddings[0].values:
        raise ValueError("Gemini API failed to return an embedding.")
        
    return response.embeddings[0].values

if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        try:
            vector = await get_embedding("FastAPI Developer")
            print(f"Generated vector with {len(vector)} dimensions.")
            print(f"First 5 numbers: {vector[:5]}")
        except Exception as e:
            print(f"Test failed: {e}")
    
    asyncio.run(run_test())