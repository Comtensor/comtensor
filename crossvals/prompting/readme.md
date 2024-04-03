# Bittensor Subnet 1
We just added prompting feature of bittensor to comtensor.

## Running prompting.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/prompting/requirements.txt
    ```

2. Check if you got validator keys.

    You need validator keys to query bittensor miners. Miners have blacklist_fn to block various attacs due to unnecessary requests.

    If you have keys, you need to replace in `prompting.py` code. (`wallet_name`, `wallet_hotkey`)

    ```python
    
        class PromptingCrossval(SynapseBasedCrossval):

            def __init__(self, netuid = 1, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
            ...
    ```

3. Running script.
    ```bash
    python crossvals/prompting/prompting.py
    ```
