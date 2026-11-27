# Dual-Style Rendering Recipes for Bevy / Aurora

Aurora supports **both** stylized painterly worlds and realistic PBR worlds on top of the **same terrain heightmap, biome masks, and Jolt collision**. Pick one `RenderStyle` preset per scene so every shader, light, and post-FX pass stays visually unified.

---

## Recipe A: Ghibli / Painterly Stylized (`RenderStyle::Ghibli`)

Designed to achieve the crisp 60 FPS painterly look (reference: Fernwake / Breath of the Wild / Studio Ghibli).

### 1. Unified Lighting & Cel Shading (Ground, Grass, Trees, Props, Characters)
**Golden Rule:** Do **not** mix PBR ground/grass with cel characters. All environment surfaces must share the same cel lighting functions in WGSL (`#import aurora::painterly`).

- **2-Tone Hand-Mixed Cel Ramp:**
  - Instead of multiplying shadow areas by black, blend between two hand-mixed colors:
    - `lit_paint`: Base color with subtle saturation lift (`mix(luma, base, 1.12)`) × warm sun tint (`vec3(1.04, 1.00, 0.90)`).
    - `shade_paint`: Base color shifted toward cool indigo/teal (`base * vec3(0.42, 0.50, 0.68)`).
  - Terminator: Crisp but anti-aliased `smoothstep(0.0, 0.04, ndotl)` (tighter on characters, slightly softer `0.08` on terrain).
  - Zero glossy PBR specular on grass, dirt, bark, and leaves (only quantized specular + rim on metal/water/characters).
- **Shared Multi-Scale Brushstroke Noise (`tStrokes`):**
  - Sample a seamless painterly brushstroke texture in **world XZ** at 3 frequencies (`/6.0`, `/25.0`, `/80.0`) on both **terrain** and **grass** so grass blades inherit the exact painterly color patches of the ground beneath them.
- **Cloud Shadows & Canopy Shadows:**
  - Scroll a low-frequency cloud shadow mask in world XZ (`0.65..1.0` multiplier) across terrain + grass + props.
  - Optional: disable expensive shadow maps if using analytical dappled canopy shadows + contact blob shadows, or use soft tinted directional shadows pushed toward cool blue.

### 2. Dense GPU-Instanced Grass Ring (60 FPS Target)
- **Geometry:** 3-segment curved blade (`4–5 cm` base width tapering `85%` to tip, height `0.18–0.85 m` modulated by noise + Nerthus biome/path mask).
- **Rendering:** **1 draw call** (`80,000–145,000` instances) torus-wrapped in a `±28 m` ring around the camera/player using custom GPU instancing + `NoFrustumCulling`.
- **Blending with Ground:**
  - Base of blade (`v = 0.0`) matches the exact terrain color + `tStrokes` tint so blades melt seamlessly into the soil.
  - Tip (`v = 1.0`) shifts slightly warmer/brighter in sunlight and bends with world-space wind waves.
  - Grass density mask = `meadow_mask * (1.0 - road_mask) * slope_mask` (with a soft noisy edge so grass tufts encroach naturally onto dirt paths).

### 3. Painterly Trees (No Solid Plastic Blobs)
- **Canopy:** Instanced alpha-cutout (`AlphaMode::Mask`) leaf spray cards with **baked spherical/fluffy normals** (pointing outward from canopy clusters) so the canopy shades like soft painted clouds instead of flat intersecting planes.
- **Camera Occlusion Dither:** Screen-door dither fade when tree canopy sits between camera and player.
- **Roots:** Flared roots sunk `0.2–0.4 m` into terrain with dark mossy vertex-color AO at the base.

### 4. Selective Ink Outlines + Selective Kuwahara Post-FX
- **Camera Setup:** `Hdr` (`Rgba16Float`), `DepthPrepass`, `Msaa::Off` (so discrete IDs aren't blended at edges), `Tonemapping::None`.
- **HDR Alpha-ID Channel:** Opaque custom materials write a material class ID into `out.a`:
  - `0.03..0.21` — Character parts (cloak, helm, weapon, armor, skin, creatures)
  - `0.40` — Interactive props / buildings
  - `1.00` — Environment (terrain, grass, trees, sky)
- **Final Fullscreen Pass (`Core3dSystems::PostProcess`):**
  1. **Depth-Aware Ink Outline:** Draw warm dark ink (`vec3(0.20, 0.14, 0.15)`) where neighboring alpha IDs differ AND `min(a, b) < 0.23`, **skipping** pixels where a closer non-inked occluder (`alpha >= 0.23`, e.g., foreground grass blades) sits in front in `DepthPrepass`.
  2. **Selective Kuwahara Filter:** Run a 4-quadrant Kuwahara brush filter **only where `alpha >= 0.6`**, giving terrain/grass/trees a hand-painted finish while keeping characters and buildings razor-sharp.
  3. **Painter's Tone Curve:** Preserve midtone paint hues faithfully below `0.62`, then apply smooth exponential highlight rolloff:
     ```wgsl
     let hi = max(c - 0.62, vec3(0.0));
     let mapped = min(c, vec3(0.62)) + 0.38 * (1.0 - exp(-hi / 0.38));
     ```

---

## Recipe B: Realistic PBR (`RenderStyle::Realistic`)

Designed for photorealistic outdoor/indoor environments using Bevy's PBR stack and optional `bevy_solari` ray tracing.

### 1. Physically Accurate Material Calibration
- **Albedo / Base Color:** Keep sRGB luminance between **0.04 (charcoal)** and **0.85 (fresh snow)**—never pure `#000000` or `#FFFFFF` (breaks energy conservation and blows out lighting).
- **Roughness Variation (Secret to Realism):** Never use a flat scalar roughness. Every surface (rock, dirt, bark, wood, metal) needs a roughness map with micro-variation (e.g., damp mud `0.25–0.45`, dry soil `0.80–0.95`, weathered rock `0.65–0.90`).
- **Terrain Multi-Texturing (`texture_2d_array`):**
  - Drive 4–8 PBR layers (grass, soil, wet mud, cliff rock, scree, snow) using Nerthus's exported **flow, wear, deposit, and slope** masks.
  - Use **height-based blending** (comparing layer heightmaps + mask weights) so pebbles/rocks poke cleanly through dirt instead of blurry alpha fades.
  - Break up tiling with **stochastic / dual-scale UV sampling** (near detail + far macro variation).

### 2. Lighting, Atmosphere & Ray Tracing
- **Sun & Sky:** `DirectionalLight` (realistic lux: `30,000–100,000` with `Atmosphere` + `Exposure::SUNLIGHT`) + `EnvironmentMapLight` / procedural sky IBL.
- **Shadows & GI:**
  - Standard path: Cascaded shadow maps + `ScreenSpaceAmbientOcclusion` (SSAO) + `VolumetricFog` + `DistanceFog`.
  - High-end native path: Enable **`SolariPlugins`** (`RaytracingMesh3d` + `SolariLighting` + optional DLSS Ray Reconstruction) for dynamic raytraced direct & indirect global illumination.
- **Post-Processing:**
  - `Tonemapping::AgX` (best highlight desaturation for realistic daylight)
  - Subtle `Bloom::NATURAL`
  - `TemporalAntiAliasing` (TAA) or `Smaa`
  - Subtle `ColorGrading` (lift/gamma/gain + slight warm/cool split)
