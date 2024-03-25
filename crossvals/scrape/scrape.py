import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import *
import torch


class ScrapeCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 3, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, search_key,  timeout: float):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]


        responses = self.dendrite.query(
            axons=axons,
            synapse = TwitterScrap(scrap_input = {"search_key" : [search_key]} ), 
            deserialize = True,
            timeout = timeout 
        )
    
        return responses
    

    def run(self, search_key):
        response = self.forward(search_key, 60)
        return response


scrape_crossval = ScrapeCrossval()

print(scrape_crossval.run("ether price"))