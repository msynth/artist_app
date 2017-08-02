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
sensor_channel = 'sensor_data'
artist_channel = 'artist_mode'
button_channel = 'update_samples'

# Standard PubNub configuration under V4 API
pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-ff1da703-9b2a-41df-bdd4-96e21bbfb0b8'
pnconfig.subscribe_key = 'sub-c-d1024ca8-74bb-11e7-8153-0619f8945a4f'

pubnub_sensor = PubNub(pnconfig)
pubnub_artist = PubNub(pnconfig)
pubnub_buttons = PubNub(pnconfig)

# Define the output port
output_IAC = mido.open_output('IAC Driver Bus 1')
#output_twister = mido.open_output('Midi Fighter Twister')

print("Successfully subscribed to PubNub...")

def publish_callback(result, status):
    print("Pushed strings to PubNub...")

    # Handle PNPublishResult and PNStatus
pubnub_buttons.publish().channel(button_channel).message(['Pub', 'Nub', 'Outsidelands','Horn','Drop']).async(publish_callback)


def scaleValuesToMidi(OldMin,OldMax,NewMin,NewMax,OldValue):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue

### MySubscribeCallback class
class MySubscribeCallbackSensor(SubscribeCallback):
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

### MySubscribeCallback class
class MySubscribeCallbackArtist(SubscribeCallback):
    def message(self, pubnub, message):

        try:
            if DEBUG:
                print ("Received: ", message.message)

            payload = message.message # assign message contents to variable "payload" (avoids confusion with mido.Message convention)

            if payload == 'bassDrop0':
                output_IAC.send(mido.Message('note_on',note=48,velocity=127))
            elif payload == 'bassDrop1':
                output_IAC.send(mido.Message('note_on',note=49,velocity=127))
            elif payload == 'bassDrop2':
                output_IAC.send(mido.Message('note_on',note=50,velocity=127))
            elif payload == 'bassDrop3':
                output_IAC.send(mido.Message('note_on',note=51,velocity=127))
            elif payload == 'bassDrop4':
                output_IAC.send(mido.Message('note_on',note=52,velocity=127))

        except Exception:
            print ("there was no valid key in the PubNub message")

# Add a listener to PubNub object with callback function defined above
pubnub_sensor.add_listener(MySubscribeCallbackSensor())
# Subscribe to the PubNub channel
pubnub_sensor.subscribe().channels(sensor_channel).execute()

# Add a listener to PubNub object with callback function defined above
pubnub_artist.add_listener(MySubscribeCallbackArtist())
# Subscribe to the PubNub channel
pubnub_artist.subscribe().channels(artist_channel).execute()
#
#
