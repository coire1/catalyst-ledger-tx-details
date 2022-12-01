import requests
import typer
import csv

app = typer.Typer()

@app.command()
def get_transactions_amount(
    address: str = typer.Option("", help="The address used to send transactions."),
    start_block: int = typer.Option(0, help="The start block start to filter transactions (inclusive)"),
    end_block: int = typer.Option(0, help="The end block to filter transactions (inclusive)"),
    blockfrost_api_key: str = typer.Option("", help="A blockfrost API key"),
    output: str = typer.Option("output.csv", help="The path to save the output CSV"),
    mir: bool = typer.Option(False, help="Look for MIRs instead of UTXOs")
):
    headers = {
        "project_id": blockfrost_api_key
    }

    results = []
    res = get_txs(address, headers, start_block, end_block, 1)
    txs = res
    counter = 1
    typer.echo(f"Getting txs batch {counter}...")
    while len(res) == 100:
        counter = counter + 1
        res = get_txs(address, headers, start_block, end_block, counter)
        typer.echo(f"Getting txs batch {counter}...")
        txs = txs + res

    typer.echo(f"Total transactions: {len(txs)}.")

    for idx, tx in enumerate(txs):
        typer.echo(f"Getting detailed info for tx {idx} of {len(txs)}")
        if mir:
            amount = get_mir_tx_amount(tx['tx_hash'], headers)
        else:
            amount = get_tx_amount(tx['tx_hash'], headers)
        results.append({
            "tx_hash": tx['tx_hash'],
            "amount": amount
        })

    with open(output, 'w') as csvfile:
        headings = ['tx_hash', 'amount']
        writer = csv.DictWriter(csvfile, fieldnames=headings)
        writer.writeheader()
        writer.writerows(results)
        csvfile.close()

    typer.echo(f"Results saved in {output}.")

def get_mir_tx_amount(tx_hash, headers):
    tot = 0
    url = f"https://cardano-mainnet.blockfrost.io/api/v0/txs/{tx_hash}/mirs"
    r  = requests.get(url, headers=headers)
    try:
        response = r.json()
        for res in response:
            tot = tot + int(res['amount'])
    except Exception as e:
        print(e)
    return round(tot / 1000000, 5)

def get_tx_amount(tx_hash, headers):
    tot = 0
    url = f"https://cardano-mainnet.blockfrost.io/api/v0/txs/{tx_hash}/utxos"
    r  = requests.get(url, headers=headers)
    try:
        response = r.json()
        inputs_addresses = [inp['address'] for inp in response['inputs']]
        print(inputs_addresses)
        for out in response['outputs']:
            if out['address'] not in inputs_addresses:
                amounts = [int(o['quantity']) for o in out['amount'] if o['unit'] == 'lovelace']
                tot = tot + sum(amounts)
    except Exception as e:
        print(e)
    return round(tot / 1000000, 5)


def get_txs(address, headers, block_from, block_to, page):
    url = f"https://cardano-mainnet.blockfrost.io/api/v0/addresses/{address}/transactions?from={block_from}&to={block_to}&count=100&page={page}"
    r  = requests.get(url, headers=headers)
    try:
        txs = r.json()
    except Exception as e:
        print(e)
    return txs
