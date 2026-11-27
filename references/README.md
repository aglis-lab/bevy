# Aurora / Bevy Environment & Visual Quality Playbook

This folder is a **practical reference for both humans and AI agents** building 3D game environments in Bevy / Aurora. It covers **both** stylized painterly worlds (Ghibli / Fernwake) and realistic PBR worlds.

## Files in This Playbook

1. **[pipeline_workflow.md](pipeline_workflow.md)** — End-to-end production workflow connecting **Nerthus -> Jackdaw -> Aurora (Bevy + Jolt + Lobo)**, folder layout, and Human vs. AI division of labor.
2. **[environment_art_direction.md](environment_art_direction.md)** — Universal visual craft rules: lighting, color harmony, value hierarchy, grounding props, composition, camera framing, atmosphere, and life/motion.
3. **[style_recipes.md](style_recipes.md)** — Concrete Bevy/WGSL rendering recipes for **Style A (Ghibli / Painterly)** and **Style B (Realistic PBR + `bevy_solari`)**, including exact shader/material/post-FX parameters.
4. **[ai_world_generation_guide.md](ai_world_generation_guide.md)** — Rules, schemas, scatter formulas, Nerthus terrain pipeline, and a **12-point visual self-critique checklist** for AI agents generating and iterating on worlds.
5. **[rigging_and_animation.md](rigging_and_animation.md)** — Practical indie/AI-assisted character rigging & animation pipeline (**AccuRIG / Mixamo / Cascadeur -> Blender -> Bevy `AnimationGraph`**) plus runtime polish tips.

---

## The AI + Human Closed-Loop Workflow

When generating or improving a scene, follow this loop instead of guessing blindly:

1. **Generate Terrain & Masks (Nerthus / DAG):**
   - Author the macro terrain shape (valley, hills, ridges, flat playable zones, riverbeds) + hydraulic/thermal erosion.
   - Export **16-bit heightmap** + **flow, wear, deposit, and slope masks**.
2. **Place Hero Landmarks & Paths First:**
   - Place focal points (village, shrine, bridge, ruins) and connect them with curved paths/roads before scattering foliage.
3. **Apply Style Preset (`Ghibli` or `Realistic`):**
   - Lock lighting (sun angle, warm/cool color pair, fog, sky) **before** tuning prop textures.
4. **Scatter in Layers (Large -> Medium -> Small -> Groundcover):**
   - Trees -> boulders/cliffs -> bushes/props -> dense GPU-instanced grass + flowers + pebbles.
5. **Render -> Capture Screenshot -> Run the 12-Point Critique:**
   - Check every item in [ai_world_generation_guide.md](ai_world_generation_guide.md#12-point-ai-visual-self-critique-checklist), fix the highest-impact gaps first, and re-capture.

---

## The 6 Most Common "Why Does My 3D Game Look Amateur?" Mistakes

| Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| **Bare "green carpet" ground** | Flat terrain texture + sparse grass tufts | Dense GPU-instanced grass blades blending into ground color at base; line path edges with tufts & pebbles. |
| **Props look "pasted on" or floating** | No contact shadow/AO, rocks sitting *on top* of ground | Sink rocks/roots 15–35% into terrain; add contact AO + base grass/dirt skirts. |
| **Muddy, dull, or "plastic" look** | Neutral grey shadows + uniform lighting | Warm sun + **cool blue/indigo shadows**; strong value separation between ground, props, and characters. |
| **World feels tiny / like a flat mat** | No distance fog + steep top-down camera | Add sky-tinted distance/height fog; lower camera pitch so layered hills and sky are visible. |
| **Cluttered or robotic layout** | Evenly spaced props on a flat plane | Group props into natural clusters (rock + bush + grass + flower) with open breathing room between clusters. |
| **Style mismatch** | Mixing PBR ground, cel trees, and dark metallic props | Unify all environment shaders under the same lighting ramp, fog curve, and color palette. |
