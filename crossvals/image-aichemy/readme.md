# Bittensor Subnet 26
We just added aichemy feature of bittensor to comtensor.

## Running aichemy.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/image-aichemy/requirements.txt
    ```

2. Check if you got validator keys.

    You need validator keys to query bittensor miners. Miners have blacklist_fn to block various attacs due to unnecessary requests.

    If you have keys, you need to replace in `aichemy.py` code. (`wallet_name`, `wallet_hotkey`)

    ```python
    
        class ImageAIchemyCrossval(SynapseBasedCrossval):

            def __init__(self, netuid = 26, wallet_name = 'my_wallet', wallet_hotkey = 'my_first_hotkey', network = "finney", topk = 1):
            ...
    ```

3. Running script.
    ```bash
    python crossvals/image-aichemy/aichemy.py
    ```
