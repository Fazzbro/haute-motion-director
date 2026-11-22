#!/usr/bin/env python3
"""
saas-code-sfx — Pure-Code Tactile SaaS SFX Synthesis & Timeline Mastering Engine
================================================================================
Generates musical, organic, non-repetitive, zero-fatigue sound effects purely in
Python (NumPy + SciPy) for SaaS product launches, UI walkthroughs, and motion
design (HyperFrames, Remotion, After Effects, FFmpeg).

Acoustic DNA calibrated from forensic DSP analysis of elite motion design:
- Scale-locked pitch grammar (zero dissonant arbitrary beeps)
- Polymorphic Variation Engine (no two consecutive events share identical timbre)
- Fletcher-Munson anti-fatigue spectral curve (<2% energy in 5-9 kHz harsh zone)
- Physical/modal modeling (Minnaert bubble pops, dual-stage Topre switches,
  formant-swept silk whooshes, FM modal glass chimes, damped stereo micro-plate)
- 100% deterministic seeded synthesis (reproducible builds, zero external samples)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000

# =============================================================================
# 1. MUSICAL SCALE ENGINE (Scale-Locked Pitch Grammar)
# =============================================================================

NOTE_TO_SEMITONE = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

# Scale presets: (root_midi_base_octave4, semitone_intervals)
# Default "b_minor_pent" / "e_minor9" matches the Hazene / System Zero harmonic DNA.
SCALES: Dict[str, Tuple[int, List[int]]] = {
    "b_minor_pent": (59, [0, 3, 5, 7, 10]),         # B, D, E, F#, A (Hazene/System Zero)
    "e_minor9":     (52, [0, 2, 3, 7, 10, 14]),     # E, F#, G, B, D, F# (Lush glassy SaaS)
    "d_major_pent": (62, [0, 2, 4, 7, 9]),          # D, E, F#, A, B (Bright friendly SaaS)
    "c_major9":     (60, [0, 2, 4, 7, 9, 11]),      # C, D, E, G, A, B (Editorial / Apple)
    "f_major_pent": (53, [0, 2, 4, 7, 9]),          # F, G, A, C, D (Warm consumer)
    "a_minor_pent": (57, [0, 3, 5, 7, 10]),         # A, C, D, E, G (Sleek dev-tool)
    "g_lydian":     (55, [0, 2, 4, 6, 7, 9, 11]),   # G, A, B, C#, D, E, F# (Futurist / AI)
}


def midi_to_hz(midi_note: float) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))


def scale_freq(
    scale_name: str,
    degree: int,
    octave: int = 0,
    detune_cents: float = 0.0,
) -> float:
    root_midi, intervals = SCALES.get(scale_name, SCALES["b_minor_pent"])
    n = len(intervals)
    oct_offset, idx = divmod(degree, n)
    midi = root_midi + intervals[idx] + 12 * (octave + oct_offset) + (detune_cents / 100.0)
    return midi_to_hz(midi)


# =============================================================================
# 2. CORE DSP UTILITIES
# =============================================================================

def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)


def ensure_stereo(x: np.ndarray, pan: float = 0.0) -> np.ndarray:
    """Convert mono (N,) or stereo (N,2) to equal-power panned stereo (N,2)."""
    pan = float(np.clip(pan, -0.85, 0.85))
    angle = (pan + 1.0) * (math.pi / 4.0)
    gL, gR = math.cos(angle), math.sin(angle)
    if x.ndim == 1:
        return np.stack([x * gL, x * gR], axis=1)
    # Apply subtle balance shift to stereo signal
    L = x[:, 0] * (gL * math.sqrt(2.0))
    R = x[:, 1] * (gR * math.sqrt(2.0))
    return np.stack([L, R], axis=1)


def micro_fade(x: np.ndarray, fade_in_ms: float = 3.0, fade_out_ms: float = 12.0, sr: int = SR) -> np.ndarray:
    """Apply smooth raised-cosine fades to eliminate any edge clicks."""
    n = x.shape[0]
    fi = min(int(fade_in_ms * sr / 1000.0), n // 2)
    fo = min(int(fade_out_ms * sr / 1000.0), n // 2)
    out = x.copy()
    if fi > 1:
        ramp = 0.5 * (1.0 - np.cos(np.linspace(0.0, math.pi, fi)))
        if out.ndim == 2:
            out[:fi] *= ramp[:, None]
        else:
            out[:fi] *= ramp
    if fo > 1:
        ramp = 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fo)))
        if out.ndim == 2:
            out[-fo:] *= ramp[:, None]
        else:
            out[-fo:] *= ramp
    return out


def sos_filter(x: np.ndarray, btype: str, cutoff: Any, order: int = 2, sr: int = SR) -> np.ndarray:
    nyq = 0.5 * sr
    if isinstance(cutoff, (list, tuple)):
        wn = [max(10.0, min(nyq * 0.95, float(c))) / nyq for c in cutoff]
        if wn[0] >= wn[1]:
            wn[1] = min(0.96, wn[0] + 0.02)
    else:
        wn = max(10.0, min(nyq * 0.95, float(cutoff))) / nyq
    sos = signal.butter(order, wn, btype=btype, output="sos")
    if x.ndim == 2:
        return np.stack([signal.sosfilt(sos, x[:, 0]), signal.sosfilt(sos, x[:, 1])], axis=1)
    return signal.sosfilt(sos, x)


def resonant_bp(x: np.ndarray, f0: float, q: float = 4.0, sr: int = SR) -> np.ndarray:
    """Zero-artifact biquad bandpass filter for physical/modal body resonance."""
    f0 = float(np.clip(f0, 30.0, sr * 0.45))
    q = float(max(0.4, q))
    w0 = 2.0 * math.pi * f0 / sr
    alpha = math.sin(w0) / (2.0 * q)
    b = np.array([alpha, 0.0, -alpha])
    a = np.array([1.0 + alpha, -2.0 * math.cos(w0), 1.0 - alpha])
    if x.ndim == 2:
        return np.stack([signal.lfilter(b, a, x[:, 0]), signal.lfilter(b, a, x[:, 1])], axis=1)
    return signal.lfilter(b, a, x)


def peaking_eq(x: np.ndarray, f0: float, gain_db: float, q: float = 1.0, sr: int = SR) -> np.ndarray:
    """RBJ Audio EQ Cookbook peaking bell filter."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * float(np.clip(f0, 20.0, sr * 0.45)) / sr
    alpha = math.sin(w0) / (2.0 * max(0.2, q))
    b0 = 1.0 + alpha * A
    b1 = -2.0 * math.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * math.cos(w0)
    a2 = 1.0 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    if x.ndim == 2:
        return np.stack([signal.lfilter(b, a, x[:, 0]), signal.lfilter(b, a, x[:, 1])], axis=1)
    return signal.lfilter(b, a, x)


def high_shelf(x: np.ndarray, f0: float, gain_db: float, slope: float = 0.7, sr: int = SR) -> np.ndarray:
    """RBJ Audio EQ Cookbook high-shelf filter for smooth analog warmth roll-off."""
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * float(np.clip(f0, 200.0, sr * 0.45)) / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / 2.0 * math.sqrt((A + 1.0 / A) * (1.0 / slope - 1.0) + 2.0)
    sq = 2.0 * math.sqrt(A) * alpha
    b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + sq)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - sq)
    a0 = (A + 1.0) - (A - 1.0) * cos_w0 + sq
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
    a2 = (A + 1.0) - (A - 1.0) * cos_w0 - sq
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    if x.ndim == 2:
        return np.stack([signal.lfilter(b, a, x[:, 0]), signal.lfilter(b, a, x[:, 1])], axis=1)
    return signal.lfilter(b, a, x)


def pink_noise(n: int, rng: np.random.Generator) -> np.ndarray:
    """Voss-McCartney / spectral 1/f pink noise (warmer & silkier than white noise)."""
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    scale = 1.0 / np.maximum(freqs, 20.0) ** 0.55
    scale[0] = 0.0
    pink = np.fft.irfft(spec * scale, n=n)
    pink /= np.max(np.abs(pink)) + 1e-12
    return pink


def micro_plate_reverb(
    stereo: np.ndarray,
    wet: float = 0.14,
    decay_s: float = 0.48,
    damping_hz: float = 2800.0,
    sr: int = SR,
) -> np.ndarray:
    """
    Lightweight, silky, deterministic stereo micro-plate reverb built via
    modulated-free prime-delay impulse response convolution (zero metallic ringing).
    """
    if wet <= 0.001:
        return stereo
    ir_len = int(max(0.25, decay_s * 2.4) * sr)
    rng = np.random.default_rng(77193)
    t = np.arange(ir_len) / sr
    # Smooth exponential envelope with 12ms pre-delay & gentle 15ms onset bloom
    pre = int(0.012 * sr)
    env = np.zeros(ir_len)
    t_eff = np.maximum(0.0, t - 0.012)
    env[pre:] = np.exp(-6.9 * t_eff[pre:] / max(0.12, decay_s)) * (
        1.0 - np.exp(-t_eff[pre:] / 0.014)
    )
    # Decorrelated L/R dense velvet noise IRs
    ir_L = rng.standard_normal(ir_len) * env
    ir_R = rng.standard_normal(ir_len) * env
    # Heavy high-frequency damping so reverb tail stays warm & glassy, never hissy
    ir_L = sos_filter(ir_L, "bandpass", [180.0, damping_hz], order=2, sr=sr)
    ir_R = sos_filter(ir_R, "bandpass", [180.0, damping_hz], order=2, sr=sr)
    norm = math.sqrt(np.sum(ir_L**2) + 1e-12)
    ir_L /= norm
    ir_R /= norm

    wet_L = signal.fftconvolve(stereo[:, 0], ir_L, mode="full")[: stereo.shape[0]]
    wet_R = signal.fftconvolve(stereo[:, 1], ir_R, mode="full")[: stereo.shape[0]]
    # Cross-feed 20% for lush stereo glue
    out_L = stereo[:, 0] * (1.0 - wet * 0.3) + (0.8 * wet_L + 0.2 * wet_R) * wet
    out_R = stereo[:, 1] * (1.0 - wet * 0.3) + (0.8 * wet_R + 0.2 * wet_L) * wet
    return np.stack([out_L, out_R], axis=1)


# =============================================================================
# 3. POLYMORPHIC ANTI-REPETITION ENGINE
# =============================================================================

@dataclass
class PolymorphicState:
    """
    Guarantees no two consecutive triggers of any SFX family ever sound identical.
    Tracks call counts, melodic walk position, and last timbre parameters.
    """
    seed: int = 42
    scale: str = "b_minor_pent"
    counts: Dict[str, int] = field(default_factory=dict)
    last_degree: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rng = np.random.default_rng(self.seed)

    def next_variant(self, family: str, explicit_degree: Optional[int] = None) -> Dict[str, float]:
        idx = self.counts.get(family, 0)
        self.counts[family] = idx + 1

        # Pick non-repeating scale degree using smooth musical step-walk
        prev = self.last_degree.get(family, -999)
        if explicit_degree is not None:
            deg = explicit_degree
        else:
            # Musical contour: gentle arpeggiated step without repeating identical note
            candidates = [0, 1, 2, 3, 4, 2, 3, 5]
            deg = candidates[idx % len(candidates)]
            if deg == prev:
                deg += 1
        self.last_degree[family] = deg

        # Bounded organic micro-variations (perceptually fresh, aesthetically cohesive)
        detune_cents = float(self.rng.uniform(-14.0, 14.0))
        cutoff_mul = float(self.rng.uniform(0.86, 1.16))
        decay_mul = float(self.rng.uniform(0.88, 1.14))
        vel_db = float(self.rng.uniform(-2.6, 0.4))
        # Natural stereo micro-drift unless caller overrides pan
        pan_jitter = float(self.rng.uniform(-0.16, 0.16))

        return {
            "idx": float(idx),
            "degree": float(deg),
            "detune_cents": detune_cents,
            "cutoff_mul": cutoff_mul,
            "decay_mul": decay_mul,
            "vel_db": vel_db,
            "pan_jitter": pan_jitter,
        }


# =============================================================================
# 4. THE 14 SIGNATURE ORGANIC SAAS SFX GENERATORS
# =============================================================================

def synth_glass_chime(
    state: PolymorphicState,
    degree: int = 0,
    octave: int = 0,
    duration: float = 0.90,
    brightness: float = 0.42,
    pan: Optional[float] = None,
    gain_db: float = -7.5,
) -> np.ndarray:
    """
    Warm felt-glass SaaS hero bell / startup chime / resolve ping.
    Enforces Anti-Piercing Constraints:
    - Warm fundamental dominance (240-660 Hz body; partials >800 Hz kept >=6 dB down)
    - 3-voice micro-chorused ensemble spread ([-9, 0, +9 cents]) with randomized
      initial phases (eliminates 35+ dB razor-thin sine tuning-fork spikes!)
    - Felt-mallet soft onset (22ms rounded rise, zero startling attack sting)
    - Subtle warm air cushion + 3.2 kHz analog low-pass silk filter
    """
    v = state.next_variant("glass_chime", explicit_degree=degree)
    rng = state.rng
    # Soft-clamp brightness so callers can't accidentally re-introduce piercing upper partials
    brightness = float(np.clip(brightness, 0.15, 0.55))
    f0 = scale_freq(state.scale, int(v["degree"]), octave=octave, detune_cents=v["detune_cents"] * 0.4)
    # Keep fundamental strictly in the warm non-piercing sweet spot (230 - 540 Hz)
    while f0 > 540.0:
        f0 *= 0.5
    while f0 < 230.0:
        f0 *= 2.0

    dur = max(0.30, duration * v["decay_mul"])
    n = int(dur * SR)
    t = np.arange(n) / SR

    # Warm fundamental-dominant partials (upper partials strictly subdued >=8 dB)
    partials = [
        (0.500, 0.40, 0.95),                # lush warm sub-octave foundation
        (1.000, 1.00, 1.00),                # primary warm fundamental
        (1.500, 0.20 * brightness, 0.60),   # soft fifth warmth (Rhodes-like)
        (2.000, 0.16 * brightness, 0.40),   # gentle octave shimmer
        (3.000, 0.05 * brightness, 0.22),   # delicate glass glint (decays fast)
    ]
    # 3-voice unison spread smears narrowband spikes across the auditory critical band
    unison_cents = (-12.0, 0.0, 12.0)
    unison_pan_L = (0.78, 0.50, 0.22)
    unison_pan_R = (0.22, 0.50, 0.78)

    L = np.zeros(n)
    R = np.zeros(n)
    base_tau = dur * 0.36
    # Velvet felt-mallet attack (~24ms smooth S-curve, zero click or sting)
    attack = (1.0 - np.exp(-t / 0.020)) ** 1.6

    for ratio, amp, tau_mul in partials:
        f_p = f0 * ratio
        if f_p > 2800.0:
            continue
        env = attack * np.exp(-t / (base_tau * tau_mul))
        # Subtle slow organic pitch drift (1.5 Hz, ±3 cents) like acoustic glass/tine
        drift_phase = 0.0016 * np.sin(2.0 * math.pi * (1.4 + 0.3 * ratio) * t)
        for c_off, wL, wR in zip(unison_cents, unison_pan_L, unison_pan_R):
            f_u = f_p * (2.0 ** (c_off / 1200.0))
            ph0 = float(rng.uniform(0.0, 2.0 * math.pi))  # random phase prevents peak stacking!
            wave = np.sin(2.0 * math.pi * f_u * t + ph0 + drift_phase)
            L += (amp / 3.0) * env * wave * wL
            R += (amp / 3.0) * env * wave * wR

    # Organic felt-mallet & studio air body (fills sterile digital vacuum between
    # partials so 800-4000 Hz never behaves like a razor-thin tuning-fork spike)
    air = pink_noise(n, rng)
    air_mid = sos_filter(air, "bandpass", [320.0, 2600.0], order=2)
    air_env = (1.0 - np.exp(-t / 0.024)) * np.exp(-t / (dur * 0.32))
    L += air_mid * air_env * 0.14
    R += np.roll(air_mid, 23) * air_env * 0.14

    stereo = np.stack([L, R], axis=1)
    # Warm analog rounding & gentle low-pass ceiling at 2.9 kHz
    stereo = sos_filter(stereo, "lowpass", 2900.0, order=2)
    stereo /= np.max(np.abs(stereo)) + 1e-12
    stereo = np.tanh(stereo * 1.15) / math.tanh(1.15)
    stereo = ensure_stereo(stereo, pan if pan is not None else v["pan_jitter"] * 0.5)
    stereo = micro_fade(stereo, 14.0, 55.0)
    return stereo * db_to_lin(gain_db)


def synth_chord_bloom(
    state: PolymorphicState,
    degrees: Optional[List[int]] = None,
    octave: int = 0,
    duration: float = 1.85,
    strum_ms: float = 42.0,
    pan: float = 0.0,
    gain_db: float = -7.5,
) -> np.ndarray:
    """
    Lush, velvet open-voiced OS startup / brand outro chord bloom.
    Uses wide 42ms harp stagger, warm low-mid voicing, randomized phases, and a
    75ms silk envelope swell so the very first sound eases in with zero peak sting.
    """
    degs = degrees if degrees is not None else [0, 2, 3, 4]
    n_total = int((duration + len(degs) * strum_ms / 1000.0 + 0.15) * SR)
    out = np.zeros((n_total, 2))
    pan_spread = np.linspace(-0.20, 0.20, len(degs))
    for i, d in enumerate(degs):
        # Keep chord voiced in warm mid-low register (octave 0, never piercing high!)
        note = synth_glass_chime(
            state,
            degree=d,
            octave=octave,
            duration=duration * (1.0 - i * 0.04),
            brightness=0.34 + 0.05 * i,
            pan=float(np.clip(pan + pan_spread[i], -0.40, 0.40)),
            gain_db=-3.0 - i * 1.4,
        )
        start = int(i * strum_ms * SR / 1000.0)
        end = min(n_total, start + note.shape[0])
        out[start:end] += note[: end - start]

    # Velvet 75ms intro bloom swell (matching Hazene's 85ms soft intro rise!)
    t = np.arange(n_total) / SR
    bloom_env = (1.0 - np.exp(-t / 0.055)) ** 1.3
    out *= bloom_env[:, None]

    # Tame ear-sensitive 1.2-3.2 kHz region slightly so chord feels warm & wide
    out = peaking_eq(out, f0=1800.0, gain_db=-2.5, q=0.9)
    out = sos_filter(out, "lowpass", 2900.0, order=2)
    out /= np.max(np.abs(out)) + 1e-12
    out = micro_fade(out, 28.0, 140.0)
    return out * db_to_lin(gain_db)


def synth_liquid_pop(
    state: PolymorphicState,
    degree: Optional[int] = None,
    octave: int = 0,
    direction: str = "up",
    size: str = "medium",
    pan: Optional[float] = None,
    gain_db: float = -4.0,
) -> np.ndarray:
    """
    Signature Hazene / Apple / Linear organic bubble-droplet pop (Minnaert physics).
    Exponential pitch chirp of a pure warm tone with microscopic woody transient.
    Perfect for window opens, modals, tooltips, and mascot appearances.
    """
    v = state.next_variant("liquid_pop", explicit_degree=degree)
    f_base = scale_freq(state.scale, int(v["degree"]), octave=octave, detune_cents=v["detune_cents"])
    size_cfg = {
        "small":  (1.35, 0.068, 1.55),
        "medium": (1.00, 0.095, 1.68),
        "large":  (0.68, 0.135, 1.75),
    }
    f_mul, base_dur, ratio = size_cfg.get(size, size_cfg["medium"])
    f0 = float(np.clip(f_base * f_mul, 180.0, 1150.0))
    dur = base_dur * v["decay_mul"]
    n = int(dur * SR)
    t = np.arange(n) / SR

    # Exponential Minnaert frequency glide
    sweep_tau = dur * 0.42
    if direction == "down":
        f_inst = f0 * (1.0 + (ratio - 1.0) * np.exp(-t / sweep_tau))
    else:
        f_inst = f0 * (1.0 + (ratio - 1.0) * (1.0 - np.exp(-t / sweep_tau)))

    phase = 2.0 * math.pi * np.cumsum(f_inst) / SR
    # Smooth bubble envelope: 2.5ms cosine rise, clean exponential body
    env = (1.0 - np.exp(-t / 0.0022)) * np.exp(-t / (dur * 0.30))
    tone = np.sin(phase) + 0.11 * np.sin(2.0 * phase) * np.exp(-t / (dur * 0.16))

    # Tiny woody/surface tension micro-click on onset (<4ms)
    rng = state.rng
    burst = rng.standard_normal(n) * np.exp(-t / 0.0025)
    burst = resonant_bp(burst, f0 * 2.2 * v["cutoff_mul"], q=3.2) * 0.14

    mono = (tone * env + burst)
    mono = sos_filter(mono, "lowpass", 3600.0 * v["cutoff_mul"], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan if pan is not None else v["pan_jitter"])
    stereo = micro_fade(stereo, 2.0, 12.0)
    return stereo * db_to_lin(gain_db + v["vel_db"] * 0.5)


def synth_bubble_cascade(
    state: PolymorphicState,
    count: int = 4,
    start_degree: int = 0,
    step: int = 1,
    spacing_ms: float = 58.0,
    direction: str = "up",
    pan_start: float = -0.18,
    pan_end: float = 0.18,
    gain_db: float = -4.5,
) -> np.ndarray:
    """
    Playful ascending/descending liquid arpeggio (heard in System Zero outro 29.1-29.7s
    and multi-item menu reveals). Accelerates slightly with natural phrasing.
    """
    count = int(np.clip(count, 2, 8))
    events = []
    t_cur = 0.0
    for i in range(count):
        deg = start_degree + i * step * (1 if direction == "up" else -1)
        p = pan_start + (pan_end - pan_start) * (i / max(1, count - 1))
        # Subtle dynamic swell peaking near penultimate note
        dyn = -3.0 + 3.0 * math.sin(math.pi * (i + 0.5) / count)
        pop = synth_liquid_pop(
            state,
            degree=deg,
            octave=0 if i < 3 else 1,
            direction=direction,
            size="medium" if i < count - 1 else "small",
            pan=p,
            gain_db=gain_db + dyn,
        )
        events.append((int(t_cur * SR), pop))
        # Subtle natural acceleration (0.94x per step) + micro-humanize
        dt = (spacing_ms / 1000.0) * (0.94 ** i) * float(state.rng.uniform(0.92, 1.08))
        t_cur += dt

    total_len = max(s + ev.shape[0] for s, ev in events) + int(0.05 * SR)
    out = np.zeros((total_len, 2))
    for s, ev in events:
        out[s : s + ev.shape[0]] += ev
    return out


def synth_tactile_click(
    state: PolymorphicState,
    style: str = "mouse",
    double_stage: bool = True,
    pan: Optional[float] = None,
    gain_db: float = -4.5,
) -> np.ndarray:
    """
    Premium physical micro-switch / mouse click / toggle actuation.
    Dual-modal woody/polycarbonate resonator (body + crisp snap) with optional
    28ms-delayed release micro-click. Completely free of harsh 6kHz screech.
    """
    v = state.next_variant("tactile_click")
    rng = state.rng
    dur = 0.085 if double_stage else 0.045
    n = int(dur * SR)
    t = np.arange(n) / SR

    def one_switch(f_body: float, f_snap: float, amp: float) -> np.ndarray:
        # Ultra-short impulse excitation (1.2ms)
        imp = np.zeros(n)
        imp_n = int(0.0014 * SR)
        imp[:imp_n] = rng.standard_normal(imp_n) * np.hanning(imp_n * 2)[:imp_n]
        # Damped physical modal resonators
        body = resonant_bp(imp, f_body, q=3.8) * 1.4
        snap = resonant_bp(imp, f_snap, q=2.8) * 0.85
        # Soft sub-tactile membrane thump
        thump = np.sin(2.0 * math.pi * (f_body * 0.42) * t) * np.exp(-t / 0.0065) * 0.45
        sig = (body + snap + thump) * np.exp(-t / 0.011)
        return sig * amp

    if style == "toggle":
        f_b, f_s = 520.0 * v["cutoff_mul"], 1950.0 * v["cutoff_mul"]
    elif style == "soft":
        f_b, f_s = 340.0 * v["cutoff_mul"], 1350.0 * v["cutoff_mul"]
    else:  # mouse
        f_b, f_s = 440.0 * v["cutoff_mul"], 1780.0 * v["cutoff_mul"]

    mono = one_switch(f_b, f_s, 1.0)
    if double_stage:
        rel_delay = int(float(rng.uniform(0.024, 0.034)) * SR)
        rel = one_switch(f_b * 1.24, f_s * 1.15, 0.48)
        if rel_delay < n:
            mono[rel_delay:] += rel[: n - rel_delay]

    mono = sos_filter(mono, "bandpass", [110.0, 4400.0], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan if pan is not None else v["pan_jitter"] * 0.7)
    stereo = micro_fade(stereo, 0.6, 8.0)
    return stereo * db_to_lin(gain_db + v["vel_db"] * 0.4)


def synth_topre_key(
    state: PolymorphicState,
    is_space_or_enter: bool = False,
    pan: Optional[float] = None,
    gain_db: float = -7.5,
) -> np.ndarray:
    """
    Warm, dampened Topre / lubed linear mechanical keystroke.
    Low rubber-dome 'thock' + subtle dampened keycap knock. Auto-varies pitch,
    timbre, and velocity so rapid typing streams sound organic & ASMR-grade.
    """
    v = state.next_variant("topre_key")
    rng = state.rng
    dur = 0.060 if is_space_or_enter else 0.042
    n = int(dur * SR)
    t = np.arange(n) / SR

    # Rubber dome thock (pitch drops slightly on impact)
    f_thock = (145.0 if is_space_or_enter else 205.0) * float(rng.uniform(0.88, 1.14))
    f_inst = f_thock * (1.0 + 0.55 * np.exp(-t / 0.004))
    phase = 2.0 * math.pi * np.cumsum(f_inst) / SR
    thock = np.sin(phase) * np.exp(-t / (0.014 if is_space_or_enter else 0.009))

    # Subtle PBT keycap transient (filtered mid-band, zero metallic ring)
    imp = rng.standard_normal(n) * np.exp(-t / 0.0032)
    cap_f = (920.0 if is_space_or_enter else 1480.0) * v["cutoff_mul"]
    cap = resonant_bp(imp, cap_f, q=2.6) * (0.55 if is_space_or_enter else 0.75)

    # Bottom-out housing resonance
    housing = resonant_bp(imp, 520.0 * v["cutoff_mul"], q=3.5) * 0.45

    mono = thock * 0.85 + cap + housing
    mono = sos_filter(mono, "bandpass", [85.0, 3600.0], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan if pan is not None else v["pan_jitter"])
    stereo = micro_fade(stereo, 0.8, 7.0)
    return stereo * db_to_lin(gain_db + v["vel_db"])


def synth_hover_tick(
    state: PolymorphicState,
    degree: Optional[int] = None,
    octave: int = 1,
    pan: Optional[float] = None,
    gain_db: float = -8.0,
) -> np.ndarray:
    """
    Ultra-crisp, dry tactile ceramic/wood micro-tick for context menu hovers &
    list scrubbing. Short decay (18-26ms) with subtle scale-locked pitch contour
    so it feels sleek and tactile rather than boomy or video-gamey.
    """
    v = state.next_variant("hover_tick", explicit_degree=degree)
    f0 = scale_freq(state.scale, int(v["degree"]), octave=octave, detune_cents=v["detune_cents"] * 0.5)
    while f0 > 1800.0:
        f0 *= 0.5
    while f0 < 520.0:
        f0 *= 2.0

    dur = 0.032 * v["decay_mul"]
    n = int(dur * SR)
    t = np.arange(n) / SR

    # Short ceramic/wood modal tap + gentle pitched fundamental
    f_env = f0 * (1.0 + 0.12 * np.exp(-t / 0.0022))
    ph = 2.0 * math.pi * np.cumsum(f_env) / SR
    body = np.sin(ph) * np.exp(-t / (dur * 0.18)) * 0.72
    # Tactile tap excitation (filtered micro-impulse at 2.2-3.4 kHz)
    imp = state.rng.standard_normal(n) * np.exp(-t / 0.0018)
    tap = resonant_bp(imp, min(3600.0, f0 * 2.4) * v["cutoff_mul"], q=3.2) * 0.65
    mono = (body + tap) * (1.0 - np.exp(-t / 0.0008))
    mono = sos_filter(mono, "bandpass", [220.0, 4600.0], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan if pan is not None else v["pan_jitter"])
    stereo = micro_fade(stereo, 0.6, 6.0)
    return stereo * db_to_lin(gain_db + v["vel_db"] * 0.5)


def synth_silk_whoosh(
    state: PolymorphicState,
    duration: float = 0.36,
    direction: str = "in",
    weight: str = "medium",
    pan_start: float = -0.25,
    pan_end: float = 0.25,
    gain_db: float = -7.0,
) -> np.ndarray:
    """
    Warm brushed-silk air transition whoosh (NEVER harsh white-noise hiss!).
    Dual-formant sweeping bandpass on 1/f pink noise + sub-air cushion, hard-tamed
    above 3.4 kHz. Moves gently across the stereo field.
    """
    v = state.next_variant("silk_whoosh")
    dur = max(0.16, duration * v["decay_mul"])
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur  # 0..1

    # Asymmetric aerodynamic pressure envelope (Beta-like curve)
    if direction == "out":
        env = (u ** 0.75) * ((1.0 - u) ** 2.2)
    else:
        env = (u ** 1.6) * ((1.0 - u) ** 1.35)
    env /= np.max(env) + 1e-12

    noise = pink_noise(n, state.rng)
    # Time-varying formant sweep via crossfaded multi-band filterbank (smooth, zero zipper noise!)
    w_cfg = {
        "light":  (420.0, 1450.0, 2600.0),
        "medium": (260.0, 920.0, 1950.0),
        "heavy":  (140.0, 560.0, 1300.0),
    }
    f_lo, f_mid, f_hi = [f * v["cutoff_mul"] for f in w_cfg.get(weight, w_cfg["medium"])]

    b_lo = sos_filter(noise, "bandpass", [f_lo * 0.65, f_lo * 1.55], order=2)
    b_mid = sos_filter(noise, "bandpass", [f_mid * 0.65, f_mid * 1.45], order=2)
    b_hi = sos_filter(noise, "bandpass", [f_hi * 0.70, min(3600.0, f_hi * 1.35)], order=2)

    # Smooth trajectory across bands
    if direction == "out":
        w_hi = np.clip(1.0 - u * 1.6, 0.0, 1.0) ** 1.2
        w_mid = np.sin(math.pi * u) ** 1.3
        w_lo = np.clip((u - 0.25) / 0.75, 0.0, 1.0) ** 1.2
    else:
        w_lo = np.clip(1.0 - u * 1.5, 0.0, 1.0) ** 1.2
        w_mid = np.sin(math.pi * u) ** 1.2
        w_hi = np.clip((u - 0.30) / 0.70, 0.0, 1.0) ** 1.4

    air = (b_lo * w_lo * 0.9 + b_mid * w_mid * 1.0 + b_hi * w_hi * 0.55) * env

    # Subtle sub-air physical movement
    sub_f = (95.0 if weight == "heavy" else 130.0) * (1.0 + 0.35 * np.sin(math.pi * u))
    sub = np.sin(2.0 * math.pi * np.cumsum(sub_f) / SR) * env * 0.16

    mono = sos_filter(air + sub, "lowpass", 3400.0, order=2)
    mono /= np.max(np.abs(mono)) + 1e-12

    # Smooth dynamic stereo pan trajectory
    pan_curve = np.linspace(pan_start, pan_end, n)
    angle = (np.clip(pan_curve, -0.75, 0.75) + 1.0) * (math.pi / 4.0)
    stereo = np.stack([mono * np.cos(angle), mono * np.sin(angle)], axis=1)
    stereo = micro_fade(stereo, 10.0, 22.0)
    return stereo * db_to_lin(gain_db)


def synth_progress_glide(
    state: PolymorphicState,
    duration: float = 0.55,
    start_degree: int = 0,
    end_degree: int = 2,
    octave: int = 1,
    with_lock_tick: bool = True,
    pan: float = 0.0,
    gain_db: float = -7.5,
) -> np.ndarray:
    """
    Sleek crystalline air-shimmer + subtle scale-locked harmonic rise for
    progress bars, benchmark fills, and loading wipes. Avoids cartoon slide-whistle
    tones by blending airy formant silk with a quiet, refined upper-register shimmer.
    """
    v = state.next_variant("progress_glide")
    f1 = scale_freq(state.scale, start_degree, octave=octave)
    f2 = scale_freq(state.scale, end_degree, octave=octave)
    if f2 <= f1:
        f2 = f1 * 1.25  # refined gentle major-3rd lift max (never cartoon siren)
    elif f2 / f1 > 1.52:
        f2 = f1 * 1.50  # cap at perfect fifth for sleek sophistication

    n = int((duration + 0.14) * SR)
    n_gl = int(duration * SR)
    t_gl = np.arange(n_gl) / SR
    u = t_gl / max(1e-6, duration)

    # Ease-out aerodynamic swell
    ease = 1.0 - (1.0 - u) ** 2.6
    env = (u ** 0.7) * ((1.0 - u) ** 1.15)
    env /= np.max(env) + 1e-12

    # 1. Primary layer: silky rising bandpass air sweep (65% of energy -> modern UI feel)
    air_raw = pink_noise(n_gl, state.rng)
    b1 = sos_filter(air_raw, "bandpass", [480.0, 1250.0], order=2)
    b2 = sos_filter(air_raw, "bandpass", [1200.0, 2650.0], order=2)
    b3 = sos_filter(air_raw, "bandpass", [2200.0, 4100.0], order=2)
    air = (b1 * (1.0 - ease) * 0.75 + b2 * np.sin(math.pi * ease) * 0.95 + b3 * ease * 0.65) * env

    # 2. Secondary layer: delicate glassy harmonic sheen (two detuned sines, subtle)
    f_inst = f1 * ((f2 / f1) ** ease)
    ph = 2.0 * math.pi * np.cumsum(f_inst) / SR
    sheen = (np.sin(ph) * 0.28 + np.sin(2.0 * ph) * 0.12) * env

    mono = np.zeros(n)
    mono[:n_gl] = air * 0.78 + sheen * 0.42
    mono = sos_filter(mono, "bandpass", [260.0, 4400.0], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan) * db_to_lin(gain_db)

    if with_lock_tick:
        tick = synth_hover_tick(state, degree=end_degree, octave=octave, pan=pan, gain_db=gain_db + 1.5)
        idx = min(n - 1, int(duration * 0.90 * SR))
        end = min(n, idx + tick.shape[0])
        stereo[idx:end] += tick[: end - idx]

    return micro_fade(stereo, 10.0, 24.0)


def synth_counter_ratchet(
    state: PolymorphicState,
    duration: float = 0.95,
    ticks: int = 10,
    start_degree: int = 0,
    with_resolve_chime: bool = True,
    pan: float = 0.0,
    gain_db: float = -6.5,
) -> np.ndarray:
    """
    Decelerating kinetic counter / percentage odometer cascade (74% -> 93%).
    Starts brisk, eases out naturally like a precision Swiss dial, and optionally
    resolves with a soft glassy confirmation chime.
    """
    ticks = int(np.clip(ticks, 3, 24))
    n = int((duration + 0.9) * SR)
    out = np.zeros((n, 2))

    # Ease-out tick times (denser early, wider near target value)
    u_pts = np.linspace(0.0, 1.0, ticks)
    times = duration * (1.0 - (1.0 - u_pts) ** 1.65)
    for i, t_ev in enumerate(times):
        deg = start_degree + (i % 5)
        vel_mod = -4.0 + 4.0 * (i / max(1, ticks - 1))
        tick = synth_hover_tick(
            state,
            degree=deg,
            octave=1,
            pan=pan + float(state.rng.uniform(-0.08, 0.08)),
            gain_db=gain_db + vel_mod,
        )
        s = int(t_ev * SR)
        e = min(n, s + tick.shape[0])
        out[s:e] += tick[: e - s]

    if with_resolve_chime:
        chime = synth_glass_chime(
            state,
            degree=start_degree + 4,
            octave=0,
            duration=0.65,
            brightness=0.38,
            pan=pan,
            gain_db=gain_db - 1.5,
        )
        s = int(duration * SR)
        e = min(n, s + chime.shape[0])
        out[s:e] += chime[: e - s]

    return micro_fade(out, 2.0, 35.0)


def synth_dither_flutter(
    state: PolymorphicState,
    duration: float = 0.24,
    grains: int = 8,
    pan: float = 0.0,
    gain_db: float = -8.5,
) -> np.ndarray:
    """
    Refined retro-digital dither / pixel-morph texture (System One -> System Zero).
    Ultra-crisp 5-10ms filtered telemetry micro-clicks + delicate airy shimmer:
    tactile pixel-snap texture without cartoon pitch trills or harsh bitcrush hiss.
    """
    v = state.next_variant("dither_flutter")
    n = int((duration + 0.06) * SR)
    out = np.zeros((n, 2))
    rng = state.rng
    gn = int(0.009 * SR)  # crisp 9ms micro-grains

    # Subtle filtered air texture bed behind the pixel grains
    bed_n = int(duration * SR)
    u_bed = np.linspace(0.0, 1.0, bed_n)
    air = pink_noise(bed_n, rng)
    air = sos_filter(air, "bandpass", [1100.0, 3800.0], order=2) * (np.sin(math.pi * u_bed) ** 1.4) * 0.22
    out[:bed_n] += ensure_stereo(air, pan)

    for i in range(grains):
        t0 = (duration * i / max(1, grains)) * float(rng.uniform(0.88, 1.10))
        s = int(t0 * SR)
        t = np.arange(gn) / SR
        # Stay within tight consonant pair (root & fifth) + bandpass transient click
        deg = int(v["degree"]) + (0 if i % 2 == 0 else 3)
        f0 = scale_freq(state.scale, deg, octave=2)
        while f0 > 3400.0:
            f0 *= 0.5
        imp = rng.standard_normal(gn) * np.exp(-t / 0.0018)
        click = resonant_bp(imp, f0, q=4.5) * 0.85
        ping = np.sin(2.0 * math.pi * f0 * t) * np.exp(-t / 0.0028) * 0.35
        grain = (click + ping) * np.hanning(gn)
        p = float(np.clip(pan + rng.uniform(-0.22, 0.22), -0.45, 0.45))
        amp = float(rng.uniform(0.45, 1.0)) * (0.55 + 0.45 * (i / max(1, grains - 1)))
        g_st = ensure_stereo(grain * amp, p)
        e = min(n, s + gn)
        out[s:e] += g_st[: e - s]

    out = sos_filter(out, "bandpass", [420.0, 4400.0], order=2)
    out /= np.max(np.abs(out)) + 1e-12
    out = micro_fade(out, 4.0, 16.0)
    return out * db_to_lin(gain_db)


def synth_sub_thud(
    state: PolymorphicState,
    duration: float = 0.24,
    start_hz: float = 115.0,
    end_hz: float = 44.0,
    gain_db: float = -4.0,
) -> np.ndarray:
    """
    Deep velvety sub-bass anchor for hero landings & major scene transitions.
    Centered in mono for maximum punch and phase coherence.
    """
    v = state.next_variant("sub_thud")
    n = int(duration * SR)
    t = np.arange(n) / SR
    f_inst = end_hz + (start_hz - end_hz) * np.exp(-t / 0.028)
    phase = 2.0 * math.pi * np.cumsum(f_inst) / SR
    env = (1.0 - np.exp(-t / 0.004)) * np.exp(-t / (duration * 0.36))
    mono = np.tanh(1.35 * np.sin(phase) * env)
    mono = sos_filter(mono, "lowpass", 240.0, order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, 0.0)
    stereo = micro_fade(stereo, 2.0, 20.0)
    return stereo * db_to_lin(gain_db)


def synth_aperture_snap(
    state: PolymorphicState,
    pan: Optional[float] = None,
    gain_db: float = -5.5,
) -> np.ndarray:
    """
    Precision Leica-style optical detent / corner-bracket focus lock.
    Dual-transient woody-metallic mechanical snap separated by 14ms.
    """
    v = state.next_variant("aperture_snap")
    n = int(0.075 * SR)
    t = np.arange(n) / SR
    rng = state.rng

    def detent(f1: float, f2: float, amp: float) -> np.ndarray:
        imp = np.zeros(n)
        k = int(0.0012 * SR)
        imp[:k] = rng.standard_normal(k) * np.hanning(k * 2)[:k]
        m1 = resonant_bp(imp, f1, q=5.0) * 1.2
        m2 = resonant_bp(imp, f2, q=4.2) * 0.9
        return (m1 + m2) * np.exp(-t / 0.009) * amp

    mono = detent(580.0 * v["cutoff_mul"], 2150.0 * v["cutoff_mul"], 1.0)
    d2 = int(0.014 * SR)
    sec = detent(720.0 * v["cutoff_mul"], 2600.0 * v["cutoff_mul"], 0.62)
    mono[d2:] += sec[: n - d2]
    mono = sos_filter(mono, "bandpass", [180.0, 4600.0], order=2)
    mono /= np.max(np.abs(mono)) + 1e-12
    stereo = ensure_stereo(mono, pan if pan is not None else v["pan_jitter"] * 0.5)
    stereo = micro_fade(stereo, 0.5, 8.0)
    return stereo * db_to_lin(gain_db)


def synth_warm_pulse_bed(
    state: PolymorphicState,
    duration: float = 10.0,
    bpm: float = 115.0,
    gain_db: float = -12.5,
) -> np.ndarray:
    """
    Optional minimal, non-fatiguing warm SaaS groove bed (sub-warmth + dry woody
    rim-click + hushed brushed shaker + glassy root pad). Keeps massive headroom
    for UI SFX to shine cleanly on top.
    """
    n = int(duration * SR)
    out = np.zeros((n, 2))
    beat_s = 60.0 / bpm
    step_s = beat_s / 4.0  # 16th notes
    total_steps = int(duration / step_s)

    root_hz = scale_freq(state.scale, 0, octave=-2)
    fifth_hz = scale_freq(state.scale, 3, octave=-2)
    third_hz = scale_freq(state.scale, 1, octave=-2)

    # 1. Warm muted bassline + soft round kick on 16-step groove
    bass_pattern = [
        (0, root_hz, 0.24),
        (3, root_hz, 0.14),
        (6, third_hz, 0.18),
        (10, fifth_hz, 0.22),
        (14, root_hz, 0.15),
    ]
    kick_steps = {0, 6, 8, 14}
    rim_steps = {4, 12}
    shaker_steps = {2, 6, 10, 14, 15}

    for step in range(total_steps):
        s_idx = int(step * step_s * SR)
        m = step % 16

        # Soft round kick
        if m in kick_steps:
            kn = int(0.14 * SR)
            kt = np.arange(kn) / SR
            kf = 46.0 + 78.0 * np.exp(-kt / 0.018)
            k_sig = np.sin(2.0 * math.pi * np.cumsum(kf) / SR) * np.exp(-kt / 0.055)
            k_sig = sos_filter(k_sig, "lowpass", 190.0, order=2) * (0.85 if m in (0, 8) else 0.52)
            e = min(n, s_idx + kn)
            out[s_idx:e] += ensure_stereo(k_sig[: e - s_idx], 0.0)

        # Warm round bass notes
        for bm, bhz, bdur in bass_pattern:
            if m == bm:
                bn = int(bdur * SR)
                bt = np.arange(bn) / SR
                benv = (1.0 - np.exp(-bt / 0.008)) * np.exp(-bt / (bdur * 0.65))
                bsig = (np.sin(2.0 * math.pi * bhz * bt) + 0.25 * np.sin(4.0 * math.pi * bhz * bt)) * benv
                bsig = sos_filter(bsig, "lowpass", 280.0, order=2) * 0.62
                e = min(n, s_idx + bn)
                out[s_idx:e] += ensure_stereo(bsig[: e - s_idx], 0.0)

        # Dry woody rim-click on 2 & 4
        if m in rim_steps:
            rn = int(0.045 * SR)
            rt = np.arange(rn) / SR
            imp = state.rng.standard_normal(rn) * np.exp(-rt / 0.0022)
            rim = (
                resonant_bp(imp, 680.0 * float(state.rng.uniform(0.95, 1.05)), q=5.5) * 0.7
                + resonant_bp(imp, 1650.0, q=4.0) * 0.35
            ) * np.exp(-rt / 0.012)
            rim /= np.max(np.abs(rim)) + 1e-12
            e = min(n, s_idx + rn)
            out[s_idx:e] += ensure_stereo(rim[: e - s_idx] * 0.28, -0.06 if m == 4 else 0.06)

        # Hushed brushed silk shaker (strictly low-passed below 4.2 kHz!)
        if m in shaker_steps:
            sn = int(0.040 * SR)
            st = np.arange(sn) / SR
            sh = pink_noise(sn, state.rng) * (1.0 - np.exp(-st / 0.004)) * np.exp(-st / 0.014)
            sh = sos_filter(sh, "bandpass", [1800.0, 4200.0], order=2)
            sh /= np.max(np.abs(sh)) + 1e-12
            vel = 0.11 if m != 15 else 0.06
            e = min(n, s_idx + sn)
            out[s_idx:e] += ensure_stereo(sh[: e - s_idx] * vel, 0.14 if m % 4 == 2 else -0.14)

    # 2. Whisper-quiet warm harmonic air pad
    t = np.arange(n) / SR
    pad_notes = [
        scale_freq(state.scale, 0, octave=0),
        scale_freq(state.scale, 2, octave=0),
        scale_freq(state.scale, 4, octave=0),
    ]
    pad_L = np.zeros(n)
    pad_R = np.zeros(n)
    for i, pf in enumerate(pad_notes):
        lfo = 0.85 + 0.15 * np.sin(2.0 * math.pi * (0.14 + 0.05 * i) * t)
        pad_L += np.sin(2.0 * math.pi * pf * t) * lfo
        pad_R += np.sin(2.0 * math.pi * (pf * 1.0018) * t) * lfo
    pad = np.stack([pad_L, pad_R], axis=1) / len(pad_notes)
    pad = sos_filter(pad, "lowpass", 1400.0, order=2) * 0.11
    out += pad

    out /= np.max(np.abs(out)) + 1e-12
    out = micro_fade(out, 180.0, 450.0)
    return out * db_to_lin(gain_db)


# =============================================================================
# 5. COMPOUND SEQUENCE HELPERS (Typing Bursts, Menu Scrubs)
# =============================================================================

def synth_typing_stream(
    state: PolymorphicState,
    chars: int = 12,
    wpm: float = 115.0,
    end_with_enter: bool = True,
    pan: float = 0.0,
    gain_db: float = -7.5,
) -> np.ndarray:
    """
    Human-paced dampened typing stream (non-robotic cadence, subtle phrasing,
    optional Enter/Space heavier thock at the end).
    """
    base_dt = 60.0 / (max(40.0, wpm) * 5.0)
    events = []
    t_cur = 0.0
    for i in range(chars):
        is_enter = end_with_enter and (i == chars - 1)
        key = synth_topre_key(
            state,
            is_space_or_enter=is_enter,
            pan=pan + float(state.rng.uniform(-0.10, 0.10)),
            gain_db=gain_db + (1.5 if is_enter else 0.0),
        )
        events.append((int(t_cur * SR), key))
        # Natural human typing rhythm: occasional micro-hesitation on word boundaries
        jitter = float(state.rng.uniform(0.72, 1.32))
        if i > 0 and i % 5 == 0:
            jitter *= 1.35
        t_cur += base_dt * jitter

    total_len = max(s + ev.shape[0] for s, ev in events) + int(0.04 * SR)
    out = np.zeros((total_len, 2))
    for s, ev in events:
        out[s : s + ev.shape[0]] += ev
    return out


def synth_menu_scrub(
    state: PolymorphicState,
    items: int = 5,
    interval_ms: float = 95.0,
    start_degree: int = 0,
    ascending: bool = True,
    end_with_click: bool = True,
    pan: float = 0.0,
    gain_db: float = -6.5,
) -> np.ndarray:
    """
    Cursor hovering across dropdown/context menu items with scale-locked
    ascending marimba ticks, finishing with a tactile mouse click.
    """
    events = []
    t_cur = 0.0
    for i in range(items):
        deg = start_degree + (i if ascending else -i)
        tick = synth_hover_tick(
            state,
            degree=deg,
            octave=1,
            pan=pan + float(state.rng.uniform(-0.06, 0.06)),
            gain_db=gain_db,
        )
        events.append((int(t_cur * SR), tick))
        t_cur += (interval_ms / 1000.0) * float(state.rng.uniform(0.92, 1.08))

    if end_with_click:
        t_cur += 0.045
        clk = synth_tactile_click(state, style="mouse", double_stage=True, pan=pan, gain_db=gain_db + 2.0)
        events.append((int(t_cur * SR), clk))

    total_len = max(s + ev.shape[0] for s, ev in events) + int(0.05 * SR)
    out = np.zeros((total_len, 2))
    for s, ev in events:
        out[s : s + ev.shape[0]] += ev
    return out


# =============================================================================
# 6. MASTER ANTI-FATIGUE FINISHING BUS
# =============================================================================

def master_bus(
    stereo: np.ndarray,
    reverb_wet: float = 0.13,
    reverb_decay: float = 0.45,
    target_peak_db: float = -1.5,
    warmth_shelf_db: float = -5.5,
) -> np.ndarray:
    """
    Hazene-calibrated anti-fatigue mastering bus:
    1. 28 Hz sub-rumble cleanup
    2. Subtle stereo micro-plate reverb for physical cohesion
    3. Fletcher-Munson ear-fatigue tame (-1.8 dB @ 4.4 kHz)
    4. Analog warmth high-shelf (-5.5 dB above 6.2 kHz) so presence sparkles
       cleanly while harsh 5-9 kHz stays well below 2.5%
    5. Gentle analog soft-clip glue + headroom peak normalization (-1.5 dBFS)
    """
    x = sos_filter(stereo, "highpass", 28.0, order=2)
    x = micro_plate_reverb(x, wet=reverb_wet, decay_s=reverb_decay, damping_hz=3100.0)
    x = peaking_eq(x, f0=4400.0, gain_db=-1.8, q=1.1)
    x = high_shelf(x, f0=6200.0, gain_db=warmth_shelf_db, slope=0.65)
    # Gentle musical warmth saturation (preserves 15+ dB crest factor!)
    peak = float(np.max(np.abs(x))) + 1e-12
    x = x / peak
    x = np.tanh(x * 1.12) / math.tanh(1.12)
    x = micro_fade(x, 8.0, 30.0)
    x *= db_to_lin(target_peak_db)
    return x


# =============================================================================
# 7. DISPATCHER & CUE-SHEET RENDERER
# =============================================================================

GENERATORS = {
    "glass_chime":     synth_glass_chime,
    "chord_bloom":     synth_chord_bloom,
    "liquid_pop":      synth_liquid_pop,
    "bubble_cascade":  synth_bubble_cascade,
    "tactile_click":   synth_tactile_click,
    "topre_key":       synth_topre_key,
    "hover_tick":      synth_hover_tick,
    "silk_whoosh":     synth_silk_whoosh,
    "progress_glide":  synth_progress_glide,
    "counter_ratchet": synth_counter_ratchet,
    "dither_flutter":  synth_dither_flutter,
    "sub_thud":        synth_sub_thud,
    "aperture_snap":   synth_aperture_snap,
    "warm_pulse_bed":  synth_warm_pulse_bed,
    "typing_stream":   synth_typing_stream,
    "menu_scrub":      synth_menu_scrub,
}


def render_cue(state: PolymorphicState, cue: Dict[str, Any]) -> np.ndarray:
    kind = cue["type"]
    if kind not in GENERATORS:
        raise ValueError(f"Unknown SFX type '{kind}'. Available: {', '.join(sorted(GENERATORS))}")
    fn = GENERATORS[kind]
    kwargs = {k: v for k, v in cue.items() if k not in ("t", "type", "label")}
    return fn(state, **kwargs)


def render_timeline(spec: Dict[str, Any]) -> np.ndarray:
    duration = float(spec["duration"])
    scale = spec.get("scale", "b_minor_pent")
    seed = int(spec.get("seed", 42))
    state = PolymorphicState(seed=seed, scale=scale)

    n_total = int((duration + 0.25) * SR)
    sfx_bus = np.zeros((n_total, 2))
    bed_bus = np.zeros((n_total, 2))

    # Optional minimal groove bed
    bed_cfg = spec.get("bed")
    if bed_cfg and bed_cfg.get("enabled", True):
        t0 = float(bed_cfg.get("start", 0.0))
        bdur = float(bed_cfg.get("duration", duration - t0))
        bed = synth_warm_pulse_bed(
            state,
            duration=bdur,
            bpm=float(bed_cfg.get("bpm", 115.0)),
            gain_db=float(bed_cfg.get("gain_db", -12.5)),
        )
        s = int(t0 * SR)
        e = min(n_total, s + bed.shape[0])
        bed_bus[s:e] += bed[: e - s]

    # Render all timed SFX cues
    for cue in spec.get("cues", []):
        t_start = float(cue["t"])
        clip = render_cue(state, cue)
        s = int(max(0.0, t_start) * SR)
        if s >= n_total:
            continue
        e = min(n_total, s + clip.shape[0])
        sfx_bus[s:e] += clip[: e - s]

    # Reverb on SFX bus, then glue with dry bed bus
    reverb_wet = float(spec.get("reverb_wet", 0.14))
    reverb_decay = float(spec.get("reverb_decay", 0.48))
    sfx_wet = micro_plate_reverb(sfx_bus, wet=reverb_wet, decay_s=reverb_decay, damping_hz=3100.0)
    mix = sfx_wet + bed_bus

    # Master finishing (without double-reverbing)
    mastered = master_bus(
        mix,
        reverb_wet=0.0,
        target_peak_db=float(spec.get("target_peak_db", -1.5)),
        warmth_shelf_db=float(spec.get("warmth_shelf_db", -5.5)),
    )
    # Trim cleanly to exact requested duration
    exact_n = int(duration * SR)
    mastered = mastered[:exact_n]
    return micro_fade(mastered, 6.0, 25.0)


def save_audio(stereo: np.ndarray, wav_path: Path, mp3_path: Optional[Path] = None) -> None:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    pcm16 = np.clip(stereo, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).astype(np.int16)
    wavfile.write(str(wav_path), SR, pcm16)
    if mp3_path is not None:
        mp3_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(wav_path),
            "-acodec", "libmp3lame", "-b:a", "192k",
            str(mp3_path),
        ]
        subprocess.run(cmd, check=True)


# =============================================================================
# 8. CLI ENTRYPOINT
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pure-Code Tactile SaaS SFX Synthesizer & Timeline Mastering Engine"
    )
    parser.add_argument("--list", action="store_true", help="List available SFX primitives & scales")
    parser.add_argument("--cues", type=str, help="Path to JSON cue-sheet timeline")
    parser.add_argument("--preset", type=str, help="Single SFX primitive name to render")
    parser.add_argument("--variants", type=int, default=1, help="Number of polymorphic variants for --preset")
    parser.add_argument("--scale", type=str, default="b_minor_pent", help="Musical scale name")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic RNG seed")
    parser.add_argument("--params", type=str, default="{}", help="JSON dict of extra kwargs for --preset")
    parser.add_argument("--out", type=str, help="Output WAV path (for --cues or single --preset)")
    parser.add_argument("--out-dir", type=str, help="Output directory (for --preset with --variants > 1)")
    parser.add_argument("--mp3", type=str, help="Optional MP3 output path (via ffmpeg)")
    args = parser.parse_args()

    if args.list:
        print("SFX Primitives:")
        for name, fn in sorted(GENERATORS.items()):
            doc = (fn.__doc__ or "").strip().splitlines()[0]
            print(f"  - {name:18s}: {doc}")
        print("\nScales:")
        for name in sorted(SCALES):
            print(f"  - {name}")
        return

    if args.cues:
        spec = json.loads(Path(args.cues).read_text(encoding="utf-8-sig"))
        stereo = render_timeline(spec)
        out_wav = Path(args.out or Path(args.cues).with_suffix(".wav"))
        out_mp3 = Path(args.mp3) if args.mp3 else None
        save_audio(stereo, out_wav, out_mp3)
        print(f"Rendered timeline ({stereo.shape[0]/SR:.2f}s) -> {out_wav}")
        if out_mp3:
            print(f"Encoded MP3 -> {out_mp3}")
        return

    if args.preset:
        if args.preset not in GENERATORS:
            sys.exit(f"Unknown preset '{args.preset}'. Run --list to view options.")
        extra = json.loads(args.params)
        state = PolymorphicState(seed=args.seed, scale=args.scale)
        if args.variants == 1 and args.out:
            clip = master_bus(GENERATORS[args.preset](state, **extra), reverb_wet=0.10)
            save_audio(clip, Path(args.out), Path(args.mp3) if args.mp3 else None)
            print(f"Rendered {args.preset} -> {args.out}")
        else:
            out_dir = Path(args.out_dir or "./sfx_out")
            out_dir.mkdir(parents=True, exist_ok=True)
            for i in range(1, args.variants + 1):
                clip = master_bus(GENERATORS[args.preset](state, **extra), reverb_wet=0.10)
                wav_p = out_dir / f"{args.preset}_v{i}.wav"
                mp3_p = (out_dir / f"{args.preset}_v{i}.mp3") if args.mp3 else None
                save_audio(clip, wav_p, mp3_p)
                print(f"Rendered {args.preset} v{i} -> {wav_p}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
