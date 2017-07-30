# PubNub imports
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# import midi library for receiving and sending midi data
import mido

# import deepcopy capabilities
import copy

counter = 0
threshold = 5

# Verbose printing if DEBUG is true
DEBUG = True

#sensor min max
sensor_min = -0.5
sensor_max = 0.5

#midi min max
midi_min = 0
midi_max = 127

# ===================================================

y_buffer = []
# Define Channel name
channel_name = 'sensor_data'

# Standard PubNub configuration under V4 API
pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-ff1da703-9b2a-41df-bdd4-96e21bbfb0b8'
pnconfig.subscribe_key = 'sub-c-d1024ca8-74bb-11e7-8153-0619f8945a4f'

pubnub = PubNub(pnconfig)

# Define the output port
output_IAC = mido.open_output('IAC Driver Bus 1')
#output_twister = mido.open_output('Midi Fighter Twister')

def scaleValuesToMidi(OldMin,OldMax,NewMin,NewMax,OldValue):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue

# Define a callback for publishing a message onto the stream
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
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

        try:
            if DEBUG:
                print ("Received: ", message.message)
            payload = message.message # assign message contents to variable "payload" (avoids confusion with mido.Message convention)

            x_midi = int(scaleValuesToMidi(sensor_min,sensor_max,midi_min,midi_max,payload['x']))
            y_midi = int(scaleValuesToMidi(sensor_min,sensor_max,midi_min,midi_max,payload['y']))

            if DEBUG:
                print(x_midi, y_midi)


            output_IAC.send(mido.Message('control_change',channel=0,control=12,value=x_midi))
            output_IAC.send(mido.Message('control_change',channel=0,control=13,value=y_midi))

        except Exception:
            print ("there was no valid key in the PubNub message")

# Add a listener to PubNub object with callback function defined above
pubnub.add_listener(MySubscribeCallback())
# Subscribe to the PubNub channel
pubnub.subscribe().channels(channel_name).execute()
#
