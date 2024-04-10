import os
import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval

import bittensor as bt
import pydantic
from typing import List
from crossvals.textprompting.protocol import StreamPromptingSynapse, PromptingSynapse
import asyncio
class TextPromtingCrossValidator(SynapseBasedCrossval):
    def __init__(self, netuid = 1, wallet_name = 'default', wallet_hotkey = 'default', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)
        self.dendrite = bt.dendrite( wallet = self.wallet )
        print([item['uid'] for item in self.top_miners])
        
    def forward(self, roles = ["user", "assistant"], messages=[
        "What's the weather like today?",
        "The weather is sunny with a high of 25 degrees.",
        "Could you set a reminder for me to take my umbrella tomorrow?",
        "Reminder set for tomorrow to take your umbrella.",
        "Thank you! What time is my first meeting tomorrow?",
        "Your first meeting tomorrow is at 9 AM.",
        "Can you play some music?",
        "Playing your favorite playlist now.",
        "How's the traffic to work?",
        "Traffic is light, it should take about 15 minutes to get to work."
    ]):
        promptSynapse = PromptingSynapse(roles = roles, messages = messages)
        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]
        responses = self.dendrite.query(
                    axons,
                    # Construct a scraping query.
                    promptSynapse,
                    # All responses have the deserialize function called on them before returning.
                    deserialize = False, 
                    timeout = 60
                )
        return responses
    def run(self, roles = ["user", "assistant"], messages=[
        "What's the weather like today?",
        "The weather is sunny with a high of 25 degrees.",
        "Could you set a reminder for me to take my umbrella tomorrow?",
        "Reminder set for tomorrow to take your umbrella.",
        "Thank you! What time is my first meeting tomorrow?",
        "Your first meeting tomorrow is at 9 AM.",
        "Can you play some music?",
        "Playing your favorite playlist now.",
        "How's the traffic to work?",
        "Traffic is light, it should take about 15 minutes to get to work."
    ]):
        response = self.forward(roles=roles, messages=messages)
        return response
async def main():
    textpromtingCrossval = TextPromtingCrossValidator()
    streamingResponse = textpromtingCrossval.run()
    while True:
        data = await streamingResponse[0].__anext__()
        print(data)
        await asyncio.sleep(1)
    # print(translate_crossval.run("Hello, how are you?"))
if __name__ == "__main__":
    asyncio.run(main())
    # print(translate_crossval.run("Hello, how are you?"))b
