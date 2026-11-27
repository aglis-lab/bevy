# AI World Generation Guide & Self-Critique Playbook

This guide defines **concrete rules, numeric ranges, and a verification checklist** so an AI agent can generate high-quality environments in **Nerthus -> Bevy/Aurora -> Jolt** with minimal trial and error.

---

## 1. Nerthus Terrain Generation Rules

When authoring or editing a Nerthus terrain graph (via MCP or `.terrain` project):

1. **Always Include Macro + Meso + Micro Frequency:**
   - **Macro (200–1000 m):** Valley bowl, ridge line, coastal slope, or plateau that frames the horizon.
   - **Meso (20–100 m):** Rolling hills, terraces, gullies, and walkable clearings (never leave the playable area dead-flat).
   - **Micro (1–10 m):** Hydraulic erosion rills, thermal scree, rocky outcrops.
2. **Playability Constraints:**
   - Keep main playable zones and paths under **18°–22° slope**.
   - Use natural steep cliffs (**> 40° slope**) or water bodies as organic world boundaries instead of invisible walls.
   - Flatten village/building pads smoothly (`radius + soft falloff`), never sharp cookie-cutter circles.
3. **Mandatory Export Set (Always Export All 5):**
   - `heightmap.exr` (or 16-bit PNG) -> Bevy terrain mesh + Jolt `HeightFieldShape` + grass vertex height
   - `mask_slope.png` -> cliff rock vs. walkable ground
   - `mask_flow.png` -> riverbeds, damp dirt, lush grass streaks
   - `mask_wear.png` -> exposed stone/rock ridges
   - `mask_deposit.png` -> soft sediment, sand, fertile meadow soil

---

## 2. Procedural Scatter & Placement Rules

When generating prop/foliage placements (JSON/RON scatter recipe or Blender `bpy` script):

### A. Distribution Algorithm
- Use **Poisson-disk / Blue-noise sampling** (never pure uniform `rand()` which creates awkward overlaps and bald spots).
- Modulate density with **multi-scale noise × biome masks**:
  - `tree_density = forest_noise * (1.0 - road_mask) * (slope < 26°)`
  - `rock_density = (slope > 22° || wear_mask > 0.4) * (1.0 - road_mask)`
  - `grass_density = (1.0 - road_mask) * (slope < 32°) * (1.0 - tree_trunk_radius)`

### B. Prop Grounding & Variation Ranges

| Asset Class | Sink Depth (`-Y`) | Random Yaw | Random Tilt | Scale Jitter | Placement Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Trees** | `0.20–0.40 m` | `0°–360°` | `±4°` | `0.75–1.35×` | Group into groves; keep `2.5 m+` clear of road center |
| **Large Boulders** | `25%–40%` of height | `0°–360°` | `±15°` | `0.60–1.60×` | Never place isolated spheres on flat grass; pair with 2–3 smaller rocks + grass tufts |
| **Bushes / Shrubs** | `0.05–0.15 m` | `0°–360°` | `±8°` | `0.70–1.30×` | Cluster around tree bases, rocks, and path bends |
| **Lamp Posts / Signs** | `0.25 m` | Follow path tangent | `0°–1°` | `0.95–1.05×` | Place along outer shoulder of curved paths (`1.2–1.8 m` from edge), add grass/pebble cluster at base |
| **Props (Workbenches, Crates)** | `0.02–0.05 m` | Align to nearby wall/path | Match terrain normal (clamped `< 5°`) | `0.95–1.05×` | Place near buildings/camps/clearings—never floating in the middle of a road |
| **Grass Blades (GPU)** | `0.02 m` | `0°–360°` | Wind-driven | `0.50–1.50×` | Continuous meadow coverage + denser edge tufts hugging roads and rocks |

### C. Path / Road Rules
- Define paths as **smooth Catmull-Rom / Bezier splines** connecting landmarks.
- Sample path distance `d` to create:
  - Inner worn dirt (`d < 0.7 * half_width`)
  - Noisy transition border (`0.7..1.3 * half_width`, perturbed by Perlin noise so edges aren't smooth!)
  - Shoulder dressing zone (`1.0..1.5 * half_width`): extra grass tufts, small pebbles, and wildflowers.

---

## 3. World Recipe Schema Example (`world.ron`)

```ron
WorldRecipe(
    name: "sunlit_valley",
    style: Ghibli, // or Realistic
    terrain: (
        heightmap: "terrain/valley_height.exr",
        world_size: (256.0, 256.0),
        max_height: 42.0,
        masks: (
            flow: "terrain/valley_flow.png",
            wear: "terrain/valley_wear.png",
            deposit: "terrain/valley_deposit.png",
        ),
    ),
    lighting: (
        sun_elevation_deg: 34.0,
        sun_azimuth_deg: 55.0,
        sun_color: (1.0, 0.94, 0.82),
        shadow_tint: (0.34, 0.44, 0.66),
        fog_color: (0.68, 0.82, 0.94),
        fog_start: 45.0,
        fog_end: 210.0,
    ),
    grass: (
        enabled: true,
        instance_count: 120000,
        ring_radius: 28.0,
        blade_width: 0.048,
        blade_height_range: (0.20, 0.78),
        avoid_road_margin: 0.35,
    ),
    clusters: [
        (name: "oak_grove", anchor: "models/tree_oak.glb", companions: ["models/bush.glb", "models/rock_small.glb"], count: 45),
        (name: "mossy_outcrop", anchor: "models/rock_large.glb", companions: ["models/rock_small.glb", "models/fern.glb"], count: 30),
    ],
)
```

---

## 4. 12-Point AI Visual Self-Critique Checklist

Whenever reviewing a rendered screenshot of a scene, score every item **PASS / FAIL** and fix all **FAIL**s before moving on:

1. **[ ] Ground Coverage:** Is the meadow covered by rich, continuous grass/surface detail instead of a bare flat green/brown mat?
2. **[ ] Path Edges:** Are dirt/road edges broken up with noise, grass tufts, and small stones (no blurry airbrush stripe)?
3. **[ ] Prop Grounding:** Do all rocks, trees, lamp posts, buildings, and characters sit firmly *in* the ground with visible contact shadows/AO (no floating bases or sphere-like boulders sitting on top)?
4. **[ ] Shadow Color:** Are shadows cool-tinted (blue/indigo-green in daylight) rather than muddy grey/black?
5. **[ ] Lighting Angle:** Is the sun cross-lighting the scene (`25°–45°` elevation) so hills, trunks, and props have clear lit and shaded sides?
6. **[ ] Atmospheric Depth:** Do distant hills and trees soften and shift toward the sky color via fog?
7. **[ ] Value & Silhouette Readability:** In grayscale, do the player character and interactive objects immediately pop out from the ground?
8. **[ ] Style Cohesion:** Do terrain, grass, trees, props, and characters share the same lighting model and color temperature (no PBR ground clashing with cel trees)?
9. **[ ] Natural Clustering:** Are trees, rocks, and bushes grouped into Big->Medium->Small clusters with breathing room, rather than grid-spaced or randomly isolated?
10. **[ ] Terrain Relief:** Does the playable area have gentle height variation and framing hills rather than looking like a flat tabletop?
11. **[ ] Camera Framing:** Can the player see layered depth (foreground -> midground -> distant hills/sky) rather than staring straight down at the floor?
12. **[ ] Sense of Life:** Does the scene include wind motion, dappled/cloud shadows, or subtle ambient particles?
