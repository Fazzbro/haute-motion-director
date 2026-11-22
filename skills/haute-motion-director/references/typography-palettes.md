# Haute Typography & Anti-Slop Palette Reference

## 1. The Anti-Slop Palette Tokens (Locked Hex Values)

Never pick arbitrary colors or saturated neon gradients. Every color must map to real-world physical and architectural materials:

### Master Canvases
| Name | Hex Token | Material Inspiration | Where to Use |
|---|---|---|---|
| **Obsidian Black** | `#000000` | Deep cosmic void / darkroom | Primary high-contrast motion stage |
| **Carbon Graphite**| `#0A0A0A` | Anodized carbon steel / obsidian | Specimen background with depth |
| **Pure Laboratory**| `#FFFFFF` | Sterile cleanroom / architectural paper | Final inverted climax & white resolution |
| **Warm Chalk**     | `#F7F5F0` | Archival cotton print paper | Dossier paper card surfaces |
| **Muted Stone**    | `#E8E6E1` | Travertine limestone / raw concrete | Secondary card dividers & paper borders |

### Inks & Typographic Tokens
| Name | Hex Token | Where to Use |
|---|---|---|
| **Stark White**    | `#FFFFFF` | Primary headlines on black canvas |
| **Bone White**     | `#E2E2DC` | Secondary body text & subheadings on black |
| **Deep Charcoal**  | `#111111` | Primary headlines on white resolution canvas |
| **Muted Graphite** | `#555555` | Secondary metadata & guideline connectors |
| **Hairline Gray**  | `rgba(255, 255, 255, 0.25)` | Technical bounding boxes & target brackets |

### Single Forensic Accents (Reserved for 1% of Canvas Area)
Pick **at most ONE** accent per film:
1. **Cadmium Scientific Red**: `#E11D48` (Tiny 10px status dot, rec label, critical metric tag).
2. **Deep Sea Emerald**: `#059669` (Rotating molecular lattice, bio-synthetic structure).
3. **Fluorite Amber**: `#D97706` (Mineral specimen annotation, warning coefficient).
4. **Cobalt Titanium**: `#2563EB` (Deep marine depth indicator, quantum energy level).

---

## 2. Typographic Hierarchy & Metric Standards

### The Dual-Font System:
High-end motion graphics rely on the contrast between an **engineered Swiss grotesk** and a **precision technical monospace**.

1. **Primary Voice**: `Inter`, `Söhne`, or `Neue Haas Grotesk`
   - Weight: `400` (Regular) or `500` (Medium). **Avoid 700/800 bold walls** which look like loud amateur ads.
   - Large Headlines (`56px – 72px`):
     - `letter-spacing: -0.035em` to `-0.045em` (tight tracking).
     - `line-height: 1.0` to `1.08`.
   - Small Labels (`14px – 18px`):
     - `letter-spacing: -0.015em`.
     - `line-height: 1.3`.

2. **Metadata & HUD Voice**: `JetBrains Mono`, `SF Mono`, or `Space Mono`
   - Weight: `400`.
   - Size: `10px – 12px`.
   - Casing: `uppercase`.
   - `letter-spacing: 0.12em` to `0.20em` (widely tracked for technical precision).
   - Usage: Coordinate readouts (`X: 490.22 Y: 150.04`), specimen indices (`REF: SCYPHOZOA-04`), scale markers (`100 µm`).

---

## 3. Kinetic Text Animation Rules

1. **The Staccato Cut**:
   - Words appear abruptly on exact audio beats without slow fades.
   - Hold times must obey cognitive reading thresholds:
     - 1-word punch: Hold for `0.20s` to `0.35s`.
     - 2-to-3 word phrase: Hold for `0.50s` to `0.80s`.
2. **The Typewriter Inset Mask**:
   - For secondary explanatory lines, reveal text using a razor-sharp CSS `clip-path`:
     ```css
     clip-path: inset(0 100% 0 0); /* start */
     clip-path: inset(0 0% 0 0);   /* end */
     ```
   - Linear or subtle `power1.out` easing over `0.4s – 0.6s`.
3. **The Discrete Numeric Slot Counter**:
   - For data statistics ($52\% \rightarrow 98\%$), do not use a smooth blur of numbers that the eye cannot register.
   - Use discrete keyframe jumps ($52\% \rightarrow 67\% \rightarrow 74\% \rightarrow 85\% \rightarrow 92\% \rightarrow 98\%$) timed to audio transients.
