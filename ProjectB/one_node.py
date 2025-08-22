from pylsl import resolve_stream, StreamInlet
import numpy as np
import mido
import time

# === CONFIG ===
CHANNEL = 9            # EEG channel to use (0-indexed)
NOTE_RANGE = (40, 80)  # MIDI note range (E2 to G5)

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

# Helper: map EEG voltage to MIDI note
def voltage_to_note(v, vmin=-100, vmax=100):
    v = np.clip(v, vmin, vmax)
    return int(np.interp(v, [vmin, vmax], NOTE_RANGE))

while True:
    try:
        # Get a sample from LSL
        sample, timestamp = inlet.pull_sample()
        eeg_value = sample[CHANNEL]

        # Map EEG value to MIDI note
        note = voltage_to_note(eeg_value)

        # Send MIDI note on & off
        msg_on = mido.Message('note_on', note=note, velocity=64)
        msg_off = mido.Message('note_off', note=note)

        outport.send(msg_on)
        print(f"🎵 Playing note: {note} (EEG value: {eeg_value:.2f})")
        time.sleep(0.1)
        outport.send(msg_off)

    except KeyboardInterrupt:
        print("\n Stopped by user.")
        break
