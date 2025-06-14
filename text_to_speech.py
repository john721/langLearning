#!/usr/bin/env python3

import sys
import os
from gtts import gTTS
import pygame
import time
from pydub import AudioSegment
import tempfile
import numpy
import math
import wave
import struct

def create_beep(duration=0.5, frequency=440):
    """Create a beep sound and save it as a WAV file."""
    sample_rate = 44100
    n_samples = int(round(duration * sample_rate))
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2**(16 - 1) - 1
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        buf[s][1] = buf[s][0]
    
    # Create a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
        with wave.open(wav_file.name, 'w') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(buf.tobytes())
        return wav_file.name

def read_text_file(filename):
    """Read all pairs of non-empty lines from the file."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        if len(lines) < 2:
            raise ValueError("File must contain at least two non-empty lines")
        if len(lines) % 2 != 0:
            raise ValueError("File must contain pairs of lines (Japanese-Chinese)")
        # Strip comments from Japanese lines (even-numbered lines)
        processed_lines = []
        for i in range(0, len(lines), 2):
            japanese = lines[i].split('#')[0].strip()  # Remove comment and strip whitespace
            chinese = lines[i+1]
            processed_lines.extend([japanese, chinese])
        return [(processed_lines[i], processed_lines[i+1]) for i in range(0, len(processed_lines), 2)]

def main():
    if len(sys.argv) != 2:
        print("Usage: python text_to_speech.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    # Read all pairs from the text file
    text_pairs = read_text_file(input_file)
    
    # Create output filename
    output_file = os.path.splitext(input_file)[0] + '.mp3'

    # Create beep sound
    beep_wav = create_beep()
    beep = AudioSegment.from_wav(beep_wav)
    os.unlink(beep_wav)  # Clean up the temporary WAV file

    # Create a list to store all audio segments
    audio_segments = []
    silence = AudioSegment.silent(duration=1000)

    # Process each pair of lines
    for i, (japanese_text, chinese_text) in enumerate(text_pairs):
        print(f"Processing pair {i+1}/{len(text_pairs)}: {japanese_text} - {chinese_text}")
        
        # Create temporary files for this pair
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as jp_file, \
             tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tw_file:

            # Generate TTS for Japanese and Chinese
            tts_jp = gTTS(text=japanese_text, lang='ja')
            tts_tw = gTTS(text=chinese_text, lang='zh-tw')

            # Save TTS to temporary files
            tts_jp.save(jp_file.name)
            tts_tw.save(tw_file.name)

            # Load audio segments
            jp = AudioSegment.from_mp3(jp_file.name)
            tw = AudioSegment.from_mp3(tw_file.name)

            # Speed up the Chinese audio by 1.5x
            tw = tw.speedup(playback_speed=1.5)

            # Add segments to the list (reusing the Japanese audio segment)
            audio_segments.extend([beep, silence, jp, silence, tw, silence, jp, silence])

            # Clean up temporary files
            os.unlink(jp_file.name)
            os.unlink(tw_file.name)

    # Combine all segments
    final_audio = sum(audio_segments)

    # Export the final audio with lower quality
    final_audio.export(output_file, format='mp3', bitrate='32k')

    print(f"Audio file created: {output_file}")

if __name__ == "__main__":
    main() 