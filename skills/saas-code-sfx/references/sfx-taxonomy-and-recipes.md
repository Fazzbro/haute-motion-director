# SFX Taxonomy, Synthesis Parameters & Cue-Sheet Schema

Complete reference for `scripts/sfx_engine.py` (48 kHz stereo float64, deterministic PRNG).

---

## 1. Musical Scales (`"scale"`)

Choose ONE scale per video so every chime, pop, tick, and glide sounds musically unified:

| Scale Key | Notes | Best SaaS Mood |
| :--- | :--- | :--- |
| `b_minor_pent` | `B, D, E, F#, A` | **Default (Hazene / System Zero)** — sleek, playful-futurist, modern AI/dev SaaS |
| `e_minor9` | `E, F#, G, B, D, F#` | Lush, atmospheric, editorial/premium product films |
| `d_major_pent` | `D, E, F#, A, B` | Bright, optimistic, friendly productivity & consumer apps |
| `c_major9` | `C, D, E, G, A, B` | Clean Apple/Linear minimalism, neutral elegance |
| `f_major_pent` | `F, G, A, C, D` | Warm, human, wellness/creative software |
| `a_minor_pent` | `A, C, D, E, G` | Focused, engineering/CLI/infrastructure tools |
| `g_lydian` | `G, A, B, C#, D, E, F#` | Wonder, science, deep-tech / AI breakthroughs |

---

## 2. Complete Primitive Parameter Reference (All 16 Generators)

All cues share common optional fields:
- `t` (float, seconds): exact onset time in timeline mode
- `pan` (float, `-0.85` to `+0.85`): stereo placement (keep subtle: `-0.25` to `+0.25`; omit to let Polymorphic Engine micro-pan)
- `gain_db` (float): relative cue level in dB
- `label` (string, ignored by engine): human-readable note for readability

### Tonal & Harmonic Primitives

1. **`glass_chime`** — Modal glass hero bell / confirmation ping
   - `degree` (int, default `0`): scale degree
   - `octave` (int, default `1`): octave offset (`0` warm mid, `1` crystalline bell)
   - `duration` (float, default `0.85`): ring-out seconds
   - `brightness` (float, `0.2–1.0`, default `0.55`): upper harmonic sheen

2. **`chord_bloom`** — Open-voiced OS startup / brand outro strummed glass chord
   - `degrees` (list[int], default `[0, 2, 4, 5]`): chord voicing on scale
   - `octave` (int, default `0`)
   - `duration` (float, default `1.85`)
   - `strum_ms` (float, default `28.0`): harp-like note stagger

3. **`liquid_pop`** — Organic Minnaert bubble pop (window open / modal / mascot / tooltip)
   - `degree` (int | null): explicit scale degree or auto-walk
   - `octave` (int, default `0`)
   - `direction` (`"up"` | `"down"`, default `"up"`): `"up"` for open/appear, `"down"` for close/collapse
   - `size` (`"small"` | `"medium"` | `"large"`, default `"medium"`)

4. **`bubble_cascade`** — Playful ascending/descending liquid arpeggio
   - `count` (int, `2–8`, default `4`)
   - `start_degree` (int, default `0`)
   - `step` (int, default `1`)
   - `spacing_ms` (float, default `58.0`)
   - `direction` (`"up"` | `"down"`, default `"up"`)
   - `pan_start` / `pan_end` (float, defaults `-0.18` / `+0.18`)

### Tactile Mechanical & Micro-UI Primitives

5. **`tactile_click`** — Physical two-stage mouse click / toggle actuation
   - `style` (`"mouse"` | `"toggle"` | `"soft"`, default `"mouse"`)
   - `double_stage` (bool, default `true`): adds natural 28ms release micro-click

6. **`topre_key`** — Single dampened Topre / lubed linear mechanical keystroke
   - `is_space_or_enter` (bool, default `false`): deeper, heavier space/return thock

7. **`typing_stream`** — Compound human-paced typing burst (auto-varied every character)
   - `chars` (int, default `12`)
   - `wpm` (float, default `115.0`)
   - `end_with_enter` (bool, default `true`)

8. **`hover_tick`** — Dry ceramic/wood melodic micro-tick for menu hovers & tabs
   - `degree` (int | null)
   - `octave` (int, default `1`)

9. **`menu_scrub`** — Compound cursor hover across dropdown items + optional final click
   - `items` (int, default `5`)
   - `interval_ms` (float, default `95.0`)
   - `start_degree` (int, default `0`)
   - `ascending` (bool, default `true`)
   - `end_with_click` (bool, default `true`)

10. **`aperture_snap`** — Leica-style dual mechanical shutter / corner-bracket focus lock
    - `pan`, `gain_db`

### Kinetic Transitions, Metrics & Textures

11. **`silk_whoosh`** — Warm formant-swept 1/f pink-noise air transition (zero harsh hiss)
    - `duration` (float, default `0.36`)
    - `direction` (`"in"` | `"out"`, default `"in"`)
    - `weight` (`"light"` | `"medium"` | `"heavy"`, default `"medium"`)
    - `pan_start` / `pan_end` (float, defaults `-0.25` / `+0.25`)

12. **`progress_glide`** — Sleek airy crystalline lift for progress bars & benchmarks
    - `duration` (float, default `0.55`)
    - `start_degree` / `end_degree` (int, defaults `0` / `2`)
    - `octave` (int, default `1`)
    - `with_lock_tick` (bool, default `true`)

13. **`counter_ratchet`** — Ease-out decelerating odometer tick cascade + confirmation chime
    - `duration` (float, default `0.95`)
    - `ticks` (int, `3–24`, default `10`)
    - `start_degree` (int, default `0`)
    - `with_resolve_chime` (bool, default `true`)

14. **`dither_flutter`** — Refined crisp pixel-morph / retro-digital telemetry flutter
    - `duration` (float, default `0.24`)
    - `grains` (int, default `8`)

15. **`sub_thud`** — Velvety centered mono sub-bass scene anchor (`115 -> 44 Hz`)
    - `duration` (float, default `0.24`)
    - `start_hz` / `end_hz` (float, defaults `115.0` / `44.0`)

### Rhythmic Bed Primitive

16. **`warm_pulse_bed`** (configured via top-level `"bed"` object or standalone preset)
    - `enabled` (bool), `start` (float seconds), `duration` (float seconds)
    - `bpm` (float, default `115.0`)
    - `gain_db` (float, default `-12.5`)

---

## 3. Cue-Sheet JSON Top-Level Schema

```json
{
  "duration": 20.0,
  "scale": "b_minor_pent",
  "seed": 108,
  "reverb_wet": 0.14,
  "reverb_decay": 0.46,
  "target_peak_db": -1.5,
  "warmth_shelf_db": -5.5,
  "bed": {
    "enabled": true,
    "start": 4.8,
    "duration": 11.4,
    "bpm": 115.0,
    "gain_db": -13.0
  },
  "cues": [
    { "t": 0.08, "type": "chord_bloom", "label": "Intro reveal" }
  ]
}
```

---

## 4. Pacing & Anti-Clutter Rules for SaaS Directors

- **Never put SFX on every single word or CSS animation.** Only accent physical state changes: window opens, user clicks, typing streams, metric locks, and major scene transitions.
- **Keep 30–40% of micro-transitions silent.** Contrast makes the remaining tactile hits feel expensive.
- **Match stereo pan to screen X-coordinates**: left sidebar (`-0.22`), center canvas (`0.0`), right inspector/CTA (`+0.22`).
- **End every video with breathing room**: drop the groove bed `2.5–4.0s` before the end so the outro chord + final CTA click resolves cleanly into silence.
