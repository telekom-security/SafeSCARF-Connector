# Use an official Python runtime as a parent image
FROM python:3-alpine

# Set environment variables
ENV SAFESCARF_ENGAGEMENT_PERIOD=7 \
    TODAY="" \
    ENDDAY="" \
    CI_PIPELINE_ID="" \
    CI_COMMIT_DESCRIPTION="Commit description" \
    CI_PROJECT_URL="https://gitlab.com/mygroup/myproject" \
    SAFESCARF_ENGAGEMENT_THREAT_MODEL="true" \
    SAFESCARF_ENGAGEMENT_API_TEST="true" \
    SAFESCARF_ENGAGEMENT_PEN_TEST="true" \
    SAFESCARF_ENGAGEMENT_CHECK_LIST="true" \
    SAFESCARF_ENGAGEMENT_STATUS="Not Started" \
    SAFESCARF_ENGAGEMENT_DEDUPLICATION_ON_ENGAGEMENT="false" \
    SAFESCARF_ENGAGEMENT_BUILD_SERVER="null" \
    SAFESCARF_ENGAGEMENT_SOURCE_CODE_MANAGEMENT_SERVER="null" \
    SAFESCARF_ENGAGEMENT_ORCHESTRATION_ENGINE="null" \
    SAFESCARF_SCAN_MINIMUM_SEVERITY="Info" \
    SAFESCARF_SCAN_ACTIVE="true" \
    SAFESCARF_SCAN_VERIFIED="true" \
    SAFESCARF_SCAN_TYPE="type" \
    SAFESCARF_SCAN_CLOSE_OLD_FINDINGS="true" \
    SAFESCARF_SCAN_PUSH_TO_JIRA="false" \
    SAFESCARF_SCAN_ENVIRONMENT="Default" \
    SAFESCARF_API_TOKEN="" \
    SAFESCARF_URL="" \
    SAFESCARF_ENGAGEMENT_ID="" \
    SAFESCARF_WORKFLOW=""

# Install any dependencies your script needs
# For example, if you require additional Python packages, add them here.
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy your Python script into the container
COPY safescarf-connector.py /app/safescarf-connector.py

# Set the working directory to /app
WORKDIR /app

# Run your script when the container launches
CMD ["python", "safescarf-connector.py"]
