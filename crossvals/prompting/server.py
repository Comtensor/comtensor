import os
from fastapi import FastAPI, HTTPException, Header, Request
from openai import OpenAI
import uvicorn
from dotenv import load_dotenv, find_dotenv


class CommuneOpenAIMiner():

    def __init__(self, messages):
        super().__init__()
        
        _ = load_dotenv(find_dotenv())
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.messages = messages

    async def get_reply(self):

        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            stream=True,
        )
        

        collected_chunks = []
        collected_messages = []

        for chunk in stream:
            collected_chunks.append(chunk)  
            chunk_message = chunk.choices[0].delta.content   
            collected_messages.append(chunk_message) 

        collected_messages = [m for m in collected_messages if m is not None]
        full_reply_content = ''.join([m for m in collected_messages])

        return full_reply_content


app = FastAPI()

@app.post("/prompting")
async def process_payload(request: Request):
    # token = request.headers.get('Authorization')
    # if token != "Bearer xcrystal":
    #     raise HTTPException(status_code=401, detail="Invalid token")

    payload = await request.json()

    
    messages = payload['messages']
    miner = CommuneOpenAIMiner(messages)
    response = await miner.get_reply()

    return response


@app.get("/")
async def get_page(request: Request):

    return "Hello"


if __name__ == "__main__":
    _ = load_dotenv(find_dotenv())
    HOST = os.environ.get("HOST_ADDRESS")
    PORT = int(os.environ.get("PORT"))
    uvicorn.run(app, host=HOST, port=PORT)