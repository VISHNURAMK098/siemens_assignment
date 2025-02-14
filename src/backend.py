from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

from functions.model import ModelResponse
from functions.google_translate import translate_to_english

app = FastAPI()

class UserMessage(BaseModel):
    user_id: str
    message: str

@app.post("/conversation")
async def conversation(user_message: UserMessage):
    user_id, message = user_message.user_id, user_message.message
    model_response = ModelResponse.model(user_id, translate_to_english(message))
    return {"user_id": user_id, "message": model_response}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8080, reload=True)
