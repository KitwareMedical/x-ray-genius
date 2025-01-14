#!/bin/bash

set -euo pipefail

# Run database migrations
./manage.py migrate

# Load sample data fixture
./manage.py loaddata sampledata

# Restart the EC2 worker so it pulls in the new code

pip install awscli

EC2_WORKER_NAME_PREFIX="xray-genius-worker-*"

INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=${EC2_WORKER_NAME_PREFIX}" \
  --query "Reservations[].Instances[?State.Name==\`running\`].InstanceId" \
  --output text)

if [ -z "$INSTANCE_ID" ]; then
  echo "No running EC2 instances found matching the prefix '${EC2_WORKER_NAME_PREFIX}'." >&2
  exit 1
fi

echo "Rebooting instance(s): $INSTANCE_ID"
aws ec2 reboot-instances --instance-ids $INSTANCE_ID
echo "Done."
