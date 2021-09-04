from abc import ABC


class Payload(ABC)
    pass

class Receiptiants(ABC):
    def get_tx_payload(count=1: int) -> Payload:
        """returns payload to send

        count - number of items in payload
        """
        pass

    def get_retry_payload(count=1):
    '''returns payload to send'''
        """returns payload to send

        count - number of items in payload
        """
        pass

    def get_failure_payload(count=1):
        pass
