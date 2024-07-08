from abc import ABC, abstractmethod
import bittensor as bt
import threading
import time
class BaseCrossval(ABC):
        
    def __init__(self, netuid = 1, wallet_name = None, wallet_hotkey = None, network = "finney", topk = 1, subtensor = None):
        self.netuid = netuid
        if wallet_name is not None and wallet_hotkey is not None:
            try:
                self.wallet = bt.wallet(name=wallet_name, hotkey=wallet_hotkey)
            except Exception as e:
                bt.logging.error(f"Error occured while importing wallet{e}")
                self.wallet = None
        if subtensor is not None:
            self.subtensor = subtensor
        else:
            self.subtensor = bt.subtensor(network = network)
        bt.logging.info(f"Syncing metagraph on netuid: {self.netuid}")
        self.metagraph = self.subtensor.metagraph(netuid = self.netuid)
        self.topk = topk
        self.top_miners = self.get_top_miners()
        self.block = self.subtensor.block
        self.is_thread_running = False
        # self.run_background_thread()
    # def query(self):
    #     ...
    #     # TODO: Developer have to implement this method to query the miner

    # Check if wallet is initialized, registered to subnet and staked with enough stake for querying miners
    def check_wallet(self):
        # Check if wallet is initialized
        if self.wallet is None:
            raise Exception("Wallet not initialized.")
        # Check if wallet is registered to subnet
        if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
            raise Exception("Wallet not registered to subnet.")
        # Check if wallet is staked with enough stake
        if self.metagraph.hotkeys[self.wallet.hotkey.ss58_address].stake < 1:
            raise Exception("Wallet not staked with enough stake.")

    def get_top_miners(self):
        """Get top K miners from metagraph"""


        metagraph_json = [{
            "netuid": self.netuid,
            "uid": i,
            "ip": axon.ip,
            "port": axon.port,
            "coldkey": axon.coldkey,
            "hotkey": axon.hotkey,
            "active": axon.is_serving,
            "rank": self.metagraph.ranks[i].item(),
            "v_trust": self.metagraph.validator_trust[i].item(),
            "v_permit": self.metagraph.validator_permit[i].item(),
            "trust": self.metagraph.trust[i].item(),
            "consensus": self.metagraph.consensus[i].item(),
            "incentive": self.metagraph.incentive[i].item(),
            "dividends": self.metagraph.dividends[i].item(),
            "emission": self.metagraph.emission[i].item(),
            "stake": self.metagraph.stake[i].item(),
            "last_update": self.metagraph.last_update[i].item(),
        } for i, axon in enumerate(self.metagraph.axons)]

        metagraph_json.sort(key = lambda x: x['emission'], reverse = True)
        top_miners = []
        for i, item in enumerate(metagraph_json):
            if item['v_trust'] > 0:
                continue
            top_miners.append(item)
            if len(top_miners) == self.topk:
                break
        
        return top_miners
    def run_thread(self):
        while True:
            self.resync_metagraph()
            self.top_miners = self.get_top_miners()
            self.run_custom_thread()
            self.block = self.subtensor.block
            time.sleep(120)
    def run_custom_thread(self):
        ...
    def run_background_thread(self):
        if not self.is_thread_running:
            self.thread = threading.Thread(target=self.run_thread)
            self.thread.start()
            self.is_thread_running = True
            bt.logging.info("Thread started")
    def stop_background_thread(self):
        if self.is_thread_running:
            self.is_thread_running = False
            self.thread.join(5)
            bt.logging.info("Thread stopped")
    def __enter__(self):
        self.run_background_thread()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_background_thread()
    def resync_metagraph(self):
        bt.logging.info("resync_metagraph")
        self.metagraph.sync(subtensor = self.subtensor)