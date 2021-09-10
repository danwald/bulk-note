import pytest

from bulk_note.imi_message import IMIPayload, IMIResponse, Status

PAYLOAD = {
    "numbers": ["+971529492034", "+97150923823"],
    "send_codes": {},
    "content": "foo bar",
}

SUCCESS_RESPONSE = """
<xiamSMS status="OK" statusText="XML contained 2 xir messages">
    <submitResponse id="545vd69-1">
        <result status="OK" messageId="33C3CF22" sendOnGroup="XXX" >+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="OK" messageId="33C3CF23" sendOnGroup="XXX" >+14165551234</result>
    </submitResponse>
</xiamSMS>
"""

PARTIAL_SUCCESS_RESPONSE = """
<xiamSMS status="OK" statusText="XML contained 2 xir messages">
    <submitResponse id="545vd69-1">
        <result status="OK" messageId="33C3CF22" sendOnGroup="XXX" >+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="FAIL" statusCode="9" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="FAIL" statusCode="11" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="FAIL" statusCode="1039" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="FAIL" statusCode="88" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
    <submitResponse id="545vd69-2">
        <result status="FAIL" statusCode="1050" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
</xiamSMS>
"""


@pytest.fixture
def all_good_imi_response():
    return IMIResponse(Status.OK, SUCCESS_RESPONSE)


@pytest.fixture
def partial_good_imi_response():
    return IMIResponse(Status.OK, PARTIAL_SUCCESS_RESPONSE)


@pytest.mark.parametrize(
    "code, status, expected",
    [
        (Status.OK, "0", True),
        ("", "0", False),
        (Status.OK, "", False),
        (Status.FAIL, "0", False),
    ],
)
def test_good_statuses(code, status, expected):
    assert Status(code, status).good == expected


@pytest.mark.parametrize(
    "code, status, expected",
    [(Status.FAIL, "9", True), (Status.FAIL, "11", True), (Status.FAIL, "88", True)],
)
def test_retry_statuses(code, status, expected):
    assert Status(code, status).retry == expected


@pytest.mark.parametrize(
    "code, status, expected",
    [
        (Status.FAIL, "0", True),
        (Status.OK, "X", True),
        (Status.FAIL, "1042", True),
        (Status.FAIL, "1050", True),
    ],
)
def test_bad_statuses(code, status, expected):
    assert Status(code, status).bad == expected


def test_impayload_full_dumps():
    payload = IMIPayload(**PAYLOAD)
    assert payload.dumps()


def test_all_good_response(all_good_imi_response):
    assert len(all_good_imi_response.process().get_success()) == 2


def test_partial_good_response(partial_good_imi_response):
    assert len(partial_good_imi_response.process().get_success()) == 1


def test_partial_retry_response(partial_good_imi_response):
    assert len(partial_good_imi_response.process().get_retry()) == 3


def test_partial_fail_response(partial_good_imi_response):
    assert len(partial_good_imi_response.process().get_fail()) == 2
