import os
import pickle
import torch
import time
import shutil
import typing
import hashlib
import sqlite3
import argparse
import traceback
from random import randint
import bittensor as bt
from rich.table import Table
from rich.console import Console
from base.synapse_based_crossval import SynapseBasedCrossval
from protocol import *
from crossvals.tensorage.utils import get_config, __version__
import allocate
from concurrent.futures import ThreadPoolExecutor


import copy
from tqdm import tqdm


# Step 2: Set up the configuration parser
# This function is responsible for setting up and parsing command-line arguments.
def get_config(wallet_name:str, wallet_hotkey:str, netuid:int):

    parser = argparse.ArgumentParser()
    # TODO(developer): Adds your custom miner arguments to the parser.
    parser.add_argument('--db_root_path', default=os.path.expanduser('~/bittensor-db'), help='Validator hashes')
    parser.add_argument('--no_bridge', action='store_true', help='Run without bridging to the network.')
    # Adds override arguments for network and netuid.
    parser.add_argument( '--netuid', type = int, default = netuid, help = "The chain subnet uid." )
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    # bt.wallet.add_args(parser)

    parser.add_argument("--wallet.name", type=str, default=wallet_name, help="wallet name")

    parser.add_argument("--wallet.hotkey", type=str, default=wallet_hotkey, help='wallet hotkey')

    # Parse the config (will take command-line arguments if provided)
    # To print help message, run python3 template/miner.py --help
    config =  bt.config(parser)

    # Step 3: Set up logging directory
    # Logging is crucial for monitoring and debugging purposes.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'validator',
        )
    )
    # Ensure the logging directory exists.
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    # Return the parsed config.
    return config



def main(config):
    # Set up logging with the provided configuration and directory.
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.info(f"Running validator for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint} with config:")
    # Log the configuration for reference.
    bt.logging.info(config)

    # Step 4: Build Bittensor validator objects
    # These are core Bittensor classes to interact with the network.
    bt.logging.info("Setting up bittensor objects.")

    # The wallet holds the cryptographic key pairs for the validator.
    wallet = bt.wallet( config = config )
    bt.logging.info(f"Wallet: {wallet}")

    # The subtensor is our connection to the Bittensor blockchain.
    subtensor = bt.subtensor( config = config )
    bt.logging.info(f"Subtensor: {subtensor}")

    # Dendrite is the RPC client; it lets us send messages to other nodes (axons) in the network.
    dendrite = bt.dendrite( wallet = wallet )
    bt.logging.info(f"Dendrite: {dendrite}")

    # The metagraph holds the state of the network, letting us know about other miners.
    metagraph = subtensor.metagraph( config.netuid )
    bt.logging.info(f"Metagraph: {metagraph}")

    # Step 5: Connect the validator to the network
    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        bt.logging.error(f"\nYour validator: {wallet} if not registered to chain connection: {subtensor} \nRun btcli register and try again.")
        exit()
    else:
        # Each miner gets a unique identity (UID) in the network for differentiation.
        my_subnet_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
        bt.logging.info(f"Running validator on uid: {my_subnet_uid}")

    # Step 6: Set up initial scoring weights for validation
    bt.logging.info("Building validation weights.")
    alpha = 0.9
    scores = torch.ones_like(metagraph.S, dtype=torch.float32)
    bt.logging.info(f"Weights: {scores}")

    # Generate allocations for the validator.
    next_allocations = []
    verified_allocations = []
    for hotkey in tqdm( metagraph.hotkeys ):
        db_path = os.path.expanduser(f"{config.db_root_path}/{config.wallet.name}/{config.wallet.hotkey}/DB-{hotkey}-{wallet.hotkey.ss58_address}")
        next_allocations.append({
            'path': db_path,
            'n_chunks': 100,
            'seed': f"{hotkey}{wallet.hotkey.ss58_address}",
            'miner': hotkey,
            'validator': wallet.hotkey.ss58_address,
            'hash': True,
        })
        verified_allocations.append( {
            'path': db_path,
            'n_chunks': 0,
            'seed': f"{hotkey}{wallet.hotkey.ss58_address}",
            'miner': hotkey,
            'validator': wallet.hotkey.ss58_address,
            'hash': True,
        })
    
    # Generate the hash allocations.
    allocate.generate( 
        allocations = next_allocations,  # The allocations to generate.
        no_prompt = True,  # If True, no prompt will be shown
        workers = 10,  # The number of concurrent workers to use for generation. Default is 10.
        restart = False # Dont restart the generation from empty files.
    )

    # Step 7: The Main Validation Loop
    bt.logging.info("Starting validator loop.")
    step = 0
    while True:
        try:
            # Iterate over all miners on the network and validate them.
            previous_allocations = copy.deepcopy( next_allocations )
            for i, alloc in tqdm( enumerate( next_allocations ) ):
                # Dont self validate.
                if alloc['miner'] == wallet.hotkey.ss58_address: continue
                print(f"Validating miner: {alloc}")

                # Select a random chunk to validate.
                chunk_i = str( randint( 1, alloc['n_chunks'] ) )
                bt.logging.debug(f"Validating chunk: {chunk_i}")

                # Get the hash of the data to validate from the database.
                db = sqlite3.connect(alloc['path'])
                try:
                    validation_hash = db.cursor().execute(f"SELECT hash FROM DB{alloc['seed']} WHERE id=?", (chunk_i,)).fetchone()[0]
                except:
                    bt.logging.error(f"Failed to get validation hash for chunk: {chunk_i} from db: {alloc['path']}")
                    continue
                bt.logging.debug(f"Validation hash: {validation_hash}")
                db.close()

                # Query the miner for the data.
                miner_data = dendrite.query( metagraph.axons[i], Retrieve( key = chunk_i ), deserialize = True )

                if miner_data == None:
                    # The miner could not respond with the data.
                    # We reduce the estimated allocation for the miner.
                    next_allocations[i]['n_chunks'] = max( int( next_allocations[i]['n_chunks'] * 0.9 ), 25 )
                    verified_allocations[i]['n_chunks'] = min( next_allocations[i]['n_chunks'], verified_allocations[i]['n_chunks'] )
                    bt.logging.debug(f"Miner did not respond with data, reducing allocation to: {next_allocations[i]['n_chunks']}")

                elif miner_data != None:
                    # The miner was able to respond with the data, but we need to verify it.
                    computed_hash = hashlib.sha256( miner_data.encode() ).hexdigest()
                    bt.logging.debug(f"   Computed hash: {computed_hash}, Validation hash: {validation_hash} ")

                    # Check if the miner has provided the correct response by doubling the dummy input.
                    if computed_hash == validation_hash:
                        # The miner has provided the correct response we can increase our known verified allocation.
                        # We can also increase our estimated allocation for the miner.
                        verified_allocations[i]['n_chunks'] = next_allocations[i]['n_chunks']
                        next_allocations[i]['n_chunks'] = int( next_allocations[i]['n_chunks'] * 1.1 )
                        bt.logging.debug(f"Miner provided correct response, increasing allocation to: {next_allocations[i]['n_chunks']}")
                    else:
                        # The miner has provided an incorrect response.
                        # We need to decrease our estimation..
                        next_allocations[i]['n_chunks'] = max( int( next_allocations[i]['n_chunks'] * 0.9 ), 25 )
                        verified_allocations[i]['n_chunks'] = min( next_allocations[i]['n_chunks'], verified_allocations[i]['n_chunks'] )
                        bt.logging.debug(f"Miner provided incorrect response, reducing allocation to: {next_allocations[i]['n_chunks']}")

            # Reallocate the validator's chunks.
            bt.logging.debug(f"Prev allocations: {[ a['n_chunks'] for a in previous_allocations ]  }")
            allocate.generate( 
                allocations = next_allocations,  # The allocations to generate.
                no_prompt = True,  # If True, no prompt will be shown
                restart = False # Dont restart the generation from empty files.
            )
            bt.logging.info(f"Allocations: {[ allocate.human_readable_size( a['n_chunks'] * allocate.CHUNK_SIZE ) for a in next_allocations ] }")

            # Periodically update the weights on the Bittensor blockchain.
            if (step + 1) % 1000 == 0:
                # TODO(developer): Define how the validator normalizes scores before setting weights.
                weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
                bt.logging.info(f"Setting weights: {weights}")
                # This is a crucial step that updates the incentive mechanism on the Bittensor blockchain.
                # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
                result = subtensor.set_weights(
                    netuid = config.netuid, # Subnet to set weights on.
                    wallet = wallet, # Wallet to sign set weights using hotkey.
                    uids = metagraph.uids, # Uids of the miners to set weights for.
                    weights = weights, # Weights to set for the miners.
                    wait_for_inclusion = True
                )
                if result: bt.logging.success('Successfully set weights.')
                else: bt.logging.error('Failed to set weights.') 

            # End the current step and prepare for the next iteration.
            step += 1
            # Resync our local state with the latest state from the blockchain.
            metagraph = subtensor.metagraph(config.netuid)
            # Wait a block step.
            time.sleep(1)

        # If we encounter an unexpected error, log it for debugging.
        except RuntimeError as e:
            bt.logging.error(e)
            traceback.print_exc()

        # If the user interrupts the program, gracefully exit.
        except KeyboardInterrupt:
            bt.logging.success("Keyboard interrupt detected. Exiting validator.")
            exit()


if __name__ == "__main__":
    config = get_config('my_wallet', 'my_first_hotkey', 7)
    
    main(config)