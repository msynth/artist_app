# PubNub imports
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# import midi library for receiving and sending midi data
import mido

# import deepcopy capabilities
import copy

# Query connected input and output devices
print("input names: ")
print(mido.get_input_names())
print("output names: ")
print(mido.get_output_names())

# Verbose printing if DEBUG is true
DEBUG = True

# ===================================================

# Define Channel name
channel_name = 'accel_data'

# Standard PubNub configuration under V4 API
pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-ff1da703-9b2a-41df-bdd4-96e21bbfb0b8'
pnconfig.subscribe_key = 'sub-c-d1024ca8-74bb-11e7-8153-0619f8945a4f'

pubnub = PubNub(pnconfig)

# Define the output port
output_IAC = mido.open_output('IAC Driver Bus 1')
output_twister = mido.open_output('USB MIDI Device')

def scaleValuesToMidi(OldMin,OldMax,NewMin,NewMax):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue

# Define a callback for publishing a message onto the stream
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        print ("entered status.is_error loop")
        #pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

### MySubscribeCallback class
class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            pubnub.publish().channel(channel_name).message("An audience member has connected to the stream!").async(my_publish_callback)

    def message(self, pubnub, message):
        print ("Received: ", message.message)

        try:

            payload = message.message # assign message contents to variable "payload" (avoids confusion with mido.Message convention)

            output_IAC.send(mido.Message(payload['type'],channel=payload['channel'],control=payload['control'],value=payload['value']))

        except Exception:
            print ("there was no valid key in the PubNub message")

# Add a listener to PubNub object with callback function defined above
pubnub.add_listener(MySubscribeCallback())
# Subscribe to the PubNub channel
pubnub.subscribe().channels(channel_name).execute()
#
