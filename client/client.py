import json
import socket
from threading import Event
from time import sleep
from typing import Optional, Any
import requests
import paho.mqtt.client as mqtt

# Feel free to add more libraries (e.g.: The REST Client library)

mqtt_client: Optional[mqtt.Client] = None

mqtt_connection_event = Event()

secret = -1


def send_secret_rest(secret_value: int):
    # Add the logic to send this secret value to the REST server.
    # We want to send a JSON structure to the endpoint `/secret_number`, using
    # a POST method.
    #
    # Assuming secret_value = 50, then the request will contain the following
    # body: {"value": 50}

    resp = requests.post(
        'http://server/secret_number', json={"value": secret_value}
    )
    return resp.status_code == 200 and resp.text == 'OK'


def on_mqtt_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    receive_secret()
    # mqtt_connection_event.set()


def on_mqtt_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
    # Implement the logic to parse the received secret (we receive a json, but
    # we are interested just on the value) and send this value to the REST
    # server... or maybe the sending to REST should be done somewhere else...
    # do you have any idea why?
    data = json.loads(msg.payload)
    result = send_secret_rest(secret_value=data['value'])
    resp = requests.get('http://server/secret_correct')
    if result and resp.text == 'YES':
        mqtt_connection_event.set()


def connect_mqtt() -> mqtt.Client:
    client = mqtt.Client(
        clean_session=True,
        protocol=mqtt.MQTTv311
    )
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    client.loop_start()
    client.connect('mqtt-broker', 1883)
    return client


def get_status():
    resp = requests.get('http://server/ready')
    msg = resp.text
    resp.raise_for_status()
    if msg != 'YES':
        raise ValueError('Server is Not Ready')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('mqtt-broker', 1883))
    if result != 0:
        raise ConnectionError("mqtt broker is not ready")
    sock.close()


def wait_for_server_ready():
    # Implement code to wait until the server is ready, it's up to you how
    # to do that. Our advice: Check the server source code and check if there
    # is anything useful that can help.
    # Hint: If you prefer, feel free to delete this method, use an external
    # tool and incorporate it in the Dockerfile
    while True:
        try:
            get_status()
            print('Server Is Ready')
            break
        except Exception as e:
            print(e)
        sleep(3)


def receive_secret():
    # We will receive the secret via MQTT to secret/number topic every second
    mqtt_client.subscribe('secret/number', 0)


def main():
    global mqtt_client

    wait_for_server_ready()

    mqtt_client = connect_mqtt()
    mqtt_connection_event.wait()

    # At this point, we have our MQTT connection established, now we need to:
    # 1. Subscribe to the MQTT topic: secret/number
    # 2. Parse the received message and extract the secret number
    # 3. Send this number via REST to the server, using a POST method on the
    # resource `/secret_number`, with a JSON body like: {"value": 50}
    # 4. (Extra) Check the REST resource `/secret_correct` to ensure it was
    # properly set
    # 5. Terminate the script, only after at least a value was sent


    try:
        mqtt_client.disconnect()
    except Exception:
        pass
    try:
        mqtt_client.loop_stop()
    except Exception:
        pass


if __name__ == '__main__':
    main()