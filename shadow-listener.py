#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
import time
import logging
import argparse


# Custom Shadow callback
def shadow_callback_delta(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print(responseStatus)
    payload_dict = json.loads(payload)
    print('++++++++DELTA++++++++++')
    print('welcome: {0}'.format(payload_dict['state'].get('welcome')))
    print('message: {0}'.format(payload_dict['state'].get('message')))
    print('version: {0}'.format(payload_dict.get('version')))
    print('+++++++++++++++++++++++\n\n')


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

# Listen on deltas
shadow_handler.shadowRegisterDeltaCallback(shadow_callback_delta)

# Loop forever
while True:
    time.sleep(1)
