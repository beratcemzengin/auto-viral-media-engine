import math
import wave
import struct
import os

try:
    from . import config
except ImportError:
    import config

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generates lists of float samples for a simple sine wave."""
    num_samples = int(duration * sample_rate)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Simple fade out to prevent clicking at the end
        fade = 1.0
        if i > num_samples - 1000:
            fade = (num_samples - i) / 1000
        samples.append(amplitude * math.sin(2 * math.pi * frequency * t) * fade)
    return samples

def generate_kids_audio_track(output_path, duration=15, sample_rate=44100):
    """Programmatically synthesizes a copyright-free kids soundtrack with ticking and reveal chimes."""
    num_samples = int(duration * sample_rate)
    track_samples = [0.0] * num_samples

    # 1. Add Background Melodic Progression (Very happy 4-chord synth pattern)
    # Chord frequencies: C major, G major, A minor, F major
    chords = [
        [261.63, 329.63, 392.00],  # C4, E4, G4
        [293.66, 392.00, 493.88],  # D4, G4, B4
        [220.00, 261.63, 329.63],  # A3, C4, E4
        [174.61, 220.00, 261.63]   # F3, A3, C4
    ]
    
    chord_duration = 2.0  # seconds per chord
    for start_sec in range(0, int(duration), 2):
        chord_idx = (start_sec // 2) % len(chords)
        chord_freqs = chords[chord_idx]
        
        # Mix the frequencies of the chord
        for freq in chord_freqs:
            chord_vol = 0.08  # Quiet background music
            samples = generate_sine_wave(freq, chord_duration, sample_rate, amplitude=chord_vol)
            start_idx = int(start_sec * sample_rate)
            for i, val in enumerate(samples):
                idx = start_idx + i
                if idx < num_samples:
                    # Simple arpeggiation/melody effect
                    mod_val = math.sin(2 * math.pi * 4 * (i / sample_rate)) * 0.3 + 0.7
                    track_samples[idx] += val * mod_val

    # 2. Add Timer Ticking Sound Effect (First 11 seconds, every 1.0s)
    # Sound is a tiny high-pitched clean "click"
    for tick_sec in range(1, 12):
        start_idx = int(tick_sec * sample_rate)
        # Click sound: 1500Hz for 0.04 seconds
        click = generate_sine_wave(1500, 0.04, sample_rate, amplitude=0.25)
        for i, val in enumerate(click):
            idx = start_idx + i
            if idx < num_samples:
                track_samples[idx] += val

    # 3. Add Timer Reveal Chime Sound Effect at 11.0 seconds
    # A bright arpeggiated C-major success chime (C5 -> E5 -> G5 -> C6)
    reveal_start_sec = 11.0
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    for note_idx, note_freq in enumerate(notes):
        note_start = reveal_start_sec + (note_idx * 0.15)
        start_idx = int(note_start * sample_rate)
        # Play note with fade out
        note_samples = generate_sine_wave(note_freq, 1.8, sample_rate, amplitude=0.15)
        for i, val in enumerate(note_samples):
            idx = start_idx + i
            if idx < num_samples:
                track_samples[idx] += val

    # 4. Normalize & Save to WAV file
    max_val = max(abs(x) for x in track_samples) if track_samples else 1.0
    if max_val == 0:
        max_val = 1.0
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, 'wb') as wav_file:
        # Mono, 2-byte samples, sample_rate
        wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
        for s in track_samples:
            # Scale to 16-bit signed integer range (-32768 to 32767)
            val = int((s / max_val) * 32767 * 0.8) # Keep it at 80% volume limit
            wav_file.writeframes(struct.pack('<h', val))

    return output_path
