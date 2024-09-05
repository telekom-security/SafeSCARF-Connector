#!/usr/bin/env python3

import argparse
import os
import json
import requests
import glob
from urllib.parse import quote
from datetime import datetime, timedelta  # Import the datetime module

# Set default values for environment variables
SAFESCARF_ENGAGEMENT_PERIOD = int(os.environ.get("SAFESCARF_ENGAGEMENT_PERIOD", 7))
TODAY = os.environ.get("TODAY", (datetime.now()).strftime("%Y-%m-%d"))
ENDDAY = os.environ.get("ENDDAY", (datetime.now() + timedelta(days=SAFESCARF_ENGAGEMENT_PERIOD)).strftime("%Y-%m-%d"))
CI_COMMIT_DESCRIPTION = os.environ.get("CI_COMMIT_DESCRIPTION", "Commit description")
CI_COMMIT_SHORT_SHA = os.environ.get("CI_COMMIT_SHORT_SHA", "")
GITLAB_VERSION_REF = os.environ["CI_MERGE_REQUEST_ID"] if "CI_MERGE_REQUEST_ID" in os.environ \
                    else os.environ["CI_COMMIT_REF_NAME"] if "CI_COMMIT_REF_NAME" in os.environ \
                    else os.environ["CI_COMMIT_TAG"] if "CI_COMMIT_TAG" in os.environ \
                    else "main"
CI_PROJECT_URL = os.environ.get("CI_PROJECT_URL", "https://gitlab.com/mygroup/myproject")
SAFESCARF_ENGAGEMENT_THREAT_MODEL = os.environ.get("SAFESCARF_ENGAGEMENT_THREAT_MODEL", True)
SAFESCARF_ENGAGEMENT_API_TEST = os.environ.get("SAFESCARF_ENGAGEMENT_API_TEST", True)
SAFESCARF_ENGAGEMENT_PEN_TEST = os.environ.get("SAFESCARF_ENGAGEMENT_PEN_TEST", True)
SAFESCARF_ENGAGEMENT_CHECK_LIST = os.environ.get("SAFESCARF_ENGAGEMENT_CHECK_LIST", True)
SAFESCARF_ENGAGEMENT_STATUS = os.environ.get("SAFESCARF_ENGAGEMENT_STATUS", "Not Started")
SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT = os.environ.get("SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT", True)
SAFESCARF_ENGAGEMENT_BUILD_SERVER = os.environ.get("SAFESCARF_ENGAGEMENT_BUILD_SERVER", None)
SAFESCARF_ENGAGEMENT_BUILD_SERVER = None if SAFESCARF_ENGAGEMENT_BUILD_SERVER == "null" else SAFESCARF_ENGAGEMENT_BUILD_SERVER
SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER = os.environ.get("SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER", None)
SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER = None if SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER == "null" else SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER
SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE = os.environ.get("SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE", None)
SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE = None if SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE == "null" else SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE
SAFESCARF_SCAN_MINIMUM_SEVERITY = os.environ.get("SAFESCARF_SCAN_MINIMUM_SEVERITY", "Info")
SAFESCARF_SCAN_ACTIVE = os.environ.get("SAFESCARF_SCAN_ACTIVE", True)
SAFESCARF_SCAN_VERIFIED = os.environ.get("SAFESCARF_SCAN_VERIFIED", True)
SAFESCARF_SCAN_CLOSE_OLD_FINDINGS = os.environ.get("SAFESCARF_SCAN_CLOSE_OLD_FINDINGS", True)
SAFESCARF_SCAN_ENVIRONMENT = os.environ.get("SAFESCARF_SCAN_ENVIRONMENT", "Default")

SAFESCARF_PRODUCT_NAME = ""

SAFESCARF_API_TOKEN = ""
SAFESCARF_URL = ""
SAFESCARF_ENGAGEMENT_ID = ""
SAFESCARF_PRODUCT_ID = ""
SAFESCARF_SCAN_TYPE = ""
SAFESCARF_TEST_SERVICE = ""
SAFESCARF_VERSION = ""
SAFESCARF_WORKFLOW = ""
SAFESCARF_NAME = ""
SAFESCARF_REIMPORT_DO_NOT_REACTIVATE = ""
SAFESCARF_BRANCH_TAG = ""
SAFESCARF_COMMIT_HASH = ""
SAFESCARF_BUILD_ID = ""
SAFESCARF_REIMPORT = True

TAGS = []

def get_available_scan_types():
    """
    Get a list of available scan types from the SafeSCARF API.

    Returns:
        list: A list of available scan types.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.get(f"{SAFESCARF_URL}/api/v2/test_types/?limit=500", headers=headers)

    if response.status_code == 200:
        test_types = response.json().get("results", [])
        return [test_type["name"] for test_type in test_types]
    else:
        print(f"Failed to fetch test types from the API. Status code: {response.status_code}")
        return []

def is_valid_scan_type(scan_type):
    """
    Check if the provided scan_type is in the list of available_scan_types.

    Args:
        scan_type (str): The scan type to check.

    Returns:
        bool: True if scan_type is valid, False otherwise.
    """
    available_scan_types = get_available_scan_types()
    valid = scan_type in available_scan_types
    if valid:
        return True
    print (f"{scan_type} is not a valid scan_type. Please check valid types with command <scan-types>")
    return False

def check_engagement_access(engagement_id):
    """
    Check if the user has access to the provided engagement_id.

    Args:
        engagement_id (str): The ID of the engagement to check.

    Returns:
        bool: True if the user has access, False otherwise.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
    }

    print(SAFESCARF_API_TOKEN)
    # Make an API request to check access to the engagement
    response = requests.get(f"{SAFESCARF_URL}/api/v2/engagements/{engagement_id}/", headers=headers)

    if response.status_code == 200:
        # The user has access to the engagement
        print(f"Access to Engagement {engagement_id} is possible.")
        return True
    elif response.status_code == 403:
        # The user does not have access to the engagement
        print(f"You don't have permissions to access {engagement_id}!")
        return False
    else:
        # Handle other status codes as needed
        print(f"Failed to check access to engagement {engagement_id}. Status code: {response.status_code}")
        return None

def check_engagement_exists(name):
    """
    Check if an engagement with the specified name already exists within the product.

    Args:
        name (str): The name of the engagement to check.

    Returns:
        str or None: The ID of the existing engagement, or None if it doesn't exist.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{SAFESCARF_URL}/api/v2/engagements/?name={name}&product={SAFESCARF_PRODUCT_ID}", headers=headers)

    if response.status_code == 200:
        engagements = response.json().get("results", [])
        if engagements:
            return engagements[0]["id"]
    return None

def check_test_exists(engagement_id, test_title):
    """
    Check if a test with the provided title exists within the specified engagement.

    Args:
        engagement_id (str): The ID of the engagement to check.
        test_title (str): The title of the test to check.

    Returns:
        bool: True if a test with the same title exists, False otherwise.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
    }
    test_title = quote(test_title)
    response = requests.get(f"{SAFESCARF_URL}/api/v2/tests/?engagement={engagement_id}&title={test_title}", headers=headers)

    if response.status_code == 200:
        tests = response.json().get("results", [])
        return bool(tests)
    else:
        print(f"Failed to fetch tests for engagement {engagement_id}. Status code: {response.status_code}")
        return False

def create_engagement():
    """
    Create a new engagement using the provided information and settings.
    """
    global SAFESCARF_ENGAGEMENT_ID
    global SAFESCARF_NAME
    # Check if SAFESCARF_ENGAGEMENT_ID is set
    if SAFESCARF_ENGAGEMENT_ID:
        print("SAFESCARF_ENGAGEMENT_ID is already set. Aborting engagement creation.")
        return

    # Add tags to the tags array using a list comprehension
    tags = TAGS

    # default engagement name to pipeline id
    if SAFESCARF_NAME == "":
        SAFESCARF_NAME = f"#{SAFESCARF_BUILD_ID}"

    if SAFESCARF_WORKFLOW:
        tags.append("flow:" + SAFESCARF_WORKFLOW)
        if SAFESCARF_WORKFLOW == "branch":
            SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT = True
            SAFESCARF_NAME = GITLAB_VERSION_REF # Tag and Branch Pipelines only (no Merge Pipeline)
            # Check if an engagement with the same name exists
            engagement_id = check_engagement_exists(SAFESCARF_NAME)
            if engagement_id:
                with open("safescarf.env", "w") as f:
                    f.write(f"SAFESCARF_ENGAGEMENT_ID={engagement_id}\n")
                print(f"Engagement with the same name already exists. Engagement ID: {engagement_id}")
                return
        elif SAFESCARF_WORKFLOW == "pipeline":
            SAFESCARF_NAME = f"#{SAFESCARF_BUILD_ID}"
            SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT = False
    engagement_data = {
        "tags": tags,
        "name": SAFESCARF_NAME,
        "description": CI_COMMIT_DESCRIPTION,
        "version": SAFESCARF_VERSION,
        "first_contacted": TODAY,
        "target_start": TODAY,
        "target_end": ENDDAY,
        "reason": "string",
        "tracker": f"{CI_PROJECT_URL}/-/issues",
        "threat_model": SAFESCARF_ENGAGEMENT_THREAT_MODEL,
        "api_test": SAFESCARF_ENGAGEMENT_API_TEST,
        "pen_test": SAFESCARF_ENGAGEMENT_PEN_TEST,
        "check_list": SAFESCARF_ENGAGEMENT_CHECK_LIST,
        "status": SAFESCARF_ENGAGEMENT_STATUS,
        "engagement_type": "CI/CD",
        "build_id": SAFESCARF_BUILD_ID,
        "commit_hash": CI_COMMIT_SHORT_SHA,
        "branch_tag": GITLAB_VERSION_REF,
        "deduplication_on_engagement": SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT,
        "product": SAFESCARF_PRODUCT_ID,
        "source_code_management_uri": f"{CI_PROJECT_URL}/-/tree/{GITLAB_VERSION_REF}/",
        "build_server": SAFESCARF_ENGAGEMENT_BUILD_SERVER,
        "source_code_management_server": SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER,
        "orchestration_engine": SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE,
    }

    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(f"{SAFESCARF_URL}/api/v2/engagements/", headers=headers, json=engagement_data)

    if response.status_code >= 200 and response.status_code < 300:
        SAFESCARF_ENGAGEMENT_ID = response.json().get("id")
        with open("safescarf.env", "w") as f:
            f.write(f"SAFESCARF_ENGAGEMENT_ID={SAFESCARF_ENGAGEMENT_ID}\n")
        print(f"Engagement <{SAFESCARF_ENGAGEMENT_ID}> created with workflow type: {SAFESCARF_WORKFLOW}")
    else:
        print(f"Failed to create engagement. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

def get_engagement_name(engagement_id):
    """
    Get the name of an engagement using its Engagement ID.

    Args:
        engagement_id (str): The Engagement ID for which to retrieve the name.

    Returns:
        str: The name of the engagement, or an empty string if the request fails.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
    }

    response = requests.get(f"{SAFESCARF_URL}/api/v2/engagements/{engagement_id}/", headers=headers)

    if response.status_code == 200:
        engagement_data = response.json()
        return engagement_data.get("name", "")
    else:
        print(f"Failed to fetch engagement data. Status code: {response.status_code}")
        return ""


def get_product_name(product_id) -> str:
    """
    Get the name of a product using its Product ID.

    Args:
        product_id (int): The Product ID for which to retrieve the name.

    Returns:
        str: The name of the product, or an empty string if the request fails.
    """
    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
    }

    response = requests.get(f"{SAFESCARF_URL}/api/v2/products/{product_id}/", headers=headers)

    if response.status_code == 200:
        product_data = response.json()
        return product_data.get("name", "")
    else:
        print(f"Failed to fetch product data. Status code: {response.status_code}")
        return ""


def upload(files):
    """
    Upload specified files to SafeSCARF as a scan with the provided settings.

    Args:
        files (list): List of file patterns to upload.
    """
    if not files:
        print("No files specified. Type 'help' for more information.")
        return

    if not is_valid_scan_type(SAFESCARF_SCAN_TYPE):
        return

    # Add tags to the tags array using a list comprehension
    tags = TAGS

    reimport = SAFESCARF_REIMPORT

    # Check if reimport is possible
    # test whether the same test title exists in the engagement
    if reimport and SAFESCARF_ENGAGEMENT_ID and SAFESCARF_NAME and check_test_exists(SAFESCARF_ENGAGEMENT_ID, SAFESCARF_NAME):
        reimport = True # set reimport true if possible
    else:
        reimport = False # default to False if impossible or not desired

    for file_pattern in files:
        matching_files = glob.glob(file_pattern)
        for file in matching_files:
            if os.path.isfile(file) and os.path.getsize(file) > 0:
                print(f"Uploading {file} to SafeSCARF")
                files = {"file": (file, open(file, "rb"))}
                data = {
                    "tags": tags,
                    "scan_date": TODAY,
                    "minimum_severity": SAFESCARF_SCAN_MINIMUM_SEVERITY,
                    "active": SAFESCARF_SCAN_ACTIVE,
                    "verified": SAFESCARF_SCAN_VERIFIED,
                    "scan_type": SAFESCARF_SCAN_TYPE,
                    "engagement": SAFESCARF_ENGAGEMENT_ID,
                    "close_old_findings": SAFESCARF_SCAN_CLOSE_OLD_FINDINGS,
                    "environment": SAFESCARF_SCAN_ENVIRONMENT,
                    "service": SAFESCARF_TEST_SERVICE,
                    "version": SAFESCARF_VERSION,
                    "test_title": SAFESCARF_NAME,
                }
                if SAFESCARF_BRANCH_TAG != "":
                    data["branch_tag"] = SAFESCARF_BRANCH_TAG
                if SAFESCARF_COMMIT_HASH != "":
                    data["commit_hash"] = SAFESCARF_COMMIT_HASH
                if SAFESCARF_BUILD_ID != "":
                    data["build_id"] = SAFESCARF_BUILD_ID

                headers = {"Authorization": f"Token {SAFESCARF_API_TOKEN}"}
                response = ""

                if reimport:
                    data["do_not_reactivate"] = SAFESCARF_REIMPORT_DO_NOT_REACTIVATE
                    data["product_name"] = get_product_name(SAFESCARF_PRODUCT_ID)
                    data["engagement_name"] = get_engagement_name(SAFESCARF_ENGAGEMENT_ID)
                    response = requests.post(
                        f"{SAFESCARF_URL}/api/v2/reimport-scan/",
                        headers=headers,
                        data=data,
                        files=files,
                    )
                else:
                    response = requests.post(
                        f"{SAFESCARF_URL}/api/v2/import-scan/",
                        headers=headers,
                        data=data,
                        files=files,
                    )
                if response.status_code >= 200 and response.status_code < 300:
                    print(f"{file} uploaded successfully.")
                else:
                    print(f"Failed to upload {file}. Status code: {response.status_code}")
                    print(f"Error message: {response.text}")
            else:
                print(f"{file} is not a valid file or is empty.")

# Create a command-line argument parser
parser = argparse.ArgumentParser(description="API Connector for easier integration in workflows.")

# Add an argument for the command
parser.add_argument("command", choices=["create-engagement", "upload", "help", "scan-types"], help="Specify the command")

# Add an argument for --workflow
parser.add_argument("--workflow", choices=["feature", "pipeline"], help="Specify the workflow type for create-engagement")

# Add an argument for --api-key
parser.add_argument("--api-key", help="Specify the API key as a string")

# Add an argument for --api-url
parser.add_argument("--api-url", help="Specify the custom API URL as a string")

# Add an argument for --branch-tag
parser.add_argument("--branch-tag", help="Specify the branch or tag that has been scanned")

# Add an argument for --build-id
parser.add_argument("--build-id", help="Specify the build id for revision")

# Add an argument for --commit-hash
parser.add_argument("--commit-hash", help="Specify the commit hash for revision")

# Add an argument for --do-not-reactivate
parser.add_argument("--do-not-reactivate", help="Reactivate findings during re-import scan")

# Add an argument for --engagement-id
parser.add_argument("--engagement-id", help="Specify the engagement ID as an integer")

# Add an argument for --environment
parser.add_argument("--environment", help="Specify the scan environment")

# Add an argument for --name
parser.add_argument("--name", help="Name the engagement (create-engagement) or current test result to be uploaded (upload)")

# Add an argument for --product-id
parser.add_argument("--product-id", help="Specify the product ID as a string")

# Add an argument for --reimport
parser.add_argument("--reimport", help="Decide whether to upload or reimport the scan")

# Add an argument for --tags
parser.add_argument("--tags", help="Specify semicolon-separated tags")

# Add an argument for --scan-type
parser.add_argument("--scan-type", help="Specify the scan type as a string")

# Add an argument for --service
parser.add_argument("--service", help="Specify the tested service within the system (e.g. a container image)")

# Add an argument for --version
parser.add_argument("--version", help="Specify the version of the engagement (create-engagement) or test (upload) that has been tested. e.g. the version of the container that has been specified with --service")

# Add arguments for files to upload
parser.add_argument("files", nargs="*", help="Files to upload")

if __name__ == "__main__":
    args = parser.parse_args()

    SAFESCARF_API_TOKEN = args.api_key if args.api_key else os.environ.get('SAFESCARF_TOKEN', "")
    SAFESCARF_URL = args.api_url if args.api_url else os.environ.get('SAFESCARF_URL', "")
    SAFESCARF_ENGAGEMENT_ID = args.engagement_id if args.engagement_id else os.environ.get('SAFESCARF_ENGAGEMENT_ID', "")
    SAFESCARF_PRODUCT_ID = args.product_id if args.product_id else os.environ.get('SAFESCARF_PRODUCT_ID', "")
    SAFESCARF_SCAN_ENVIRONMENT = args.environment if args.environment else os.environ.get('SAFESCARF_SCAN_ENVIRONMENT', "")
    SAFESCARF_WORKFLOW = args.workflow if args.workflow else os.environ.get('SAFESCARF_WORKFLOW', "")
    SAFESCARF_SCAN_TYPE = args.scan_type if args.scan_type else os.environ.get('SAFESCARF_SCAN_TYPE', "")
    SAFESCARF_TEST_SERVICE = args.service if args.service else os.environ.get('SAFESCARF_TEST_SERVICE', "")
    SAFESCARF_VERSION = args.version if args.version else GITLAB_VERSION_REF
    SAFESCARF_NAME = args.name if args.name else os.environ.get('SAFESCARF_NAME', "")
    SAFESCARF_REIMPORT_DO_NOT_REACTIVATE = args.do_not_reactivate if args.do_not_reactivate else os.environ.get('SAFESCARF_REIMPORT_DO_NOT_REACTIVATE', False)
    SAFESCARF_BRANCH_TAG = args.branch_tag if args.branch_tag else os.environ.get('SAFESCARF_BRANCH_TAG', GITLAB_VERSION_REF)
    SAFESCARF_COMMIT_HASH = args.commit_hash if args.commit_hash else os.environ.get('SAFESCARF_COMMIT_HASH', "")
    SAFESCARF_BUILD_ID = args.build_id if args.build_id else os.environ.get('SAFESCARF_BUILD_ID', "")
    SAFESCARF_REIMPORT = args.reimport if args.reimport else os.environ.get('SAFESCARF_REIMPORT', True)

    # verify that given engagement id is accessible
    if SAFESCARF_ENGAGEMENT_ID != "" and int(SAFESCARF_ENGAGEMENT_ID) > 0:
        res = check_engagement_access(SAFESCARF_ENGAGEMENT_ID)
        if not res:
            quit()

    if args.tags:
        TAGS.extend(args.tags.split(";"))
    if args.command == "create-engagement":
        create_engagement()
    elif args.command == "upload":
        upload(args.files)
    elif args.command == "help":
        parser.print_help()
    elif args.command == "test-types":
        if SAFESCARF_URL != "" and SAFESCARF_API_TOKEN != "":
            print(get_available_scan_types())
        else:
            print("--api-url and --api-key are neccessary for this command!")
    else:
        print("Invalid command. Check 'help' for more information.")
