import os
import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
import pydantic
from typing import List

class Translate(bt.Synapse):
    source_texts: List[str] = pydantic.Field(..., allow_mutation=False)
    translated_texts: List[str] = []
    source_lang: str = pydantic.Field(..., allow_mutation=False)
    target_lang: str = pydantic.Field(..., allow_mutation=False)
    required_hash_fields: list[str] = pydantic.Field(  ["source_texts", "source_lang", "target_lang"], allow_mutation = False)
class TranslateCrossValidator(SynapseBasedCrossval):
    def __init__(self, netuid = 2, wallet_name = 'default', wallet_hotkey = 'default', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)
        print([item['uid'] for item in self.top_miners])
        self.dendrite = bt.dendrite( wallet = self.wallet )
        self.source_lang = "en"
        self.target_lang = "es"
        self.timeout = 60
    def forward(self, text):
        translate_synapse = Translate(
            source_texts = [text],
            source_lang = self.source_lang,
            target_lang = self.target_lang
        )
        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]
        responses = self.dendrite.query(
                    axons,
                    # Construct a scraping query.
                    translate_synapse,
                    # All responses have the deserialize function called on them before returning.
                    deserialize = False, 
                    timeout = 60
                )
        return responses
    def run(self, text):
        response = self.forward(text)
        return response
    def setLang(self, source, target):
        self.source_lang = source
        self.target_lang = target
    def setTimeout(self, timeout):
        self.timeout = timeout

if __name__ == "__main__":
    translate_crossval = TranslateCrossValidator()
    print(translate_crossval.run("Hello, how are you?"))
