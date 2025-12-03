from music21 import stream, note, chord, key, tempo, meter
import numpy as np

# === CONFIG ===
SEED_NOTE = 60        # Start note (C4)
CHUNK_SIZE = 16       # Notes per section
SECTION_COUNT = 4     # Number of sections
TIME_SIGNATURE = '4/4'
TEMPO_BPM = 90
KEYS = ['C', 'G', 'A', 'F']  # Key progression
PASSING_NOTE_PROB = 0.3      # chance to add a passing note
ARPEGGIO_PROB = 0.4          # chance to arpeggiate chord

# Simulate EEG-derived notes
def simulate_eeg_notes(seed, count):
    return [seed + np.random.choice([-2, -1, 0, 1, 2]) for _ in range(count)]

# Generate motifs with small leaps
def generate_motif(seed_note, scale_notes, length=8):
    motif = []
    current_note = seed_note
    for _ in range(length):
        step = np.random.choice([-2, -1, 1, 2])
        idx = (scale_notes.index(current_note) + step) % len(scale_notes)
        new_note = scale_notes[idx]
        motif.append(new_note)
        current_note = new_note
    return motif

# Determine note length (staccato/legato variation)
def note_length_with_style():
    r = np.random.rand()
    if r < 0.35:
        return 0.25  # staccato
    elif r < 0.8:
        return 0.5   # medium
    else:
        return 1.0   # legato

# Determine note velocity
def note_velocity(note_val):
    return int(np.interp(note_val, [50, 72], [50, 100]))  # MIDI velocity

# Optionally add passing note between two notes
def add_passing_note(n1, n2):
    if np.random.rand() < PASSING_NOTE_PROB:
        mid = (n1 + n2) // 2
        return note.Note(mid, quarterLength=0.25)
    return None

# Create a musical section
def create_section(notes_chunk, key_name, articulation='mixed'):
    k = key.Key(key_name)
    scale_notes = [p.midi for p in k.pitches]
    section = stream.Stream()
    
    for n in notes_chunk:
        closest_note = min(scale_notes, key=lambda x: abs(x - n))
        motif = generate_motif(closest_note, scale_notes, length=4)
        
        for i, m in enumerate(motif):
            ql = note_length_with_style() if articulation=='mixed' else (1.0 if articulation=='legato' else 0.25)
            n_obj = note.Note(m, quarterLength=ql)
            n_obj.volume.velocity = note_velocity(m)
            section.append(n_obj)
            
            # Occasionally add passing note
            if i < len(motif)-1:
                p_note = add_passing_note(m, motif[i+1])
                if p_note:
                    section.append(p_note)
            
            # Add chords or arpeggios
            c_notes = [m, m+4, m+7]
            if np.random.rand() < ARPEGGIO_PROB:
                for cn in c_notes:
                    c_obj = chord.Chord([cn], quarterLength=0.25)
                    c_obj.volume.velocity = note_velocity(cn)
                    section.append(c_obj)
            else:
                c_obj = chord.Chord(c_notes)
                c_obj.volume.velocity = note_velocity(m)
                section.append(c_obj)
    return section

# Build full composition
composition = stream.Stream()
composition.append(tempo.MetronomeMark(number=TEMPO_BPM))
composition.append(meter.TimeSignature(TIME_SIGNATURE))

# Section articulations: alternate staccato/legato/mixed
articulations = ['staccato', 'legato', 'mixed', 'mixed']

for i in range(SECTION_COUNT):
    eeg_chunk = simulate_eeg_notes(SEED_NOTE, CHUNK_SIZE)
    current_key = KEYS[i % len(KEYS)]
    section = create_section(eeg_chunk, current_key, articulation=articulations[i % len(articulations)])

    # Add smooth transition to next key
    if i < SECTION_COUNT - 1:
        next_key = KEYS[(i+1) % len(KEYS)]
        pivot = stream.Stream()
        last_element = section.notes[-1]
        if isinstance(last_element, note.Note):
            last_note = last_element.pitch.midi
        elif isinstance(last_element, chord.Chord):
            last_note = last_element.root().midi
        for step in range(2):
            pivot_note = last_note + step + 1
            pivot_obj = note.Note(pivot_note, quarterLength=0.5)
            pivot_obj.volume.velocity = note_velocity(pivot_note)
            pivot.append(pivot_obj)
        section.append(pivot)

    composition.append(section)

# Play the piece
composition.show('midi')
# Optional: save as MIDI
# composition.write('midi', fp='expressive_EEG_composition.mid')
