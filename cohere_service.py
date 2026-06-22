import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_embedding(text: str) -> list:
    try:
        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings[0]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def ask_cohere(user_message: str, financial_context: str) -> str:
    try:
        system_prompt = f"""You are a helpful personal finance assistant.
You have access to the user's financial data:

{financial_context}

Give practical, specific financial advice based on their actual data.
Keep responses concise and friendly."""

        response = co.chat(
            message=user_message,
            preamble=system_prompt,
            model="command-r-plus-08-2024",
            temperature=0.3
        )
        return response.text
    except Exception as e:
        return f"AI service error: {str(e)}"