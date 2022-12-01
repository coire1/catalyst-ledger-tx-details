import typer

from commands import distribution_integrity
from commands import test_tx_checker
from commands import tx_details

app = typer.Typer()

app.add_typer(
    test_tx_checker.app,
    name="test-tx-checker",
    help="Test TX checker."
)

app.add_typer(
    distribution_integrity.app,
    name="distribution-integrity",
    help="Distribution integrity."
)

app.add_typer(
    tx_details.app,
    name="tx-details",
    help="Tx details."
)

if __name__ == "__main__":
    app()
