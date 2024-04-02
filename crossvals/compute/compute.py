import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import Challenge
import typing
import random
from crossvals.compute.utils import (    
    pow_min_difficulty,
    pow_max_difficulty,
    pow_timeout,
    SUSPECTED_EXPLOITERS_HOTKEYS,
    SUSPECTED_EXPLOITERS_COLDKEYS,
    __version_as_int__,
    weights_rate_limit,
    specs_timeout,
    run_validator_pow
)



class ComputeCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 29, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, timeout: float,):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        difficulty = random.randint(pow_min_difficulty, pow_max_difficulty)
        password, _hash, _salt, mode, chars, mask = run_validator_pow(length=difficulty)

        synapse = Challenge(
                challenge_hash=_hash,
                challenge_salt=_salt,
                challenge_mode=mode,
                challenge_chars=chars,
                challenge_mask=mask,
                challenge_difficulty=difficulty,
            ),

        responses = self.dendrite.query(
            axons=axons,
            synapse=synapse,
            deserialize=True,
            timeout=timeout,
        )
        

        return responses
    

    def run(self):
        response = self.forward(60)
        return response


compute_crossval = ComputeCrossval()


print("success:",compute_crossval.run())