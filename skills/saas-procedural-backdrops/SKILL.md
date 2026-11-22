---
name: saas-procedural-backdrops
description: >-
  Pure-code procedural studio backdrop and atmosphere generator for high-end SaaS
  and motion graphics compositions in HyperFrames and Remotion.
  Synthesizes 6 zero-slop architectural backdrops:
  (1) The Electric Cobalt Horizon with Curved Dashed Grid (Linear / Codesm Scene 1),
  (2) The Obsidian Deep-Sea Radial Gradient (Scene 6 arctic-blue signal space),
  (3) The Twilight Horizon with 3D Spherical Wireframe Arcs & HUD Coordinates (Scene 7 & 9),
  (4) The Deep Space Darkroom with Cyan-Mist Floor Glow (Scene 11 matrix stage),
  (5) The Architectural Micro-Dot & Dashed Guideline Canvas, and
  (6) Split-Screen Clean Seam Covers for live video/UI compositions.
  Use when generating, styling, or coding background environments, ambient lighting,
  wireframe grids, telemetry overlays, and studio backdrops purely in CSS and SVG.
version: 1.0.0
---

# SaaS Procedural Backdrops & Atmospheres (`saas-procedural-backdrops`)

Never settle for flat `#111111` boxes or generic muddy gradients. Elite SaaS films (Codesm, Linear, Raycast, Apple) build deep, cinematic, mathematical atmospheres using layered CSS gradients, SVG orbital wireframes, dashed guideline systems, and telemetry coordinate tags.

This skill provides ready-to-use pure-code blueprints that render instantly at 60 fps with zero external textures or images.

---

## The 6 Signature Procedural Backdrops

### Backdrop 1: The Electric Cobalt Studio Canvas (Scene 1 Hero)
- **Palette**: Solid royal electric cobalt `#3241CF`.
- **Architectural Grid**: SVG dashed radial curves centered off-canvas, framing typography dynamically.
```html
<div class="s1-bg" style="position: absolute; inset: 0; background: #3241CF;">
  <svg viewBox="0 0 1600 960" style="position: absolute; inset: -120px -160px; pointer-events: none;">
    <ellipse cx="800" cy="480" rx="720" ry="420" stroke="rgba(255,255,255,0.22)" stroke-width="1.2" stroke-dasharray="6 6" fill="none"/>
    <ellipse cx="800" cy="480" rx="540" ry="310" stroke="rgba(255,255,255,0.18)" stroke-width="1.2" stroke-dasharray="6 6" fill="none"/>
    <line x1="80" y1="480" x2="1520" y2="480" stroke="rgba(255,255,255,0.18)" stroke-dasharray="6 6"/>
  </svg>
</div>
```

---

### Backdrop 2: The Obsidian Arctic-Blue Radial Horizon (Scene 6 Feed Space)
- **Concept**: Deep carbon obsidian (`#000000`) with an intense Arctic-blue glow emanating from the bottom horizon (`#88B8DD → #264878 → #070C1D → #000000`).
- **CSS**:
```css
.arctic-horizon {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 96% 62% at 50% 108%, #88B8DD 0%, #264878 38%, #070C1D 68%, #000000 100%);
}
```
- **Telemetry Tag Layer**: Monospace coordinates (`JetBrains Mono`, `10px`, `letter-spacing: 0.04em`, `color: rgba(188, 204, 224, 0.72)`) anchored around the perimeter with 4px geometric corner dots:
```html
<span style="position: absolute; left: 130px; top: 120px; font-family: monospace; font-size: 10px; color: rgba(190,210,240,0.7);">
  <span style="width:4px; height:4px; background:#ABC; display:inline-block; margin-right:5px;"></span>[02, 1]
</span>
```

---

### Backdrop 3: Twilight Horizon with 3D Spherical Orbital Arcs (Scene 7 & 9)
- **Concept**: A curved planetary/celestial horizon that feels intellectual and expansive.
- **Gradient**:
```css
.twilight-sky {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, #000000 0%, #050918 36%, #142D50 66%, #4B91AC 100%);
}
```
- **Orbital Wireframe SVG**: Faint upper-sky orbital ellipses combined with vertical perspective meridians:
```html
<svg viewBox="0 0 1280 720" style="position: absolute; inset: 0; pointer-events: none;">
  <!-- Orbital rings -->
  <g fill="none" stroke="rgba(180,210,245,0.085)" stroke-width="1">
    <ellipse cx="640" cy="-140" rx="860" ry="380" />
    <ellipse cx="640" cy="-140" rx="740" ry="310" />
    <ellipse cx="640" cy="-140" rx="620" ry="240" />
    <!-- Meridians -->
    <path d="M120 0 Q190 210 280 390" />
    <path d="M290 0 Q340 200 410 380" />
    <path d="M470 0 Q495 190 530 370" />
    <path d="M640 0 L640 370" />
    <path d="M810 0 Q785 190 750 370" />
    <path d="M990 0 Q940 200 870 380" />
  </g>
</svg>
```

---

### Backdrop 4: Deep Navy-to-Cyan Floor Glow (Scene 11 Matrix)
- **Concept**: Ultra-clean studio stage for product tables, bento grids, and comparisons.
- **CSS**:
```css
.matrix-stage {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 90% 55% at 50% 112%, #68B4D4 0%, #1A3E62 36%, #030816 68%, #000000 100%);
}
```

---

### Backdrop 5: Obsidian-to-Deep-Navy Social Thread Backdrop (Scene 3 Reddit)
- **Concept**: Mood-locked dark mode with subtle bottom luminescent bounce so floating white text cards and user avatars pop with zero glare.
- **CSS**:
```css
.thread-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, #000000 0%, #020510 46%, #112440 78%, #2E547A 100%);
}
```

---

### Backdrop 6: Architectural Dashed Rulers & Guide Frame
- 1px hairline guide lines with `stroke-dasharray="6 6"` running at key golden-ratio coordinates (`x: 292px, 1014px`, `y: 248px, 446px`), providing technical structure to open typography.
