import pytest

from bulk_note import imi_message


PAYLOAD = {"numbers": ["+971529492034", "+97150923823"]}

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
        <result status="FAIL" statusCode="9999" messageId="33C3CF23">+14165551234</result>
    </submitResponse>
</xiamSMS>
"""


@pytest.fixture
def all_good_imi_response():
    return imi_message.IMIResponse("OK", SUCCESS_RESPONSE)


@pytest.fixture
def partial_good_imi_response():
    return imi_message.IMIResponse("OK", PARTIAL_SUCCESS_RESPONSE)


@pytest.mark.parametrize(
    "code, status, expected",
    [("OK", "0", True), ("", "0", True), ("OK", "", True), ("FAIL", "0", False)],
)
def test_good_statuses(code, status, expected):
    assert (
        imi_message.IMIResponse.good_status(imi_message.Status(code, status))
        == expected
    )


def test_impayload_full_dumps():
    payload = imi_message.IMIPayload(**PAYLOAD)
    print(f"{payload.dumps()}")
    assert payload.dumps()


def test_all_good_response(all_good_imi_response):
    assert len(all_good_imi_response.get_success()) == 2


def test_partial_good_response(partial_good_imi_response):
    assert len(partial_good_imi_response.get_success()) == 1
