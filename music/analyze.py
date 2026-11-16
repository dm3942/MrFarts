"""Level / balance report and a spectrogram PNG for mr_farts_theme.wav (numpy + Pillow)."""
import os, sys, wave
import numpy as np
from PIL import Image, ImageDraw

here = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "mr_farts_theme.wav")
w = wave.open(path); n = w.getnframes(); sr = w.getframerate()
d = np.frombuffer(w.readframes(n), dtype="<i2").astype(float).reshape(-1, 2) / 32768
m = d.mean(1)
print(f"{os.path.basename(path)}: {n} frames, {sr} Hz, {n / sr:.2f} s")

X = np.abs(np.fft.rfft(m)) ** 2; f = np.fft.rfftfreq(len(m), 1 / sr)
tot = X[(f >= 20) & (f < 16000)].sum()
print("band energy (per Hz, relative):")
for lo, hi in [(20, 80), (80, 200), (200, 500), (500, 1500), (1500, 4000), (4000, 8000), (8000, 16000)]:
    e = X[(f >= lo) & (f < hi)].sum() / tot / (hi - lo) * 1000
    print(f"  {lo:>5}-{hi:<5} Hz {10 * np.log10(e):6.1f} dB")
rms = 20 * np.log10(np.sqrt((d ** 2).mean())); peak = 20 * np.log10(np.abs(d).max())
print(f"rms {rms:.1f} dBFS  peak {peak:.1f} dBFS  crest {peak - rms:.1f} dB  full-scale samples {int((np.abs(d) >= 0.999).sum())}")
bar = n // 16
print("per-bar rms:", " ".join(f"{20 * np.log10(np.sqrt((d[b * bar:(b + 1) * bar] ** 2).mean())):.1f}" for b in range(16)))

# spectrogram: log-frequency, 2 bars per row is too busy, so one row for the whole loop
win = 2048; hop = 441                       # 10 ms per column
frames = (len(m) - win) // hop
hann = np.hanning(win)
S = np.empty((frames, win // 2 + 1))
for i in range(frames):
    S[i] = np.abs(np.fft.rfft(m[i * hop:i * hop + win] * hann))
S = 20 * np.log10(S + 1e-6)
fbins = np.fft.rfftfreq(win, 1 / sr)
H = 360; lo, hi = 30, 16000
fy = np.exp(np.linspace(np.log(hi), np.log(lo), H))          # rows top (hi) -> bottom (lo)
idx = np.clip(np.searchsorted(fbins, fy), 0, len(fbins) - 1)
img = S[:, idx].T                                           # (H, frames)
img = np.clip((img - (img.max() - 70)) / 70, 0, 1)
rgb = np.zeros((H, frames, 3), np.uint8)
rgb[..., 0] = (255 * np.clip(img * 1.6 - 0.3, 0, 1)); rgb[..., 1] = (255 * np.clip(img * 1.6 - 0.6, 0, 1)); rgb[..., 2] = (255 * np.clip(img * 2.2, 0, 1) * (1 - img * 0.5))
im = Image.fromarray(rgb)
dr = ImageDraw.Draw(im)
for b in range(1, 16):
    x = int(b * bar / hop); dr.line([(x, 0), (x, H)], fill=(255, 255, 255) if b % 8 == 0 else (120, 120, 120), width=1)
for fr in (50, 100, 200, 500, 1000, 2000, 5000, 10000):
    y = int(np.interp(np.log(fr), np.log(fy[::-1]), np.arange(H)[::-1])); dr.line([(0, y), (12, y)], fill=(255, 255, 0)); dr.text((14, y - 5), f"{fr}", fill=(255, 255, 0))
out = os.path.join(here, "spectrogram.png"); im.save(out); print("spectrogram ->", out)
