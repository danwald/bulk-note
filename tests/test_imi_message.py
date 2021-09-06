import pytest

from bulk_note import imi_message


PAYLOAD = {"numbers": ["+971529492034", "+97150923823"]}


def test_impayload_full_dumps():
    payload = imi_message.IMIPayload(**PAYLOAD)
    print(f"{payload.dumps()}")
    assert payload.dumps()
