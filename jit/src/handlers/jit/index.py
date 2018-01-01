import boto3

from jit import Jit

iot = boto3.client('iot')


def handler(event, context):
    print(event)
    jit = Jit(event, context, iot)
    jit.main()
