import pytest

from bulk_note import imi_message


PAYLOAD_PARTIAL = {
    "cid": "1",
    "to": "+971529492034",
    "frm": "+97150923823",
    "content": "foo bar mofo",
}

PAYLOAD_FULL = {
    "cid": "2",
    "to": "+971529492034",
    "frm": "+97150923823",
    "content": "foo bar mofo",
    "send_on_group": "123321",
}


def test_impayload_full_dumps():
    payload = imi_message.IMIPayload(**PAYLOAD_FULL)
    assert payload.dumps().find("sendOnGroup") != -1


def test_impayload_partial_duumps():
    payload = imi_message.IMIPayload(**PAYLOAD_PARTIAL)
    assert payload.dumps().find("sendOnGroup") == -1
