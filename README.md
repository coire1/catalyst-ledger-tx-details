## Extract txs amounts

Install deps:

`pip install -r requirements.txt`

Command help:

```
Usage: main.py tx-details get-transactions-amount [OPTIONS]

Options:
  --address TEXT                  The address used to send transactions.
  --start-block INTEGER           The start block start to filter transactions
                                  (inclusive)  [default: 0]
  --end-block INTEGER             The end block to filter transactions
                                  (inclusive)  [default: 0]
  --blockfrost-api-key TEXT       A blockfrost API key
  --output TEXT                   The path to save the output CSV  [default:
                                  output.csv]
  --mir / --no-mir                Look for MIRs instead of UTXOs  [default:
                                  False]
```

## Funds distribution integrity checks

```
Usage: main.py distribution-integrity check [OPTIONS]                                                                

Options ────────────────────────────────────────────────────────────────────
  --sheet-url                 TEXT  The URL to use to pull funding file.
  --sheet-name                TEXT  The sheet name of the funding file.
  --ledger-sheet-url          TEXT  The URL to use to store the integrity result.
  --ledger-sheet-name         TEXT  The sheet name of the integrity result.
  --tx-id-col                 TEXT  The cell with the TX id. [default: K]
  --integrity-col             TEXT  The col to update with the integrity result. [default: I]
  --blockfrost-api-key        TEXT  A blockfrost API key
  --network                   TEXT  Cardano network [default: mainnet]
```

Example usage:

```
python main.py distribution-integrity check --sheet-url [https://docs.google.com/...] --sheet-name [Nov16] --blockfrost-api-key [mainnet...] --tx-id-col J --ledger-sheet-url [https://docs.google.com/...] --ledger-sheet-name [Fund9]
```

It's necessary to create a Service Account for Google APIs to interact with spreadsheets.

1. Enable API Access for a Project if you haven’t done it yet.
2. Search for Sheet and Drive APIs and activate them.
3. Go to “APIs & Services > Credentials” and choose “Create credentials > Service account key”.
4. Fill out the form
5. Click “Create” and “Done”.
6. Press “Manage service accounts” above Service Accounts.
7. Press on ⋮ near recently created service account and select “Create key”.
8. Select JSON key type and press “Create”.
9. Copy the downloaded json to google-accounts/service_account.json
