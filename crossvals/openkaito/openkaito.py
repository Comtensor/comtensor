import bittensor as bt
from base.synapse_based_crossval import SynapseBasedCrossval
from crossvals.openkaito.protocol import SearchSynapse, StructuredSearchSynapse
from crossvals.openkaito.utils import get_version
import random
from crossvals.openkaito.tasks import (
    generate_author_index_task,
    generate_structured_search_task,
    random_query,
)

class OpenkaitoCrossVal(SynapseBasedCrossval):

    def __init__(self, netuid = 5, wallet_name = 'default', wallet_hotkey = 'default', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)
        self.dendrite = bt.dendrite( wallet = self.wallet )
    
    async def forward(self, query_string):
        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]
        random_number = random.random()
        # mixed tasks, deprecated SearchSynapse
        if random_number < 0:
            search_query = SearchSynapse(
                query_string=query_string,
                size=5,
                version=get_version(),
            )
            search_query.timeout = 90
        else:
            # 80% chance to send index author data task with crawling and indexing
            if random_number < 0.8:
                search_query = generate_author_index_task(
                    size=10,  # author index data size
                    num_authors=2,
                )
                # this is a bootstrap task for users to crawl more data from the author list.
                # miners may implement a more efficient way to crawl and index the author data in the background,
                # instead of relying on the validator tasks
                search_query.timeout = 90
            # 10% chance to send author search task without crawling
            elif random_number < 0.9:
                search_query = generate_author_index_task(
                    size=10,  # author index data size
                    num_authors=2,
                )
                search_query.timeout = 10
            # 10% chance to send structured search task
            else:
                search_query = generate_structured_search_task(
                    query_string=query_string,
                    size=5,
                )
                search_query.timeout = 90
        
        print(search_query)

        responses = await self.dendrite(
            # Send the query to selected miner axons in the network.
            axons=axons,
            synapse=search_query,
            deserialize=True,
            timeout=search_query.timeout,
        )

        return responses

    async def run(self, query_string):
        response = await self.forward(query_string);
        return response