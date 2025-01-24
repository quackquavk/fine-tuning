from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from chat_response import generate_response, ConversationContext

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    message: str
    conversationHistory: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        # Generate response using our chat logic
        response = generate_response(request.message)
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For testing the API directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 