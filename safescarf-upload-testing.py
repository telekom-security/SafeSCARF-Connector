import requests
import argparse
import os
from datetime import datetime, timedelta
import json
import sys
from typing import Optional
import re
import validators

SAFESCARF_TESTING_MODE_ENABLE = os.environ.get("SAFESCARF_TESTING_MODE_ENABLE", "false")

def validate_input(args):
    if len(args) != 6:
        raise ValueError(f"Invalid number of arguments. Expected 5 arguments: <Token> <Engagement ID> <Scan Title> <Minutes Delay> <URL>, but provided {len(args)-1} arguments")

    token = args[1]
    if not re.match(r"^[a-f0-9]{40}$", token):
        raise ValueError(f"Invalid token format: {token}. Expected a 40-character hexadecimal string.")

    engagement_id = args[2]
    if not engagement_id.isdigit():
        raise ValueError(f"Invalid engagement ID: {engagement_id}. Expected a numeric value.")

    scan_title = args[3]
    if len(scan_title.strip()) == 0:
        raise ValueError("Invalid scan title: Title cannot be empty.")

    try:
        minutes_delay = int(args[4])
        if minutes_delay <= 0:
            raise ValueError(f"Invalid minutes delay: {minutes_delay}. It must be a positive integer.")
    except ValueError:
        raise ValueError(f"Invalid minutes delay: {args[4]}. It must be an integer.")

    # Validate the URL (Argument 5)
    url = args[5]
    if not validators.url(url):
        raise ValueError(f"Invalid URL: {url}.")

    print("All inputs are valid!")
    return True


def main():
    if SAFESCARF_TESTING_MODE_ENABLE == "false":
        print("SafeScarf Testing Mode is disabled. Exiting...")
        quit()
    validate_input(sys.argv)
    password = sys.argv[1]
    engagement_id = sys.argv[2]
    title = sys.argv[3]
    minutes_delay = int(sys.argv[4])
    safescarf_url = sys.argv[5]

    print(f"Sending request to SafeScarf API to collect all tests for engagement with id {engagement_id}")

    url = f"{safescarf_url}/api/v2/tests/?engagement={engagement_id}"
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
    print(f"Searching for test with title \'{title}\' and updating date less than current not more than {minutes_delay} min")

    expected_test = find_expected_test(tests, title, minutes_delay)
    
    if expected_test:
            print(f"The following test was found: {json.dumps(expected_test, indent=2)} \n All expected scans are present in engagement")
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
