import bittensor as bt
import asyncio
import os
from constants import BASE_DIR, HEALTHCARE_ALL_LABELS
from base.commit_based_crossval import CommitBasedCrossval
from huggingface_hub import snapshot_download
import time
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
class HealthcareCrossval(CommitBasedCrossval):
    def __init__(self, netuid = 1, wallet_name = None, wallet_hotkey = None, network = "finney", topk = 10, subtensor = None):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk, subtensor)
        self.local_dir = os.path.join("crossvals/healthcare/model")
        self.cache_dir = os.path.join(BASE_DIR, "crossvals/healthcare/cache")
        self.minimum_threshold = 0.1
        print([item['uid'] for item in self.top_miners])
    def load_image(self, image_path, target_size = (224, 224)):
        try:
            img = load_img(image_path, target_size = target_size)
            img_array = img_to_array(img)
            image_array = np.array(image.smart_resize(img_array, target_size))
            image_array = image_array / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            return image_array
        except Exception as e:
            bt.logging.error(f"Error occured while loading image: {e}")
            return None
        
    def run(self, image_path):
        """ Diagnosis disease from the provided image """
        input_image = self.load_image(image_path)
        try:
            model_path = self.local_dir
            model = load_model(model_path)
        except Exception as e:
            bt.logging.error(f"Error occured while loading model: {e}")
            return None
        prediction = model.predict(input_image)
        prediction = prediction[0]
        bt.logging.info(f"Prediction: {prediction}")
        masked_index = []
        for idx, accuracy in enumerate(prediction):
            if accuracy > self.minimum_threshold:
                masked_index.append(idx)
        if not masked_index:
            return "Not Finding"
        labels_list = HEALTHCARE_ALL_LABELS.split("|")
        selected_labels = [labels_list[idx] for idx in masked_index]
        return "|".join(selected_labels)
    def run_custom_thread(self):
        commits = []
        for miner_axon in self.top_miners:
            commit = self.getCommit(miner_axon=miner_axon)
            print(f"Commit from miner {miner_axon['uid']}: {commit}")
            commits.append(commit)
        for commit in commits:
            self.download_model(commit)
    def download_model(self, commit):
        try:
            repo_id = commit.split(' ')[0]
            commit_hash = commit.split(' ')[1]
            snapshot_download(repo_id = repo_id, revision = commit_hash, local_dir = self.local_dir, cache_dir = self.cache_dir)
            bt.logging.success(f"Model downloaded successfully")
        except Exception as e:
            bt.logging.error(f"Error occured while downloading model: {e}")

if __name__ == "__main__":
    healthcareCrossval = HealthcareCrossval(netuid = 31, topk=1)
    healthcareCrossval.run_custom_thread()
    result = healthcareCrossval.run("crossvals/healthcare/test_image.jpg")
    print(result)
    # with HealthcareCrossval(netuid = 31, topk=1) as healthcareCrossval:
    #     while True:
    #         bt.logging.info("Running healthcare")
            
    #         time.sleep(60)
    

    