"""Console script for bulk_note."""
import logging
import sys
import time
import xml

import click
import requests

from . import settings
from .imi_message import IMIRecipients, IMIResponse, Status

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
    good_count = retry_count = fail_count = 0
    receipients = IMIRecipients(numbers, content, send_codes, bulk_size, verbose)
    with open(settings.GOOD_OUT, "a") as good_out, open(
        settings.FAIL_OUT, "a"
    ) as fail_out, open(settings.RETRY_OUT, "a") as retry_out:
        while payload := receipients.get_tx_payload().dumps():  # noqa:  E231
            time.sleep(1)
            try:
                resp = requests.post(
                    settings.SERVER_URL,
                    data=payload,
                    headers={"Content-type": "text/xml"},
                )
                resp.raise_for_status()
                logger.debug("Sent bulk")
                processed = IMIResponse(Status.OK, resp.text).process()
                for ok in processed.get_success():
                    good_out.write(f"{ok}\n")
                    good_count += 1
                for r in processed.get_retry():
                    retry_out.write(f"{r}\n")
                    retry_count += 1
                for f in processed.get_fail():
                    fail_out.write(f"{f}\n")
                    fail_count += 1
                sys.stdout.write(
                    f"\rProcessed: {good_count+retry_count+fail_count} number "
                    f"(good:{good_count}|retry{retry_count}|fail{fail_count})"
                )
            except requests.HTTPError as e:  # noqa F821
                logger.exception("Except when sending Failed to send request")
                fail_out.write(f"Bad Response {resp.status_code}:\n{resp.text}\n<>\n")
            except xml.etree.ElementTree.ParseError as p:  # noqa F821
                logger.exception("XmlParsing error")
                fail_out.write(f"XmlParser:\n{resp.text}\n<>\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
