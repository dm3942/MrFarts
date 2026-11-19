"""Convert the voice clips in sounds/ from WAV to MP3 - the game only plays the MP3s.

    python tools_wav_to_mp3.py           every sounds/*.wav becomes sounds/<same name>.mp3 and the WAV is deleted
    python tools_wav_to_mp3.py --keep    the same, but keep the WAVs

Drop a new recording into sounds/ as a WAV, run this, then add its .mp3 name to Voice.clips in index.html.
Needs `pip install lameenc`. Mono clips are encoded at 96 kbps, stereo at 160 kbps (16- or 24-bit PCM WAVs).
"""
import glob, os, sys, wave
import numpy as np
import lameenc

HERE = os.path.dirname(os.path.abspath(__file__))
keep = "--keep" in sys.argv[1:]


def read_pcm16(path):
    with wave.open(path) as w:
        ch, width, rate, raw = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.readframes(w.getnframes())
    if width == 2:
        pcm = np.frombuffer(raw, dtype="<i2")
    elif width == 3:                                   # 24-bit: keep the top 16 bits
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        pcm = (((b[:, 2] << 24) | (b[:, 1] << 16) | (b[:, 0] << 8)) >> 16).astype("<i2")
    else:
        raise ValueError(f"{width * 8}-bit WAV not supported (use 16- or 24-bit PCM)")
    return ch, rate, pcm


wavs = sorted(glob.glob(os.path.join(HERE, "sounds", "*.wav")))
if not wavs:
    print("no WAV files in sounds/")
before = after = 0
for path in wavs:
    ch, rate, pcm = read_pcm16(path)
    enc = lameenc.Encoder()
    enc.set_bit_rate(96 if ch == 1 else 160); enc.set_in_sample_rate(rate); enc.set_channels(ch); enc.set_quality(2)
    out = path[:-4] + ".mp3"
    with open(out, "wb") as f:
        f.write(enc.encode(pcm.tobytes()) + enc.flush())
    before += os.path.getsize(path); after += os.path.getsize(out)
    print(f"{os.path.basename(out):34s} {os.path.getsize(path) / 1e3:7.0f} kB -> {os.path.getsize(out) / 1e3:5.0f} kB")
    if not keep:
        os.remove(path)
if wavs:
    print(f"total {before / 1e6:.2f} MB -> {after / 1e6:.2f} MB" + ("" if keep else " (WAVs removed)"))
