# ruff: noqa: T201
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
    if (
        event['requestContext']['http']['method'] != 'POST'
        or event['headers']['authorization'] != 'Bearer ' + os.environ['WEBHOOK_TOKEN']
    ):
        return {
            'statusCode': 404,
        }

    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:Name', 'Values': [EC2_WORKER_NAME_PREFIX + '*']}]
    )

    print(instances)
    instances_to_reboot = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            state: InstanceStateNameType = instance['State']['Name']
            if state == 'running':
                print(f'Rebooting instance {instance["InstanceId"]}')
                instances_to_reboot.append(instance['InstanceId'])

    if len(instances_to_reboot) > 0:
        resp = ec2.reboot_instances(InstanceIds=instances_to_reboot)
        print(resp)
    else:
        logger.critical('No running instances found!')
        sentry_sdk.capture_message('No running instances found!')

    return {
        'statusCode': 200,
    }
