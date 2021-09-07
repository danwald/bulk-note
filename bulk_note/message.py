from abc import ABC, abstractmethod

from typing import List, Union


class Payload(ABC):
    pass


class Outcome(ABC):
    pass


class Response(ABC):
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
    def get_tx_payload(self, count: int = 1) -> Payload:
        """returns payload to send

        count - number of items in payload
        """
        pass

    @abstractmethod
    def get_retry_payload(self, count: int = 1) -> Payload:
        """returns retry payload to send

        count - number of items in payload
        """
        pass

    @abstractmethod
    def get_failure_payload(self, count: int = 1) -> Payload:
        """returns failure payload

        count - number of items in payload
        """
        pass
