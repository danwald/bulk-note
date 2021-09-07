"""Console script for bulk_note."""
import sys
import click
from .imi_message import IMIRecipients


@click.command()
@click.option("--numbers", required=True, type=click.File("r"), help="file of numbers")
@click.option(
    "--send-codes",
    type=click.File("rb"),
    default=None,
    help="file of pickled sendcodes",
)
@click.option("--bulk-size", default=10, help="batch size per send")
@click.option("-v", "--verbose", count=True)
def main(numbers, send_codes, bulk_size, verbose):
    receipients = IMIRecipients(numbers, send_codes, bulk_size, verbose)
    server_url = "https://74af928a-87c2-4a1e-8b5f-e23376aa9a83.mock.pstmn.io/"

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
