from __future__ import annotations
import logging
import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from io import StringIO
from itertools import islice
from typing import Dict, List, Optional, io

from . import message


FROM = "+121212"
CONTENT = "foo bar"
CID_PREFIX = "2021-09-07"

logger = logging.getLogger(__name__)


@dataclass
class IMIPayload(message.Payload):
    cid = 0
    numbers: List[str]
    send_codes: Dict[str, str]
    content: str

    def dumps(self) -> str:
        payload = StringIO()
        for to in self.numbers:
            payload.write(
                (
                    f'<submitRequest id="{CID_PREFIX}_{IMIPayload.cid:07}">'
                    f"<from>{FROM}</from>"
                    f"<to>{to}</to>"
                    f'<content type="text">{self.content}</content>'
                    f'<sendOnGroup value=""/>'
                    f'<requestDeliveryReport value="yes"/>'
                    f"</submitRequest>"
                )
            )
            IMIPayload.cid += 1
            # not using send group
            # send_on_group = self.send_codes.get(to)
            # if send_on_group:
            #    payload.write(f"{payload}<sendOnGroup" 'value="{self.send_on_group}"/>')
            # payload.write("</submitRequest>")
            # payload = StringIO(f"<xiamSMS>{payload.getvalue()}</submitRequest></xiamSMS>")
        payload = payload.getvalue()
        return f"<xiamSMS>{payload}</xiamSMS>" if payload else ""


class Status:
    def __init__(self, status: str = "", status_code: str = "0", **kwargs):
        self.status = status
        self.status_code = status_code

    def __str__(self):
        return f"{self.status},{self.status_code}"

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

    def __str__(self):
        return f"{super().__str__()},{self.number},{self.client_message_id},{self.imi_message_id}"


@dataclass
class IMIResponse(message.Response):
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        self.good = self.fail = self.retry = None

    def process(self) -> IMIResponse:
        self.good = self.fail = self.retry = []
        root = ET.fromstring(self.payload)
        root_status = Status(root.attrib.get("status"))
        if not any([self.status_code == "OK", root_status.good]):
            return self

        for response in root:
            client_message_id = response.attrib.get("id").strip()
            for request in response:
                append_to = None
                number = request.text.strip()
                request_status = Status(**request.attrib)
                imi_message_id = request.attrib.get("id")
                if not request_status.good:
                    logger.debug("Failed to send to %s (%s)", number, request_status)

                if request_status.good:
                    append_to = self.good
                elif request_status.retry:
                    append_to = self.retry
                elif request_status.bad:
                    append_to = self.fail

                append_to.append(
                    IMIOutcome(
                        number=number,
                        client_message_id=client_message_id,
                        imi_message_id=imi_message_id,
                        status=request_status.status,
                        status_code=request_status.status_code,
                    )
                )
        return self

    def get_success(self) -> List[message.Outcome]:
        return self.good

    def get_fail(self) -> List[message.Outcome]:
        return self.fail

    def get_retry(self) -> List[message.Outcome]:
        return self.retry


class IMIRecipients:
    def __init__(
        self,
        receipients: io.TextIO,
        content: io.TextIO,
        send_groups: Optional[io.BinaryIO],
        batch_size=10,
        verbose=0,
    ) -> None:
        self.receipients = filter(None, (line.strip() for line in receipients))
        self.send_groups = pickle.load(send_groups) if send_groups else {}
        self.batch_size = batch_size
        self.verbose = verbose
        self.content = content.readline().strip()

    def get_tx_payload(self) -> IMIPayload:
        return IMIPayload(
            islice(self.receipients, self.batch_size), self.send_groups, self.content
        )
