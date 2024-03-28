import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import sys
import numpy as np
import random
from loguru import logger

class GenerationRequest(BaseModel):
    seed: int
    text: str

app = FastAPI()

# Configure Loguru logger
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")

pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

def preprocess_text(text, limit=76):
    tokens = text.split()[:limit]
    return ' '.join(tokens)

@app.post('/generate')
async def generate(request_data: GenerationRequest):
    try:
        seed = request_data.seed
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        prompt = preprocess_text(request_data.text)

        video_frames = pipe(prompt, num_inference_steps=25).frames
        video_path = export_to_video(video_frames)

        with open(video_path, 'rb') as video_file:
            video_data = video_file.read()

        video_base64_encoded = base64.b64encode(video_data)
        video_base64_string = video_base64_encoded.decode('utf-8')

        torch.cuda.empty_cache()

        return {'completion': video_base64_string}
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            logger.error("CUDA out of memory. Consider reducing the request rate or payload size.")
            raise HTTPException(status_code=503, detail="CUDA out of memory. Try again later.")
        else:
            logger.exception("An error occurred during request processing - Runtime")
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("An error occurred during request processing")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)