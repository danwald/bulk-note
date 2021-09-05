from abc import ABC, abstractmethod


class Payload(ABC):
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
