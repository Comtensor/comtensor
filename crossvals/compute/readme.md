# Bittensor Subnet 27
We just added compute feature of bittensor to comtensor.

## Running compute.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/compute/requirements.txt
    ```

2. Check if you got validator keys.

    You need validator keys to query bittensor miners. Miners have blacklist_fn to block various attacs due to unnecessary requests.

    If you have keys, you need to replace in `compute.py` code. (`wallet_name`, `wallet_hotkey`)

    ```python

        class ComputeCrossval(SynapseBasedCrossval):

            def __init__(self, netuid = 27, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
    
            ...
    ```

3. Running script.
    ```bash
    python crossvals/compute/compute.py
    ```
