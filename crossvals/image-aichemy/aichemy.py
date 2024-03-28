import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import ImageGeneration
import typing


class ImageAIchemyCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 26, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, prompt, timeout:float, task_type="text_to_image", image=None):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]


        synapse = (
            ImageGeneration(
                generation_type=task_type,
                prompt=prompt,
                prompt_image=image,
                seed=-1,
            )
            if image is not None
            else ImageGeneration(
                generation_type=task_type,
                prompt=prompt,
                seed=-1,
            )
        )

        responses = self.dendrite.query(
            axons=axons,
            synapse=synapse,
            deserialize=True,
            timeout=timeout,
        )

        return responses
    

    def run(self, query):
        response = self.forward(query, 60)
        return response


aichemy_crossval = ImageAIchemyCrossval()

print(aichemy_crossval.run('Make the apple'))