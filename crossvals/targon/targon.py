import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import *
import torch


class TargonCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 4, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, private_input, timeout: float):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]


        sampling_params= InferenceSamplingParams()


        synapse = Challenge(
            sources = [private_input["sources"]],
            query = private_input["query"],
            sampling_params = sampling_params,
        )

        responses = self.dendrite.query(
            axons = axons,
            synapse = synapse,
            deserialize = False,
            timeout = timeout,
        )
    
        return responses
    

    def run(self, private_input):
        response = self.forward(private_input,60)
        return response


scrape_crossval = TargonCrossval()
input = {
    "sources": '',
    "query" : "what is targon?"
}
print("success:",scrape_crossval.run(input))