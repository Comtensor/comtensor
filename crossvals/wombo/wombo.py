import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import ImageGenerationSynapse, ImageGenerationInputs
import torch
import random
import base64


class WomboCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 30, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )
        self.step = 1

    def forward(self, timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        max_seed = 2 ** 32
        random_int = random.randint(0, max_seed)
        seed = (self.step * random_int) % max_seed

        base_prompt = str(self.step * random_int)
        selection = random.randint(0, 2)

        if selection == 1:
            prompt = base_prompt.encode("utf-8").hex()
        elif selection == 2:
            prompt = base64.b64encode(base_prompt.encode("utf-8")).decode("ascii")
        else:
            prompt = base_prompt

        input_parameters = {
            "prompt": prompt,
            "seed": seed,
            "width": 512,
            "height": 512,
            "steps": 15,
        }

        inputs = ImageGenerationInputs(**input_parameters)

        responses = self.dendrite.query(
            axons=axons,
            synapse=ImageGenerationSynapse(inputs=inputs),
            deserialize=False,
            timeout=timeout,
        )
    
        return responses
    

    def run(self):
        response = self.forward(60)
        return response


wombo_crossval = WomboCrossval()

print(wombo_crossval.run())