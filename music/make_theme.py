"""Mr Farts theme - 80s retro calypso / Latin jazz loop, synthesized with numpy.

Renders a seamless 16-bar loop (128 BPM, F major) to mr_farts_theme.wav.
Everything is synthesized from scratch: no samples, no extra libraries beyond numpy.

    python make_theme.py            -> music/mr_farts_theme.wav

Layout (one bar = 16 sixteenth-note steps):
  A section (bars 1-8)   steel-drum hook, synth-brass off-beat stabs, calypso bass
  B section (bars 9-16)  80s square lead answers, marimba montuno, cowbell, bigger drums
Chords: F | F | Bb | Bb | Gm7 | C7 | F | C7 | Dm7 | Dm7 | Bb | Bb | Gm7 | C7 | F | C7
"""
import math, os, wave
from functools import lru_cache
import numpy as np

SR = 44100
BPM = 128
BARS = 16
STEPS_PER_BAR = 16
STEPS = BARS * STEPS_PER_BAR
STEP_S = 60.0 / BPM / 4.0                    # one sixteenth in seconds
LOOP_N = int(round(STEPS * STEP_S * SR))      # loop length in samples (exact integer)
STEP_N = LOOP_N / STEPS                       # samples per step (positions are rounded)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mr_farts_theme.wav")
# Peak level of the rendered file. The old -1 dBFS master turned down to 15% (-16.5 dB) gave -17.5 dBFS; that was
# then halved again (-6 dB, 7.5% of the old master) so the game's sound effects and voices stay clear. The game plays
# the file at up to 100%, so the quiet level is baked in here (iPhones ignore volume settings on audio elements).
PEAK_DB = -23.5

rng = np.random.default_rng(7)

# ------------------------------------------------------------------ helpers
def midi(n): return 440.0 * 2 ** ((n - 69) / 12.0)
def t_arr(n): return np.arange(n) / SR
def sec(n): return int(n * SR)

def env(n, a, d, s, r):
    """ADSR in seconds; note held for n samples, then a release of r seconds. Length n + r."""
    a, d, r = max(1, sec(a)), max(1, sec(d)), max(1, sec(r))
    out = np.zeros(n + r)
    aa = min(a, n); out[:aa] = np.linspace(0, 1, aa, endpoint=False)
    dd = min(d, n - aa)
    if dd > 0: out[aa:aa + dd] = 1 + (s - 1) * np.linspace(0, 1, dd, endpoint=False)
    if n - aa - dd > 0: out[aa + dd:n] = s
    out[n:] = out[n - 1] * np.exp(-np.linspace(0, 6, r))
    return out

def saw(f, n, nh=48, phase=None):
    """Band-limited sawtooth (additive). phase: optional phase array for vibrato."""
    ph = 2 * np.pi * f * t_arr(n) if phase is None else phase
    H = int(min(nh, (SR / 2.2) / f)); out = np.zeros(n)
    for k in range(1, H + 1): out += np.sin(k * ph) / k
    return out * (2 / np.pi)

def square(f, n, nh=32, phase=None):
    ph = 2 * np.pi * f * t_arr(n) if phase is None else phase
    H = int(min(nh, (SR / 2.2) / f)); out = np.zeros(n)
    for k in range(1, H + 1, 2): out += np.sin(k * ph) / k
    return out * (4 / np.pi)

def pulse(f, n, duty=0.25, nh=40, phase=None):
    ph = 2 * np.pi * f * t_arr(n) if phase is None else phase
    H = int(min(nh, (SR / 2.2) / f)); out = np.zeros(n)
    for k in range(1, H + 1):
        out += (np.sin(k * ph) - np.sin(k * (ph + 2 * np.pi * duty))) / k
    return out * (2 / np.pi)

def fft_filter(x, lo=None, hi=None, slope=2.0):
    """Static filter in the frequency domain: highpass at lo and/or lowpass at hi (Hz)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * slope))
    if lo: g *= 1 / np.sqrt(1 + (lo / f) ** (2 * slope))
    return np.fft.irfft(X * g, n=len(x))

def svf_lp(x, cutoff, res=0.3):
    """Chamberlin state-variable lowpass; cutoff may be an array (filter envelope)."""
    fc = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    fcoef = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    q = 2 - 2 * min(res, 0.95)
    lp = bp = 0.0; out = np.empty_like(x)
    for i in range(len(x)):
        hp = x[i] - lp - q * bp
        bp += fcoef[i] * hp
        lp += fcoef[i] * bp
        out[i] = lp
    return out

def noise(n): return rng.standard_normal(n)

def pan(x, p):
    """p in [-1, 1]; equal-power pan -> (L, R)."""
    th = (p + 1) * np.pi / 4
    return x * np.cos(th), x * np.sin(th)

# ------------------------------------------------------------------ drum voices
@lru_cache(None)
def kick(vel=1.0):
    n = sec(0.42); t = t_arr(n)
    f = 52 + 120 * np.exp(-t * 30)                       # pitch drop 172 -> 52 Hz
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 9.5)
    click = fft_filter(noise(n), lo=1500) * np.exp(-t * 180) * 0.7
    x = np.tanh(1.6 * (body + click)) * vel * 0.85
    return pan(x, 0.0)

@lru_cache(None)
def clap(vel=1.0):
    n = sec(0.32); t = t_arr(n); x = np.zeros(n)
    for i, g in enumerate([1.0, 0.8, 0.7]):               # three flams then the tail
        s = sec(0.011 * i); x[s:] += g * noise(n - s) * np.exp(-np.arange(n - s) / SR * 220)
    x += 0.9 * noise(n) * np.exp(-t * 14)
    x = fft_filter(x, lo=900, hi=5500) * vel * 0.9
    return pan(x, 0.08)

@lru_cache(None)
def hat(open_=False, vel=1.0):
    n = sec(0.5 if open_ else 0.07); t = t_arr(n)
    x = fft_filter(noise(n), lo=7000, slope=3) * np.exp(-t * (6 if open_ else 55)) * vel * 1.05
    return pan(x, 0.35)

@lru_cache(None)
def shaker(vel=1.0):
    n = sec(0.06); t = t_arr(n)
    x = fft_filter(noise(n), lo=5000, hi=12000) * np.exp(-t * 70) * vel * 0.6
    return pan(x, -0.4)

@lru_cache(None)
def cowbell(vel=1.0):
    n = sec(0.22); t = t_arr(n)
    x = (square(587, n, nh=4) + square(845, n, nh=4)) * np.exp(-t * 16)
    x = fft_filter(x, lo=400, hi=4000) * vel * 0.45
    return pan(x, 0.55)

@lru_cache(None)
def clave(vel=1.0):
    n = sec(0.08); t = t_arr(n)
    x = np.sin(2 * np.pi * 2480 * t) * np.exp(-t * 90) * vel
    return pan(x, -0.55)

@lru_cache(None)
def conga(kind="open", vel=1.0):
    if kind == "slap":
        n = sec(0.12); t = t_arr(n)
        x = np.sin(2 * np.pi * (330 + 90 * np.exp(-t * 60)) * t) * np.exp(-t * 32)
        x += fft_filter(noise(n), lo=1200, hi=6000) * np.exp(-t * 60) * 0.5
    else:
        hi = kind == "high"
        n = sec(0.3); t = t_arr(n)
        f0 = 240 if hi else 185
        f = f0 * (1 + 0.12 * np.exp(-t * 40)); ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.exp(-t * 11)
        x += fft_filter(noise(n), lo=800) * np.exp(-t * 90) * 0.25
    return pan(np.tanh(1.5 * x) * vel * 0.8, 0.25 if kind == "high" else -0.3)

@lru_cache(None)
def tom(pitch=140, vel=1.0):
    n = sec(0.35); t = t_arr(n)
    f = pitch * (1 + 0.5 * np.exp(-t * 25)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 9) + fft_filter(noise(n), lo=600) * np.exp(-t * 60) * 0.3
    return pan(np.tanh(1.3 * x) * vel * 0.9, (pitch - 140) / 120)

@lru_cache(None)
def crash(vel=1.0):
    n = sec(1.6); t = t_arr(n)
    x = fft_filter(noise(n), lo=4500, hi=14000, slope=1.5) * np.exp(-t * 2.6) * vel * 0.55
    return pan(x, 0.2)

# ------------------------------------------------------------------ tonal voices
@lru_cache(None)
def bass(note, steps, vel=1.0):
    """80s synth bass: saw + sub square through a resonant lowpass with a snappy envelope."""
    n = max(sec(0.09), int(steps * STEP_N) - sec(0.02)); f = midi(note)
    x = 0.7 * saw(f, n + sec(0.05), nh=40) + 0.35 * square(f, n + sec(0.05), nh=3)
    e = env(n, 0.003, 0.08, 0.7, 0.05)
    fenv = 220 + 2200 * vel * np.exp(-t_arr(len(e)) * 14)
    x = svf_lp(x[:len(e)] * e, fenv, res=0.45)
    return pan(np.tanh(1.4 * x) * vel * 0.8, 0.0)

@lru_cache(None)
def brass(notes, steps, vel=1.0):
    """Synth brass stab: detuned saws per note, filter envelope, short release."""
    n = int(steps * STEP_N) - sec(0.01); tot = n + sec(0.12)
    L = np.zeros(tot); R = np.zeros(tot)
    for nt in notes:
        f = midi(nt)
        L += saw(f * 1.006, tot, nh=32) + 0.6 * saw(f * 0.997, tot, nh=32)
        R += saw(f * 0.994, tot, nh=32) + 0.6 * saw(f * 1.003, tot, nh=32)
    e = env(n, 0.012, 0.09, 0.55, 0.12)
    fenv = 600 + 3400 * vel * np.exp(-t_arr(tot) * 16)
    L = svf_lp(L * e, fenv, 0.25); R = svf_lp(R * e, fenv, 0.25)
    g = vel * 0.18 / math.sqrt(len(notes))
    return L * g, R * g

@lru_cache(None)
def pad(notes, steps):
    """Warm 80s pad: detuned saws, slow attack, dark lowpass, wide stereo."""
    n = int(steps * STEP_N); tot = n + sec(0.35)
    L = np.zeros(tot); R = np.zeros(tot)
    for nt in notes:
        f = midi(nt)
        L += saw(f * 1.004, tot, nh=20) + saw(f * 0.9985, tot, nh=20)
        R += saw(f * 0.996, tot, nh=20) + saw(f * 1.0015, tot, nh=20)
    e = env(n, 0.25, 0.3, 0.8, 0.35)
    L = fft_filter(L * e, hi=1100, slope=1.5); R = fft_filter(R * e, hi=1100, slope=1.5)
    g = 0.09 / math.sqrt(len(notes))
    return L * g, R * g

@lru_cache(None)
def steel(note, steps, vel=1.0):
    """Steel pan: additive partials with a quick 'boing' pitch settle and a bright attack."""
    f = midi(note); n = int(steps * STEP_N); tot = n + sec(0.45); t = t_arr(tot)
    bend = 1 + 0.025 * np.exp(-t * 45)
    ph = 2 * np.pi * f * np.cumsum(bend) / SR
    x = (np.sin(ph) * np.exp(-t * 3.0) + 0.7 * np.sin(2 * ph + 0.3) * np.exp(-t * 4.5)
         + 0.45 * np.sin(3 * ph) * np.exp(-t * 7) + 0.25 * np.sin(4.02 * ph) * np.exp(-t * 10)
         + 0.15 * np.sin(5.9 * ph) * np.exp(-t * 16))
    x += fft_filter(noise(tot), lo=2500) * np.exp(-t * 120) * 0.3    # mallet click
    e = env(n, 0.002, 0.05, 1.0, 0.45)
    x = x * e * vel * 0.55
    return pan(x, -0.15)

@lru_cache(None)
def chip(note, steps, vel=1.0):
    """80s square/pulse lead with vibrato and a mellowing lowpass."""
    f = midi(note); n = int(steps * STEP_N) - sec(0.015); tot = n + sec(0.08); t = t_arr(tot)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.8 * t) * np.minimum(1, t * 6)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = pulse(f, tot, duty=0.28, nh=24, phase=ph) + 0.35 * pulse(f, tot, duty=0.5, nh=12, phase=ph * 0.5)
    e = env(n, 0.006, 0.06, 0.8, 0.08)
    x = fft_filter(x * e, hi=4500, slope=1.5) * vel * 0.33
    return pan(x, 0.2)

@lru_cache(None)
def marimba(note, vel=1.0):
    f = midi(note); n = sec(0.28); t = t_arr(n)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.4 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 40)
         + 0.15 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t * 70))
    x[:sec(0.002)] *= np.linspace(0, 1, sec(0.002))
    return pan(x * vel * 0.4, 0.45)

# ------------------------------------------------------------------ score
# chord per bar: (bass root midi, stab voicing, pad voicing)
CH = {
    "F":  (41, (60, 64, 65, 69), (53, 57, 60, 64)),
    "Bb": (46, (62, 65, 69, 70), (50, 53, 57, 62)),
    "Gm": (43, (58, 62, 65, 67), (50, 53, 58, 62)),
    "C7": (36, (58, 62, 64, 67), (48, 52, 58, 62)),
    "Dm": (38, (60, 62, 65, 69), (50, 53, 57, 60)),
}
PROG = ["F", "F", "Bb", "Bb", "Gm", "C7", "F", "C7", "Dm", "Dm", "Bb", "Bb", "Gm", "C7", "F", "C7"]

# melodies: per bar, list of (step, midi, length_in_steps)
MEL_A = [
    [(0, 69, 2), (2, 72, 2), (4, 77, 3), (7, 76, 1), (8, 74, 2), (11, 72, 3), (14, 69, 2)],
    [(2, 74, 1), (3, 72, 1), (4, 69, 4), (10, 65, 2), (12, 67, 2), (14, 69, 2)],
    [(0, 70, 2), (2, 74, 2), (4, 77, 3), (7, 79, 1), (8, 77, 2), (11, 74, 3), (14, 70, 2)],
    [(2, 72, 1), (3, 74, 1), (4, 77, 4), (10, 74, 2), (12, 72, 2), (14, 70, 2)],
    [(0, 67, 2), (2, 70, 2), (4, 74, 3), (7, 77, 1), (8, 74, 2), (11, 70, 3), (14, 67, 2)],
    [(0, 67, 2), (2, 70, 2), (4, 76, 4), (10, 74, 2), (12, 72, 2), (14, 70, 2)],
    [(0, 69, 2), (2, 72, 2), (4, 77, 3), (7, 81, 1), (8, 79, 2), (11, 77, 3), (14, 72, 2)],
    [(0, 74, 2), (2, 76, 2), (4, 79, 4), (10, 76, 2), (12, 74, 2), (14, 72, 1), (15, 73, 1)],
]
MEL_B = [
    [(0, 69, 2), (2, 74, 2), (4, 77, 2), (6, 76, 2), (8, 74, 3), (11, 72, 1), (12, 69, 4)],
    [(2, 77, 1), (3, 76, 1), (4, 74, 4), (10, 69, 2), (12, 72, 2), (14, 74, 2)],
    [(0, 74, 2), (2, 77, 2), (4, 82, 3), (7, 81, 1), (8, 79, 2), (11, 77, 3), (14, 74, 2)],
    [(2, 77, 1), (3, 79, 1), (4, 81, 4), (10, 77, 2), (12, 79, 2), (14, 77, 2)],
    [(0, 79, 2), (2, 77, 2), (4, 74, 3), (7, 70, 1), (8, 74, 2), (11, 77, 3), (14, 79, 2)],
    [(0, 76, 2), (2, 79, 2), (4, 82, 4), (10, 81, 2), (12, 79, 2), (14, 76, 2)],
    [(0, 77, 2), (2, 81, 2), (4, 84, 3), (7, 81, 1), (8, 79, 2), (11, 77, 3), (14, 72, 2)],
    [(0, 74, 2), (2, 76, 2), (4, 79, 3), (8, 76, 2), (10, 72, 2), (12, 67, 2), (14, 70, 2)],
]

events = []   # (step, bus, (L, R)); bus: "dry" or "fx" (gets delay + reverb send)
def hit(step, lr, bus="dry"): events.append((step, bus, lr))

for bar in range(BARS):
    b0 = bar * STEPS_PER_BAR
    name = PROG[bar]; root, stab, padv = CH[name]
    nxt = CH[PROG[(bar + 1) % BARS]]
    B = bar >= 8; last = bar % 8 == 7; even = bar % 2 == 1

    # --- drums: calypso/soca kick, backbeat clap, off-beat accented hats, clave, congas
    for s in (0, 6, 8, 14): hit(b0 + s, kick(1.0 if s in (0, 8) else 0.8))
    if last: hit(b0 + 10, kick(0.7))
    for s in (4, 12): hit(b0 + s, clap(1.0), "fx")
    if bar % 4 == 3: hit(b0 + 15, clap(0.55), "fx")                 # push into the next bar
    for s in range(0, 16, 2):
        if s == 14 and even: hit(b0 + s, hat(True, 0.7))
        else: hit(b0 + s, hat(False, 1.0 if s % 4 == 2 else 0.45))   # accent the "&"s
    for s in range(16): hit(b0 + s, shaker(0.9 if s % 4 == 2 else (0.35 if s % 2 else 0.55)))
    for s in ((4, 8) if even else (0, 6, 12)): hit(b0 + s, clave(0.9), "fx")   # 3-2 son clave
    hit(b0 + 4, conga("slap", 0.9)); hit(b0 + 12, conga("open", 1.0)); hit(b0 + 14, conga("open", 0.85))
    if even: hit(b0 + 7, conga("high", 0.6)); hit(b0 + 10, conga("high", 0.5))
    if B or last:
        for s in (0, 4, 8, 12): hit(b0 + s, cowbell(0.9 if s in (0, 8) else 0.6))
    if bar in (0, 8): hit(b0, crash(0.9))
    if bar == 7:                                             # tom fill into B
        for s, p in ((12, 220), (13, 180), (14, 150), (15, 120)): hit(b0 + s, tom(p, 0.9), "fx")
    if bar == 15:                                            # conga + tom fill back to the top
        for s, k in ((8, "high"), (9, "high"), (10, "open"), (11, "slap")): hit(b0 + s, conga(k, 0.9))
        for s, p in ((12, 220), (13, 180), (14, 150), (15, 120)): hit(b0 + s, tom(p, 1.0), "fx")

    # --- bass: syncopated calypso line, anticipating the next chord on the "& of 4"
    approach = nxt[0] - 1 if nxt[0] > root else nxt[0] + 2
    if nxt[0] == root: approach = root + 7
    line = [(0, root, 2), (3, root + 12, 1), (6, root + 7, 2), (8, root, 2), (11, root + 12, 1), (12, root + 7, 2), (14, approach, 2)]
    if last: line = [(0, root, 2), (3, root + 12, 1), (6, root + 7, 2), (8, root + 10, 1), (10, root + 12, 1), (12, root + 7, 1), (13, root + 10, 1), (14, approach, 2)]
    for s, nt, ln in line: hit(b0 + s, bass(nt, ln, 1.0 if s in (0, 8) else 0.85))

    # --- off-beat brass stabs; the last one anticipates the next bar's chord
    for s in (2, 6, 10, 14):
        v = stab if s != 14 else nxt[1]
        hit(b0 + s, brass(v, 1.5 if s in (6, 14) else 1.2, 1.0 if s in (6, 14) else 0.8), "fx")
    if last: hit(b0 + 12, brass(stab, 1, 0.7), "fx")

    # --- pad (one per bar)
    hit(b0, pad(padv, STEPS_PER_BAR))

    # --- melody
    if not B:
        for s, nt, ln in MEL_A[bar]: hit(b0 + s, steel(nt, ln, 1.0 if s % 4 == 0 else 0.85), "fx")
    else:
        for s, nt, ln in MEL_B[bar - 8]:
            hit(b0 + s, chip(nt, ln, 1.0 if s % 4 == 0 else 0.85), "fx")
            hit(b0 + s, steel(nt - 12, ln, 0.4), "fx")            # steel pan shadows an octave below
        tones = [n + 12 for n in stab]                            # marimba montuno (tresillo arpeggio)
        for i, s in enumerate((0, 3, 6, 8, 11, 14)):
            hit(b0 + s, marimba(tones[(0, 1, 2, 3, 2, 1)[i]], 0.9 if s in (3, 11) else 0.7), "fx")

# ------------------------------------------------------------------ render
# Render three copies back to back and keep the middle one: every tail, delay echo and
# reverb from the end of the loop then lands at the start of the kept copy, exactly as it
# will when the file loops.
COPIES = 3
TOT = LOOP_N * COPIES
bus = {"dry": (np.zeros(TOT), np.zeros(TOT)), "fx": (np.zeros(TOT), np.zeros(TOT))}

def place(dst, pos, L, R):
    end = min(TOT, pos + len(L)); k = end - pos
    if k > 0: dst[0][pos:end] += L[:k]; dst[1][pos:end] += R[:k]

print(f"loop: {BARS} bars at {BPM} BPM = {LOOP_N / SR:.3f} s ({LOOP_N} samples), {len(events)} events per loop")
for step, b, (L, R) in events:
    for c in range(COPIES):
        place(bus[b], int(round((step + c * STEPS) * STEP_N)), L, R)

def delay_line(x, D, fb):
    """y[n] = x[n-D] + fb * y[n-D], computed D samples at a time."""
    y = np.zeros_like(x)
    for i in range(D, len(x), D):
        j = min(len(x), i + D)
        y[i:j] = x[i - D:j - D] + fb * y[i - D:j - D]
    return y

def shift(x, d): return np.concatenate([np.zeros(d), x[:-d]])

# ping-pong eighth-note delay: odd echoes left, even echoes right
D = int(round(2 * STEP_N))
fxL, fxR = bus["fx"]
send = fft_filter(0.5 * (fxL + fxR), lo=300, hi=4500)
echoL = delay_line(shift(send, D), 2 * D, 0.45 ** 2)
echoR = delay_line(shift(send, 2 * D), 2 * D, 0.45 ** 2) * 0.45

mixL = bus["dry"][0] + fxL + 0.22 * echoL
mixR = bus["dry"][1] + fxR + 0.22 * echoR

# short bright reverb (exponentially decaying noise impulse) on the fx bus
irn = sec(0.9); irt = t_arr(irn)
ir = fft_filter(noise(irn), lo=400, hi=6000) * np.exp(-irt * 6.5); ir /= np.sqrt(np.sum(ir ** 2))
def convolve(x, h):
    n = 1 << (len(x) + len(h) - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[:len(x)]
revL = convolve(fxL + 0.3 * echoL, ir); revR = convolve(fxR + 0.3 * echoR, ir)
mixL += 0.09 * revR; mixR += 0.09 * revL          # cross-feed for width

# gentle glue: soft clip, then normalise the kept copy to PEAK_DB
L = mixL[LOOP_N:2 * LOOP_N]; R = mixR[LOOP_N:2 * LOOP_N]
L = np.tanh(L * 1.15) / np.tanh(1.15); R = np.tanh(R * 1.15) / np.tanh(1.15)
peak = max(np.abs(L).max(), np.abs(R).max())
g = 10 ** (PEAK_DB / 20) / peak
L *= g; R *= g

data = np.empty(2 * LOOP_N, dtype="<i2")
data[0::2] = np.clip(np.round(L * 32767), -32768, 32767).astype("<i2")
data[1::2] = np.clip(np.round(R * 32767), -32768, 32767).astype("<i2")
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

# MP3 copy for the game (about a tenth of the WAV's size); needs `pip install lameenc`.
# MP3 encoders add a little silence at both ends, which would leave a gap each time the loop restarts. So the MP3
# holds MP3_PAD extra frames of the loop's own tail before it and its head after it, and the game loops exactly
# the 30 s that starts MP3_PAD frames in (index.html: THEME.start = 4096 / 44100). Keep the two numbers in step.
MP3 = OUT[:-4] + ".mp3"
MP3_PAD = 4096
try:
    import lameenc
    frames = data.reshape(-1, 2)
    padded = np.concatenate([frames[-MP3_PAD:], frames, frames[:MP3_PAD]])
    enc = lameenc.Encoder(); enc.set_bit_rate(160); enc.set_in_sample_rate(SR); enc.set_channels(2); enc.set_quality(2)
    with open(MP3, "wb") as f: f.write(enc.encode(padded.tobytes()) + enc.flush())
    print(f"wrote {MP3}: {os.path.getsize(MP3) / 1e6:.2f} MB")
except ImportError:
    print("lameenc not installed: skipped the MP3 (pip install lameenc)")

rms = 20 * np.log10(np.sqrt(np.mean((L ** 2 + R ** 2) / 2)))
print(f"wrote {OUT}: {LOOP_N / SR:.2f} s, peak {PEAK_DB:.1f} dBFS, rms {rms:.1f} dBFS, pre-clip peak {peak:.2f}")
print(f"loop seam: last sample L={L[-1]:+.4f} R={R[-1]:+.4f}  first sample L={L[0]:+.4f} R={R[0]:+.4f}")
