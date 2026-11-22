# SaaS Kinetic Typography Recipes & Code Snippets

Ready-to-drop components for HyperFrames and Remotion compositions.

---

## 1. Expanding Highlight Inversion Box

### CSS:
```css
.highlight-shell {
  display: inline-block;
  background: #FFFFFF;
  overflow: hidden;
  vertical-align: top;
  will-change: transform;
}
.highlight-text {
  padding: 8px 64px 16px 28px;
  font-size: 114px;
  font-weight: 400;
  letter-spacing: -0.045em;
  line-height: 1.02;
  color: #3241CF; /* Matches background */
  white-space: nowrap;
}
```

### HTML:
```html
<div class="line">
  <span class="plain-text">your</span>
  <div class="highlight-shell" id="hl-1">
    <div class="highlight-text">market</div>
  </div>
</div>
```

### GSAP:
```javascript
tl.fromTo("#hl-1",
  { scaleX: 0, transformOrigin: "0% 50%" },
  { scaleX: 1, duration: 0.36, ease: "power3.inOut" }
);
```

---

## 2. In-Situ Forum/Review Thread (Reddit / Slack / Discord)

### HTML & SVG Branching Stems:
```html
<div class="thread-stage">
  <svg class="thread-stem-svg" viewBox="0 0 1280 720">
    <!-- Vertical stem from Avatar 1 -->
    <line x1="173" y1="264" x2="173" y2="428" stroke="rgba(255,255,255,0.8)" stroke-width="2.2" />
    <!-- Circular collapse icon -->
    <circle cx="173" cy="444" r="14" fill="#FFFFFF" />
    <line x1="166.5" y1="444" x2="179.5" y2="444" stroke="#080D1B" stroke-width="3" stroke-linecap="round" />
    <!-- Curved L-branch to Avatar 2 -->
    <path d="M 173 458 L 173 502 Q 173 535 212 535 L 246 535" stroke="rgba(255,255,255,0.72)" stroke-width="2.2" fill="none" />
  </svg>

  <div class="comment-1">
    <img class="avatar" src="assets/avatar1.png" />
    <span class="user">username_1</span>
    <div id="c1-body" class="body-text"></div>
  </div>

  <div class="comment-2" style="margin-left: 118px;">
    <img class="avatar" src="assets/avatar2.png" />
    <span class="user">username_2</span>
    <div id="c2-body" class="body-text"></div>
  </div>
</div>
```

### GSAP Character Typing & Thread Scroll:
```javascript
const c1Text = "Worth every penny for our team. Saves us hours.";
const c2Text = "Really? We cancelled after a month.";

const s1 = { len: 0 }, s2 = { len: 0 };

tl.fromTo(s1, { len: 0 }, {
  len: c1Text.length,
  duration: 0.70,
  ease: "none",
  onUpdate: () => { document.getElementById("c1-body").textContent = c1Text.slice(0, Math.round(s1.len)); }
}, 0.1);

// Thread scrolls up as reply begins typing
tl.to(".thread-stage", { y: -280, duration: 0.52, ease: "power2.inOut" }, 0.55);

tl.fromTo(s2, { len: 0 }, {
  len: c2Text.length,
  duration: 0.65,
  ease: "none",
  onUpdate: () => { document.getElementById("c2-body").textContent = c2Text.slice(0, Math.round(s2.len)); }
}, 0.70);
```
