import shutil
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from crossvals.translate.translate import TranslateCrossValidator
from crossvals.healthcare.healthcare import HealthcareCrossval
from crossvals.textprompting.text import TextPromtingCrossValidator
from crossvals.sybil.sybil import SybilCrossVal
from crossvals.openkaito.openkaito import OpenkaitoCrossVal

from fastapi import UploadFile, File, HTTPException
import asyncio
from pydantic import BaseModel

app = FastAPI()

# Enable all cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# healthcare_crossval.run_background_thread()

class TranlsateItem(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "es"
    timeout: int = None
class TextPropmtItem(BaseModel):
    roles: list[str] = ["user", "assistant"]
    messages: list[str] = [
        "What's the weather like today?",
        "The weather is sunny with a high of 25 degrees.",
        "Could you set a reminder for me to take my umbrella tomorrow?",
        "Reminder set for tomorrow to take your umbrella.",
        "Thank you! What time is my first meeting tomorrow?",
        "Your first meeting tomorrow is at 9 AM.",
        "Can you play some music?",
        "Playing your favorite playlist now.",
        "How's the traffic to work?",
        "Traffic is light, it should take about 15 minutes to get to work."
    ]

class SybilItem(BaseModel):
    sources: str
class OpenkaitoItem(BaseModel):
    query: str

@app.get("/")
def read_root():
    return translate_crossval.run("Hello, how are you?")

@app.post("/translate/")
def tranlsate_item(item: TranlsateItem):
    
    translate_crossval.setLang(item.source_lang, item.target_lang)
    if item.timeout:
        translate_crossval.setTimeout(item.timeout)
    return translate_crossval.run(item.text)

@app.post("/sybil/")
def sybil_search(item: SybilItem):
    return sybil_crossval.run({'sources': item.sources, 'query': item.query})

@app.post("/openkaito/")
async def openkaito_search(item: OpenkaitoItem):
    await openkaito_crossval.run(item.query)

class ImageUpload(BaseModel):
    file: UploadFile = File(...)

# @app.post("/healthcare/")
# async def analyze_healthcare_image(image: ImageUpload):
#     print(image.file.filename)
#     file_location = f"images/{image.file.filename}"
#     with open(file_location, "wb+") as file_object:
#         file_object.write(await image.file.read())
#     result = healthcare_crossval.run(file_location)
#     return {"result": result}

@app.post("/healthcare/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Save the file to disk or process it
        with open(f"{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            result = healthcare_crossval.run(image.filename)
            # print(result)     
        # You can process the file here, and then return a response
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-prompting/")
def text_prompting(item: TextPropmtItem):
    return textpromtingCrossval.run(item.roles, item.messages)

# @app.websocket("/textprompting")
# async def text_prompting(websocket: WebSocket):
#     print("sdf")
#     await websocket.accept()
#     # data = await websocket.receive_text()
#     streamingResponse = textpromtingCrossval.run()
#     while True:
#         print("tread_running...")
#         data = await streamingResponse[0].__anext__()
#         await websocket.send_json({"message": data})
#         print(data)
#         await asyncio.sleep(1)


translate_crossval = TranslateCrossValidator()
healthcare_crossval = HealthcareCrossval(netuid = 31, topk = 1)
textpromtingCrossval = TextPromtingCrossValidator()
sybil_crossval = SybilCrossVal()
openkaito_crossval = OpenkaitoCrossVal()
