import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, List, Dict, io

from io import StringIO

from . import message


FROM = "+121212"
CONTENT = "foo bar"
CID_PREFIX = "2021-09-07"


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
        return f"<xiamSMS>{payload.getvalue()}</submitRequest><xiamSMS>"


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
