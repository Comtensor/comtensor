# Bittensor Subnet 30 
We just added tradingggggg feature of bittensor to comtensor.


## Running http server using fastapi

```bash
uvicorn crossvals.trading.server:app --reload
```

-------

### How to test

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/api/receive-signal/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        'trade_pair': ["SPX", "SPX", 0.0005, 0.001, 500],
        'order_type': 'LONG',
        'leverage': 1.0,
        'api_key': 'xxxx'
    }'

```

## Running trading.py script locally

1. Install dependancies

    ```bash
    pip install -r crossvals/trading/requirements.txt
    ```

2. Running script.
    ```bash
    python crossvals/trading/trading.py
    ```
