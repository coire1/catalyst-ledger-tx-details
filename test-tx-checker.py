from pycardano import Address, Network
import requests
import typer
import csv

app = typer.Typer()

@app.command()
def get_test_transactions(
    address: str = typer.Option("", help="The address used to send transactions."),
    start_block: int = typer.Option(0, help="The start block start to filter transactions (inclusive)"),
    end_block: int = typer.Option(0, help="The end block to filter transactions (inclusive)"),
    blockfrost_api_key: str = typer.Option("", help="A blockfrost API key"),
    output: str = typer.Option("output.csv", help="The path to save the output CSV"),
    network: str = typer.Option("mainnet", help="Cardano network"),
    strict: bool = typer.Option(False, help="When active doesn't use the stake key to check returning transaction.")
):

    network_url = f"cardano-{network}"
    network = Network.MAINNET if network == 'mainnet' else Network.TESTNET
    headers = {
        "project_id": blockfrost_api_key
    }
    results = []

    # get incoming/outcoming addresses
    res = get_txs(address, headers, network_url, start_block, end_block, 1)
    txs = res
    counter = 1
    typer.echo(f"Getting txs batch {counter}...")
    while len(res) == 100:
        counter = counter + 1
        res = get_txs(address, headers, network_url, start_block, end_block, counter)
        typer.echo(f"Getting txs batch {counter}...")
        txs = txs + res

    typer.echo(f"Total transactions: {len(txs)}.")

    test_tx_recipients = {}
    test_tx_sender = {}
    for idx, tx in enumerate(txs):
        typer.echo(f"Getting detailed info for tx {idx} of {len(txs)}")
        tx_type, inc_addr, out_addr = get_tx_details(tx['tx_hash'], headers, network_url, address)
        if tx_type == 'outcoming':
            test_tx_recipients = add_to_dict(test_tx_recipients, out_addr, tx['tx_hash'])
        else:
            test_tx_sender = add_to_dict(test_tx_sender, inc_addr, tx['tx_hash'])

    test_tx_recipients = convert_keys(test_tx_recipients, network, strict)
    test_tx_sender = convert_keys(test_tx_sender, network, strict)
    # match outcoming correspondences to incoming
    results = check_returned_txs(test_tx_recipients, test_tx_sender)

    formatted_results = format_results(results)

    with open(output, 'w') as csvfile:
        headings = ['address', 'check_key', 'confirmed', 'test_tx', 'confirmation_tx']
        writer = csv.DictWriter(csvfile, fieldnames=headings)
        writer.writeheader()
        writer.writerows(formatted_results)
        csvfile.close()

def get_txs(address, headers, network_url, block_from, block_to, page):
    url = f"https://{network_url}.blockfrost.io/api/v0/addresses/{address}/transactions?from={block_from}&to={block_to}&count=100&page={page}"
    r  = requests.get(url, headers=headers)
    try:
        txs = r.json()
    except Exception as e:
        print(e)
    return txs


def get_tx_details(tx_hash, headers, network_url, input_address):
    # Separate incoming/outcoming transactions
    # collect incoming/outcoming address
    url = f"https://{network_url}.blockfrost.io/api/v0/txs/{tx_hash}/utxos"
    r  = requests.get(url, headers=headers)
    inputs = []
    outputs = []
    tx_type = ''
    try:
        response = r.json()
        inputs = [inp['address'] for inp in response['inputs']]
        outputs = [out['address'] for out in response['outputs']]
        if input_address in inputs:
            tx_type = 'outcoming'
            outputs.remove(input_address)
        elif input_address in outputs:
            tx_type = 'incoming'
    except Exception as e:
        print(e)
    return tx_type, inputs, outputs

def add_to_dict(dict, keys, value):
    for key in keys:
        if key in dict:
            dict[key]['tx_hashes'] = dict[key]['tx_hashes'] + [value]
        else:
            dict[key] = {}
            dict[key]['tx_hashes'] = [value]
    return dict

def convert_keys(dict, network, to_address=False):
    new_dict = {}
    for address in dict:
        new_addr = address
        if not to_address:
            try:
                loc_addr = Address.from_primitive(address)
                new_addr = str(Address(staking_part=loc_addr.staking_part, network=network))
            except:
                pass
        new_dict[new_addr] = dict[address]
        new_dict[new_addr]['address'] = address
    return new_dict

def check_returned_txs(tx_recipients, tx_sender):
    updated_tx_recipients = {}
    for tx_recipient in tx_recipients:
        if tx_recipient in tx_sender:
            tx_recipients[tx_recipient]['confirmed'] = True
            tx_recipients[tx_recipient]['confirmation_tx'] = tx_sender[tx_recipient]['tx_hashes']
        else:
            tx_recipients[tx_recipient]['confirmed'] = False
        updated_tx_recipients[tx_recipient] = tx_recipients[tx_recipient]
    return updated_tx_recipients

def format_results(results):
    formatted_results = []
    for key in results:
        formatted = {
            'address': results[key]['address'],
            'check_key': key,
            'confirmed': results[key]['confirmed'],
            'test_tx': "\n".join(results[key]['tx_hashes'])
        }
        if 'confirmation_tx' in results[key]:
            formatted['confirmation_tx'] = "\n".join(results[key]['confirmation_tx'])
        formatted_results.append(formatted)
    return formatted_results



if __name__ == "__main__":
    app()
