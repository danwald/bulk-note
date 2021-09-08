"""Console script for bulk_note."""
import sys
import click
import requests
import logging
from .imi_message import IMIRecipients, IMIResponse

SERVER_URL = "https://74af928a-87c2-4a1e-8b5f-e23376aa9a83.mock.pstmn.io/txt-500"
HEADERS = {"Content-type": "text/xml"}

logger = logging.getLogger(__name__)


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
    with open("./good.out", "w+") as good_out:
        with open("./fail.out", "w+") as fail_out:
            while payload := receipients.get_tx_payload().dumps():
                try:
                    resp = requests.post(SERVER_URL, data=payload, headers=HEADERS)
                    resp.raise_for_status()
                    logger.info("Sent bulk")
                except requests.HTTPError as e:
                    logger.exception(f"Except when sending Failed to send request {e}")
                    fail_out.write(f"{resp.text}\n")
                else:
                    for ir in IMIResponse("OK", resp.text).get_success():
                        good_out.write(f"{ir}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
