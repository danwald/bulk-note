import datetime

URLS = {
    "test": "https://74af928a-87c2-4a1e-8b5f-e23376aa9a83.mock.pstmn.io/txt-200-partial",
    "short": "",
    "long": "",
}

SERVER_URL = URLS["test"]

RUN_PREFIX = f"{datetime.date.today}"
FROM = "+121212"

FAIL_OUT = f"./{RUN_PREFIX}-fail.out"
GOOD_OUT = f"./{RUN_PREFIX}-good.out"
RETRY_OUT = f"./{RUN_PREFIX}-retry.out"
