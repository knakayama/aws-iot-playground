#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
import time
import logging
import argparse


def shadow_callback_update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == 'timeout':
        print('Update request {0} time out!'.format(token))
    if responseStatus == 'accepted':
        payload_dict = json.loads(payload)
        print('~~~~~~~~~~~~~~~~~~~~~~~')
        print('Update request with token: {0} accepted!'.format(token))
        print('welcome: {0}'.format(payload_dict['state']['desired'].get('welcome')))
        print('message: {0}'.format(payload_dict['state']['desired'].get('message')))
        print('version: {0}'.format(payload_dict.get('version')))
        print('~~~~~~~~~~~~~~~~~~~~~~~\n\n')
    if responseStatus == 'rejected':
        print('Update request {0} rejected!'.format(token))


def shadow_callback_delete(payload, responseStatus, token):
    if responseStatus == 'timeout':
        print('Delete request {0} timeout'.format(token))
    if responseStatus == 'accepted':
        print('~~~~~~~~~~~~~~~~~~~~~~~')
        print('Delete request with token: {0} accepted!'.format(token))
        print('~~~~~~~~~~~~~~~~~~~~~~~\n\n')
    if responseStatus == 'rejected':
        print('Delete request {0} rejected!'.format(token))


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', action='store', dest='endpoint', help='Targeted endpoint')
parser.add_argument('-i', '--client-id', action='store', dest='client_id', help='Targeted client id')
parser.add_argument('-t', '--thing-name', action='store', dest='thing_name', help='Thing name')
parser.add_argument('-r', '--root-ca', action='store', dest='root_ca', help='Root CA')
parser.add_argument('-c', '--certificate', action='store', dest='certificate', help='Certificate')
parser.add_argument('-p', '--private', action='store', dest='private', help='Private')
args = parser.parse_args()

# Configure logging
logger = logging.getLogger('AWSIoTPythonSDK.core')
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

shadow = AWSIoTMQTTShadowClient(args.client_id)
shadow.configureEndpoint(args.endpoint, 8883)
shadow.configureCredentials(args.root_ca, args.private, args.certificate)
# AWSIoTMQTTShadowClient configuration
shadow.configureAutoReconnectBackoffTime(1, 32, 20)
shadow.configureConnectDisconnectTimeout(10)  # 10 sec
shadow.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
shadow.connect()

# Create a deviceShadow with persistent subscription
shadow_handler = shadow.createShadowHandlerWithName(args.thing_name, True)

# Delete shadow JSON doc
shadow_handler.shadowDelete(shadow_callback_delete, 5)

# Update shadow in a loop
loop_count = 0
while True:
    payload = {
        'state': {
            'desired': {
                'welcome': 'aws-iot-{0}'.format(loop_count),
                'message': loop_count
            }
        }
    }
    shadow_handler.shadowUpdate(json.dumps(payload), shadow_callback_update, 5)
    loop_count += 1
    time.sleep(5)
