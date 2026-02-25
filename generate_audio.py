import os
import wave
import struct
import math

def generate_tone(filename, frequency, duration, volume=0.5, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        num_samples = int(duration * sample_rate)
        for i in range(num_samples):
            # Sine wave
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            # Pack value as 16-bit integer
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

if __name__ == "__main__":
    # Red Warning (Lower pitch, urgent)
    generate_tone("sounds/warning_5s_red.wav", frequency=440, duration=0.5, volume=0.5)
    
    # Yellow Warning (Higher pitch, noticeably different)
    generate_tone("sounds/warning_5s_yellow.wav", frequency=880, duration=0.5, volume=0.5)
    
    # 3, 2, 1 count ("Po")
    generate_tone("sounds/count.wav", frequency=1000, duration=0.1, volume=0.5)
    
    # 0 end ("Poon")
    generate_tone("sounds/end.wav", frequency=1500, duration=0.8, volume=0.5)
    
    print("Dummy audio files generated in 'sounds' folder.")
