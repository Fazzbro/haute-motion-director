# Reference Forensics: Hazene — "System Zero by RightNow" (31.02s, 48 kHz Stereo)

Forensic DSP measurements extracted from `"Hazene Motion Designer - can't stop rewatching it.mp4"` — the empirical blueprint behind `saas-code-sfx`.

---

## 1. Macro Acoustic Metrics

| Metric | Measured Value | Design Takeaway |
| :--- | :--- | :--- |
| **Duration** | `31.02 s` (`48 kHz` stereo) | Tight 30s SaaS launch format |
| **True Peak** | `-1.33 dBFS` | Clean headroom, zero limiting distortion |
| **Integrated RMS** | `-18.44 dBFS` | Warm, comfortable listening level |
| **Crest Factor** | `17.12 dB` | High dynamic punch; zero brickwall fatigue |
| **Stereo Correlation** | `0.75` (`Side/Mid = -8.44 dB`) | Solid centered low-end + tactile stereo micro-panning (`±0.05 to ±0.17`) |
| **Tempo** | `~114.8 BPM` | Confident, unhurried editorial groove |
| **Dominant Scale / Key** | `E minor 9 / B minor pentatonic` (`B, C#, D, E, F#, G`) | Every tonal UI cue locks to this single harmonic family |
| **Harmonic vs Percussive RMS** | `-21.43 dB` vs `-31.17 dB` | Tonal resonance leads by `+9.7 dB`; transients stay soft & organic |
| **Breathing Range (`p90 - p10`)** | `21.62 dB` | Huge contrast between open intro/outro and rhythmic middle |
| **Adjacent Onset Diversity** | `0.269` (cosine distance) | High timbre/pitch variety across consecutive SFX events |

---

## 2. The Anti-Fatigue Spectral Fingerprint (Welch PSD)

| Frequency Band | Energy Share | Relative Level | Role in the Mix |
| :--- | ---: | ---: | :--- |
| **Sub (`20–80 Hz`)** | `62.81%` | `-2.02 dB` | Velvety physical weight & round bass cushion |
| **Bass (`80–250 Hz`)** | `24.86%` | `-6.05 dB` | Warm body & Topre/kick punch |
| **Low-Mid (`250–800 Hz`)** | `6.99%` | `-11.56 dB` | Woody/liquid droplet fundamentals |
| **Mid (`800–2500 Hz`)** | `2.66%` | `-15.74 dB` | Clean melodic articulation & tactile clicks |
| **Presence (`2500–5000 Hz`)** | `1.26%` | `-18.99 dB` | Crystalline glass partials & crisp micro-transients |
| **Harsh/Sibilant (`5000–9000 Hz`)** | **`0.88%`** | **`-20.55 dB`** | **Strictly suppressed — primary reason for zero ear fatigue** |
| **Air (`9000–20000 Hz`)** | **`0.18%`** | **`-27.53 dB`** | **Gentle analog roll-off — zero metallic hiss** |

**Key Insight**: `94.7%` of total acoustic energy sits below `800 Hz`, while the ear-piercing `5–20 kHz` zone accounts for barely `1.06%`. Typical amateur code-generated SFX (raw white noise whooshes, unfiltered square/saw synth pings) dump `25–45%` into `3–10 kHz`, causing immediate listener fatigue within 5 seconds.

---

## 3. Macro 3-Act Loudness & Density Arc

```text
00–06s (Intro — Open & Tactile)     : RMS -26.8 -> -21.9 dB | Sparse chime, typing, whoosh, dither, logo ping
06–26s (Body — Groove & Micro-UI)   : RMS -17.3 -> -15.4 dB | Tight minimal groove + scale-locked pops/hovers/glides
26–31s (Outro — Strip Back & Bell)  : RMS -24.7 -> -33.4 dB | Beat drops out -> chord bloom + bubble cascade + final click/bell
```

---

## 4. STFT Micro-Forensics of Signature Events

### A. Intro Glassy OS Startup Chime (`0.06s – 1.94s`)
- **Spectral Flatness**: `0.01 – 0.06` (purely tonal, zero broadband static).
- **Soft Velvet Onset & Headroom**: Intro peak sits at `-5.32 dBFS` (`@ 0.185s`) with an `85.7 ms` `10% → 90%` bloom rise — never a sudden full-scale spike.
- **Zero Narrowband Piercing**: `800–4000 Hz` peak-to-mean spectral spike ratio is only **`16.0 dB`** (whereas naive pure-sine additive chimes spike at `35+ dB` and sting the ear). Warm `250–510 Hz` fundamentals dominate; upper partials sit `-6 dB` to `-8 dB` lower.
- **Detected Partials**: `164 Hz (E3)`, `328 Hz (E4)`, `492 Hz (B4)`, `656 Hz (E5)`, `984 Hz (B5)`, `1125 Hz (C#6)`, `1477 Hz (F#6)`, `1969 Hz (B6)`, `2297 Hz (D7)`.
- **Physics**: Open-voiced minor-9th harmonic chord with warm unison voice spread, randomized phases, felt-mallet attack, and integer bell partials (`0.5x, 1x, 1.5x, 2x, 3x`) where higher overtones decay 2–3× faster than fundamentals, bathed in a high-damped stereo plate.

### B. Outro Playful Liquid Bubble Cascade (`29.11s – 29.75s`)
- **Spectral Flatness**: `0.01 – 0.02`.
- **Frame-by-Frame Fundamental Trajectory (~60 ms spacing)**:
  `305 Hz -> 422 Hz -> 469 Hz -> 516 Hz -> 797 Hz -> 656 Hz -> 352 Hz` (with quiet 2nd harmonic `-6 to -12 dB`).
- **Physics**: Minnaert bubble-droplet resonance — rapid exponential upward sine chirp (`f0 -> 1.65*f0` over `40–70 ms`), 2 ms smooth attack, clean exponential tail.

### C. Final CTA Confirmation Bell (`29.87s – 30.75s`)
- **Detected Partials**: `1570 Hz` -> `3141 Hz` (`2:1` octave) + `4688 Hz` (`3:1` octave+fifth), decaying smoothly over `~800 ms` with flatness `0.01`.
- **Physics**: Pure glassy harmonic resolve — bright enough to feel decisive, mathematically consonant, zero aliasing or harshness above `5 kHz`.
