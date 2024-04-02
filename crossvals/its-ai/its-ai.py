import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import TextSynapse



class ItsAICrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 32, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, query_string,  timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        responses = self.dendrite.query(
            axons=axons,
            synapse=TextSynapse(texts=[query_string], predictions=[]),
            deserialize=True,
            timeout=timeout,
        )

    
        return responses
    

    def run(self, query_string):
        response = self.forward(query_string, 60)
        return response


itsai_crossval = ItsAICrossval()

print("success:",itsai_crossval.run("This is it's AI."))