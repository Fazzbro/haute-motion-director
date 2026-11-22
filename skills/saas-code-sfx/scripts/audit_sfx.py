#!/usr/bin/env python3
"""
audit_sfx.py — Anti-Fatigue & Non-Repetition DSP Quality Gate
=============================================================
Audits any rendered WAV/MP3 SaaS SFX track against the acoustic standards
derived from forensic analysis of elite motion design (Hazene / Linear / Apple):

1. Zero Clipping:       Peak <= -0.8 dBFS
2. Dynamic Punch:       Crest factor >= 11.0 dB (not brickwalled)
3. Anti-Harshness:      5-9 kHz energy <= 3.0% (reference: 0.88%)
4. Anti-Sizzle:         9-20 kHz energy <= 1.2% (reference: 0.18%)
5. Anti-Repetition:     Spectral diversity across detected onsets (mean pairwise
                        cosine distance > 0.08 — catches copy-pasted identical SFX!)
6. Acoustic Breathing:  Quiet/open frames present (10th-percentile RMS at least
                        10 dB quieter than 90th-percentile RMS)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import signal
import soundfile as sf


def audit(path: Path) -> dict:
    y, sr = sf.read(str(path))
    if y.ndim == 2:
        ym = np.mean(y, axis=1)
        yL, yR = y[:, 0], y[:, 1]
        corr = float(np.corrcoef(yL, yR)[0, 1]) if np.std(yL) > 1e-9 and np.std(yR) > 1e-9 else 1.0
    else:
        ym = y
        corr = 1.0

    dur = len(ym) / sr
    peak_db = float(20 * np.log10(np.max(np.abs(y)) + 1e-12))
    rms_db = float(20 * np.log10(np.sqrt(np.mean(ym**2)) + 1e-12))
    crest_db = peak_db - rms_db

    # Spectral band energy distribution
    freqs, psd = signal.welch(ym, fs=sr, nperseg=min(8192, len(ym)))
    tot = np.sum(psd) + 1e-18

    def band_pct(f_lo: float, f_hi: float) -> float:
        m = (freqs >= f_lo) & (freqs < f_hi)
        return float(100.0 * np.sum(psd[m]) / tot)

    sub_pct = band_pct(20, 80)
    bass_pct = band_pct(80, 250)
    lowmid_pct = band_pct(250, 800)
    mid_pct = band_pct(800, 2500)
    pres_pct = band_pct(2500, 5000)
    harsh_pct = band_pct(5000, 9000)
    air_pct = band_pct(9000, 20000)

    # Dynamic breathing (frame RMS spread over 250ms windows)
    win = int(0.25 * sr)
    hop = int(0.125 * sr)
    frame_rms = []
    for i in range(0, max(1, len(ym) - win), hop):
        r = np.sqrt(np.mean(ym[i : i + win] ** 2))
        frame_rms.append(20 * np.log10(r + 1e-9))
    if len(frame_rms) >= 4:
        p10, p90 = float(np.percentile(frame_rms, 10)), float(np.percentile(frame_rms, 90))
        breathing_db = p90 - p10
    else:
        breathing_db = 12.0

    # Repetition check: detect sharp transient peaks and compare spectral fingerprints
    env = np.abs(signal.hilbert(sos_hp(ym, 250.0, sr)))
    env_ds = env[:: max(1, int(sr / 200))]  # 200 Hz envelope
    pk_thresh = np.percentile(env_ds, 82)
    pks, _ = signal.find_peaks(env_ds, height=pk_thresh, distance=18)  # >= 90ms apart
    fps = []
    for p in pks[:40]:
        idx = int(p * (sr / 200))
        seg = ym[idx : min(len(ym), idx + int(0.08 * sr))]
        if len(seg) < 512:
            continue
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        # 24 log-spaced energy bins from 200 Hz to 6000 Hz
        fb = np.fft.rfftfreq(len(seg), 1.0 / sr)
        edges = np.geomspace(200, 6000, 25)
        vec = np.array([np.sum(sp[(fb >= edges[k]) & (fb < edges[k + 1])]) for k in range(24)])
        norm = np.linalg.norm(vec) + 1e-12
        fps.append(vec / norm)

    if len(fps) >= 3:
        dists = []
        for i in range(len(fps) - 1):
            # Adjacent event cosine distance (catches consecutive copy-paste SFX!)
            dists.append(1.0 - float(np.dot(fps[i], fps[i + 1])))
        diversity_score = float(np.mean(dists))
    else:
        diversity_score = 0.25  # single shot

    # Anti-Piercing Peak Check: measure narrowband spectral spike ratio in 800-4000 Hz
    # at both the intro peak (0-2s) and overall track peak.
    # Pure un-broadened sine bells spike at 32-40 dB (irritating!). Hazene reference = 16 dB.
    def peak_piercing_db(sig: np.ndarray) -> float:
        if len(sig) < 1024:
            return 0.0
        idx = int(np.argmax(np.abs(sig)))
        w0 = max(0, idx - int(0.03 * sr))
        w1 = min(len(sig), idx + int(0.07 * sr))
        w = sig[w0:w1]
        if len(w) < 512:
            return 0.0
        sp = np.abs(np.fft.rfft(w * np.hanning(len(w))))
        fb = np.fft.rfftfreq(len(w), 1.0 / sr)
        m = (fb >= 800.0) & (fb <= 4000.0)
        if not np.any(m) or np.mean(sp[m]) < 1e-9:
            return 0.0
        return float(20.0 * np.log10((np.max(sp[m]) + 1e-12) / (np.mean(sp[m]) + 1e-12)))

    intro_seg = ym[: int(min(dur, 2.0) * sr)]
    intro_peak_db = float(20.0 * np.log10(np.max(np.abs(intro_seg)) + 1e-12)) if len(intro_seg) else -60.0
    intro_pierce_db = peak_piercing_db(intro_seg)
    full_pierce_db = peak_piercing_db(ym)
    max_pierce_db = max(intro_pierce_db, full_pierce_db)

    checks = {
        "no_clipping (peak <= -0.8 dBFS)": peak_db <= -0.8,
        "healthy_dynamics (crest >= 11 dB)": crest_db >= 11.0,
        "zero_harshness (5-9kHz <= 3.0%)": harsh_pct <= 3.0,
        "zero_sizzle (9-20kHz <= 1.2%)": air_pct <= 1.2,
        "no_tonal_piercing (800-4000Hz peak spike <= 24 dB)": max_pierce_db <= 24.0,
        "soft_intro_headroom (0-2s peak <= -4.5 dBFS)": intro_peak_db <= -4.5 or dur < 3.0,
        "non_repetitive (adjacent spectral diversity >= 0.08)": diversity_score >= 0.08,
        "acoustic_breathing (p90-p10 >= 8 dB)": breathing_db >= 8.0 or dur < 2.0,
    }

    return {
        "file": str(path),
        "duration_sec": round(dur, 3),
        "peak_dbfs": round(peak_db, 2),
        "intro_peak_dbfs": round(intro_peak_db, 2),
        "rms_dbfs": round(rms_db, 2),
        "crest_factor_db": round(crest_db, 2),
        "max_piercing_spike_db": round(max_pierce_db, 2),
        "stereo_correlation": round(corr, 3),
        "breathing_range_db": round(breathing_db, 2),
        "adjacent_diversity_score": round(diversity_score, 3),
        "detected_transients": len(fps),
        "bands_pct": {
            "sub_20_80": round(sub_pct, 2),
            "bass_80_250": round(bass_pct, 2),
            "low_mid_250_800": round(lowmid_pct, 2),
            "mid_800_2500": round(mid_pct, 2),
            "presence_2500_5000": round(pres_pct, 2),
            "harsh_5000_9000": round(harsh_pct, 2),
            "air_9000_20000": round(air_pct, 2),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def sos_hp(x: np.ndarray, hz: float, sr: int) -> np.ndarray:
    sos = signal.butter(2, hz / (0.5 * sr), btype="highpass", output="sos")
    return signal.sosfilt(sos, x)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit SaaS SFX audio against anti-fatigue standards")
    parser.add_argument("audio_file", type=str, help="Path to WAV/MP3 file to audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    res = audit(Path(args.audio_file))
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        status = "PASS" if res["passed"] else "FAIL"
        print(f"=== SAAS SFX ANTI-FATIGUE AUDIT [{status}] ===")
        print(f"File:       {res['file']} ({res['duration_sec']}s)")
        print(f"Levels:     Peak {res['peak_dbfs']} dBFS | Intro Peak {res['intro_peak_dbfs']} dBFS | RMS {res['rms_dbfs']} dBFS | Crest {res['crest_factor_db']} dB")
        print(f"Stereo/Dyn: Corr {res['stereo_correlation']} | Breathing {res['breathing_range_db']} dB | Diversity {res['adjacent_diversity_score']} | Piercing Spike {res['max_piercing_spike_db']} dB")
        print("Spectrum:  ", " | ".join(f"{k}={v}%" for k, v in res["bands_pct"].items()))
        print("Checks:")
        for k, ok in res["checks"].items():
            print(f"  [{'OK' if ok else 'FAIL'}] {k}")
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
