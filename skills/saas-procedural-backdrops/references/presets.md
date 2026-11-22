# Pure-CSS & SVG Backdrop Presets

Drop these container classes directly into any HyperFrames scene `<template>`.

---

## 1. Arctic Signal Space
```html
<div class="bg-arctic" style="position: absolute; inset: 0; background: radial-gradient(ellipse 96% 62% at 50% 108%, #88B8DD 0%, #264878 38%, #070C1D 68%, #000000 100%);"></div>
```

## 2. Twilight Celestial Horizon
```html
<div class="bg-twilight" style="position: absolute; inset: 0; background: linear-gradient(180deg, #000000 0%, #050918 36%, #142D50 66%, #4B91AC 100%);"></div>
```

## 3. Cobalt Studio Launch Canvas
```html
<div class="bg-cobalt" style="position: absolute; inset: 0; background: #3241CF;"></div>
```

## 4. Darkroom Discussion Thread (Social Proof)
```html
<div class="bg-discussion" style="position: absolute; inset: 0; background: linear-gradient(180deg, #000000 0%, #020510 46%, #112440 78%, #2E547A 100%);"></div>
```

## 5. Overlay Guide Frame (Wireframe + Dashed Lines)
```html
<svg viewBox="0 0 1280 720" style="position: absolute; inset: 0; pointer-events: none;" data-layout-ignore="true">
  <line x1="292" y1="0" x2="292" y2="720" stroke="rgba(255,255,255,0.20)" stroke-width="1" stroke-dasharray="6 6" />
  <line x1="1014" y1="0" x2="1014" y2="720" stroke="rgba(255,255,255,0.20)" stroke-width="1" stroke-dasharray="6 6" />
  <line x1="0" y1="248" x2="1280" y2="248" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="6 6" />
  <line x1="0" y1="446" x2="1280" y2="446" stroke="rgba(255,255,255,0.14)" stroke-width="1" stroke-dasharray="6 6" />
</svg>
```
