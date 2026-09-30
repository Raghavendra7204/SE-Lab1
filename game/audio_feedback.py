import io
import math
import struct
import wave

import pygame


class AudioFeedback:
    sample_rate = 22050

    def __init__(self):
        self.hit_sound = None
        self.miss_sound = None
        self.game_over_sound = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=self.sample_rate,
                    size=-16,
                    channels=1,
                )
            self.hit_sound = self._create_sound(((880, 1.0),), 90)
            self.miss_sound = self._create_sound(((220, 1.0),), 150)
            self.game_over_sound = self._create_sound(
                ((392, 1.0), (294, 1.0)), 420
            )
        except pygame.error:
            self.hit_sound = None
            self.miss_sound = None
            self.game_over_sound = None

    def _create_sound(self, tones, duration_ms):
        sample_count = int(self.sample_rate * duration_ms / 1000)
        fade_in = max(1, int(self.sample_rate * 0.01))
        fade_out = max(1, int(self.sample_rate * 0.04))
        total_amplitude = sum(amplitude for _, amplitude in tones)
        samples = bytearray(sample_count * 2)

        for index in range(sample_count):
            envelope = min(1.0, index / fade_in, (sample_count - index) / fade_out)
            sample = sum(
                math.sin(2 * math.pi * frequency * index / self.sample_rate)
                * amplitude
                for frequency, amplitude in tones
            ) / total_amplitude
            value = int(32767 * 0.25 * envelope * sample)
            struct.pack_into("<h", samples, index * 2, value)

        audio_file = io.BytesIO()
        with wave.open(audio_file, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(samples)
        audio_file.seek(0)
        return pygame.mixer.Sound(file=audio_file)

    @staticmethod
    def _play(sound):
        if sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass

    def play_hit_sound(self):
        self._play(self.hit_sound)

    def play_miss_sound(self):
        self._play(self.miss_sound)

    def play_game_over_sound(self):
        self._play(self.game_over_sound)