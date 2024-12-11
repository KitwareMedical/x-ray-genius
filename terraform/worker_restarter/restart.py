from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import boto3
import sentry_sdk

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events.api_gateway_proxy import APIGatewayProxyEventV2
    from types_boto3_ec2.literals import InstanceStateNameType

sentry_sdk.init()

logger = logging.getLogger(__name__)

EC2_WORKER_NAME_PREFIX = 'xray-genius-worker-'


def handler(event: APIGatewayProxyEventV2, context: Context):
    ec2 = boto3.client('ec2')

    # Request must be a POST request with the proper credentials
    if event['requestContext']['http']['method'] != 'POST' or event['headers']['authorization'] != 'Bearer ' + os.environ['WEBHOOK_TOKEN']:
        return {
            'statusCode': 404,
        }

    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Name', 'Values': [EC2_WORKER_NAME_PREFIX + '*']}]
    )

    print(instances)
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            state: InstanceStateNameType = instance['State']['Name']
            if state != 'running':
                err_msg = f'Instance {instance["InstanceId"]} is in unexpected state "{state}"'
                print(err_msg)
                sentry_sdk.capture_message(err_msg, level='critical')
                continue

            print(f'Rebooting instance {instance['InstanceId']}')
            resp = ec2.reboot_instances(InstanceIds=[instance['InstanceId']])
            print(resp)

    return {
        'statusCode': 200,
    }
