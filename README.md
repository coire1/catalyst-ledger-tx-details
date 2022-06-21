# Extract MIR txs

Install deps:

`pip install -r requirements.txt`

Command help:

```
Usage: tx-details.py [OPTIONS]

Options:
  --address TEXT                  The address used to send transactions.
  --start-block INTEGER           The start block start to filter transactions
                                  (inclusive)  [default: 0]
  --end-block INTEGER             The end block to filter transactions
                                  (inclusive)  [default: 0]
  --blockfrost-api-key TEXT       A blockfrost API key
  --output TEXT                   The path to save the output CSV  [default:
                                  output.csv]
```
