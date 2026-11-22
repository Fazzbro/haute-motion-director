---
name: saas-kinetic-typography
description: >-
  Master design and implementation skill for world-class SaaS kinetic typography
  and live textual micro-interactions in HyperFrames and Remotion.
  Synthesizes 5 proven auteur typographic styles:
  (1) The Cobalt Dynamic Highlight Box & Fisheye Ribbon Echo (Codesm Beat 1-4 / Linear hero),
  (2) In-Situ Thread Reply & Real-Time Character Typing (Reddit / Slack / Discord nested thread scroll with depth-of-field blur),
  (3) Staccato Voice-Locked Kinetic Headline Reveals (word-by-word Gary Provost rhythmic delivery with velocity-blur transitions),
  (4) Decelerating Numerical Tickers & Metric Odometers (precision Swiss easing with lock-in confirmation), and
  (5) Curved Category Wheel & Monospace AST Token Streaming.
  Use when writing, animating, or designing kinetic type, headlines, hero text,
  forum threads, customer review cards, or live typing streams for SaaS product videos.
version: 1.0.0
---

# SaaS Kinetic Typography & Textual Micro-Interactions (`saas-kinetic-typography`)

Auteur-grade motion design never fades in large blocks of static text. Words arrive with intentional musical cadence, tactile micro-interactions, physical camera framing, and in-situ software realism.

This skill provides ready-to-use, zero-slop architectural recipes for the 5 signature SaaS kinetic typography styles.

---

## The 5 Core SaaS Kinetic Typography Styles

### Style 1: The Cobalt Dynamic Highlight Box & Fisheye Ribbon Echo
**Seen In**: Codesm Research (Scene 1), Linear Launch films, Apple keynote teasers.  
**Best For**: Big opening problem statements (`"Every day, your market is telling you something"`).

#### Key Ingredients:
1. **Ultra-Tight Grotesk Ink**: `Inter` / `Helvetica Neue`, `font-size: 80px–118px`, `font-weight: 400`, `letter-spacing: -0.045em`, `line-height: 1.02`. Solid white ink on cobalt `#3241CF` or obsidian `#000000`.
2. **Expanding Inverted Highlight Boxes**: Rather than coloring text with a highlighter pen, text wraps inside an expanding solid white box (`background: #FFFFFF; color: #3241CF`) that scales its width from left to right (`width: 0 → fit-content` with `clip-path` or `scaleX` origin left).
3. **Ghost Word Departures**: As the camera pans right toward the next word, previous words drift to the left and drop in opacity (`opacity: 1 → 0.18`, `x: 0 → -120px`), creating spatial continuity.
4. **Fisheye Ribbon Echo Punch**: The final climactic word (`"something"`) cuts hard to a 5-row echoing cascade spanning the screen, curved along a cylindrical 3D arc using SVG paths or scale/perspective transforms (`center row: 148px, 1.0 opacity; flanking rows: 112px, 86px with 0.55/0.25 opacity`), capped by cropped framing words (`so` / `g`).

#### Implementation Blueprint (GSAP + HyperFrames):
```html
<div class="word-group">
  <div class="plain-word">Every day</div>
  <div class="highlight-shell">
    <div class="highlight-inner">your market</div>
  </div>
</div>
```
```javascript
// Expand white box smoothly across syllable cadence
tl.fromTo(".highlight-shell",
  { scaleX: 0, transformOrigin: "0% 50%" },
  { scaleX: 1, duration: 0.38, ease: "power3.inOut" },
  0.45
);
// Hard punch into 5-row fisheye ribbon echo on downbeat
tl.set(".beat-echo", { opacity: 1 }, 2.75);
tl.fromTo(".echo-row-center",
  { scale: 1.25, filter: "blur(8px)" },
  { scale: 1.00, filter: "blur(0px)", duration: 0.35, ease: "expo.out" },
  2.75
);
```

---

### Style 2: In-Situ Nested Thread & Real-Time Character Typing
**Seen In**: Codesm Research (Scene 3 Reddit thread), Slack / Discord customer voice scenes, Linear changelog cards.  
**Best For**: Showing real buyer sentiment, unfiltered feedback, competitor reviews, and social proof.

#### Key Ingredients:
1. **Native Social Chrome**: Crisp user avatars (`36px–86px`), username (`font-weight: 500, color: #F3F4F6`), subtle timestamp (`color: #6B7280`), and accurate vector icons (Upvote, Reply, Award, Share, `•••`).
2. **Continuous SVG Thread Stems**: Vertical line under avatar 1 connecting down to a circular white `(-)` collapse icon (`cx=173, cy=444, r=14`), which branches via a curved bezier `Q` path into avatar 2:
   ```html
   <svg viewBox="0 0 1280 720">
     <line x1="173" y1="264" x2="173" y2="428" stroke="rgba(255,255,255,0.8)" stroke-width="2.2" />
     <circle cx="173" cy="444" r="14" fill="#FFFFFF" />
     <path d="M 173 458 L 173 502 Q 173 535 212 535 L 246 535" stroke="rgba(255,255,255,0.72)" stroke-width="2.2" fill="none" />
   </svg>
   ```
3. **Character-by-Character String Typing**: Never use blinking monospace terminal text for human comments. Animate a JS proxy counter from `0` to `text.length` and slice the string on `onUpdate`:
   ```javascript
   const state = { count: 0 };
   const fullText = "Worth every penny for our team. We use it daily.";
   tl.fromTo(state, { count: 0 }, {
     count: fullText.length,
     duration: 0.85,
     ease: "none",
     onUpdate: () => { el.textContent = fullText.slice(0, Math.round(state.count)); }
   });
   ```
4. **Cinematic Upward Thread Scroll & Depth-of-Field Blur**:
   - The thread scrolls upward (`y: 0 → -330px`) as the reply appears.
   - Comment 1's action bar starts with slight tilt-shift blur (`filter: blur(2.4px)`), sharpens as it passes the lens center (`blur(0px)`), and drifts back into soft optical blur (`blur(2.2px)`) near the top edge.

---

### Style 3: Staccato Voice-Locked Kinetic Headlines
**Seen In**: Codesm Research (Scene 7 `"Just never in one place / and never on time"`, Scene 9 `"it watches the whole market"`).  
**Best For**: Problem transitions, product thesis reveals, feature milestones.

#### Rules:
- **Tight Line Tracking**: Headline `font-size: 64px–76px`, line-height `1.03`, tracking `-0.045em`.
- **Staggered Syllable / Word Entrance**: Each word arrives on the voiceover transient (`0.12s` stagger).
- **Directional Velocity Blur**: Words reveal with a fast `12px–20px` Y-axis or X-axis push, accompanied by directional blur that immediately resolves to zero:
  ```javascript
  tl.fromTo(word,
    { y: 18, filter: "blur(6px)", opacity: 0 },
    { y: 0, filter: "blur(0px)", opacity: 1, duration: 0.28, ease: "power3.out" }
  );
  ```
- **Pre-Cut Word Departures**: In two-part thoughts (`"Just never in one place"` → `"Never on time"`), the words don't sit dead until the cut; they stagger away `0.18s` before the hard transition.

---

### Style 4: Decelerating Numerical Tickers & Metric Odometers
**Seen In**: Codesm Research (`$2 → $39` pricing counter), SaaS revenue graphs, benchmark comparisons.

#### Rules:
- **Zero-Overshoot Exponential Braking**: Numbers step through realistic discrete values using `power3.out` or `expo.out` easing (dense steps early, wider intervals near target).
- **Lock-in Recoil**: The final metric scale-bounces subtly (`scale: 1.05 → 1.00` in 80ms) upon locking.
- **Pairs with Tactile Audio**: Always pair with `counter_ratchet` or `hover_tick` from `saas-code-sfx`.

---

### Style 5: Curved Rotary Category Wheel
**Seen In**: Codesm Research (Scene 10 category switcher).

#### Rules:
- **Curved Polar Geometry**: Categories (`reviews`, `headlines`, `conversations`) sit on rotating radial spokes pivoted off-canvas to the left (`transform-origin: -140px 50%`).
- **Active Selection Glow**: The active category is high-contrast pure white with a glowing blue indicator (`>`), while inactive categories fade to `rgba(255,255,255,0.28)` and scale down (`0.85x`).
- **Snapping Step Easing**: The wheel rotates with mechanical step-easing (`ease: "power2.inOut"`, rotation angle steps of `12°–18°`).
