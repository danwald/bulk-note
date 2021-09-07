import logging
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, List, Dict, io, NamedTuple
from io import StringIO

import requests
from . import message

FROM = "+121212"
CONTENT = "foo bar"
CID_PREFIX = "2021-09-07"

logger = logging.getLogger(__name__)


@dataclass
class IMIPayload(message.Payload):
    cid = 0
    numbers: List[str]
    send_codes: Optional[Dict[str, str]] = None

    def dumps(self) -> str:
        payload = StringIO()

        for to in self.numbers:
            payload.write(
                (
                    f'<submitRequest id="{CID_PREFIX}_{IMIPayload.cid:07}">'
                    "<from>{FROM}</from>"
                    "<to>{to}</to>"
                    '<content type="text">{CONTENT}</content>'
                )
            )
            IMIPayload.cid += 1
            send_on_group = self.send_codes and self.send_codes.get(to)
            if send_on_group:
                payload.write(f"{payload}<sendOnGroup" 'value="{self.send_on_group}"/>')
        return f"<xiamSMS>{payload.getvalue()}</submitRequest></xiamSMS>"


class Status(NamedTuple):
    status: str
    status_code: str


@dataclass
class IMIResponse(message.Response):
    def get_status(status: Dict[str, str]) -> Status:
        return Status(status["status"], status["statusCode"])

    def good_status(status: Status) -> bool:
        return any([Status.status in set(["OK"]), Status.status_code in set(["0"])])

    def retry_status(status: Status) -> bool:
        return all(
            [
                Status.status in set(["FAIL"]),
                Status.status_code in set(["9", "10", "1039"]),
            ]
        )

    def bad_status(status: Status) -> bool:
        return not all(
            [IMIResponse.good_status(status), IMIResponse.retry_status(status)]
        )

    def unsub_status(status: Status) -> bool:
        return status.status_code in set(["88", "1050"])

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.reply = payload
        self.good = self.fail = self.retry = None

    def get_success(self) -> List[message.Outcome]:
        if self.good is None:
            if self.status_code != requests.codes.OK:
                self.good = []
                return self.good

            for response in ET.fromstring(self.reply):
                client_id = response.text.trim()
                for request in response:
                    number = request.text.trim()
                    status = self.get_status(request.attrib)
                    if not self.good_status(status):
                        logger.warning("Failed to send to %s (%s)", number, status)
                        continue

        return self.good

    def get_fail(self) -> List[message.Outcome]:
        if self.fail is None:
            pass
        return self.fail

    def get_retry(self) -> List[message.Outcome]:
        if self.retry is None:
            pass
        return self.retry


class IMIRecipients:
    def __init__(
        self, receipients: io.TextIO, send_groups: Optional[io.BinaryIO]
    ) -> None:
        self.receipients = filter(None, (line.trim() for line in receipients))
        self.send_groups = pickle.load(send_groups) if send_groups else None

    def get_tx_payload(self, count: int = 1) -> IMIPayload:
        pass

    def get_retry_payload(self, count: int = 1) -> IMIPayload:
        pass

    def get_failure_payload(self, count: int = 1) -> IMIPayload:
        pass
