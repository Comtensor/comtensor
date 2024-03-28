import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import PromptingSynapse
import torch


class PromptingCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 1, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, message,  timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        responses = self.dendrite.query(
            axons=axons,
            synapse=PromptingSynapse(roles=["user"], messages=[message]),
            timeout=timeout,
        )
    
        return responses
    

    def run(self, message):
        response = self.forward(message, 60)
        return response


prompting_crossval = PromptingCrossval()

print(prompting_crossval.run("What is the comtensor?"))