from cohere import ClientV2
from app.core.config import settings

co = ClientV2(api_key=settings.COHERE_API_KEY)

async def generate_response(prompt: str) -> str:
    response = co.chat(
        model="command-a-03-2025",  
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.message.content[0].text


print("COHERE KEY =", settings.COHERE_API_KEY)
