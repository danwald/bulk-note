import pickle
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, io

from . import message


@dataclass
class IMIPayload(message.Payload):
    cid: str
    to: str
    frm: str
    content: str
    send_on_group: Optional[str] = None

    def dumps(self) -> str:
        payload = (
            f'<submitRequest id="{self.cid}">'
            "<from>{self.frm}</from>"
            "<to>{self.to}</to>"
            '<content type="text">{self.content}</content>'
        )
        if send_on_group:
            payload = f'{payload}<sendOnGroup value="{self.send_on_group}"/>'
        return f"{payload}</submitRequest>"


class IMIRecipient(message.Recipient):
    def __init__(
        self, receipients: io.TextIO, send_groups: io.BinaryIO, content: str
    ) -> None:
        self.receipients = filter(None, (line.trim() for line in receipients))
        self.send_groups = pickle.load(send_groups)
        self.content = content

    def get_tx_payload(self, count: int = 1) -> IMIPayload:
        pass

    def get_retry_payload(self, count: int = 1) -> IMIPayload:
        pass

    def get_failure_payload(self, count: int = 1) -> IMIPayload:
        pass
