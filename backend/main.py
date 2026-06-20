from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # enforcing data rules

app = FastAPI()

# Configure CORS so your Next.js frontend can communicate with FastAPI
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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # This is a temporary mock response until you choose your LLM approach
    user_message = request.message
    bot_response = f"Backend received your message: '{user_message}'. The LLM pipeline will hook into this step later!"

    return {"response": bot_response}


def main():
    print("Hello from backend!")


if __name__ == "__main__":
    main()
