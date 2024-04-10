from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from crossvals.sybil.sybil import SybilCrossVal
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable all cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

sybil_crossval = SybilCrossVal()

class SybilInput(BaseModel):
    sources: str
    query: str

@app.get("/")
def read_root():
    return sybil_crossval.run({"This is sybil", "what is sybil"})


@app.post("/sybil/")
def sybil_search(item: SybilInput):
    return sybil_crossval.run({'sources': item.sources, 'query': item.query})
