import os
import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval

import bittensor as bt
import pydantic
from typing import List
from crossvals.prompting.protocol import StreamPromptingSynapse, PromptingSynapse
import asyncio

class PromtingCrossValidator(SynapseBasedCrossval):
    def __init__(self, netuid = 1, wallet_name = 'default', wallet_hotkey = 'default', network = "finney", topk = 1, subtensor = None):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk, subtensor)
        self.dendrite = bt.dendrite( wallet = self.wallet )

    async def process_response(self, uid: int, responses):
        """Process a single response asynchronously."""
        try:
            chunk = None  # Initialize chunk with a default value
            for resp in responses:
                async for chunk in resp:
                    bt.logging.debug(f"\nchunk for uid {uid}: {chunk}")

                if chunk is not None:
                    synapse = chunk  # last object yielded is the synapse itself with completion filled

                    # Assuming chunk holds the last value yielded which should be a synapse
                    if isinstance(synapse, StreamPromptingSynapse):
                        return synapse

            bt.logging.debug(
                f"Synapse is not StreamPromptingSynapse. Miner uid {uid} completion set to '' "
            )
        except Exception as e:
            # bt.logging.error(f"Error in generating reference or handling responses: {e}", exc_info=True)
            # traceback_details = traceback.format_exc()
            # bt.logging.error(
            #     f"Error in generating reference or handling responses for uid {uid}: {e}\n{traceback_details}"
            # )

            failed_synapse = StreamPromptingSynapse(
                roles=["user"], messages=["failure"], completion=""
            )

            return failed_synapse
        
    async def forward(self, input, timeout):
        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]
        uid = [i['uid'] for i in self.top_miners][0]
        responses = await self.dendrite(
            axons=axons,
            synapse=StreamPromptingSynapse(roles=input.roles, messages=input.messages),
            timeout=timeout,
            deserialize=False,
            streaming=True,
        )
        responses = await self.process_response(uid, responses)
        return responses
    
    async def run(self, private_input):
        response = await self.forward(private_input, timeout=60)
        return response
    
async def main():
    textpromptingCrossval = PromtingCrossValidator()
    streamingResponse = textpromptingCrossval.run()
    while True:
        data = await streamingResponse[0].__anext__()
        print(data)
        await asyncio.sleep(1)
    # print(translate_crossval.run("Hello, how are you?"))

if __name__ == "__main__":
    asyncio.run(main())
    # print(translate_crossval.run("Hello, how are you?"))b
