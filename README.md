# Haute Motion Director Plugin

Modular Antigravity plugin bundling auteur motion direction, Remotion markup/motion blur, kinetic typography, procedural studio backdrops, and procedural sound design skills for SaaS product videos and motion graphics.

## Dual Execution System: Replication vs. From-Scratch

Haute Motion Director supports two distinct, production-grade operational modes:

1. **Pathway A: High-Density Motion Forensics & Replication** (When reference footage is provided):
   - Dense frame sampling ($6–10\text{ frames/cut}$) to eliminate static slide blind spots.
   - Forensic mapping of the 7 Motion Signatures (rotational recoil, active feed scrolling, data ticking, tactile click depression, staggered cascades, 3D spatial drift, staccato kinetic type).

2. **Pathway B: Autonomous From-Scratch Auteur Creation** (When creating from a GitHub repo, web app URL, product description, or brand concept):
   - Eliminates the "static slide deck / raw screenshot" trap.
   - Strictly enforces the **4-Layer Scene Architecture** across every composition:
     - **Layer 1: Procedural Atmospheric Backdrops & Optical Shaders** (`saas-procedural-backdrops` & `saas-procedural-gradients`): 6 pure-code SVG/CSS backdrops (Cobalt Studio, Arctic-Blue Horizon, Twilight Wireframe Arcs, Deep Space Floor Glow) or 13 dynamic 60fps canvas shader engines (Melt, Mesh, Silk, Beams, Glow, Ripple) with cryptographic film grain.
     - **Layer 2: Kinetic Typography Architecture** (`saas-kinetic-typography`): 5 signature kinetic type engines (Dynamic Inverted Highlight Box & Fisheye Ribbon Echo, In-Situ Nested Thread Typing, Gary Provost Staccato, Decelerating Odometers, and AST Monospace Streaming).
     - **Layer 3: Tactile Micro-UI Forensics & 3D Stage Choreography**: Authentic window frames, 3D perspective gimbal trajectories, live SVG vector cursor actuation with tactile click depression (`scale: 0.94`), real-time input streaming, and staggered cascades.
     - **Layer 4: Procedural Non-Fatiguing SFX & Anti-Fatigue Audio** (`saas-code-sfx`): 100% pure Python DSP synthesis (`sfx_engine.py`) with mandatory 8/8 PASS from `audit_sfx.py`.

## Bundled Skills

- **`haute-motion-director`** (`skills/haute-motion-director/SKILL.md`) — Zero-slop art direction, 60+ negative aesthetic constraints, 6 visual archetypes, high-density continuous motion forensics, and HyperFrames multi-scene engineering.
- **`saas-kinetic-typography`** (`skills/saas-kinetic-typography/SKILL.md`) — 5 signature kinetic typography styles:
  1. Cobalt expanding highlight box & fisheye ribbon echo punch
  2. In-situ nested forum/review thread (Reddit/Slack/Discord) with SVG stems, real-time typing, and optical depth-of-field blur
  3. Staccato voice-locked kinetic headline reveals with directional velocity blur
  4. Decelerating numerical tickers & metric odometers
  5. Curved category wheel & monospace AST token streaming
- **`saas-procedural-backdrops`** (`skills/saas-procedural-backdrops/SKILL.md`) — 6 pure-code CSS/SVG atmospheric backdrops (electric cobalt studio canvas, obsidian arctic-blue radial horizon, twilight celestial sky with 3D orbital arcs, deep space floor glow, and dashed architectural guideline grids).
- **`saas-procedural-gradients`** (`skills/saas-procedural-gradients/SKILL.md`) — 13 deterministic 60fps procedural gradient engines (Melt, Mesh, Silk, Beams, Glow, Ripple, Ribbons, Tide, Halo, Horizon, Linear, Radial, Conic), fluted glass optical refraction pass (`glassPass`), film grain noise (`grainPass`), and archetype color palettes for Remotion and HyperFrames.
- **`saas-code-sfx`** (`skills/saas-code-sfx/SKILL.md`) — Pure-code Python (`NumPy` + `SciPy`) tactile SaaS SFX synthesis engine (16 organic primitives, polymorphic anti-repetition, scale-locking, anti-piercing peak guards) plus an automated 8-gate DSP anti-fatigue auditor.
- **`remotion-markup`** (`skills/remotion-markup/SKILL.md`, upstream `remotion-dev/remotion@4.0.545`) — Official Remotion React markup, animation, transitions, and shutter-angle motion blur (`motion-blur.md`: `<HtmlInCanvasMotionBlur>` and `<TransitionSeries.Transition motionBlur>`).

## Extending This Plugin

Add new specialized skills by creating a new folder under:

```text
skills/<new-skill-name>/SKILL.md
```

Everything inside `skills/` is automatically discovered and toggled together as one plugin unit.
