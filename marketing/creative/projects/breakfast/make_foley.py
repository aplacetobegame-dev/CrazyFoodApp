"""Original, restrained non-vocal Foley for the 25s Breakfast: Final Boss edit.

Uses only NumPy and the standard library. This is a quiet sound-effects layer,
not a music bed. Optional JSON overrides may contain an ``events`` object with
any of the named event dictionaries below (for example, to move a pan sizzle).
No speech, reaction vocals, sirens, pitched celebrations or existing recordings.
"""
from pathlib import Path
import argparse
import copy
import json
import math
import wave
import numpy as np

ROOT = Path(__file__).resolve().parent
SR = 48000
DURATION = 25.0
DEFAULT_EVENTS = {
    "meter_ticks": {"times": [.12, .30, .48, .64, .80, .94, 1.07, 1.19, 1.30, 1.40, 1.48], "gain": .048},
    "meter_lock": {"times": [1.55], "gain": .13},
    "inventory": {"times": [4.75, 4.95, 5.15, 5.35], "gain": .052},
    "pan_sizzle": {"start": 6.50, "end": 7.40, "gain": .028},
    "bacon_snap": {"times": [7.65], "gain": .10},
    "scoop": {"times": [8.50], "gain": .031},
    "drizzle": {"start": 8.90, "end": 9.40, "gain": .014},
    "share_tap": {"times": [13.35], "gain": .080},
    "hearts": {"times": [13.50, 13.68, 13.86, 14.04, 14.24, 14.40], "gain": .024},
    "cuts": {"times": [16.40, 17.60, 18.80, 20.00], "gain": .035},
    "photo_snaps": {"times": [21.20, 21.28, 21.36, 21.44], "gain": .062},
}


def lowpass(signal, cutoff, taps=65):
    """Short windowed-sinc FIR, sufficient for noise/transient sound shaping."""
    index = np.arange(taps) - (taps - 1) / 2
    fc = min(max(float(cutoff), 40.0), SR * .46) / SR
    kernel = 2 * fc * np.sinc(2 * fc * index) * np.hanning(taps)
    kernel /= kernel.sum()
    return np.convolve(signal, kernel, mode="same")


def normalize_peak(signal):
    return signal / max(float(np.max(np.abs(signal))), 1e-12)


def noise(rng, seconds, low=0, high=3200):
    n = max(1, round(seconds * SR))
    raw = rng.standard_normal(n)
    out = lowpass(raw, high)
    if low:
        out -= lowpass(raw, low)
    return normalize_peak(out)


def edge_fade(signal, attack=.002, release=.012):
    n = len(signal)
    a = max(1, min(n, round(attack * SR)))
    b = max(1, min(n, round(release * SR)))
    envelope = np.ones(n)
    envelope[:a] *= np.sin(np.linspace(0, math.pi / 2, a)) ** 2
    envelope[-b:] *= np.sin(np.linspace(math.pi / 2, 0, b)) ** 2
    return signal * envelope


def click(rng, seconds=.035, high=3300):
    out = noise(rng, seconds, 140, high)
    t = np.arange(len(out)) / SR
    out *= np.exp(-t * 150)
    return normalize_peak(edge_fade(out, .0008, .008))


def lock(rng):
    n = round(.11 * SR)
    out = np.zeros(n)
    first = click(rng, .034, 3800)
    out[:len(first)] += first
    thump = noise(rng, .09, 50, 650)
    t = np.arange(len(thump)) / SR
    thump *= np.exp(-t * 50)
    out[round(.008 * SR):round(.008 * SR) + len(thump)] += thump * .60
    return normalize_peak(edge_fade(out, .0005, .020))


def pickup(rng):
    out = noise(rng, .060, 300, 2700)
    t = np.arange(len(out)) / SR
    out *= np.exp(-t * 88)
    return normalize_peak(edge_fade(out, .0015, .015))


def sizzle(rng, seconds):
    out = noise(rng, seconds, 1200, 6500) * .43
    # Irregular little pan bubbles, kept below the steady background sizzle.
    for _ in range(max(1, round(seconds * 34))):
        length = rng.uniform(.004, .012)
        bubble = click(rng, length, rng.uniform(2800, 6200))
        start = int(rng.integers(0, max(1, len(out) - len(bubble))))
        end = min(len(out), start + len(bubble))
        out[start:end] += bubble[:end-start] * rng.uniform(.08, .27)
    return normalize_peak(edge_fade(out, .10, .13))


def crunch(rng):
    out = np.zeros(round(.18 * SR))
    for at, gain, length in [(0, 1, .028), (.012, .62, .035), (.039, .46, .040), (.073, .22, .055)]:
        piece = noise(rng, length, 320, 5700)
        t = np.arange(len(piece)) / SR
        piece = edge_fade(piece * np.exp(-t * 95), .0008, .005)
        start = round(at * SR)
        out[start:start+len(piece)] += piece * gain
    return normalize_peak(edge_fade(out, .0005, .025))


def scoop(rng):
    out = noise(rng, .24, 180, 1550)
    t = np.arange(len(out)) / SR
    envelope = np.sin(np.pi * np.clip(t / .24, 0, 1)) ** 1.8
    # A soft scrape followed by a quiet release, with no tonal pitch bend.
    out *= envelope * (.70 + .30 * np.sin(np.pi * t / .24))
    contact = click(rng, .030, 1700) * .20
    out[:len(contact)] += contact
    return normalize_peak(edge_fade(out, .012, .045))


def drizzle(rng, seconds):
    out = noise(rng, seconds, 170, 2450)
    t = np.arange(len(out)) / SR
    envelope = np.sin(np.pi * np.clip(t / max(seconds, .001), 0, 1)) ** 1.3
    out *= envelope * (.70 + .30 * np.sin(t * 27 + .7))
    return normalize_peak(edge_fade(out, .05, .08))


def air(rng, seconds=.13, high=2500):
    out = noise(rng, seconds, 180, high)
    t = np.arange(len(out)) / SR
    out *= np.sin(np.pi * t / seconds) ** 2
    return normalize_peak(edge_fade(out, .008, .025))


def shutter(rng):
    out = np.zeros(round(.075 * SR))
    for at, gain, length, high in [(0, 1, .026, 3200), (.033, .52, .026, 2100)]:
        piece = click(rng, length, high) * gain
        start = round(at * SR)
        out[start:start+len(piece)] += piece
    return normalize_peak(edge_fade(out, .0005, .012))


def load_events(path=None):
    events = copy.deepcopy(DEFAULT_EVENTS)
    if path:
        payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        overrides = payload.get("events", payload)
        unknown = set(overrides) - set(events)
        if unknown:
            raise ValueError(f"Unknown Foley event names: {sorted(unknown)}")
        for name, values in overrides.items():
            if values is False:
                events[name]["gain"] = 0
            elif isinstance(values, dict):
                events[name].update(values)
            else:
                raise ValueError(f"Event override {name} must be an object or false")
    return events


def make_foley(output=None, events_path=None, seed=11262026):
    output = Path(output or ROOT / "build/audio/breakfast-foley.wav")
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    events = load_events(events_path)
    samples = np.zeros((round(SR * DURATION), 2), dtype=np.float64)
    ledger = []

    def add(signal, at, gain, pan=0, name=""):
        if gain <= 0:
            return
        start = round(float(at) * SR)
        offset = max(0, -start)
        start = max(0, start)
        count = min(len(signal)-offset, len(samples)-start)
        if count <= 0:
            return
        pan = max(-1, min(1, pan))
        left, right = 1-max(pan, 0)*.5, 1+min(pan, 0)*.5
        signal = signal[offset:offset+count] * float(gain)
        samples[start:start+count, 0] += signal * left
        samples[start:start+count, 1] += signal * right
        ledger.append({"event": name, "start_seconds": float(at), "duration_seconds": count/SR, "gain": float(gain)})

    generators = {
        "meter_ticks": lambda: click(rng, .025, 3000),
        "meter_lock": lambda: lock(rng),
        "inventory": lambda: pickup(rng),
        "bacon_snap": lambda: crunch(rng),
        "scoop": lambda: scoop(rng),
        "share_tap": lambda: click(rng, .040, 3300),
        "hearts": lambda: air(rng, .105, 2200),
        "cuts": lambda: air(rng, .13, 2600),
        "photo_snaps": lambda: shutter(rng),
    }
    for name, generator in generators.items():
        config = events[name]
        for index, at in enumerate(config["times"]):
            pan = 0 if name in ("meter_lock", "bacon_snap", "share_tap", "scoop") else (-.18 if index%2 else .18)
            add(generator(), at, config["gain"], pan, name)
    for name, generator in [("pan_sizzle", sizzle), ("drizzle", drizzle)]:
        config = events[name]
        seconds = float(config["end"])-float(config["start"])
        if seconds <= 0:
            raise ValueError(f"{name} end must follow start")
        add(generator(rng, seconds), config["start"], config["gain"], -.06, name)

    # Preserve quiet intended levels. This bound only catches unusually hot overrides.
    peak_before = float(np.max(np.abs(samples)))
    scale = min(1, .18 / max(peak_before, 1e-12))
    samples *= scale
    pcm = (np.clip(samples, -.999, .999) * 32767).astype("<i2")
    with wave.open(str(output), "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    with wave.open(str(output), "rb") as f:
        assert f.getnchannels()==2 and f.getsampwidth()==2 and f.getframerate()==SR
        assert f.getnframes()==round(SR*DURATION)
        check = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(np.float64)/32768
    peak = float(np.max(np.abs(check)))
    rms = float(np.sqrt(np.mean(check**2)))
    assert peak < .181 and np.isfinite(check).all()
    return {"output":str(output.resolve()), "duration_seconds":DURATION, "sample_rate":SR,
            "channels":2, "sample_width_bits":16, "peak_dbfs":round(20*math.log10(max(peak, 1e-12)), 2),
            "rms_dbfs":round(20*math.log10(max(rms, 1e-12)), 2), "override_bound_scale":scale,
            "non_vocal":True, "generated_locally":True, "events":ledger}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--events", type=Path, help="JSON named-event overrides; false disables an event")
    parser.add_argument("--seed", type=int, default=11262026)
    args = parser.parse_args()
    print(json.dumps(make_foley(args.output, args.events, args.seed), indent=2))
