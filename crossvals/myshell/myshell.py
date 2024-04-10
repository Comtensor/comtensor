import bittensor as bt
import asyncio
import os
from constants import BASE_DIR, HEALTHCARE_ALL_LABELS
from base.commit_based_crossval import CommitBasedCrossval
from huggingface_hub import snapshot_download
import time
import torch
from safetensors.torch import load_file
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
class MyshellCrossval(CommitBasedCrossval):
    def __init__(self, netuid = 3, wallet_name = None, wallet_hotkey = None, network = "finney", topk = 1, subtensor = None):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk, subtensor)
        print([item['uid'] for item in self.top_miners])
        self.local_dir = os.path.join("crossvals/myshell/model")
        self.cache_dir = os.path.join(BASE_DIR, "crossvals/myshell/cache")
    def run(self, text):
        """ Run the model """
        try:
            model_path = self.local_dir
            # convert to pth file
            loaded = load_file(model_path + "/checkpoint.safetensors")
            loaded = {"model": loaded}
            torch.save(loaded, "crossvals/myshell/model/checkpoint.pth")
        except Exception as e:
            bt.logging.error(f"Error occured while loading model: {e}")
            return None
    
        
    def run_custom_thread(self):
        try:
            commits = []
            for miner_axon in self.top_miners:
                commit = self.getCommit(miner_axon=miner_axon)
                print(f"Commit from miner {miner_axon['uid']}: {commit}")
                commits.append(commit)
            for commit in commits:
                self.download_model(commit)
        except Exception as e:
            bt.logging.error(f"Error occured while running custom thread: {e}")
    def download_model(self, commit):
        try:
            repo_id = commit.split(':')[0] + '/' + commit.split(':')[1]
            
            snapshot_download(repo_id = repo_id, local_dir = self.local_dir, cache_dir = self.cache_dir)
            bt.logging.success(f"Model downloaded successfully")
        except Exception as e:
            bt.logging.error(f"Error occured while downloading model: {e}")
    # def download_model(self, commit):
    #     try:
    #         repo_id = commit.split(' ')[0]
    #         commit_hash = commit.split(' ')[1]
    #         snapshot_download(repo_id = repo_id, revision = commit_hash, local_dir = self.local_dir, cache_dir = self.cache_dir)
    #         bt.logging.success(f"Model downloaded successfully")
    #     except Exception as e:
    #         bt.logging.error(f"Error occured while downloading model: {e}")

if __name__ == "__main__":
    myshellCrossval = MyshellCrossval(netuid = 3, topk=1)
    myshellCrossval.run_custom_thread()
    myshellCrossval.run("Hello, how are you?")
    # result = healthcareCrossval.run("crossvals/healthcare/test_image.jpg")
    # print(result)
    # with HealthcareCrossval(netuid = 31, topk=1) as healthcareCrossval:
    #     while True:
    #         bt.logging.info("Running healthcare")
            
    #         time.sleep(60)
    

    