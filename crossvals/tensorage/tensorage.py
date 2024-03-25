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


ALPHA = 0.9
STEP_TIME = 150
SCORES_TIME = 600
CHUNK_SIZE = 1 << 22  # 4194304 (4 MB)
DEFAULT_N_CHUNKS = 1280  # 5GB per hotkey (256 x 512MB = 128GB disk alocated)
VALIDATION_INCREASING_RATE = 2560  # 10GB
VALIDATION_DECREASING_RATE = 256  # 1GB
DEFAULT_TIMEOUT = 12
DEFAULT_RESPONSE_TIME = 20




def log_table(
    scores: torch.Tensor,
    n_chunks_list: typing.List[int],
    hotkeys: typing.List[str],
    title: str = "Score",
):
    """
    It shows a score table to console.

    Args:
        - scores (torch.Tensor): List of tensors with scores of all hotkeys.
        - n_chunks_list (typing.List[int]): List with the number of chunks for each hotkey.
        - hotkeys (typing.List[str]): List of all hotkeys in the metagraph.
        - title (str): Title of the table.
    """
    # Initialize the table and add headers.
    table = Table(title=title)
    table.add_column("Uid", justify="right", style="cyan")
    table.add_column("Score", justify="right", style="cyan")
    table.add_column("Hotkey", justify="right", style="cyan")
    table.add_column("N. Chunks", justify="right", style="cyan")

    # Add each row of data.
    [
        table.add_row(str(i), str(score), str(hotkeys[i]), str(n_chunks_list[i]))
        for i, score in enumerate(scores)
    ]

    # Show table in default console.
    console = Console()
    console.print(table)


class TensorageCrossval(SynapseBasedCrossval):

    def __init__(self, netuid = 7, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
        super().__init__(netuid, wallet_name, wallet_hotkey, network, topk)

        self.dendrite = bt.dendrite( wallet = self.wallet )
        self.config = get_config(wallet_name=wallet_name, wallet_hotkey=wallet_hotkey, netuid=netuid)

    # Returns current version.
    async def ping(self, synapse: Ping) -> Ping:
        """
        Answer the call indicating that it's a validator and its version.

        Args:
            - synapse (Ping): Synapse object with ping data.

        Returns:
            - Ping: Synapse object with ping data.
        """
        synapse.data = f"validator-{__version__}"
        return synapse


    # Returns a default message if any other validator requests data.
    async def retrieve(self,  synapse: Retrieve ) -> Retrieve:
        """
        Answer the call indicating that it's a validator and its UID.

        Args:
            - synapse (Retrieve): Synapse object with ping data.

        Returns:
            - Retrieve: Synapse object with ping data.
        """
        synapse.data = f"I am a validator on SN 7! UID: {self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)}"
        return synapse
    

    
    def forward(self, timeout: float):

        axons = [self.metagraph.axons[i['uid']] for i in self.top_miners]

        axon = bt.axon(config = self.config, wallet=self.wallet)
        subtensor = bt.subtensor(config=self.config)
        metagraph = subtensor.metagraph(self.config.netuid)
        
        axon.attach(self.ping).attach(self.retrieve)
        axon.serve(netuid=self.config.netuid, subtensor=subtensor)

        axon.start()

        scores = torch.ones_like(metagraph.S, dtype=torch.float32)

        # Set DBs directory.
        wallet_db_path = os.path.join(
            os.path.expanduser(self.config.db_root_path),
            self.config.wallet.name,
            self.config.wallet.hotkey,
            "validator",
        )

        print(wallet_db_path, '-------------------------')

        # Create DBs directory if not exists.
        if not os.path.exists(
            wallet_db_path
        ):  # Ensure the wallet_db_path directory exists.
            os.makedirs(wallet_db_path, exist_ok=True)

        # Load previously stored allocations.
        old_allocations = []
        allocations_pkl = os.path.join(wallet_db_path, "..", "validator-allocations.pkl")
        if not self.config.no_restore_weights:
            if os.path.exists(allocations_pkl):
                with open(allocations_pkl, "rb") as f:
                    old_allocations = pickle.load(f)

                bt.logging.success("✅ Successfully restored previously-saved weights.")

            else:
                bt.logging.info("Previous weights state not found.")

        else:
            bt.logging.info("Ignoring previous weights state.")

        # Get the own hotkey from the wallet.
        own_hotkey = self.wallet.hotkey.ss58_address

        # Generate allocations for the validator.
        allocations = []
        response_times = [DEFAULT_RESPONSE_TIME] * len(metagraph.hotkeys)
        for hotkey in metagraph.hotkeys:
            # Look for old verified allocations for current hotkey.
            n_chunks = DEFAULT_N_CHUNKS
            for allocation in old_allocations:
                if allocation["hotkey"] == hotkey:
                    n_chunks = max(1, allocation["n_chunks"])
                    break

            allocations.append(
                {
                    "db_path": os.path.join(wallet_db_path, f"DB-{own_hotkey}-{hotkey}"),
                    "n_chunks": n_chunks,
                    "own_hotkey": own_hotkey,
                    "hotkey": hotkey,
                }
            )

        # Delete DB if hotkey is not registered.
        for filename in os.listdir(wallet_db_path):
            hotkey = filename.replace(f"DB-{own_hotkey}-", "")
            if hotkey not in metagraph.hotkeys:
                os.remove(os.path.join(wallet_db_path, filename))

        # Generate the hash allocations.
        allocate.generate(
            allocations=allocations,
            disable_prompt=True,
            only_hash=True,
            workers=self.config.workers,
        )


        def validate_allocation(i: int, allocation: dict):
            """
            Validates how much space each hotkey has allocated.

            Args:
                - i (int): Index of enumerated list "allocations".
                - allocation (dict): A dictionary containing allocation details.
            """
            response_times[i] = DEFAULT_RESPONSE_TIME

            # Don't self validate and skip 0.0.0.0 axons.
            if allocation["hotkey"] == own_hotkey or metagraph.axons[i].ip == "0.0.0.0":
                allocation["n_chunks"] = 0
                return

            # Init hashes to compare.
            computed_hash = None
            validation_hash = ""

            # Select first or random chunk to validate.
            chunk_i = (
                0
                if allocation["n_chunks"] < 2
                else randint(
                    max(0, allocation["n_chunks"] - VALIDATION_DECREASING_RATE),
                    allocation["n_chunks"] - 1,
                )
            )

            # Query the miner for the data. TODO: Add timeout param and solve "Timeout context manager should be used inside a task" error.
            response = bt.dendrite(wallet=self.wallet).query(
                metagraph.axons[i],
                Retrieve(key=chunk_i),
                timeout=DEFAULT_TIMEOUT,
                deserialize=False,
            )
            response_times[i] = response.dendrite.process_time or DEFAULT_RESPONSE_TIME

            # Handle time-out
            if response is None or response.dendrite.status_code == 408:
                allocation["n_chunks"] = 0
                bt.logging.debug(
                    f"💤 Request for miner [uid {i}] has timed out. Setting allocation to zero."
                )
                return

            miner_data = response.data
            # If the miner can respond with the data, we need to verify it.
            if miner_data is not None:
                # Calculate hash of data received.
                computed_hash = hashlib.sha256(miner_data.encode()).hexdigest()

                # Get the hash of the data to validate from the database.
                db = sqlite3.connect(allocation["db_path"])
                try:
                    validation_hash = (
                        db.cursor()
                        .execute(
                            f"SELECT hash FROM DB{allocation['own_hotkey']}{allocation['hotkey']} WHERE id = {chunk_i}"
                        )
                        .fetchone()[0]
                    )

                except Exception as e:
                    bt.logging.debug(
                        f"❌ Failed to get validation hash for chunk_{chunk_i} in file {allocation['db_path']}: {e}"
                    )
                    return
                db.close()

                # Check if the miner has provided the correct response.
                if computed_hash == validation_hash:
                    # The miner has provided the correct response. We can increase our known verified allocation and our estimated allocation for the miner.
                    allocation["n_chunks"] = int(chunk_i + VALIDATION_INCREASING_RATE)
                    bt.logging.success(
                        f"✅ Miner [uid {i}] provided correct chunk_{chunk_i}. Increasing allocation to: {allocation['n_chunks']}."
                    )
                    allocate.run_rust_generate(allocation, only_hash=True)

                else:
                    # The miner has provided an incorrect response. We need to decrease our estimation.
                    allocation["n_chunks"] = max(chunk_i - VALIDATION_DECREASING_RATE, 1)
                    bt.logging.debug(
                        f"❌ Miner [uid {i}] provided incorrect chunk_{chunk_i}. Reducing allocation to: {allocation['n_chunks']}."
                    )
            else:
                allocation["n_chunks"] = max(chunk_i - VALIDATION_DECREASING_RATE, 1)
                bt.logging.debug(
                    f"❌ Miner [uid {i}] has not provided response for key {chunk_i}. Reducing allocation to: {allocation['n_chunks']}."
                )

        

        # The main validation Loop.
        step = 0
        bt.logging.info("🚀 Starting validator loop.")
        while True:
            try:
                # Prepare for the next iteration.
                step += 1

                # Measure the time it takes to validate all the miners running on the subnet.
                start_time = time.time()

                # Iterate over all hotkeys on the network and validate them.
                with ThreadPoolExecutor(max_workers=self.config.workers) as executor:
                    [
                        executor.submit(validate_allocation, i, allocation)
                        for i, allocation in enumerate(allocations)
                    ]

                # Log the time it took to validate all miners.
                elapsed_time = round(time.time() - start_time)
                bt.logging.info(
                    f"Finished validation step {step} in {elapsed_time} seconds."
                )

                if not self.config.no_store_weights:  # Save verified allocations.
                    with open(allocations_pkl, "wb") as f:
                        pickle.dump(allocations, f)
                    bt.logging.success(
                        "✅ Successfully stored verified allocations locally."
                    )

                    # TODO: Store verified allocations on wandb.
                    # # Initialize a new run in Weights & Biases
                    # run = wandb.init(project="salahawk/tensorage", job_type="store_data")
                    # # Create a new artifact with timestamp
                    # artifact = wandb.Artifact(f'allocations_{int(time.time())}', type='dataset')
                    # # Add the file to the artifact
                    # artifact.add_file(allocations_pkl)
                    # # Log the artifact
                    # run.log_artifact(artifact)
                    # bt.logging.success("✅ Successfully stored verified allocations on wandb.")

                # Wait for validate again.
                seconds_to_wait = STEP_TIME - elapsed_time
                if seconds_to_wait > 0:
                    bt.logging.info(f"Waiting {seconds_to_wait} seconds for the next step.")
                    time.sleep(seconds_to_wait)

                # Resync our local state with the latest state from the blockchain.
                metagraph = subtensor.metagraph(self.config.netuid)

                # Update allocations if hotkey of uid change.
                for i, hotkey in enumerate(metagraph.hotkeys):
                    if i < len(allocations):
                        # No hotkey change for this uid.
                        if allocations[i]["hotkey"] == hotkey:
                            continue

                        # Old hotkey was deregistered and new hotkey registered on this uid so reset the allocation for this uid.
                        bt.logging.info(f"✨ Found new hotkey: {hotkey}.")

                        # Delete old DB file.
                        os.remove(allocations[i]["db_path"])

                        # Generate new allocation.
                        db_path = os.path.join(wallet_db_path, f"DB-{own_hotkey}-{hotkey}")
                        allocations[i] = {
                            "db_path": db_path,
                            "n_chunks": DEFAULT_N_CHUNKS,
                            "own_hotkey": own_hotkey,
                            "hotkey": hotkey,
                        }
                    else:  # If new hotkey has been added to metagraph (not all 256 slots are filled up)
                        bt.logging.info(f"✨ Found new hotkey {hotkey} at uid {i}:")
                        allocations.append(
                            {
                                "db_path": os.path.join(
                                    wallet_db_path, f"DB-{own_hotkey}-{hotkey}"
                                ),
                                "n_chunks": DEFAULT_N_CHUNKS,
                                "own_hotkey": own_hotkey,
                                "hotkey": hotkey,
                            }
                        )
                        response_times.append(DEFAULT_RESPONSE_TIME)

                    allocate.run_rust_generate(allocations[i], only_hash=True)

                # Periodically update the weights on the Bittensor blockchain.
                if step % int(SCORES_TIME / STEP_TIME) == 0:
                    max_time = max(response_times)
                    min_time = min(response_times)
                    # Calculate score with n_chunks of allocations.
                    for index, uid in enumerate(metagraph.uids):
                        try:
                            allocation_index = next(
                                i
                                for i, obj in enumerate(allocations)
                                if obj["hotkey"] == metagraph.neurons[uid].axon_info.hotkey
                            )
                            chunks = allocations[allocation_index]["n_chunks"]
                            seconds = response_times[allocation_index]

                        except StopIteration:
                            chunks = 0
                            seconds = max_time

                        time_reward = (
                            (seconds - min_time) / (max_time - min_time)
                            if max_time != min_time
                            else 1
                        ) + 1
                        score = chunks / time_reward if time_reward > 0 else chunks

                        scores[index] = ALPHA * scores[index] + (1 - ALPHA) * score

                    # TODO: Define how the validator normalizes scores before setting weights.
                    weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
                    bt.logging.info("Setting weights:")
                    log_table(
                        scores=weights,
                        n_chunks_list=[
                            allocation["n_chunks"] for allocation in allocations
                        ],
                        hotkeys=metagraph.hotkeys,
                    )

                    # This is a crucial step that updates the incentive mechanism on the Bittensor blockchain. Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
                    if subtensor.set_weights(
                        netuid=self.config.netuid,
                        wallet=self.wallet,
                        uids=metagraph.uids,
                        weights=weights,
                    ):
                        bt.logging.success("✅  Successfully set weights.")

                    else:
                        bt.logging.error("❌  Failed to set weights.")

            # If we encounter an unexpected error, log it for debugging.
            except RuntimeError as e:
                bt.logging.error(e)
                traceback.print_exc()

            # If the user interrupts the program, gracefully exit.
            except KeyboardInterrupt:
                axon.stop()
                bt.logging.info("Keyboard interrupt detected. Exiting validator.")
                exit()


    def run(self):
        response = self.forward(60)



scrape_crossval = TensorageCrossval()

scrape_crossval.run()