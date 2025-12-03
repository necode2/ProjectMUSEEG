from pylsl import resolve_stream, StreamInlet
import numpy as np
import mido
import time

# === CONFIG ===
CHANNEL1 = 0            # EEG channel to use (0-indexed)
CHANNEL2 = 1            # EEG channel to use (0-indexed)
CHANNEL3 = 2            # EEG channel to use (0-indexed)
CHANNEL4 = 3            # EEG channel to use (0-indexed)
CHANNEL5 = 4            # EEG channel to use (0-indexed)
CHANNEL6 = 5            # EEG channel to use (0-indexed)
CHANNEL7 = 6            # EEG channel to use (0-indexed)
CHANNEL8 = 7            # EEG channel to use (0-indexed)
CHANNEL9 = 8            # EEG channel to use (0-indexed)
CHANNEL10 = 9           # EEG channel to use (0-indexed)
CHANNEL11 = 10          # EEG channel to use (0-indexed)        
CHANNEL12 = 11          # EEG channel to use (0-indexed)
CHANNEL13 = 12          # EEG channel to use (0-indexed)
CHANNEL14 = 13          # EEG channel to use (0-indexed)
CHANNEL15 = 14          # EEG channel to use (0-indexed)
CHANNEL16 = 15          # EEG channel to use (0-indexed)
# Note ranges
NOTE_RANGE1 = (0, 40) # MIDI note range (C0 to E2)
NOTE_RANGE2 = (40, 80)  # MIDI note range (E2 to G5)
NOTE_RANGE3 = (80, 120)  # MIDI note range (G5 to C6)

# === OPEN MIDI OUTPUT ===
print("Available MIDI outputs:")
print(mido.get_output_names())
outport = mido.open_output('GarageBand Virtual In')
print("connected to MIDI output: GarageBand Virtual In")

# === CONNECT TO LSL STREAM ===
print("Looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])
print("Connected to LSL EEG stream.")

# Helpers: map EEG voltage to MIDI note
"""
reasoning for vmin and vmax:
- vmin: -100 is a common lower bound for EEG signals, representing the lowest voltage change
- vmax: 100 is a common upper bound for EEG signals, representing the highest voltage
- These ranges can be adjusted based on the specific EEG data characteristics and the desired MIDI note mapping
- The ranges are chosen to ensure that the EEG signal values are effectively mapped to the MIDI note

np.interp is used to linearly map the EEG voltage values to the MIDI note ranges defined above.
"""

# bass
def voltage_to_note1(v, vmin=-100, vmax=100): 
    v = np.clip(v, vmin, vmax)
    return int(np.interp(v, [vmin, vmax], NOTE_RANGE1))
# mid
def voltage_to_note2(v, vmin=-100, vmax=100):
    v = np.clip(v, vmin, vmax)
    return int(np.interp(v, [vmin, vmax], NOTE_RANGE2))
# treble
def voltage_to_note3(v, vmin=-100, vmax=100):
    v = np.clip(v, vmin, vmax)
    return int(np.interp(v, [vmin, vmax], NOTE_RANGE3))

while True:
    try:
        # Get a sample from LSL
        sample, timestamp = inlet.pull_sample()
        eeg_value1 = sample[CHANNEL1]
        eeg_value2 = sample[CHANNEL2]
        eeg_value3 = sample[CHANNEL3]
        eeg_value4 = sample[CHANNEL4]
        eeg_value5 = sample[CHANNEL5]
        eeg_value6 = sample[CHANNEL6]
        eeg_value7 = sample[CHANNEL7]
        eeg_value8 = sample[CHANNEL8]
        eeg_value9 = sample[CHANNEL9]
        eeg_value10 = sample[CHANNEL10]
        eeg_value11 = sample[CHANNEL11]
        eeg_value12 = sample[CHANNEL12]
        eeg_value13 = sample[CHANNEL13]
        eeg_value14 = sample[CHANNEL14]
        eeg_value15 = sample[CHANNEL15]
        eeg_value16 = sample[CHANNEL16]

        # Map EEG value to MIDI note (play around with voltage ranges!)
        note1 = voltage_to_note1(eeg_value1)
        note2 = voltage_to_note2(eeg_value2)
        note3 = voltage_to_note3(eeg_value3)
        note4 = voltage_to_note2(eeg_value4)
        note5 = voltage_to_note3(eeg_value5)
        note6 = voltage_to_note1(eeg_value6)
        note7 = voltage_to_note2(eeg_value7)
        note8 = voltage_to_note3(eeg_value8)
        note9 = voltage_to_note2(eeg_value9)
        note10 = voltage_to_note3(eeg_value10)
        note11 = voltage_to_note2(eeg_value11)
        note12 = voltage_to_note3(eeg_value12)
        note13 = voltage_to_note2(eeg_value13)
        note14 = voltage_to_note3(eeg_value14)
        note15 = voltage_to_note2(eeg_value15)
        note16 = voltage_to_note3(eeg_value16)

        # Send MIDI note on & off
        msg_on1 = mido.Message('note_on', note=note1, velocity=64)
        msg_on2 = mido.Message('note_on', note=note2, velocity=64)
        msg_on3 = mido.Message('note_on', note=note3, velocity=64)
        msg_on4 = mido.Message('note_on', note=note4, velocity=64)
        msg_on5 = mido.Message('note_on', note=note5, velocity=64)
        msg_on6 = mido.Message('note_on', note=note6, velocity=64)
        msg_on7 = mido.Message('note_on', note=note7, velocity=64)
        msg_on8 = mido.Message('note_on', note=note8, velocity=64)
        msg_on9 = mido.Message('note_on', note=note9, velocity=64)
        msg_on10 = mido.Message('note_on', note=note10, velocity=64)
        msg_on11 = mido.Message('note_on', note=note11, velocity=64)
        msg_on12 = mido.Message('note_on', note=note12, velocity=64)
        msg_on13 = mido.Message('note_on', note=note13, velocity=64)
        msg_on14 = mido.Message('note_on', note=note14, velocity=64)
        msg_on15 = mido.Message('note_on', note=note15, velocity=64)
        msg_on16 = mido.Message('note_on', note=note16, velocity=64)

        msg_off1 = mido.Message('note_off', note=note1)
        msg_off2 = mido.Message('note_off', note=note2)
        msg_off3 = mido.Message('note_off', note=note3)
        msg_off4 = mido.Message('note_off', note=note4)
        msg_off5 = mido.Message('note_off', note=note5)
        msg_off6 = mido.Message('note_off', note=note6)
        msg_off7 = mido.Message('note_off', note=note7)
        msg_off8 = mido.Message('note_off', note=note8)
        msg_off9 = mido.Message('note_off', note=note9)
        msg_off10 = mido.Message('note_off', note=note10)
        msg_off11 = mido.Message('note_off', note=note11)
        msg_off12 = mido.Message('note_off', note=note12)
        msg_off13 = mido.Message('note_off', note=note13)
        msg_off14 = mido.Message('note_off', note=note14)
        msg_off15 = mido.Message('note_off', note=note15)
        msg_off16 = mido.Message('note_off', note=note16)

        # Send MIDI messages
        print(f"🎵 Playing notes: {note1}, {note2}, {note3}, {note4}, {note5}, {note6}, {note7}, {note8}, {note9}, {note10}, {note11}, {note12}, {note13}, {note14}, {note15}, {note16}")
        outport.send(msg_on1)
        outport.send(msg_on2)
        outport.send(msg_on3)
        outport.send(msg_on4)
        outport.send(msg_on5)
        outport.send(msg_on6)
        outport.send(msg_on7)
        outport.send(msg_on8)
        outport.send(msg_on9)
        outport.send(msg_on10)
        outport.send(msg_on11)
        outport.send(msg_on12)
        outport.send(msg_on13)
        outport.send(msg_on14)
        outport.send(msg_on15)
        outport.send(msg_on16)

        time.sleep(0.1)

        outport.send(msg_off1)
        outport.send(msg_off2)
        outport.send(msg_off3)
        outport.send(msg_off4)
        outport.send(msg_off5)
        outport.send(msg_off6)
        outport.send(msg_off7)
        outport.send(msg_off8)
        outport.send(msg_off9)
        outport.send(msg_off10)
        outport.send(msg_off11)
        outport.send(msg_off12)
        outport.send(msg_off13)
        outport.send(msg_off14)
        outport.send(msg_off15)
        outport.send(msg_off16)

    except KeyboardInterrupt:
        print("\n Stopped by user.")
        break
