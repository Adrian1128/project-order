from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # enforcing data rules
from langchain_ollama import OllamaLLM

app = FastAPI()

llm = OllamaLLM(model="aya", base_url="http://localhost:11434")

# Configure CORS so Next.js frontend can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the structure of the incoming request
class ChatRequest(BaseModel):
    message: str


@app.get("/")
def read_root():
    return {"status": "Backend is running"}


@app.get("/api/test-ai")
def test_ai_connection():
    try:
        response = llm.invoke("Mi magyarország fővárosa")
        return {"status": "Success", "ai_response": response}
    except Exception as e:
        return {"status": "Error", "details": str(e)}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # Temporary mock response
    user_message = request.message
    bot_response = f"Backend received your message: '{user_message}'. The LLM pipeline will hook into this step later!"

    return {"response": bot_response}


def main():
    print("Hello from backend!")


if __name__ == "__main__":
    main()
