# Bittensor Subnet 5
We just added openkaito feature of bittensor to comtensor.

## Running openkaito.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/openkaito/requirements.txt
    ```

2. Check if you got validator keys.

    You need validator keys to query bittensor miners. Miners have blacklist_fn to block various attacs due to unnecessary requests.

    If you have keys, you need to replace in `openkaito.py` code. (`wallet_name`, `wallet_hotkey`)

    ```python
    
        class OpenkaitoCrossval(SynapseBasedCrossval):

            def __init__(self, netuid = 5, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
            ...
    ```

3. Running script.
    ```bash
    python crossvals/openkaito/openkaito.py
    ```
