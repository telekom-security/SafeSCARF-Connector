import requests
from datetime import datetime, timedelta
import json
import sys
from typing import Optional


def main():
    if len(sys.argv) != 5:
        raise ValueError("Invalid number of arguments, expected 4 arguments: ${TOKEN} ${ENGAGEMENT_ID} ${SAFESCARF_SCAN_TITLE} delayTimeInMinutes")

    password = sys.argv[1]
    engagement_id = sys.argv[2]
    title = sys.argv[3]
    minutes_delay = int(sys.argv[4])

    print(f"Sending request to SafeScarf API to collect all tests for engagement with id {engagement_id}")

    url = f"https://dt-sec.safescarf.pan-net.cloud/api/v2/tests/?engagement={engagement_id}"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {password}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"HTTP response code is {response.status_code}")
        print(f"HTTP response body is {response.text}")
        raise RuntimeError("Couldn't get tests from SafeScarf API")

    tests = json.loads(response.text).get("results")
    print(f"Found {len(tests)} tests")
    print(f"Searching for test with title {title} and updating date less than current not more than 2 min")

    expected_test = find_expected_test(tests, title, minutes_delay)
    
    if expected_test:
            print(f"The following test was found: {json.dumps(expected_test, indent=2)}")
    else:
        raise RuntimeError(f"Could not find expected tests for engagement with id: {engagement_id}")

def find_expected_test(tests, title, minutes_delay) -> Optional[dict]:
    now = datetime.now()
    earlier = datetime.now() - timedelta(minutes=minutes_delay)
    for test in tests:
        if test.get("test_type_name") == title and now > datetime.strptime(test.get("updated"), "%Y-%m-%dT%H:%M:%S.%fZ") > earlier:
            print(test)
            return test
    return None


if __name__ == "__main__":
    main()
