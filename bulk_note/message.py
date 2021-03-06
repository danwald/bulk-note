from __future__ import annotations
from abc import ABC, abstractmethod

from typing import List


class Payload(ABC):
    pass


class Outcome(ABC):
    pass


class Response(ABC):
    @abstractmethod
    def process(self) -> Response:
        pass

    @abstractmethod
    def get_success(self) -> List[Outcome]:
        pass

    @abstractmethod
    def get_fail(self) -> List[Outcome]:
        pass

    @abstractmethod
    def get_retry(self) -> List[Outcome]:
        pass


class Recipient(ABC):
    @abstractmethod
    def get_tx_payload(self) -> Payload:
        """returns payload to send"""
        pass
