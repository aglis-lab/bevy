# Visual & Engine Gap Analysis: Original Fernwake (`painted_valley.mjs`) vs. Estella Engine Migration

**Date:** 2026-11-27  
**Reference Build (Original):** `http://127.0.0.1:8765/` (`index.html`, `painted_valley.mjs`)  
**Target Build (Estella):** `assets/scenes/main.esscene`, `assets/materials/*`, `.esengine/`

---

## Executive Summary

The original Fernwake build looks noticeably sharper, more cohesive in its toon shading, and runs lush long/slim grass at **60 FPS** while the Estella migration has shorter/chunkier grass, weaker toon cohesion, no selective character ink lines, and runs at **12–18 FPS** under full detail.

The root cause is **not** a single missing slider—it is **four architectural & engine-level gaps**:

1. **GPU-Instanced Camera-Following Grass vs. Static CPU-Merged Cells:** The original renders **145,000 slim curved blades** (`4.8 cm` wide, `~0.18–0.85 m` tall) in **1 draw call** wrapped in a 56 m × 56 m torus around the player using `THREE.InstancedBufferGeometry`. Estella's `Foliage` system builds static CPU-merged `FoliageCell` meshes across fixed grid cells; scaling that to 145k slim multi-segment blades explodes CPU bake time and GPU triangle counts (`1.1–1.5M tris` at 12–18 FPS).
2. **Custom `.esshader` Runtime Loading Is Broken in Estella Play Mode (404):** Custom shaders placed in `assets/shaders/*.esshader` fail to load in Play mode (`Failed to fetch 'assets/shaders/<name>.esshader': 404 Not Found`), forcing the migration back onto built-in shaders (`builtin:toon`, `builtin:foliage`, `builtin:terrain`).
3. **Built-in Foliage & Terrain Are PBR-Lit (Not Toon-Lit):** In the original, ground, grass, tree trunks, canopies, rocks, props, and characters all share custom GLSL cel functions (`meadowGreen`, `meadowLight`, 2-tone `smoothstep` terminator, shared `tStrokes` brushwork). In Estella, `builtin:foliage` and `builtin:terrain` both run PBR `applyLightingSurface(...)`, breaking visual unity between the ground/grass and toon characters.
4. **No Alpha-ID Screen-Space Ink Outline or Selective Kuwahara Pass in Estella:** The original writes a per-part `INK` ID into the HDR alpha channel (`< 0.23` for characters/weapons, `0.40` for props, `1.0` for environment) so the final full-screen pass draws **crisp depth-aware ink lines around characters (never inked over occluding grass)** and applies a **4-quadrant Kuwahara paint filter only where `alpha >= 0.6`**. Estella's `edgeOutline` operates globally on scene depth/normals with no material/entity ID mask, and Estella has no built-in Kuwahara pass.

---

## Side-by-Side Architecture Comparison

| Area                          | Original Fernwake (`painted_valley.mjs` + `index.html`)                                                                                                                                                                                                                                                        | Estella Engine Migration (`main.esscene` + `builtin:*`)                                                                                                                                                                                           |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Grass Geometry & Density**  | `createPaintedGrass`: `145,000` desktop (`55,000` touch) GPU-instanced 3-segment curved blades (`4.8 cm` base width tapering `85%` to tip, height `~0.18–0.85 m` modulated by multi-scale noise), torus-wrapped in `±28 m` around hero (`1` draw call).                                                        | `Foliage` component (`id: 95`): CPU-merged static `20×20 m` cells (`count: 680` clumps/cell) using `ghibli_grass_clump.esmesh` (`14` blades, `42` tris/clump, `0.11–0.38 m` height). High blade counts require splitting into many static cells.  |
| **Grass & Ground Shading**    | **Custom GLSL cel + brushwork:** Ground (`createPaintedGround`) and grass (`createPaintedGrass`) both sample `tStrokes` at 3 frequencies (`/6`, `/25`, `/80`) and compute shared `meadowGreen(tone) * meadowTint(w) * meadowLight(cloudAt)` with zero specular sheen.                                          | **PBR (`applyLightingSurface`):** `builtin:foliage` (`ghibli_foliage_master.esmaterial`) and `builtin:terrain` (`ghibli_terrain_valley.esmaterial`) use physically based BRDF lighting rather than cel bands or shared painterly brushwork.       |
| **Character & Prop Toon**     | `createPaintedCharMaterial` & `paintWorldMaterial`: 2-tone hand-mixed warm `litPaint` (`litTint` + chroma lift `1.12`) and cool indigo `shadePaint` blended across a crisp `smoothstep(0.0, 0.038, ...)` terminator, plus quantized steel specular & rim.                                                      | `builtin:toon` (`hero_toon_master.esmaterial`): Multiplicative `ambient + lit + u_shadeColor * (1 - lightAmount)` — lacks custom chroma-lifted lit paint, hand-mixed cool shadow paint remapping, and `openAt()` canopy shadow modulation.        |
| **Outlines & Brush Finish**   | **Alpha-ID Ink + Selective Kuwahara (`createPaintedFrame`):** Per-part `INK` IDs in HDR alpha drive `inkAt()` (outlines `< 0.23` with depth occlusion test so foreground grass covers hero feet cleanly) and `painted()` (Kuwahara filter skipped for `alpha < 0.6`).                                          | `edgeOutline` / `depthOutline` (`basic.js`): Global depth + G-buffer normal threshold across the entire frame. No per-entity/material ID channel, so outlines either bleed onto grass/terrain or miss internal part seams. No Kuwahara effect.    |
| **Custom Shaders at Runtime** | Inline `THREE.ShaderMaterial` (WebGL2/GLSL3) loaded directly by JS modules — zero asset pipeline friction.                                                                                                                                                                                                     | Custom `assets/shaders/*.esshader` files fail in Estella Play mode with `Failed to fetch 'assets/shaders/<name>.esshader': 404 Not Found` (`AssetPlugin.js:9448`).                                                                                |
| **Tree Canopies & Shadows**   | `createPaintedTrees`: Procedural mossy curved trunks + instanced 4-tone `tLeaf` alpha-cutout spray cards using baked sphere normals (`aBall`), camera-to-hero dither fade (`treeOccKeep`), and analytical dappled ground shadows (`openAt`). Real shadow maps disabled (`renderer.shadowMap.enabled = false`). | Static GLB import `tree_spring_anime.esmesh` (smooth solid blobs, no cutout leaf cards or camera-hero dither). Auto-generated `_lod2` meshes broke UV islands, causing trunk cyan/green texture bleed. Relies on `2048` 2-cascade GPU shadow map. |
| **Tone Curve**                | `THREE.NoToneMapping` + custom painter's curve (`min(c, 0.62) + 0.38 * (1 - exp(-hi / 0.38))`) preserving midtone paint hues faithfully before sRGB output.                                                                                                                                                    | Project `outputTransform: "neutral"` in `linear` space (good hue preservation, but lacks the custom `0.62` midtone lock + exponential highlight rolloff).                                                                                         |
| **Frame Rate / Cost**         | **60 FPS** (`1` draw call for 145k grass blades, analytical shadows, instanced leaf cards).                                                                                                                                                                                                                    | **12–18 FPS** (`~1.1–1.5M` triangles, static merged foliage cells, full-detail meshes, 2-cascade `2048` shadows, `renderScale: 0.85`).                                                                                                            |

---

## Missing / Broken Estella Engine Features (Verified Gaps)

### GAP-1 (Blocker Bug): Custom `.esshader` Assets Return 404 in Estella Play Mode

- **Observed Behavior:** Creating `assets/shaders/ghibli-toon.esshader` or `assets/shaders/ghibli-ground.esshader` and referencing them from `.esmaterial` works inside the editor context or crashes Play mode during asset load with:
  `Error: Failed to fetch 'assets/shaders/<name>.esshader': 404 Not Found` (thrown from `AssetPlugin.js:9448`).
- **Impact:** Blocks **all** custom `.esshader` development for Play/Export builds—meaning we cannot implement Painted Valley 2-tone cel shading, custom toon grass/terrain, custom alpha-ID output, or custom leaf-card shaders in `.esshader` until the Play server/bundler includes or serves project `.esshader` files.

### GAP-2 (Missing Feature): GPU-Instanced Foliage / Camera-Following Grass Ring (`InstancedMesh`)

- **Estella Current Design:** `foliagePlugin.js` and `lodDistance.js` (`src/foliage/builder.ts`) split a terrain area into `cellSize × cellSize` static chunks (`FoliageCell`), generate vertex/index buffers (`Uint32Array`) on workers/CPU, and merge all plants in each cell into one static mesh (`mesh` copies or built-in tapered blades).
- **Why This Fails for Fernwake Grass:**
  - Matching the original requires **~50,000–145,000 ultra-slim (`4–5 cm` wide) multi-segment curved blades** concentrated around the camera (`±28 m`).
  - With CPU-merged static cells across a `160×160 m` meadow, hitting the same visual density requires multiplying vertex/triangle count across dozens of cells, causing heavy main-thread/worker rebuilds and millions of triangles per frame.
  - Estella currently exposes no public ECS `InstancedMesh` component or torus-wrapped camera-ring grass primitive for custom shader instancing.

### GAP-3 (Missing Feature): Toon / Stylized Lighting Mode on `builtin:foliage` and `builtin:terrain`

- **Estella Current Design:** `builtin:foliage` (`foliageSupport.js` / `foliage.esshader`) and `builtin:terrain` shade surfaces via PBR `applyLightingSurface(...)`.
- **Gap:** Even if blade shape matches, PBR-lit grass and PBR-lit terrain respond smoothly to roughness/specular/GI rather than matching the **2-step painterly cel ramp** and shared **brushstroke noise (`tStrokes`)** used by `createPaintedGrass` and `createPaintedGround`. There is no `toon` / `stylized` lighting toggle or shade-color ramp in `builtin:foliage` or `builtin:terrain`.

### GAP-4 (Missing Feature): Per-Entity / Material ID Buffer + ID-Masked Ink & Selective Kuwahara Post-Processing

- **Original (`painted_valley.mjs:10–21, 1057–1107`):**
  - Renders an `INK` float ID into HDR color alpha (`CLOAK: 0.03`, `HELM: 0.06`, `WEAPON: 0.09`, `BOOTS: 0.12`, `LEGS: 0.15`, `ARMOR: 0.18`, `SKIN: 0.21`, `CREATURE: 0.16`, `PROP: 0.40`, `ENV: 1.0`).
  - `inkAt()` draws warm dark ink (`mix(c, min(c, 1.2) * vec3(0.20, 0.14, 0.15), ink * 0.92)`) **only** where `min(a, b) < 0.23` AND skips edges where a closer non-inked occluder (`>= 0.23`, e.g., tall grass blades) sits in front in the depth buffer.
  - `painted()` runs a 4-quadrant Kuwahara brush filter **only** where `alpha >= 0.6`, smoothing grass/ground/trees into brushstrokes while keeping characters and buildings razor-sharp.
- **Estella Current Design:** `depthOutline` and `edgeOutline` (`basic.js`, `customSky.js`) read only scene depth and G-buffer world normals. Without an entity/material/alpha ID channel, Estella cannot:
  - Ink characters and creatures cleanly **without** outlining every grass blade and terrain fold,
  - Suppress outlines cleanly behind occluding grass using per-pixel ID + depth comparison, or
  - Mask a Kuwahara painterly filter away from characters (`alpha < 0.6`).

### GAP-5 (Missing Feature): 2-Tone Hand-Mixed Cel Paint & Painter's Tone Curve in `builtin:toon` / Output Transform

- **Original (`createPaintedCharMaterial`, `createPaintedFrame`):**
  - Performs saturation boost (`mix(luma, base, 1.12)`), distinct `litTint` vs cool indigo `shadePaint` blending (not simple shadow darkening), sky-lum vs sun balance, and a **painter's tone curve** keeping RGB values `< 0.62` completely faithful before soft exponential highlight rolloff.
- **Estella Current Design:** `builtin:toon` multiplies `u_shadeColor` across unlit areas, and `outputTransform: "neutral"` applies neutral tone mapping rather than a customizable midtone-preserving painter's curve (requiring custom `displayLut` authoring to approximate).

### GAP-6 (Engine Bug): `Foliage` Multi-Level Async LOD Hard-Popping

- **Observed Behavior (`foliage.esshader:261–265`):** When `farLevels >= 2`, the vertex shader immediately culls near-cell geometry (`keep = -1`) once past `lodDistance * foliageDistanceScale`, before async worker far-level cells finish building/uploading—causing visible grass holes/popping during camera movement. (Currently mitigated in `main.esscene` only by forcing `farLevels: 1`, `lodDistance: 58`, `drawDistance: 78`.)

### GAP-7 (Asset Pipeline Bug): Mesh Importer Auto-LOD (`_lod2.esmesh`) Breaks UV Island Seams

- **Observed Behavior:** Estella's auto-generated `_lod2.esmesh` variants for multi-material/atlas props (such as `tree_spring_anime.esmesh`) collapsed vertices across UV boundaries, bleeding green leaf-canopy UVs onto brown tree trunks (appearing as bright cyan/green triangles on bark). Avoiding this required locking entities to full-detail base `.esmesh` files, directly inflating frame triangle counts.

---

## What _Is_ Possible in Estella Today (and Its Hard Limits)

Without engine changes, only partial approximations exist:

| Technique Available Today                                                                                                                                                                 | What It Improves                                                                                                          | Hard Limit vs. Original                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Use `Foliage` procedural blade mode (`mesh: ""`)** with narrow/tall blade params (`bladeWidth: ~0.05`, `bladeHeight: ~0.55`, `bladeLean: ~0.25`) instead of `ghibli_grass_clump.esmesh` | Produces taller, slimmer single blades instead of thick 3D clump meshes, with built-in vertex-color taper and wind curve. | **Still CPU-merged static `FoliageCell` chunks** (cannot reach 145k blades at 60 FPS without severe triangle/FPS drop) and **still PBR-lit** (`builtin:foliage`). |
| **Author Blender sphere-normal leaf-card trees** (`u_alphaCutoff`)                                                                                                                        | Replaces solid `tree_spring_anime` blobs with painterly cutout leaf sprays and soft shading normals.                      | Still lacks custom `treeOccKeep` camera-to-hero dither transparency and analytical `openAt()` dappled ground shadows unless Play `.esshader` 404 is fixed.        |
| **Inverted-hull outline child meshes on characters** (`cull: Front`, vertex-offset along normal)                                                                                          | Gives characters silhouette outlines without outlining terrain/grass.                                                     | Missing internal part-to-part seam lines (`INK.HELM` vs `INK.ARMOR` vs `INK.LEGS`) and cannot adapt thickness cleanly in screen space like `inkAt()`.             |
| **`displayLut` (1024×32) + `colorGrade`**                                                                                                                                                 | Approximates the painter's `0.62` tone curve and warm/cool color balance.                                                 | Cannot replicate selective Kuwahara smoothing or per-pixel depth/ID-aware ink.                                                                                    |

---

## Recommended Estella Engine Roadmap (Priority Order)

1. **P0 — Fix custom `.esshader` serving/bundling in Play & Web export (`AssetPlugin.js` / Play host):** Resolving the `404 Not Found` immediately unlocks custom `.esshader` cel materials, toon grass/terrain, leaf cards, and custom post-process effects (`registerEffect`).
2. **P0 — Add GPU-Instanced Camera-Ring Grass / Public `InstancedMesh` Component:** Support hardware instancing (`InstancedBufferGeometry` equivalent) with per-instance attributes (`vec4 aOff`) and camera-wrapped torus distribution so `50k–150k` slim grass blades render in 1–2 draw calls at 60 FPS.
3. **P1 — Add Stylized/Toon Shading Option to `builtin:foliage` & `builtin:terrain`:** Expose 2-tone cel terminator (`smoothstep` width + cool `u_shadeColor` paint mix) and multi-scale world brushwork modulation so terrain and grass unify seamlessly with `builtin:toon`.
4. **P1 — Add Material/Entity ID G-Buffer Channel + ID-Masked Outline & Kuwahara Effect:** Allow materials to emit an 8-bit `outlineId` / `paintMask`, then expose depth-aware selective ink outlining and optional selective Kuwahara filtering in `PostProcessVolume`.
5. **P2 — Fix `Foliage` LOD Transition Synchronization & Importer UV-Seam Preservation:** Keep near cell LODs alive until async far LODs are resident, and respect UV/material seams during `_lod2` mesh simplification.
