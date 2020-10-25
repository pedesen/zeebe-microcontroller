"""
This device connects via WiFi and subscribes to the MQTT channel zeebe/job.
Whenever a message arrives, it publishes an MQTT message to the channel
zeebe/grpc/publishMessage containing the current temperature as a variable.
"""

import network 
from machine import ADC
import time
import ujson
from umqtt.simple import MQTTClient

WIFI_SSID = <your-ssid>
WIFI_PSK = <your-psk>
MQTT_HOST = <your-mqtt-host>
MQTT_PORT = 1883

adc = ADC(0)

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PSK) 
        while not wlan.isconnected():
            pass
    print('WiFi connected:', wlan.ifconfig()[0])

def on_message(topic, msg):
    variables = ujson.loads(str(msg.decode('utf-8')))['variables']
    processId = ujson.loads(variables)['processId']

    payload = {
        'name': 'Temperature',
        'correlationKey': processId,
        'variables': { 'temperature': adc.read() / 10 }
    }
            
    client.publish(b'zeebe/grpc/publishMessage', ujson.dumps(payload))

wifi_connect()

client = MQTTClient('Micropython ESP8266', MQTT_HOST, port=MQTT_PORT) 
client.set_callback(on_message)
client.connect()
client.subscribe(topic='zeebe/job')

while True:
    if True:
        # Blocking wait for message
        client.wait_msg()
    else:
        # Non-blocking wait for message
        client.check_msg()
        # Then need to sleep to avoid 100% CPU usage (in a real
        # app other useful actions would be performed instead)
        time.sleep(1)

client.disconnect()
