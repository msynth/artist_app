import mido
import copy

print("input names: ")
print(mido.get_input_names())
print("output names: ")
print(mido.get_output_names())

port = mido.open_output('USB MIDI Device')


with mido.open_input('USB MIDI Device') as inport:
    for msg in inport:
        #print(msg)
        new_msg = copy.copy(msg)  # Immutable mutation
        new_msg2 = copy.copy(msg)  # Immutable mutation
        new_msg.control = new_msg.control + 1
        new_msg2.control = new_msg2.control + 2
        port.send(new_msg)
        port.send(new_msg2)
