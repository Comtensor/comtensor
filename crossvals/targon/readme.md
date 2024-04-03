# Bittensor Subnet 4 
We just added targon feature of bittensor to comtensor.

## Running targon.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/targon/requirements.txt
    ```

2. Check if you got validator keys.

    You need validator keys to query bittensor miners. Miners have blacklist_fn to block various attacs due to unnecessary requests.

    If you have keys, you need to replace in `targon.py` code. (`wallet_name`, `wallet_hotkey`)

    ```python
        class TargonCrossval(SynapseBasedCrossval):

            def __init__(self, netuid = 4, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
            ...
    ```

3. Running script.
    ```bash
    python crossvals/targon/targon.py
    ```
