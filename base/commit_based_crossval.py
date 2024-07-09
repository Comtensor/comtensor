from abc import ABC, abstractmethod
from base.crossval import BaseCrossval
from utils import run_in_subprocess, functools
import bittensor as bt
from utils import functools, run_in_subprocess
class CommitBasedCrossval(BaseCrossval):
    def __init__(self, netuid = 1, wallet_name = None, wallet_hotkey = None, network = "finney", topk = 10, subtensor = None):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk, subtensor)
    
    @abstractmethod
    def run(self):
        ...
    
    def getCommit(self, miner_axon = None) -> str:
        """Get the commit from the miner"""
        # * Check if wallet is initialized, registered to subnet and staked with enough stake for querying miners
        if miner_axon is None:
            raise Exception("Miner UID not provided.")
        if miner_axon['hotkey'] not in self.metagraph.hotkeys:
            raise Exception("Miner UID not found in metagraph.")
        
        partial = functools.partial(self.subtensor.get_commitment, netuid = self.netuid, uid = miner_axon['uid'])
        last_commit = run_in_subprocess(partial, 30)

        # last_commit = self.subtensor.get_commitment(netuid = self.netuid, uid = miner_axon['uid'])


        return last_commit

if __name__ == "__main__":
    subtensor = bt.subtensor()
    partial = functools.partial(subtensor.get_commitment, 3, 175)
    latest_commit = run_in_subprocess(partial, 30)
    print(latest_commit)