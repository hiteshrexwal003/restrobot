from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from agents.intent import process_user_query

app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    sessionId: str

# Import your handle_user_query function here
# from agents.agent import handle_user_query

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    # Call your intent handler and agent logic
    response = await process_user_query(chat_request.query, chat_request.sessionId)
    result_content = response.messages[-1].content
    
    # Convert Pydantic model to dict for JSON serialization
    if hasattr(result_content, 'model_dump'):
        result_dict = result_content.model_dump()
    else:
        result_dict = result_content
    
    return JSONResponse(content={"response": result_dict})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}