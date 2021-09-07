import logging
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, List, Dict, io, NamedTuple
from io import StringIO

import pytest
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


class Status:
    def __init__(self, status: str = "", status_code: str = "0", **kwargs):
        self.status = status
        self.status_code = status_code

    @property
    def good(self) -> bool:
        if self.status == "FAIL":
            return False
        else:
            return any([self.status in set(["OK"]), self.status_code in set(["0"])])

    @property
    def retry(self) -> bool:
        return all(
            [self.status in set(["FAIL"]), self.status_code in set(["9", "10", "1039"])]
        )

    @property
    def bad(self) -> bool:
        return not all([self.good, self.retry])

    @property
    def unsubscribe(self) -> bool:
        return self.status_code in set(["88", "1050"])


class IMIOutcome(Status, message.Outcome):
    def __init__(
        self,
        number: str = "",
        client_message_id: str = "",
        imi_message_id: str = "",
        **kwargs,
    ):
        self.number = number
        self.client_message_id = client_message_id
        self.imi_message_id = imi_message_id
        super().__init__(**kwargs)


@dataclass
class IMIResponse(message.Response):
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        self.good = self.fail = self.retry = None

    def get_success(self) -> List[message.Outcome]:
        if self.good is None:
            self.good = []
            root = ET.fromstring(self.payload)
            root_status = Status(root.attrib.get("status"))
            if not any([self.status_code == "OK", root_status.good]):
                return self.good

            for response in root:
                client_message_id = response.attrib.get("id").strip()
                for request in response:
                    number = request.text.strip()
                    request_status = Status(**request.attrib)
                    imi_message_id = request.attrib.get("id")
                    if not request_status.good:
                        logger.warning(
                            "Failed to send to %s (%s)", number, request_status
                        )
                        continue
                    self.good.append(
                        IMIOutcome(
                            number=number,
                            client_message_id=client_message_id,
                            imi_message_id=imi_message_id,
                            status=request_status.status,
                            status_code=request_status.status_code,
                        )
                    )
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
