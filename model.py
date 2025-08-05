from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from chroma import Chroma_db

# Load environment variables from .env file
load_dotenv()

# Retrieve values from environment variables
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
model_name = os.getenv("MODEL_NAME")

# Configure the local LLM endpoint
llm = ChatOpenAI(
    base_url=base_url,
    api_key=api_key,
    model=model_name
)

def generate_response(prompt):
    chroma_init = Chroma_db()
    prompt = chroma_init.ask_chromadb(prompt, nb_context=3)
    for chunk in llm.stream(prompt):
        yield chunk.content

# Test the model
if __name__ == "__main__":
    response = llm.invoke("Hello, how are you?")
    print(response.content)





