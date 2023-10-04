#!/usr/bin/env python3

import argparse
import os
import json
import requests
import glob
from datetime import datetime, timedelta  # Import the datetime module

# Set default values for environment variables
SAFESCARF_ENGAGEMENT_PERIOD = 7
TODAY = os.environ.get("TODAY", (datetime.now()).strftime("%Y-%m-%d"))
ENDDAY = os.environ.get("ENDDAY", (datetime.now() + timedelta(days=SAFESCARF_ENGAGEMENT_PERIOD)).strftime("%Y-%m-%d"))
CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID", "")
CI_COMMIT_DESCRIPTION = os.environ.get("CI_COMMIT_DESCRIPTION", "Commit description")
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
SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT = os.environ.get("SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT", False)
SAFESCARF_ENGAGEMENT_BUILD_SERVER = os.environ.get("SAFESCARF_ENGAGEMENT_BUILD_SERVER", "null")
SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER = os.environ.get("SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER", "null")
SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE = os.environ.get("SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE", "null")
SAFESCARF_SCAN_MINIMUM_SEVERITY = os.environ.get("SAFESCARF_SCAN_MINIMUM_SEVERITY", "Info")
SAFESCARF_SCAN_ACTIVE = os.environ.get("SAFESCARF_SCAN_ACTIVE", True)
SAFESCARF_SCAN_VERIFIED = os.environ.get("SAFESCARF_SCAN_VERIFIED", True)
SAFESCARF_SCAN_CLOSE_OLD_FINDINGS = os.environ.get("SAFESCARF_SCAN_CLOSE_OLD_FINDINGS", True)
SAFESCARF_SCAN_PUSH_TO_JIRA = os.environ.get("SAFESCARF_SCAN_PUSH_TO_JIRA", False)
SAFESCARF_SCAN_ENVIRONMENT = os.environ.get("SAFESCARF_SCAN_ENVIRONMENT", "Default")

SAFESCARF_API_TOKEN = ""
SAFESCARF_URL = ""
SAFESCARF_ENGAGEMENT_ID = ""
SAFESCARF_PRODUCTID = ""
SAFESCARF_SCAN_TYPE = ""
SAFESCARF_WORKFLOW = ""

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
    response = requests.get(f"{SAFESCARF_URL}/api/v2/engagements/?name={name}&product={SAFESCARF_PRODUCTID}", headers=headers)

    if response.status_code == 200:
        engagements = response.json().get("results", [])
        if engagements:
            return engagements[0]["id"]
    return None

def create_engagement():
    """
    Create a new engagement using the provided information and settings.
    """
    global SAFESCARF_ENGAGEMENT_ID
    # Check if SAFESCARF_ENGAGEMENT_ID is set
    if SAFESCARF_ENGAGEMENT_ID:
        print("SAFESCARF_ENGAGEMENT_ID is already set. Aborting engagement creation.")
        return

    # Add tags to the tags array using a list comprehension
    tags = ["GITLAB-CI"]
    tags.extend(TAGS)
    name = f"#{CI_PIPELINE_ID}"
    version = GITLAB_VERSION_REF

    if SAFESCARF_WORKFLOW:
        tags.append("flow:" + SAFESCARF_WORKFLOW)
        # set version depending on workflow
        if SAFESCARF_WORKFLOW == "branch":
            name = CI_COMMIT_REF_NAME # Tag and Branch Pipelines only (no Merge Pipeline)
            version = CI_COMMIT_REF_NAME
            # Check if an engagement with the same name exists
            engagement_exists = check_engagement_exists(name)
            if engagement_exists:
                print(f"Engagement with the same name already exists. Engagement ID: {engagement_exists}")
                return
        elif SAFESCARF_WORKFLOW == "pipeline":
            name = f"#{CI_PIPELINE_ID}"
            version = GITLAB_VERSION_REF
    engagement_data = {
        "tags": tags,
        "name": f"#{CI_PIPELINE_ID}",
        "description": CI_COMMIT_DESCRIPTION,
        "version": version,
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
        "build_id": CI_PIPELINE_ID,
        "commit_hash": CI_COMMIT_SHORT_SHA,
        "branch_tag": CI_COMMIT_REF_NAME,
        "deduplication_on_engagement": SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT,
        "product": SAFESCARF_PRODUCTID,
        "source_code_management_uri": f"{CI_PROJECT_URL}/-/tree/{CI_COMMIT_REF_NAME}/",
        "build_server": SAFESCARF_ENGAGEMENT_BUILD_SERVER,
        "source_code_management_server": SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER,
        "orchestration_engine": SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE,
    }

    headers = {
        "Authorization": f"Token {SAFESCARF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(f"{SAFESCARF_URL}/api/v2/engagements/", headers=headers, json=engagement_data)

    if response.status_code == 200:
        SAFESCARF_ENGAGEMENT_ID = response.json().get("id")
        os.environ["ENGAGEMENTID"] = SAFESCARF_ENGAGEMENT_ID  # Export engagement_id
        print(f"Engagement <{SAFESCARF_ENGAGEMENT_ID}> created with workflow type: {SAFESCARF_WORKFLOW}")
    else:
        print(f"Failed to create engagement. Status code: {response.status_code}")

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
    tags = ["GITLAB-CI"]
    tags.extend(TAGS)

    for file_pattern in files:
        matching_files = glob.glob(file_pattern)
        for file in matching_files:
            if os.path.isfile(file) and os.path.getsize(file) > 0:
                print(f"Uploading {file} to SafeSCARF")
                files = {"file": (file, open(file, "rb"))}
                data = {
                    "scan_date": TODAY,
                    "minimum_severity": SAFESCARF_SCAN_MINIMUM_SEVERITY,
                    "active": SAFESCARF_SCAN_ACTIVE,
                    "verified": SAFESCARF_SCAN_VERIFIED,
                    "scan_type": SAFESCARF_SCAN_TYPE,
                    "engagement": SAFESCARF_ENGAGEMENT_ID,
                    "close_old_findings": SAFESCARF_SCAN_CLOSE_OLD_FINDINGS,
                    "push_to_jira": SAFESCARF_SCAN_PUSH_TO_JIRA,
                    "environment": SAFESCARF_SCAN_ENVIRONMENT,
                }
                headers = {"Authorization": f"Token {SAFESCARF_API_TOKEN}"}
                response = requests.post(
                    f"{SAFESCARF_URL}/api/v2/import-scan/",
                    headers=headers,
                    data=data,
                    files=files,
                )
                if response.status_code >= 200 and response.status_code <= 300:
                    print(f"{file} uploaded successfully.")
                else:
                    print(f"Failed to upload {file}. Status code: {response.status_code}")
            else:
                print(f"{file} is not a valid file or is empty.")

# Create a command-line argument parser
parser = argparse.ArgumentParser(description="API Connector for easier integration in workflows.")

# Add an argument for the command
parser.add_argument("command", choices=["create-engagement", "upload", "help", "scan-types"], help="Specify the command")

# Add an argument for --workflow
parser.add_argument("--workflow", choices=["branch", "pipeline"], help="Specify the workflow type for create-engagement")

# Add an argument for --api-key
parser.add_argument("--api-key", help="Specify the API key as a string")

# Add an argument for --api-url
parser.add_argument("--api-url", help="Specify the custom API URL as a string")

# Add an argument for --engagement-id
parser.add_argument("--engagement-id", help="Specify the engagement ID as an integer")

# Add an argument for --environment
parser.add_argument("--environment", help="Specify the scan environment")

# Add an argument for --product-id
parser.add_argument("--product-id", help="Specify the product ID as a string")

# Add an argument for --tags
parser.add_argument("--tags", help="Specify semicolon-separated tags")

# Add an argument for --scan-type
parser.add_argument("--scan-type", help="Specify the scan type as a string")

# Add arguments for files to upload
parser.add_argument("files", nargs="*", help="Files to upload")

if __name__ == "__main__":
    args = parser.parse_args()

    SAFESCARF_API_TOKEN = args.api_key if args.api_key else os.environ.get('SAFESCARF_TOKEN', "")
    SAFESCARF_URL = args.api_url if args.api_url else os.environ.get('SAFESCARF_URL', "")
    SAFESCARF_ENGAGEMENT_ID = args.engagement_id if args.engagement_id else os.environ.get('ENGAGEMENTID', "")
    SAFESCARF_PRODUCTID = args.product_id if args.product_id else os.environ.get('SAFESCARF_PRODUCTID', "")
    SAFESCARF_SCAN_ENVIRONMENT = args.environment if args.environment else os.environ.get('SAFESCARF_SCAN_ENVIRONMENT', "")
    SAFESCARF_WORKFLOW = args.workflow if args.workflow else os.environ.get('SAFESCARF_WORKFLOW', "")
    SAFESCARF_SCAN_TYPE = args.scan_type if args.scan_type else os.environ.get('SAFESCARF_SCAN_TYPE', "")

    # verify that given engagement id is accessible
    if int(SAFESCARF_ENGAGEMENT_ID) > 0:
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
