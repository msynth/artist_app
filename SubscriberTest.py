'''
========== HACKATHON DEMO ============
Lamtharn (Hanoi) Hantrakul
11 May 2017

hackSubscribe.py is intended to be used in conjunction with hackPublish.py

This code receives messages from the PubNub network, parses the information
and sends MIDI commands to Ableton Live via an IAC Driver and lighting commands
to a second MF3D.
======================================
'''

# PubNub imports
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
# MIDI and Music-related imports
import mido
# Time imports for capturing roundtrip delay
from datetime import datetime

# Verbose printing if DEBUG is true
DEBUG = True
# Using PubNub Laptop?
Use_PubNub_laptop = False

# Define Channel name
channel_name = 'channel_1'

# Standard PubNub configuration under V4 API
pnconfig = PNConfiguration()

pnconfig.publish_key = 'pub-c-a462739c-eb05-4624-b92c-6f3f71b7d667'
pnconfig.subscribe_key = 'sub-c-243047a8-3511-11e7-9d73-0619f8945a4f'

pubnub = PubNub(pnconfig)

# Define the IAC Driver name
if Use_PubNub_laptop:
    IAC_driver_name = 'IAC Driver Bus 1'  # On PubNub laptop the driver is called 'IAC Driver Bus 1'
else:
    IAC_driver_name = 'IAC Driver IAC Bus 1'  # On personal laptop the driver is called "IAC Driver IAC Bus 1"

# Open midi port to send MIDI data
output_IAC = mido.open_output(IAC_driver_name)  # For IAC communication
output_MF3D = mido.open_output('Midi Fighter 3D')  # For sending light commands to MF3D

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
            payload = message.message  # assign message contents to variable "payload" (avoids confusion with mido.Message convention)

            if payload['type'] == 'note_on':
                if payload['trapify'] == 1:
                    color = 14  # Red RGB
                else:
                    color = 127  # Blue RGB

                # Send message through midi ports using values defined from payload
                output_IAC.send(mido.Message('note_on',note=payload['note'],velocity=127))
                output_MF3D.send(mido.Message('note_on',note=payload['note'],velocity=color))

            elif message.message['type'] == 'note_off':
                # Send message through midi ports using values defined from payload
                output_IAC.send(mido.Message('note_off',note=payload['note'],velocity=127))
                output_MF3D.send(mido.Message('note_off',note=payload['note'],velocity=127))

        except Exception:
            print ("there was no valid key in the PubNub message")

# Add a listener to PubNub object with callback function defined above
pubnub.add_listener(MySubscribeCallback())
# Subscribe to the PubNub channel
pubnub.subscribe().channels(channel_name).execute()
