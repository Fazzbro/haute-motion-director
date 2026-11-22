---
name: saas-code-sfx
description: >-
  Pure-code procedural SFX synthesis and anti-fatigue audio mastering skill for
  SaaS product launches, UI walkthroughs, and motion design videos (HyperFrames,
  Remotion, FFmpeg). Synthesizes organic, scale-locked, non-repetitive tactile
  sound effects (glass chimes, Minnaert liquid pops, Topre typing streams,
  ceramic hover ticks, two-stage mouse clicks, formant-swept silk whooshes,
  counter ratchets, dither flutters, progress glides, and minimal warm groove
  beds) strictly in Python (NumPy + SciPy) with zero external sample packs.
  Use when generating or replacing SFX for SaaS demos, motion graphics, UI
  animations, or when the user asks for procedural / code-generated sound
  effects that are non-repetitive and non-irritating.
---

# SaaS Pure-Code SFX Engine (`saas-code-sfx`)

Generate studio-grade, tactile, musical, zero-fatigue sound effects for SaaS videos **100% in code** — deterministic, sample-free, scale-locked, and verified against objective DSP anti-fatigue gates.

Derived from forensic spectral & transient analysis of elite motion design (see [reference-forensics.md](./references/reference-forensics.md)).

---

## Core Acoustic Laws (Why This Never Sounds Irritating or Repetitive)

1. **Scale-Locked Pitch Grammar**: Every tonal cue (chimes, liquid pops, hover ticks, progress glides, cascades) locks to a single pentatonic/extended scale (`b_minor_pent`, `e_minor9`, `d_major_pent`, `c_major9`, `g_lydian`). Never emit arbitrary dissonant frequencies (`440 Hz`, `1000 Hz`, `2000 Hz` beeps).
2. **Polymorphic Anti-Repetition**: Every sequential trigger automatically shifts pitch contour, filter cutoff (`0.86x–1.16x`), decay (`0.88x–1.14x`), velocity (`-2.6 to +0.4 dB`), and stereo micro-panning (`±0.16`). **Never reuse one static WAV file across repeated clicks, keystrokes, or hovers.**
3. **Fletcher-Munson Anti-Fatigue Curve**: Human ears fatigue fastest in `3.5–9 kHz`. Raw white noise, sawtooths, and digital pings dump 25–40% energy there. Every primitive here models physical/modal acoustics (pink-noise formants, pure damped partials, wooden/ceramic biquads) and passes through an analog warmth master bus keeping `5–9 kHz < 3.0%` and `9–20 kHz < 1.2%`.
4. **Acoustic Breathing (The 30–40% Silence Law)**: Leave open air! Follow the 3-act dynamic arc:
   - **Act 1 (Intro)**: Sparse glassy chime + delicate typing/whoosh (`-26 to -22 dB RMS`)
   - **Act 2 (Core Walkthrough)**: Optional minimal warm groove (`-13 dB` below SFX) + crisp melodic UI interactions (`-18 to -16 dB RMS`)
   - **Act 3 (Outro Resolve)**: Strip the beat away -> open chord bloom + playful bubble cascade + final CTA click & bell ring-out.
5. **High Crest Factor & Zero Clipping**: Target `-1.5 dBFS` peak with `15–19 dB` crest factor and mandatory raised-cosine micro-fades on every event.

---

## Hard Anti-Irritation Constraints (Peak & Piercingness Bans)

Never allow a sharp, stinging, or tuning-fork-like peak — especially on opening chords, chimes, and resolve bells:

1. **NO Single-Sine Tuning-Fork Spikes (`800–4000 Hz` Narrowband Spike `<= 24 dB`)**:
   - **NEVER** synthesize bells, chimes, or opening chords with single un-broadened phase-locked `sin(2πft)` oscillators above `700 Hz` (they collapse energy into 1 Hz needle spikes `35+ dB` above the spectral floor, causing immediate ear irritation).
   - **MANDATORY**: Spread every sustained tonal voice across a **3-voice micro-chorused unison (`-8.5, 0, +8.5 cents`)** with **randomized initial oscillator phases** (prevents constructive peak stacking), subtle organic pitch drift, and a whisper-quiet (`-26 dB`) filtered pink-noise air cushion.
2. **Warm Fundamental Dominance on Chimes & Chords**:
   - **NEVER** let `800–3500 Hz` partials rival the fundamental on chimes or chord blooms. Keep fundamentals anchored in `230–660 Hz`, attenuate `2x`/`3x` partials by at least `-6 dB` to `-12 dB`, and apply a `2.9–3.2 kHz` analog silk low-pass ceiling.
3. **Velvet Soft-Hammer Onset (NO Sharp Chime Attack Sting)**:
   - **NEVER** trigger a sustained chime with `< 15 ms` attack or an opening chord with `< 55 ms` bloom rise. Use felt-mallet rounded attacks (`>= 18 ms` on `glass_chime`, `>= 55–85 ms` bloom swell + `>= 40 ms` strum stagger on `chord_bloom`).
4. **Soft Intro & Tonal Peak Ceiling (`<= -4.5 dBFS` in `0–2s`, `<= -6.0 dBFS` on Chimes)**:
   - **NEVER** let a tonal bell or opening chord hit full-scale peak (`-1.5 dBFS`) or be the loudest peak in the mix. Keep `0–2s` intro peaks `<= -4.5 dBFS` (matching Hazene's `-5.32 dBFS` intro) so the viewer's ear eases into the video smoothly.

---

## Quick-Start Workflow

### Step 1: Map Visual Events to SFX Primitives

Read [sfx-taxonomy-and-recipes.md](./references/sfx-taxonomy-and-recipes.md) for the full parameter table of all 16 primitives. Quick mapping:

| Visual UI / Motion Moment | Primitive (`type`) | Notes |
| :--- | :--- | :--- |
| Brand intro / outro / hero reveal | `chord_bloom`, `glass_chime` | Open-voiced glassy chime; never stack with harsh cymbals |
| Window / modal / card pop-in | `liquid_pop` | Use `size: "large"` for windows, `"small"` for tooltips; `direction: "down"` for close |
| Multi-item reveal / outro sparkle | `bubble_cascade` | 3–6 ascending pentatonic droplets with gentle stereo pan arc |
| Dropdown / context menu hover | `menu_scrub` or `hover_tick` | Dry ceramic/wood micro-ticks walking up the scale |
| Mouse click / CTA / toggle | `tactile_click` | `double_stage: true` gives authentic press + 28ms release micro-click |
| Text input / CLI command typing | `typing_stream` or `topre_key` | Dampened rubber-dome thock; human-jittered cadence, optional heavy Enter |
| Metric odometer (`74% -> 93%`) | `counter_ratchet` | Ease-out decelerating ticks + soft confirmation chime on lock |
| Panel wipe / card slide / camera surge | `silk_whoosh` | Swept 1/f pink-noise formants (zero white-noise hiss); pan follows motion |
| Progress bar / benchmark fill | `progress_glide` | Airy crystalline lift + lock-in tick (never cartoon slide-whistle) |
| Pixel dither / retro-digital morph | `dither_flutter` | Crisp 9ms scale-locked telemetry micro-grains + gentle air bed |
| Heavy scene anchor / hero landing | `sub_thud` | Centered mono `115 -> 44 Hz` velvety impact |
| Target brackets / focus frame lock | `aperture_snap` | Leica-style 14ms dual mechanical detent |
| Optional subtle background groove | `bed` config (`warm_pulse_bed`) | Low-passed round bass + dry woody rim + hushed shaker (`-13 dB`) |

### Step 2: Author a Cue-Sheet JSON (or Export Individual Variants)

**Mode A — Full Timeline Master (Recommended for HyperFrames / FFmpeg / Remotion):**
Write a deterministic cue-sheet JSON (e.g. `sfx_cues.json`) aligned to your exact scene/GSAP timestamps:

```json
{
  "duration": 16.0,
  "scale": "b_minor_pent",
  "seed": 108,
  "reverb_wet": 0.14,
  "bed": { "enabled": true, "start": 3.5, "duration": 9.5, "bpm": 115.0, "gain_db": -13.0 },
  "cues": [
    { "t": 0.08, "type": "chord_bloom", "degrees": [0, 2, 4, 5], "duration": 1.6, "gain_db": -6.0 },
    { "t": 0.40, "type": "typing_stream", "chars": 11, "wpm": 125, "end_with_enter": false },
    { "t": 2.10, "type": "silk_whoosh", "duration": 0.36, "direction": "in", "pan_start": -0.22, "pan_end": 0.22 },
    { "t": 3.50, "type": "aperture_snap" },
    { "t": 5.00, "type": "menu_scrub", "items": 5, "interval_ms": 100, "end_with_click": true },
    { "t": 7.20, "type": "liquid_pop", "size": "large", "direction": "up" },
    { "t": 9.40, "type": "counter_ratchet", "duration": 0.85, "ticks": 9, "with_resolve_chime": true },
    { "t": 13.20, "type": "chord_bloom", "degrees": [0, 2, 4, 5], "duration": 2.2 },
    { "t": 14.30, "type": "bubble_cascade", "count": 5, "spacing_ms": 60 },
    { "t": 15.05, "type": "tactile_click", "double_stage": true },
    { "t": 15.10, "type": "glass_chime", "degree": 4, "octave": 1, "duration": 0.9 }
  ]
}
```

Render to 48 kHz stereo WAV + 192 kbps MP3 using [sfx_engine.py](./scripts/sfx_engine.py):

```bash
python "C:\Users\NEW\.gemini\config\plugins\haute-motion-director\skills\saas-code-sfx\scripts\sfx_engine.py" \
  --cues sfx_cues.json \
  --out assets/sfx_master.wav \
  --mp3 assets/sfx_master.mp3
```

**Mode B — Individual Polymorphic SFX Variants (For Interactive Apps or Per-Clip Tracks):**
Always generate `--variants 4` (or more) so consecutive triggers cycle variants:

```bash
python "C:\Users\NEW\.gemini\config\plugins\haute-motion-director\skills\saas-code-sfx\scripts\sfx_engine.py" \
  --preset liquid_pop --scale e_minor9 --variants 4 --out-dir assets/sfx/ --mp3 1
```

List all available primitives and scales anytime:
```bash
python "C:\Users\NEW\.gemini\config\plugins\haute-motion-director\skills\saas-code-sfx\scripts\sfx_engine.py" --list
```

### Step 3: Run the Automated Anti-Fatigue DSP Audit (MANDATORY)

Before attaching the rendered audio to any video, run [audit_sfx.py](./scripts/audit_sfx.py):

```bash
python "C:\Users\NEW\.gemini\config\plugins\haute-motion-director\skills\saas-code-sfx\scripts\audit_sfx.py" assets/sfx_master.wav
```

All 8 gates must print `[OK]`:
- `no_clipping` (`peak <= -0.8 dBFS`)
- `healthy_dynamics` (`crest >= 11 dB`)
- `zero_harshness` (`5–9 kHz <= 3.0%`)
- `zero_sizzle` (`9–20 kHz <= 1.2%`)
- `no_tonal_piercing` (`800–4000 Hz` peak narrowband spike `<= 24 dB`)
- `soft_intro_headroom` (`0–2s` intro peak `<= -4.5 dBFS`)
- `non_repetitive` (`adjacent spectral diversity >= 0.08`)
- `acoustic_breathing` (`p90 - p10 RMS >= 8 dB`)

Then **listen to the rendered `.mp3` directly** (via `read_file` on the MP3) to verify musical phrasing and absence of mechanical artifacts before finalizing.

---

## HyperFrames & FFmpeg Integration

- **HyperFrames (`index.html`)**: Place the mastered timeline track on a root `<audio>` element so it stays perfectly frame-locked during Studio scrubbing and MP4 render:
  ```html
  <audio id="sfx-master" src="assets/sfx_master.mp3" data-start="0" data-duration="16"></audio>
  ```
- **When mixing with external music**: Set `"bed": { "enabled": false }` in `sfx_cues.json`, match `"scale"` to the music track's key, and place both `<audio>` elements in HyperFrames (music at `data-volume="0.55"`, SFX master at `data-volume="0.95"`).
- **Direct FFmpeg Mux**:
  ```bash
  ffmpeg -y -i video.mp4 -i assets/sfx_master.wav -c:v copy -c:a aac -b:a 192k -shortest final_with_sfx.mp4
  ```
