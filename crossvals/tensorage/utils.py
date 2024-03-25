import os
import argparse
import re
import requests
import subprocess
import bittensor as bt
import multiprocessing


__version__ = "1.2.3"
__spec_version__ = 123





def get_config(wallet_name:str, wallet_hotkey:str, netuid:int) -> bt.config:
    """
    Parse params and preparare config object.

    Returns:
        - bittensor.config: Nested config object created from parser arguments.
    """
    # Create parser and add all params.
    parser = argparse.ArgumentParser(description="Configure the validator.")
    parser.add_argument(
        "--db_root_path", default="./tensorage-db", help="Path to the database."
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        default=False,
        help="If set, the validator will reallocate its DB entirely.",
    )
    parser.add_argument(
        "--workers",
        default=multiprocessing.cpu_count(),
        type=int,
        help="The number of concurrent workers to use for hash generation.",
    )
    parser.add_argument(
        "--no_store_weights",
        action="store_true",
        default=False,
        help="If False, the validator will store newly-set weights.",
    )
    parser.add_argument(
        "--no_restore_weights",
        action="store_true",
        default=False,
        help="If False, the validator will keep the weights from the previous run.",
    )

    # Override default netuid.
    parser.add_argument("--netuid", type=int, default=netuid, help="Netuid to rebase into.")

    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)

    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)

    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    # bt.wallet.add_args(parser)
    parser.add_argument("--wallet.name", type=str, default=wallet_name, help="wallet name")

    parser.add_argument("--wallet.hotkey", type=str, default=wallet_hotkey, help='wallet hotkey')


    # Adds axon specific arguments i.e. --axon.port...
    bt.axon.add_args(parser)

    # Parse config.
    config = bt.config(parser)

    # Ensure the logging directory exists.
    config.full_path = os.path.join(
        os.path.expanduser(config.logging.logging_dir),
        config.wallet.name,
        config.wallet.hotkey,
        f"netuid{config.netuid}",
        "validator",
    )
    
    if not os.path.exists(config.full_path):
        os.makedirs(config.full_path, exist_ok=True)

    return config





def version_str_to_num(version: str) -> int:
    """
    Convert version number as string to number (1.2.0 => 120).
    Multiply the first version number by one hundred, the second by ten, and the last by one. Finally add them all.

    Args:
        - version (str): The version number as string.

    Returns:
        - int: Version number as int.
    """
    version_split = version.split(".")
    return (
        (100 * int(version_split[0]))
        + (10 * int(version_split[1]))
        + int(version_split[2])
    )


def check_version():
    """
    Check current version of the module on GitHub. If it is greater than the local version, download and update the module.
    """
    latest_version = get_latest_version()
    current_version = tensorage.__version__

    # If version in GitHub is greater, update module.
    if (
        version_str_to_num(current_version) < version_str_to_num(latest_version)
        and latest_version is not None
    ):
        bt.logging.info("Updating to the latest version...")
        subprocess.run(["git", "reset", "--hard"], cwd=os.getcwd())
        subprocess.run(["git", "pull"], cwd=os.getcwd())
        subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=os.getcwd())
        subprocess.run(["pip", "install", "-e", "."], cwd=os.getcwd())
        subprocess.run(
            ["cargo", "build", "--release"],
            cwd=os.path.join(os.getcwd(), "neurons/generate_db"),
        )
        exit(0)


def get_latest_version() -> str:
    """
    Retrieve latest version number from GitHub repository..

    Returns:
        - str: Version number as string (X.X.X).
    """

    # The raw content URL of the file on GitHub.
    url = "https://raw.githubusercontent.com/tensorage/tensorage/main/tensorage/__init__.py"

    # Send an HTTP GET request to the raw content URL.
    response = requests.get(url)

    # Check if the request was successful.
    if response.status_code == 200:
        version_match = re.search(r'__version__ = "(.*?)"', response.text)

        if not version_match:
            raise Exception("Version information not found in the specified line")

        return version_match.group(1)

    else:
        bt.logging.error(
            f"Failed to fetch file content. Status code: {response.status_code}"
        )


# check whether a certain hotkey is validator or not
def is_validator(metagraph, hotkey) -> bool:
    try:
        uid = metagraph.hotkeys.index(hotkey)
        return metagraph.validator_permit[uid]
    except ValueError:
        return False
