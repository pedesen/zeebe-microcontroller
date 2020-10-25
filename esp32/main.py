'''
This device connects via WiFi and publishes a message to the MQTT channel
zeebe/grpc/createWorkflowInstance, whenever an attached button is pressed.
'''

import network
from umqtt.simple import MQTTClient 
from machine import Pin, ADC
import time
import ujson

WIFI_SSID = <your-ssid>
WIFI_PSK = <your-psk>
MQTT_HOST = <your-mqtt-host>
MQTT_PORT = 1883
BPMN_PROCESS_ID = 'ExampleWorkflow'

button = Pin(22, Pin.IN, Pin.PULL_UP)
adc = ADC(Pin(32))

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PSK) 
        while not wlan.isconnected():
            pass
    print('WiFi connected:', wlan.ifconfig()[0])

wifi_connect()
client = MQTTClient('Micropython ESP32', MQTT_HOST, port=MQTT_PORT) 
client.connect()

while True:
    first = button.value()
    time.sleep(0.01)
    second = button.value()
    if first and not second:
        # if a button was pressed
        print('create workflow instance')
        client.publish(b'zeebe/grpc/createWorkflowInstance', ujson.dumps({
            'bpmnProcessId': BPMN_PROCESS_ID,
        }))
