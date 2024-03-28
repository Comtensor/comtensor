import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import SearchSynapse, StructuredSearchSynapse
from utils import get_version


class OpenkaitoCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 5, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, query_string,  timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        search_query = SearchSynapse(
            query_string = query_string,
            size = 5,
            version = get_version(),
        )

        responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=axons,
            synapse=search_query,
            deserialize=True,
            timeout=timeout,
        )

    
        return responses
    

    def run(self, query_string):
        response = self.forward(query_string, 90)
        return response


openkaito_crossval = OpenkaitoCrossval()

print(openkaito_crossval.run("BTC"))