# Environment Art Direction Guide (Universal Visual Craft)

These rules apply to **every** 3D environment—whether Ghibli painterly or photorealistic PBR. Violating even 2–3 of these is what makes a scene feel "off" or "toy-like."

---

## 1. Value Hierarchy & Readability (Most Important Rule)

If you convert a screenshot of a great game to **grayscale**, you can instantly tell what is playable ground, what is an obstacle, and who the player is.

- **Characters & Interactive Objects:** Highest contrast and crispest silhouettes (brightest highlights or darkest accents / selective ink outlines).
- **Playable Ground & Paths:** **Low-frequency, low-contrast, medium value.** Never put noisy, high-contrast gravel or harsh dark blotches on walkable ground—it fights with the player character.
- **Background & Distant Hills:** Lower contrast, compressed value range, shifted toward sky color via atmospheric fog.
- **60–30–10 Color Rule:**
  - **60% Dominant** (e.g., lush meadow greens or muted earth tones)
  - **30% Secondary** (e.g., warm dirt paths, tree bark, stone)
  - **10% Accent** (e.g., hero cloak, flowers, lanterns, roofs, glowing shrines)

---

## 2. Lighting & Shadow Color (No Muddy Grey Shadows)

Never use pure white sun (`#FFFFFF`) with pure black/grey shadows.

- **Warm Sun / Cool Shadow Law (Daylight):**
  - Sun/Key light: Warm cream/golden (`#FFF3D6` to `#FFE4B5`).
  - Ambient/Shadow fill: Cool sky blue or indigo-teal (`#4A6B9C` to `#2B3D63`), **never** neutral grey.
- **Sun Angle:**
  - Avoid overhead noon lighting (85°–90°)—it flattens terrain relief and shrinks shadows into awkward blobs directly under objects.
  - **Sweet spot:** **25°–45° elevation** and **45°–70° off-axis from the camera** (cross-lighting). This carves hills, casts long readable tree shadows across paths, and separates lit/shaded sides on every rock and character.
- **Rim / Backlight:**
  - Subtle warm or sky-tinted rim light on characters and foliage edges separates them cleanly from dark tree shadows.

---

## 3. Grounding Objects (Eliminating the "Floating / Pasted On" Look)

Objects look fake when a hard mesh edge meets a flat terrain plane with no transition.

1. **Sink Geometry Into Terrain:**
   - **Boulders / Rocks:** Sink **20–40%** of their height into the ground. Never leave a spherical rock resting on a single point.
   - **Tree Trunks / Roots:** Flare roots into the slope; sink base **0.15–0.4 m** so uphill/downhill slopes never expose a gap underneath.
   - **Fences, Posts, Lamp Posts, Buildings:** Extend foundations/posts **0.2–0.5 m** below `y = 0` so slopes never leave floating corners.
2. **Contact Shadows / Contact AO:**
   - Darken the immediate 10–30 cm ring where an object touches the ground (via SSAO, baked vertex AO, decal blob shadow, or height-based AO in the shader).
3. **Transition Dressing (Skirts):**
   - Place **small grass tufts, weeds, pebbles, or dirt decals** specifically around the base of trees, rocks, fences, and buildings.
   - **Path / Road Edges:** Never leave a smooth airbrushed gradient between dirt and grass. Break up the edge with denser grass blades, small stones, and wildflowers hugging both sides of the path.

---

## 4. Natural Composition & Clustering

Human brains instantly detect random uniform scatter or grid alignment.

- **The "Big -> Medium -> Small" Cluster Rule:**
  - Never place a lone rock or lone bush in the middle of an empty field unless it's an intentional landmark.
  - Build natural clusters: **1 Large anchor** (tree or cliff/boulder) + **2–3 Medium companions** (smaller rocks, bushes) + **5–10 Small details** (tall grass clumps, ferns, wildflowers, fallen twigs).
- **Negative Space (Breathing Room):**
  - Leave clear, readable open areas (meadows, paths, courtyards) between clusters so the eye can rest and the player can navigate easily.
- **Curved Lines > Straight Lines:**
  - Roads, rivers, fence lines, and lamp-post rows should follow terrain contours with gentle S-curves, not ruler-straight lines.
- **Landmarks & Sightlines (Weenie Principle):**
  - Every camera view should have at least one tall or distinct landmark in the mid/background (windmill, ruins, giant tree, mountain peak, bridge) that draws the player forward.
- **Three Depth Planes:**
  - **Foreground:** Frame edges with grass, overhanging branches, or fence/roof corners.
  - **Midground:** Playable path, characters, village/props.
  - **Background:** Layered rolling hills, distant silhouettes, sky, and clouds.

---

## 5. Camera Framing & Scale

- **Avoid Steep "Flat Carpet" Angles:**
  - Looking down at 55°–70° hides the sky and turns the screen into 85% bare floor.
  - Even for third-person adventure games, keeping camera pitch around **15°–32°** (with FOV `45°–60°`) reveals layered hills, tree canopies, and sky—instantly making the world feel 3× larger.
- **Consistent Human-Scale Reference:**
  - Standardize world scale (1 unit = 1 meter):
    - Human character: `1.6–1.8 m` (stylized chibi: `1.2–1.4 m`)
    - Doorway: `2.1–2.4 m`
    - Lamp post: `2.8–3.8 m`
    - Small bush: `0.6–1.2 m`
    - Meadow grass blade: `0.2–0.7 m`
    - Trees: `5–14 m` (vary height by `±30%` so canopies don't form a flat ceiling)

---

## 6. Atmosphere, Depth & Living Motion

Still screenshots look dead without atmosphere; live frames feel dead without secondary motion.

- **Distance Fog + Height Fog:**
  - Exponential distance fog blending into the **horizon sky color** (never pure grey).
  - Optional low-lying valley/morning mist (`height fog`) softens the transition between terrain and distant mountains.
- **Dappled Light & Cloud Shadows:**
  - Slowly scrolling cloud shadow noise across the entire valley breaks up uniform sunlight and makes the landscape feel vast and alive.
- **Secondary Motion (Always Have At Least 2):**
  - Wind waves rolling across instanced grass (world-space scrolling sine/noise field, not random per-blade jitter).
  - Gentle canopy leaf sway.
  - Ambient particles (drifting pollen, dandelion seeds, leaves, dust motes, or fireflies at dusk).
  - Animated water ripples + shoreline foam.
