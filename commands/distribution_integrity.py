from utils.gsheet import GSheet

import requests
import typer
import csv

from rich import print

from typing import List

app = typer.Typer()

gsheet = GSheet()

@app.command()
def check(
    sheet_url: str = typer.Option("", help="The URL to use to pull funding file."),
    sheet_name: str = typer.Option("", help="The sheet name of the funding file."),
    ledger_sheet_url: str = typer.Option("", help="The URL to use to store the integrity result."),
    ledger_sheet_name: str = typer.Option("", help="The sheet name of the integrity result."),
    tx_id_col: str = typer.Option("K", help="The cell with the TX id."),
    integrity_col: str = typer.Option("I", help="The col to update with the integrity result."),
    blockfrost_api_key: str = typer.Option("", help="A blockfrost API key"),
    network: str = typer.Option("mainnet", help="Cardano network"),
    dry_run: bool = typer.Option(False, help="When True it doesn't write the results on the sheet."),
    seed_account_addresses: List[str] = typer.Option([], help="The addresses of the seed account.")
):
    headers = {
        "project_id": blockfrost_api_key
    }

    funding_file, sheet = gsheet.get_df(sheet_url, sheet_name, return_sheet=True)

    tx_ids = sheet.get(f"{tx_id_col}2:{tx_id_col}")
    tx_ids = [tx[0].strip() for tx in tx_ids]

    tot = 0
    all_inputs = []
    all_outputs = []
    for tx_id in tx_ids:
        print(f"Tx id is [bold green]{tx_id}[/bold green].")
        if tx_id:
            inputs, outputs = get_tx_details(tx_id, headers, network)
            all_inputs = all_inputs + inputs
            all_outputs = all_outputs + outputs

    for idx, proposal in funding_file.iterrows():
        proposal_address = proposal[0].strip()
        if proposal_address != '':
            tot = tot + 1
            proposal_amount = int(proposal['lovelace to send'])
            tx_fragment = find_by_address_and_amount(all_outputs, proposal_address, proposal_amount)
            if len(tx_fragment) > 0:
                tx_fragment[0]['checked'] = True
                print(f"Amount distributed for [bold green]{proposal['Idea']}[/bold green] is correct ([bold green]{tx_fragment[0]['quantity']}[/bold green]).")
            else:
                print(f"Amount distributed for [bold red]{proposal['Idea']} is NOT correct[/bold red]")
    final = final_check(all_outputs, all_inputs, tot, seed_account_addresses)
    if final and (dry_run is False):
        print("Updating fund ledger...")
        ledger_df, ledger_sheet = gsheet.get_df(ledger_sheet_url, ledger_sheet_name, return_sheet=True)
        affected_rows = ledger_df[ledger_df['Tx ID'].isin(tx_ids)].index.tolist()
        if len(tx_ids) != len(affected_rows):
            print(f"[bold red]Please check that tx ids are correctly typed in ledger file.[/bold red]")
        for r in affected_rows:
            ledger_sheet.update(f"{integrity_col}{r+2}", True)
        print(f"[bold green]{len(affected_rows)} rows updated in Ledger file.[/bold green]")



def get_tx_details(tx_hash, headers, network):
    # Separate incoming/outcoming transactions
    # collect incoming/outcoming address
    url = f"https://{network}.blockfrost.io/api/v0/txs/{tx_hash}/utxos"
    r  = requests.get(url, headers=headers)
    inputs = []
    outputs = []
    try:
        response = r.json()
        inputs = response['inputs']
        outputs = [extract_lovelace_amount(o) for o in response['outputs']]
    except Exception as e:
        print(e)
    return inputs, outputs

def find_by_address_and_amount(ll, address, amount):
    results = [
        line
        for line in ll
        if line['address'] == address and line['quantity'] == amount and line['checked'] == False
    ]
    return results

def extract_lovelace_amount(q):
    qty = -1
    for sq in q['amount']:
        if sq['unit'] == 'lovelace':
            qty = int(sq['quantity'])
    return {
        'address': q['address'],
        'quantity': qty,
        'checked': False
    }

def check_address_inputs(inputs, not_checked):
    '''
    Check that every address in not checked is part of inputs list.
    '''
    result = True
    for single_not_checked in not_checked:
        result = result and (single_not_checked['address'] in inputs)
    return result


def final_check(outputs, inputs, tot, seed_addresses):
    not_checked = [el for el in outputs if el['checked'] != True]
    if (len(seed_addresses) > 0):
        reduced_inputs = seed_addresses
    else:
        reduced_inputs = set([el['address'] for el in inputs])
    if (
        len(not_checked) == len(reduced_inputs) and
        check_address_inputs(reduced_inputs, not_checked) and
        len(outputs) - len(reduced_inputs) == tot
    ):
        print(f"No of outputs correct.[bold green] Fund distributed to {len(outputs) - len(reduced_inputs)} wallets[/bold green].")
        return True
    else:
        print(f"[bold red]No of outputs not correct. Fund distributed to {len(outputs) - len(reduced_inputs)} wallets[/bold red].")
        return False
