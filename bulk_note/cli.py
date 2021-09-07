"""Console script for bulk_note."""
import sys
import click
import requests
from .imi_message import IMIRecipients

SERVER_URL = "https://74af928a-87c2-4a1e-8b5f-e23376aa9a83.mock.pstmn.io/txt-200"
HEADERS = {"Content-type": "text/xml"}


@click.command()
@click.option("--numbers", required=True, type=click.File("r"), help="file of numbers")
@click.option("--content", required=True, type=click.File("r"), help="file of content")
@click.option(
    "--send-codes",
    type=click.File("rb"),
    default=None,
    help="file of pickled sendcodes",
)
@click.option("--bulk-size", default=10, help="batch size per send")
@click.option("-v", "--verbose", count=True)
def main(numbers, content, send_codes, bulk_size, verbose):
    receipients = IMIRecipients(numbers, content, send_codes, bulk_size, verbose)
    while payload := receipients.get_tx_payload().dumps():
        request = requests.post(SERVER_URL, data=payload, headers=HEADERS)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
