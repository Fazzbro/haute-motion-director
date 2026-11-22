# The 6 World-Class Motion Archetypes Reference Guide

## 1. Native SaaS & High-Velocity UI Walkthrough

### Philosophy
Software should feel alive, tactile, and fast. The viewer should feel like an elite operator using the app at master-level speed.

### Palette & Surface Rules
- **Canvases**: Crisp Studio Pure White (`#FFFFFF`), Clean Paper (`#F8F9FA`), or Anodized Dark (`#0D0E10`).
- **Surface Elevation**:
  - Main Window: `background: #FFFFFF; border: 1px solid #E5E7EB; box-shadow: 0 24px 64px -16px rgba(0, 0, 0, 0.12); border-radius: 12px;`
  - Floating Action Sheets: `background: #111111; color: #FFFFFF; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15);`
- **STRICT BANS**:
  - **No dull greyish toggle overlays**: No `#2A2A2A` or semi-transparent grey boxes. Every card has either crisp black/white contrast or pure optical glass.
  - **No capsule eyebrow pills**: Never enclose category/feature eyebrows in dark rounded stadium pills (`border-radius: 999px`). Use pure, unboxed typography (a clean hairline or small sans-serif label).
  - **No glowing status dots**: Never place faux glowing green/red LED dots (`●` with `box-shadow`) next to text as cheap decoration.
  - **No red/green strikethrough diff cards**: Never build stacked comparison boxes with red/green borders, monospace micro-labels (`RAW / UNFILTERED` vs `CLEAN / FORMATTED`), and strikethroughs (`~~um~~`). Show transformations organically *inside* the native UI window (e.g. real input replacement, clean caret backspacing) or through crisp typography.
  - **No monospace marketing copy**: Monospace is forbidden for marketing headlines, feature tags, and subtitles; keep monospace strictly in genuine code editors, terminal CLIs, or financial tickers.

### Key CSS & GSAP Snippets
```css
/* Authentic SVG Mouse Cursor */
.svg-cursor {
  position: absolute;
  width: 24px;
  height: 24px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.25));
  pointer-events: none;
  z-index: 100;
}

/* Pulsing text insertion caret */
.typing-caret {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: #2563EB;
  margin-left: 2px;
  animation: blink 0.8s infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
```

---

## 2. Teenage Engineering / Braun Industrial Hardware

### Philosophy
Mechanical, tactile, precision-milled physical hardware. Zero digital gradients; pure physical materials.

### Palette & Material Rules
- **Canvases**: Bead-Blasted Aluminum (`#E2E2E0`), Warm ABS Plastic (`#DCD6CD`), Matte Carbon (`#161616`), Safety Orange (`#FF5722`).
- **Typography**: Industrial Monospace (`BM mini`, `JetBrains Mono`, `DIN 1451`). All uppercase, tracked `0.15em`.
- **Display Screens**: Amber 7-segment LEDs or 5x7 Dot-Matrix displays on recessed dark displays.

### Key CSS & GSAP Snippets
```css
/* Dot Matrix Display Simulation */
.dot-matrix {
  display: grid;
  grid-template-columns: repeat(24, 6px);
  gap: 3px;
  background: #101210;
  padding: 8px;
  border-radius: 4px;
  border: 2px solid #252825;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #1e241e;
}
.dot.on {
  background: #FF5722;
  box-shadow: 0 0 4px #FF5722;
}

/* Rotary Dial Click Animation */
/* GSAP ease must be "steps(1)" or "power4.out" with 0.08s duration to simulate physical detents */
```

---

## 3. Developer Terminal & Cybernetic Monospace

### Philosophy
Raw developer power, compiler speed, and terminal ergonomics.

### Palette & Material Rules
- **Canvases**: Pure Console Black (`#0A0B0C`), CRT Amber (`#1A1100`), or Carbon (`#111214`).
- **Typography**: `JetBrains Mono` or `Fira Code`.
- **Frames**: UTF-8 box characters (`┌`, `─`, `┐`, `│`, `└`, `┘`).

### Key Snippets
```html
<div class="terminal-box">
  <div class="terminal-header">
    ┌──[ willow-daemon // v2.4.1 ]───────────────────────────┐
  </div>
  <div class="terminal-body">
    │ $ willow listen --device="mic-0" --format="raw-pcm"     │
    │ > Hook initialized: active window = Slack.app           │
    │ > Buffer streaming: 48,000 Hz / 16-bit stereo           │
    │ > Latency: 142ms [OK]                                   │
  </div>
  <div class="terminal-footer">
    └──[ STATUS: STREAMING ]─────────────────────────────────┘
  </div>
</div>
```

---

## 4. Swiss Editorial Monograph & Kinetic Typography (Pentagram / A24)

### Philosophy
Massive scale, intense contrast, and editorial discipline.

### Palette & Material Rules
- **Canvases**: Stark High-Contrast Black/White (`#000000` / `#FFFFFF`), Warm Archival Travertine (`#EDE8DF`), Deep Hunter Green (`#122B1E`).
- **Typography**: Swiss Grotesk (`Inter`, `Söhne`, `Neue Haas Grotesk`) at colossal scales (`180px – 260px`).
- **Layout**: Dynamic architectural columns with 1px hairline divider borders.

---

## 5. Deep-Tech / Scientific Specimen (The Tension of Opposites)

### Philosophy
Cold mathematical precision framing organic, raw natural and biological phenomena.

### Palette & Material Rules
- **Canvases**: Obsidian Black (`#000000`), Carbon Graphite (`#0A0A0A`), Cleanroom White (`#FFFFFF`).
- **Signatures**: Microscope apertures, 4-corner SVG target brackets, 3D CSS perspective dossier cards, large slot-counter numeric sweeps.

---

## 6. Living Data & Kinetic Infographics

### Philosophy
Quantitative clarity, exponential growth curves, and dynamic data visualization.

### Palette & Material Rules
- **Canvases**: Fine Cartesian dot-grid graph paper (10px dot spacing).
- **Signatures**: Real-time SVG cubic bezier splines, live telemetry delta tags (`+340%`), animated sankey flow networks, zero-overshoot bar charts.
