#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import logging
import argparse


def on_message(message):
    print('Received a new message: ')
    print(message.payload)
    print('from topic: ')
    print(message.topic)
    print('--------------\n\n')


def callback(client, userdata, message):
    print('Received a new message: ')
    print(message.payload)
    print('from topic: ')
    print(message.topic)
    print('--------------\n\n')


def suback_callback(mid, data):
    print('Received SUBACK packet id: ')
    print(mid)
    print('Granted QoS: ')
    print(data)
    print('++++++++++++++\n\n')


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', action='store', dest='endpoint', help='Targeted endpoint')
parser.add_argument('-i', '--client-id', action='store', dest='client_id', help='Targeted client id')
parser.add_argument('-t', '--topic', action='store', dest='topic', help='Targeted topic')
parser.add_argument('-r', '--root-ca', action='store', dest='root_ca', help='Root CA')
parser.add_argument('-c', '--certificate', action='store', dest='certificate', help='Certificate')
parser.add_argument('-p', '--private', action='store', dest='private', help='Private')

args = parser.parse_args()

logger = logging.getLogger('AWSIoTPythonSDK.core')
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

mqtt = AWSIoTMQTTClient(args.client_id)

mqtt.configureEndpoint(args.endpoint, 8883)
mqtt.configureCredentials(args.root_ca, args.private, args.certificate)
mqtt.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
mqtt.configureDrainingFrequency(2)  # Draining: 2 Hz
mqtt.configureConnectDisconnectTimeout(10)  # 10 sec
mqtt.configureMQTTOperationTimeout(5)  # 5 sec
#mqtt.onMessage = on_message
mqtt.connect()

mqtt.subscribe(args.topic, 1, callback)
#mqtt.subscribeAsync(args.topic, 1, ackCallback=suback_callback)
time.sleep(2)

while True:
    time.sleep(1)
