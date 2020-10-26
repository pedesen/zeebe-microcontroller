# zeebe-microcontroller
This is a PoC that microcontrollers can be used with Zeebe

In this example one microcontroller (ESP32) creates a BPMN workflow instance on a physical button press.
A second microcontroller (ESP8266) acts as a job worker measuring and publishing the current temperature as message. The temperature is then available as variable in the workflow instance in Zeebe.

![Workflow](docs/workflow.png)

## zeebe-mqtt-bridge

The main ingredient is the [zeebe-mqtt-bridge](zeebe-mqtt-bridge/src/zeebe-mqtt-bridge.py) python script which serves the following purposes: 

* subscribe to Zeebe as job worker via GRPC
* publish jobs via MQTT
* subscribe to MQTT and listens for messages
* publish messages to Zeebe via GRPC

The script is based on https://gitlab.com/stephane.ludwig/zeebe_python_grpc by [Stéphane Ludwig](https://gitlab.com/stephane.ludwig).

![Setup](docs/setup.png)

## Why Microcontrollers?

ESP32 and ESP8266 microcontrollers by Espressif Systems are widely used in Internet of Things (IoT) projects. They have WiFi on board and a bunch of GPIO pins to connect sensors, buttons, LEDs or servo motors and more. There are different low cost development boards are available, while the microcontroller chip itself is even cheaper.

Please note that both microcontroller types could serve both purposes (button and temperature sensor), it's just a proof of concept, that both microcontrollers can be used to communicate with Zeebe via MQTT.

## Requirements

* a running Zeebe instance
* a running MQTT broker
* the following microcontrollers flashed with MicroPython:
    * ESP32 with attached button
    * ESP8266 with attached TMP36 temperature sensor

## Deploy example workflow to zeebe

```bash
zbctl --insecure deploy resources/example.bpmn
```

## Running zeebe-mqtt-bridge

```bash
cd zeebe-mqtt-bridge
python3 -m venv ./env
source env/bin/activate
pip install -r requirements.txt
python3 src/zeebe-mqtt-bridge
```

## ESP32 Microcontroller

The ESP32 needs to be flashed with MicroPython firmware (see https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) and a physical push button needs to be connected. In this example a [ESP32-DevKitC V4](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32/get-started-devkitc.html) is used, but the code should work with most ESP32 development boards.

Please add WiFi and MQTT credentials to [esp32/main.py](esp32/main.py) and upload the script to the microcontroller.

The ESP32 connects to WiFi and the MQTT broker. On each button press an MQTT message gets published to `/zeebe/grpc/createWorkflowInstance` to create a new workflow instance for `ExampleWorkflow` (see [example.bpmn](resources/example.bpmn)) deployed in Zeebe.  

![Setup](docs/esp32.png)

## ESP8266 Microcontroller

The ESP8266 needs to be flashed with MicroPython firmware (see https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html) and a TMP36 temperature sensor needs to be connected. In this example a [D1 mini development board](https://docs.wemos.cc/en/latest/d1/d1_mini.html) is used, but the code might work with other ESP8266 development boards with small adjustments. 

Please add WiFi and MQTT credentials to [esp8266/main.py](esp8266/main.py) and upload the script to the microcontroller.

The ESP8266 connects to WiFi and the MQTT broker. It subscribes to `zeebe/job` MQTT topic. On every arriving MQTT message for this topic the temperature is measured. Then an MQTT message is published to `zeebe/grpc/publishMessage` containing the temperature as variable.

![Workflow](docs/esp8266.png)


## Resources

### Tutorials for MicroPython on ESP32, ESP8266 Microcontrollers
https://docs.micropython.org/en/latest/esp32/tutorial/intro.html  
https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html

### Zeebe docs
https://docs.zeebe.io/  
https://gitlab.com/stephane.ludwig/zeebe_python_grpc

### Zeebe modeler
https://github.com/zeebe-io/zeebe-modeler

### Hardware
D1 mini development board: https://docs.wemos.cc/en/latest/d1/d1_mini.html  
ESP32-DevKitC V4: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32/get-started-devkitc.html  
TMP36 Temperature Sensor: https://learn.adafruit.com/tmp36-temperature-sensor

