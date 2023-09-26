# SafeSCARF API Connector
## Functionality

The SafeSCARF API Connector provides the following functionality:

1. **Create Engagements**: You can use this script to create engagements in
   SafeSCARF, making it easy to track and manage your security assessments for
   different CI/CD workflows.

1. **Upload Scan Results**: The script enables you to upload scan results (e.g.,
   security scans, vulnerability reports) to SafeSCARF, associating them with
   the relevant engagements.

1. **List Available Test Types**: You can fetch a list of available test types
   from the SafeSCARF API, which can be useful when specifying the scan type for
   your uploads.

## Parameters

Here are the parameters you can use when running the script:

| Parameter                | Description                                                                                                 | Mandatory |
|--------------------------|-------------------------------------------------------------------------------------------------------------|-----------|
| `command`                | Specifies the command to execute. Available options: `create-engagement`, `upload`, `help`, `test-types`.   | Yes       |
| `--workflow`             | Specifies the workflow type for creating engagements. Available options: `branch`, `pipeline`.              | No        |
| `--api-key`              | Specifies the SafeSCARF API key as a string.                                                                | No        |
| `--api-url`              | Specifies the custom SafeSCARF API URL as a string.                                                         | No        |
| `--engagement-id`        | Specifies the engagement ID as an integer.                                                                  | No        |
| `--environment`          | Specifies the scan environment.                                                                             | No        |
| `--product-id`           | Specifies the product ID as a string.                                                                       | No        |
| `--test-type`            | Specifies the scan type as a string.                                                                        | No        |
| `files`                  | Files to upload. (only for upload command)                                                                  | No        |

## Usage

### Create Engagement

To create an engagement, use the following command:

```bash
python safescarf-connector.py create-engagement --workflow [workflow_type]
```

Replace `[workflow_type]` with either `branch` or `pipeline` depending on your
CI/CD workflow.

### Upload Scan Results

To upload scan results, use the following command:

```bash
python safescarf-connector.py upload [file_paths]
```

Replace `[file_paths]` with the paths to the files you want to upload. Asterisk
like `file*.json` is allowed.

### List Available Test Types

To list available test types, use the following command:

```bash
python safescarf-connector.py test-types
```

### Help

To get help and see all available commands and options, use the following command:

```bash
python safescarf-connector.py help
```

## Example

Here's an example of how you can create an engagement and upload scan results using the script:

```bash
# Create an engagement for a branch workflow
python safescarf-connector.py create-engagement --workflow branch

# Upload scan results for a specific environment. Engagement ID from previous
# command is stored in an environmental variable.
python safescarf-connector.py upload /path/to/scan-results.json --environment staging
```

## Requirements

This script requires Python 3.x and the following Python packages:

* argparse
* os
* json
* requests
* glob
* datetime

Please make sure you have these packages installed or install them using pip
before running the script. A `requirements.txt` is provided.

```bash
python3 -m pip install -r requirements.txt
```

## Note

Before using the script, ensure you have the SafeSCARF API key and URL available
for authentication and API access.