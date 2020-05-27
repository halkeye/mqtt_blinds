import os
import time
import paho.mqtt.client as mqtt
from json import dumps

try:
    import RPi.GPIO as GPIO
except RuntimeError:

    class GPIO:
        HIGH = 0
        LOW = 0
        OUT = 0
        IN = 0
        BOARD = 0

        def setmode(*args):
            pass

        def setup(*args, **kwargs):
            pass

    print(
        "Error importing RPi.GPIO!  " +
        "This is probably because you need superuser privileges.  " +
        "You can achieve this by using 'sudo' to run your script")


PIN_BANK1_CHANNEL2 = 5
PIN_BANK1_CHANNEL1 = 7
PIN_BANK1_CLOSE = 11
PIN_BANK1_OPEN = 13

PIN_BANK2_CHANNEL2 = 37
PIN_BANK2_CHANNEL1 = 35
PIN_BANK2_CLOSE = 33
PIN_BANK2_OPEN = 31

CMD_OPEN = {
    "1": PIN_BANK1_OPEN,
    "2": PIN_BANK1_OPEN,
    "3": PIN_BANK1_OPEN,
    "4": PIN_BANK1_OPEN,

    "5": PIN_BANK2_OPEN,
    "6": PIN_BANK2_OPEN,
    "7": PIN_BANK2_OPEN,
    "8": PIN_BANK2_OPEN
}

CMD_CLOSE = {
    "1": PIN_BANK1_CLOSE,
    "2": PIN_BANK1_CLOSE,
    "3": PIN_BANK1_CLOSE,
    "4": PIN_BANK1_CLOSE,

    "5": PIN_BANK2_CLOSE,
    "6": PIN_BANK2_CLOSE,
    "7": PIN_BANK2_CLOSE,
    "8": PIN_BANK2_CLOSE
}

CMD_CHANNEL = {
    "1": [[PIN_BANK1_CHANNEL1, PIN_BANK1_CHANNEL2], [GPIO.HIGH, GPIO.HIGH]],
    "2": [[PIN_BANK1_CHANNEL1, PIN_BANK1_CHANNEL2], [GPIO.LOW, GPIO.HIGH]],
    "3": [[PIN_BANK1_CHANNEL1, PIN_BANK1_CHANNEL2], [GPIO.HIGH, GPIO.LOW]],
    "4": [[PIN_BANK1_CHANNEL1, PIN_BANK1_CHANNEL2], [GPIO.LOW, GPIO.LOW]],

    "5": [[PIN_BANK2_CHANNEL1, PIN_BANK2_CHANNEL2], [GPIO.HIGH, GPIO.HIGH]],
    "6": [[PIN_BANK2_CHANNEL1, PIN_BANK2_CHANNEL2], [GPIO.LOW, GPIO.HIGH]],
    "7": [[PIN_BANK2_CHANNEL1, PIN_BANK2_CHANNEL2], [GPIO.HIGH, GPIO.LOW]],
    "8": [[PIN_BANK2_CHANNEL1, PIN_BANK2_CHANNEL2], [GPIO.LOW, GPIO.LOW]]
}

INVERSE_CHANNELS = ["1", "2"]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/blinds/set/#")

    for key in CMD_OPEN:
        client.publish(
            "homeassistant/cover/blinds" + key + "/config",
            payload=dumps({
                'name': os.environ.get('BLINDS_NAME_' + key, 'blinds' + key),
                'device_class': 'shade',
                'unique_id': 'blinds_' + key,
                'command_topic': 'home/blinds/set/' + key
            }),
            retain=True
        )


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_BANK1_CHANNEL2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK1_CHANNEL1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK1_CLOSE, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK1_OPEN, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(PIN_BANK2_CHANNEL2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK2_CHANNEL1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK2_CLOSE, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_BANK2_OPEN, GPIO.OUT, initial=GPIO.LOW)

    channel = str(msg.topic.split("/")[-1])
    mode = msg.payload.decode('ascii').lower()

    if channel in INVERSE_CHANNELS:
        print("inversing")
        if mode == "open" or mode == "on":
            mode = "close"
        elif mode == "close" or mode == "off":
            mode = "open"

    print("Setting mode of " + mode)
    print("select channel %s" % channel)

    print(CMD_CHANNEL[channel][0], CMD_CHANNEL[channel][1])
    GPIO.output(CMD_CHANNEL[channel][0], CMD_CHANNEL[channel][1])

    # sleep after channel selection so it takes effect properly
    time.sleep(0.5)

    if mode == "close" or mode == "off":
        print(CMD_CLOSE[channel], GPIO.HIGH)
        GPIO.output(CMD_CLOSE[channel], GPIO.HIGH)
    elif mode == "open" or mode == "on":
        print(CMD_OPEN[channel], GPIO.HIGH)
        GPIO.output(CMD_OPEN[channel], GPIO.HIGH)
    else:
        print("not sure what to do with mode(" + mode + ") and channel(" + channel + ")")

    # sleep after command is issued so it has time to send/clear
    time.sleep(1)

    GPIO.cleanup()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print('client.connect(' + os.environ['MQTT_SERVER'] + ', ' + str(os.environ['MQTT_PORT']) + ', 60)')
client.connect(os.environ['MQTT_SERVER'], int(os.environ['MQTT_PORT']), 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
