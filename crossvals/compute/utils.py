# The MIT License (MIT)
# Copyright © 2023 Rapiiidooo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import string
import random
import secrets
import hashlib
import math
import bittensor as bt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Define the version of the template module.
__version__ = "1.4.0"
__minimal_miner_version__ = "1.4.0"
__minimal_validator_version__ = "1.4.0"

version_split = __version__.split(".")
__version_as_int__ = (100 * int(version_split[0])) + (10 * int(version_split[1])) + (1 * int(version_split[2]))

# General static vars
# Amount staked to be considered as a valid validator
validator_permit_stake = 1.024e3
weights_rate_limit = 100

# Validators static vars
# Time before the specs requests will time out. time unit = seconds
specs_timeout = 60
# Time before the proof of work requests will time out. time unit = seconds
pow_timeout = 30
# Initial and minimal proof of work difficulty. Needs benchmark and adjustment.
pow_min_difficulty = 6
# Maximal proof of work difficulty, this to ensure a miner can not be rewarded for an unlimited unreasonable difficulty. Needs benchmark and adjustment.
pow_max_difficulty = 12
# Model: BLAKE2b-512($pass.$salt)
pow_default_mode = "610"
pow_default_chars = str(string.ascii_letters + string.digits + "!@#$%^&*()-_+=[]{};:,.<>")

# Miners static vars
miner_priority_specs = 1  # Lowest priority
miner_priority_challenge = 2  # Medium priority
miner_priority_allocate = 3  # The highest priority
miner_hashcat_location = "hashcat"
miner_hashcat_workload_profile = "3"

SUSPECTED_EXPLOITERS_COLDKEYS = []
SUSPECTED_EXPLOITERS_HOTKEYS = [
    "5HZ1ATsziEMDm1iUqNWQatfEDb1JSNf37AiG8s3X4pZzoP3A",
    "5H679r89XawDrMhwKGH1jgWMZQ5eeJ8RM9SvUmwCBkNPvSCL",
    "5FnMHpqYo1MfgFLax6ZTkzCZNrBJRjoWE5hP35QJEGdZU6ft",
    "5H3tiwVEdqy9AkQSLxYaMewwZWDi4PNNGxzKsovRPUuuvALW",
    "5E6oa5hS7a6udd9LUUsbBkvzeiWDCgyA2kGdj6cXMFdjB7mm",
    "5DFaj2o2R4LMZ2zURhqEeFKXvwbBbAPSPP7EdoErYc94ATP1",
    "5H3padRmkFMJqZQA8HRBZUkYY5aKCTQzoR8NwqDfWFdTEtky",
    "5HBqT3dhKWyHEAFDENsSCBJ1ntyRdyEDQWhZo1JKgMSrAhUv",
    "5FAH7UesJRwwLMkVVknW1rsh9MQMUo78d5Qyx3KpFpL5A7LW",
    "5GUJBJmSJtKPbPtUgALn4h34Ydc1tjrNfD1CT4akvcZTz1gE",
    "5E2RkNBMCrdfgpnXHuiC22osAxiw6fSgZ1iEVLqWMXSpSKac",
    "5DaLy2qQRNsmbutQ7Havj49CoZSKksQSRkCLJsiknH8GcsN2",
    "5GNNB5kZfo6F9hqwXvaRfYdTuJPSzrXbtABzwoL499jPNBjt",
    "5GVjcJLQboN5NcQoP4x8oqovjAiEizdscoocWo9HBYYmPdR3",
    "5FswTe5bbs9n1SzaGpzUd6sDfnzdPfWVS2MwDWNbAneeT15k",
    "5F4bqDZkx79hCxmbbsVMuq312EW9hQLvsBzKsAJgcEqpb8L9",
]

TRUSTED_VALIDATORS_HOTKEYS = [
    "5F4tQyWrhfGVcNhoqeiNsR6KjD4wMZ2kfhLj4oHYuyHbZAc3",  # Opentensor Foundation
    "5Hddm3iBFD2GLT5ik7LZnT3XJUnRnN8PoeCFgGQgawUVKNm8",  # τaosτaτs & Corcel
    "5HEo565WAy4Dbq3Sv271SAi7syBSofyfhhwRNjFNSM2gP9M2",  # Foundry
    "5HK5tp6t2S59DywmHRWPBVJeJ86T61KjurYqeooqj8sREpeN",  # Bittensor Guru Podcast
    "5EhvL1FVkQPpMjZX4MAADcW42i3xPSF1KiCpuaxTYVr28sux",  # TAO-Validator.com
    "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v",  # RoundTable21
    "5DvTpiniW9s3APmHRYn8FroUWyfnLtrsid5Mtn5EwMXHN2ed",  # FirstTensor
    "5HbLYXUBy1snPR8nfioQ7GoA9x76EELzEq9j7F32vWUQHm1x",  # Tensorplex
    "5CXRfP2ekFhe62r7q3vppRajJmGhTi7vwvb2yr79jveZ282w",  # Rizzo
    "5HNQURvmjjYhTSksi8Wfsw676b4owGwfLR2BFAQzG7H3HhYf",  # Neural Inτerneτ
    "5DnXm2tBGAD57ySJv5SfpTfLcsQbSKKp6xZKFWABw3cYUgqg",  # Love
]


def gen_hash(password, salt=None):
    salt = secrets.token_hex(8) if salt is None else salt
    salted_password = password + salt
    data = salted_password.encode("utf-8")
    hash_result = hashlib.blake2b(data).hexdigest()
    return f"$BLAKE2${hash_result}", salt


def gen_random_string(available_chars=pow_default_chars, length=pow_min_difficulty):
    # Generating private/public keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Using the private key bytes as seed for guaranteed randomness
    seed = int.from_bytes(private_bytes, "big")
    random.seed(seed)
    return "".join(random.choice(available_chars) for _ in range(length))


def gen_password(available_chars=pow_default_chars, length=pow_min_difficulty):
    try:
        password = gen_random_string(available_chars=available_chars, length=length)
        _mask = "".join(["?1" for _ in range(length)])
        _hash, _salt = gen_hash(password)
        return password, _hash, _salt, _mask
    except Exception as e:
        bt.logging.error(f"Error during PoW generation (gen_password): {e}")
        return None



def run_validator_pow(length=pow_min_difficulty):
    """
    Don't worry this function is fast enough for validator to use CPUs
    """
    available_chars = pow_default_chars
    available_chars = list(available_chars)
    random.shuffle(available_chars)
    available_chars = "".join(available_chars)
    password, _hash, _salt, _mask = gen_password(available_chars=available_chars[:10], length=length)
    return password, _hash, _salt, pow_default_mode, available_chars[:10], _mask



def force_to_float_or_default(a, default=0.0):
    try:
        return float(a)
    except Exception:
        return default
    

def calc_difficulty(uid):
    difficulty = pow_min_difficulty
    try:
        stat = stats[uid]
        current_difficulty = math.ceil(force_to_float_or_default(stat.get("last_20_difficulty_avg"), default=pow_min_difficulty))
        last_20_challenge_failed = force_to_float_or_default(stat.get("last_20_challenge_failed"))
        challenge_successes = force_to_float_or_default(stat.get("challenge_successes"))
        if challenge_successes >= 20:
            if last_20_challenge_failed <= 1:
                difficulty = min(current_difficulty + 1, pow_max_difficulty)
            elif last_20_challenge_failed > 2:
                difficulty = max(current_difficulty - 1, pow_min_difficulty)
            else:
                difficulty = current_difficulty
    except KeyError:
        pass
    except Exception as e:
        bt.logging.error(f"{e} => difficulty minimal: {pow_min_difficulty} attributed for {uid}")
    return max(difficulty, 1)