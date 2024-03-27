import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import Challenge, InferenceeSamplingParams
import typing


class FractalResearchCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 29, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, private_input: typing.Dict[str,str], sampling_params: InferenceeSamplingParams,   timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        synapse = Challenge(
            sources = [private_input["sources"]],
            query = private_input["query"],
            sampling_params=sampling_params,
        )

        responses = self.dendrite.query(
            axons=axons,
            synapse=synapse,
            deserialize=True,
            timeout=timeout,
        )

        return responses
    

    def run(self, private_input, sampling_params):
        response = self.forward(private_input, sampling_params, 60)
        return response


fractal_crossval = FractalResearchCrossval()

p_input = {
    "sources": "reddit",
    "query": "what is the bittensor?"
}
params = {
    'seed': 10
}

print(fractal_crossval.run(p_input, params))