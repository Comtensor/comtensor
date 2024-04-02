import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import Challenge
from datetime import datetime, timedelta
import time
from pytz import timezone


class SnpOracleCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 28, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):

        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )

    def forward(self, timeout: float,):

        ny_timezone = timezone('America/New_York')
        current_time_ny = datetime.now(ny_timezone)     
        current_time_ny = datetime.now(ny_timezone)
        timestamp = current_time_ny.isoformat()

        synapse = Challenge(
            timestamp=timestamp,
        )


        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        responses = self.dendrite.query(
            axons=axons,
            synapse=synapse,
            timeout=timeout,
        )
    
        return responses
    

    def run(self):
        response = self.forward(60)
        return response


snp_crossval = SnpOracleCrossval()

print("success:",snp_crossval.run())