# Character Rigging & Animation Guide (Indie + AI-Assisted -> Bevy / Aurora)

A practical guide for solo/indie devs and AI workflows to get clean, game-ready character rigs and animations into Bevy without fighting broken "one-click text-to-animation" outputs.

---

## 1. Reality Check: What Works vs. What Sucks

| Approach | Verdict | Why |
| :--- | :--- | :--- |
| **Pure Text-to-Animation** | **Avoid for final game** | Floaty weight, foot sliding, broken loops, unnatural combat timing. |
| **Auto-Rigging Complex Outfits / Monsters** | **Needs Blender cleanup** | Long cloaks, layered armor, belts, and tails almost always pinch/clip without quick weight-paint tweaks. |
| **Humanoid / Creature Auto-Rigging (`Mesh2Motion` / `AccuRIG` / `Mixamo`)** | **Great (100% Free)** | **Mesh2Motion** is free & open-source (humans + quadrupeds + monsters, exports `.glb`/`.fbx`); **AccuRIG** & **Mixamo** are free for humanoids. |
| **Physics-Assisted Animation (`Cascadeur`)** | **Paid only for FBX/GLB** | Great AutoPhysics, **but the free tier only saves `.casc`** (FBX/glTF export requires a paid plan). |
| **Mocap Libraries + Blender / Video-to-Mocap** | **Best 100% Free path** | Mixamo / Mesh2Motion (CC0) for base clips + **Rokoko Video** (free phone mocap -> FBX) + **Blender (Rigify / IK)** for custom edits & direct `.glb` export. |

---

## 2. Recommended Tool Stack (100% Free / Open-Source Export to `.glb` / `.fbx`)

1. **Rigging + Base Animations (100% Free & Open Source):**
   - **[Mesh2Motion](https://mesh2motion.org) (Free / Open Source):** Auto-rigs **humanoids, quadrupeds, and creatures**, applies CC0 game animations, and exports packed `.glb` / `.gltf` / `.fbx` directly for Bevy.
   - **AccuRIG (Free, Reallusion):** Best free auto-rigger for custom humanoids (very clean fingers & shoulders, free FBX/glTF export).
   - **Mixamo (Free, Adobe):** Thousands of free humanoid mocap clips (`idle`, `walk`, `run`, `jump`, `attack`) with free FBX export.
2. **Custom Animation (Free FBX/GLB Export):**
   - **Blender (Free / Open Source):** Built-in **Rigify** (IK/FK snapping) + NLA tracks + direct `.glb` export. For quick custom motions without animating from scratch, record yourself on your phone via **Rokoko Video** (free FBX export) and clean up/tweak the keyframes in Blender.
   - **Cascadeur (Optional Paid Upgrade):** Only worth considering if you later buy Indie/Pro for heavy acrobatic combat animations (since free tier locks FBX/glTF export to `.casc`).
3. **Non-Humanoid / Arbitrary Meshes:**
   - **Mesh2Motion** (quadrupeds/monsters) or **UniRig** (open-source ML) + quick weight-paint cleanup in **Blender**.

---

## 3. Step-by-Step Pipeline -> Bevy / Aurora

### Step 1: Prepare the Character Mesh (Before Rigging)
- **Pose:** Clean **A-pose** (preferred for better shoulder deformation) or **T-pose**, symmetrical on X.
- **Scale & Orientation:** `1 unit = 1 meter`, `+Y` up, facing `-Z` (or consistent facing), all transforms applied (`Ctrl+A` in Blender).
- **Joint Loops:** Ensure at least 2–3 edge loops at elbows, knees, wrists, and waist so limbs bend smoothly instead of collapsing.
- **Keep Props Separate:** Export weapons, shields, hats, and lanterns as separate `.glb` meshes and attach them to bone sockets in Bevy rather than skinning them into the body mesh.

### Step 2: Rig the Character
- Import the clean mesh into **AccuRIG** (or **Mixamo**).
- Verify shoulder, hip, and finger joint positions carefully before generating skin weights.
- Test with an extreme pose (arms raised overhead, deep squat) — if a cloak or armor plate clips, do a 5-minute weight-paint fix in Blender.

### Step 3: Author / Retarget Animations
- **Locomotion set (minimum viable game set):**
  - `idle`, `walk`, `run`, `jump_start`, `fall_loop`, `land`
- **Action set (Cascadeur):**
  - Block 3–4 key poses (anticipation -> contact/strike -> follow-through -> recovery).
  - Run **AutoPhysics** in Cascadeur for natural center-of-mass and secondary motion.
- **In-Place vs. Root Motion:**
  - For most action/adventure games in Bevy + Jolt, export locomotion **in-place** (Jolt's character controller drives movement speed) and match animation playback speed to actual ground velocity to eliminate foot sliding.

### Step 4: Export `.glb` for Bevy
- Export as **glTF Binary (`.glb`)** with:
  - Applied transforms (`scale = 1.0`)
  - All clips named cleanly (`idle`, `run`, `attack_01`, etc.)
  - Baked keyframes (`Always Sample Animations` enabled in Blender)
  - Separate material slots if using Fernwake/Ghibli **HDR Alpha-ID** ink outlines (`CLOAK`, `ARMOR`, `SKIN`, `WEAPON`) so internal part seams get crisp ink lines.

---

## 4. Bevy Runtime Polish (Makes Simple Animations Feel 2× Better)

Even basic Mixamo/Cascadeur clips look dramatically better with 3 lightweight runtime tricks in Bevy:

1. **Smooth Cross-Fading (`AnimationGraph` + `AnimationTransitions`):**
   - Blend transitions over `0.10–0.20 s` (`transitions.play(..., Duration::from_millis(150))`) so characters never snap between idle, run, and jump.
2. **Velocity-Matched Playback Speed:**
   - Scale `ActiveAnimation::set_speed(current_speed / clip_base_speed)` so feet stay planted on the ground with zero sliding.
3. **Procedural Secondary Motion (No Hand-Animating Cloth):**
   - Attach weapons/props to hand bone entities.
   - Add subtle procedural lean when turning, head look-at toward target/camera, and simple spring-damped rotation on cloak/hair/tail bones (or vertex-shader wind sway on cloaks).

---

## 5. Character Animation Quality Checklist

- [ ] **Zero Foot Sliding:** Ground speed matches walk/run stride speed.
- [ ] **Clean Loops:** First and last frames of `idle`, `walk`, `run`, and `fall_loop` match smoothly with no hitch.
- [ ] **Readable Silhouettes:** Poses read clearly from the gameplay camera angle (especially attacks and jumps).
- [ ] **No Severe Clipping:** Shoulders, hips, and cloaks deform cleanly during extreme poses.
- [ ] **Snappy Game Feel:** Attacks have clear anticipation (`3–6` frames), crisp impact (`1–2` frames), and smooth blend back to idle/run.
