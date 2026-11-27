# AI-Assisted Game Production Budget & Timeline (Design -> MVP -> Ship)

A realistic budget and day-by-day schedule for building a 3D game on the **Aurora stack (Bevy + Jolt + Lobo + Nerthus + Jackdaw)** with AI-assisted coding (`5k–10k LOC/day`) and AI-assisted 3D/animation tools (**Tripo3D**, **Cascadeur**).

---

## 1. Why the Total Cost Is Surprisingly Low

Most of the expensive parts of game development are **100% Free & Open Source** in this stack:

| Layer | Tool | Cost |
| :--- | :--- | :--- |
| **Game Engine & Ray Tracing** | Bevy + `bevy_solari` | **$0** (MIT/Apache-2.0) |
| **Physics** | Jolt Physics | **$0** (MIT) |
| **UI Framework** | Lobo (`vello_cpu` / `wgpu`) | **$0** (Your own) |
| **Terrain & Erosion** | Nerthus (with MCP) | **$0** (Open Source) |
| **Visual Level Editor** | Jackdaw | **$0** (Open Source) |
| **3D Cleanup / Rigging / Base Anim** | Blender + Mesh2Motion + AccuRIG + Mixamo | **$0** |
| **Paid Accelerator #1 (3D Models)** | **Tripo3D** | **$20/mo** (Pro: 3,000 credits) or **$90/mo** (Max: 25,000 credits) |
| **Paid Accelerator #2 (Custom Anim)** | **Cascadeur Indie** | **$19/mo** (or **$96/yr** with perpetual fallback license) |
| **AI Coding Assistant** | **Claude Pro** (+ overage buffer) | **$20/mo** regular (up to **$40/mo** if exceeding usage limits) |
| **Audio / SFX / Storefront (Optional)** | CC0 / Suno / ElevenLabs + Steam Direct | **$0–$150** ($100 one-time for Steam) |

> **Key insight:** You don't even need Tripo3D or Cascadeur active every month — only subscribe during the 1–2 months you are actively generating 3D assets or polishing custom animations.

---

## 2. Realistic Tripo3D Credit Math (Converting Game Needs -> Credits)

Don't budget using the marketing "15 credits per model" number. Production-ready game assets need **generation + retopology + UV/texture + rigging + ~2–3× retries** to get good silhouettes:

| Asset Type | Operations Needed | Credits / Attempt | With ~2.5× Retries |
| :--- | :--- | :--- | :--- |
| **Hero / Playable Character** | HD Gen (15) + Smart Mesh/Retopo (40) + HD Texture (25) + Auto-Rig (25) | ~105 credits | **~260 credits** |
| **NPC / Creature / Enemy** | HD Gen (15) + Retopo (20) + Texture (20) + Rig (25) | ~80 credits | **~200 credits** |
| **Building / Landmark** | HD Gen (15) + Retopo (20) + HD Texture (25) | ~60 credits | **~150 credits** |
| **Environment Prop (Rock, Crate, Tree, Lamp, Weapon)** | HD Gen (15) + Fast Texture (10) + Normal Retopo (10) | ~35 credits | **~85 credits** |

### Example: Medium Indie Action-Adventure Asset Budget (Fernwake Scale)
- 2 Hero characters (`2 × 260`) = **520 credits**
- 10 NPCs & enemies (`10 × 200`) = **2,000 credits**
- 8 Buildings / landmarks (`8 × 150`) = **1,200 credits**
- 35 Props / weapons / rocks / trees (`35 × 85`) = **2,975 credits**
- **Total:** **~6,700 credits** (~2–3 months of **Tripo Pro** at `$20/mo` = **$40–$60**, or 1 month of **Tripo Max** at **$90** with huge headroom!).

---

## 3. Reality Check on "5k–10k LOC/Day" with AI

AI can easily output `5,000–10,000 LOC/day`, **but code generation is rarely the bottleneck** in a 3D game:
- **Fast (AI crushes this):** Engine scaffolding, ECS systems, WGSL shaders, Lobo UI widgets, Jolt bindings, terrain loaders, inventory/quest/dialogue systems.
- **Slower (Human-in-the-loop bottleneck):** Picking/re-rolling 3D models in Tripo3D, fixing shoulder/cloak weights in Blender, tuning combat feel & camera, laying out levels in Jackdaw, playtesting & bug-hunting.

Because of this, realistic timelines for a **solo dev + AI** scale by **content & polish complexity**, not just LOC:

| Game Scope | Example | Estimated Timeline | Estimated Total Budget |
| :--- | :--- | :--- | :--- |
| **Tier 1: Small / Vertical Slice** | 1–2 zones, 1–2 hrs gameplay, ~20 assets | **30–45 days** (~1.5 mo) | **$80 – $200** |
| **Tier 2: Medium Indie (Recommended Target)** | 3–5 zones (Fernwake-style), 6–10 hrs gameplay, ~55 assets | **75–105 days** (~3 mo) | **$220 – $480** |
| **Tier 3: Large Indie RPG** | 8–12 zones, 20+ hrs gameplay, 150+ assets | **160–240 days** (~6–8 mo) | **$550 – $1,200** |

---

## 4. Detailed Phase-by-Phase Roadmap (Tier 2: ~90 Days / 3 Months)

### Phase 1: Design & Architecture (**Days 1–7** — 1 week)
- **Deliverables:** Game Design Doc (core loop, controls, 3–5 zones, enemy/prop list), Aurora workspace (`Bevy + Jolt + Lobo`), `RenderStyle` choice (`Ghibli` or `Realistic`).
- **Paid Tools Active:** AI Coding sub only (`$0` on Tripo/Cascadeur yet).

### Phase 2: Core Engine & Vertical Slice MVP (**Days 8–32** — 3.5 weeks)
- **Days 8–16 (Aurora Core):** Jolt physics + character controller, Nerthus heightmap/mask loader, 145k GPU grass ring, unified cel/PBR shader + Ink/Kuwahara post-FX, Lobo HUD overlay.
- **Days 17–25 (Core Gameplay):** Player locomotion, combat/interaction, camera, 1 test zone built in Nerthus + Jackdaw, 1 hero + 2 enemy characters generated in Tripo3D + rigged in AccuRIG/Mesh2Motion.
- **Days 26–32 (MVP Playtest):** Playable 15-minute vertical slice from start to finish. Fix feel, frame rate (lock 60 FPS), and visual polish using the 12-point checklist.
- **Paid Tools Active:** AI Coding sub + **Tripo3D Pro Month 1** (`$20`).

### Phase 3: Full Content Production — Alpha (**Days 33–67** — 5 weeks)
- **Days 33–50 (Asset & World Sprint):** Generate remaining NPCs, enemies, buildings, and props in Tripo3D; build zones 2–5 in Nerthus + Jackdaw.
- **Days 51–60 (Animation Pass):** Retarget locomotion (Mixamo/Mesh2Motion) + author custom combat/boss/emote animations in **Cascadeur Indie** (export `.glb`/`.fbx`).
- **Days 61–67 (Systems & Narrative):** Quests, dialogue UI in Lobo, audio/SFX/music, save/load, menus, settings.
- **Paid Tools Active:** AI Coding sub + **Tripo3D Pro Month 2–3** (`$40`) + **Cascadeur Indie** (`$19/mo` for 1–2 mo, or `$96` annual perpetual).

### Phase 4: Polish, Optimization & Ship (**Days 68–90** — 3 weeks)
- **Days 68–78 (Visual Polish):** Run the 12-point visual critique on every zone (grass density, prop grounding, fog, lighting, shadows, particle effects).
- **Days 79–85 (Bugfix & Performance):** Profile CPU/GPU, fix Jolt edge cases, test on mid-range GPUs, balance difficulty & pacing.
- **Days 86–90 (Release Prep):** Trailer, screenshots, Steam/itch.io page, final builds (Windows/macOS/Linux).
- **Paid Tools Active:** AI Coding sub (cancel Tripo3D & Cascadeur monthly if done) + Steam Direct fee (`$100` one-time, optional).

---

## 5. Total Budget Summary (Tier 2: 90-Day Complete Game)

| Budget Level | Claude (3 mo) | Tripo3D | Cascadeur | Audio / Misc | Steam Fee | **Total** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bootstrap (Leanest)** | $60 ($20/mo) | $40 (2 mo Pro) | $0 *(use Mesh2Motion + Blender)* | $0 *(CC0)* | $0 *(itch.io)* | **~$100** |
| **Sweet-Spot Indie** | $60–$120 ($20–$40/mo) | $60 (3 mo Pro) | $38 *(2 mo Indie)* or $96 *(1 yr perpetual)* | $40 | $100 | **~$300 – $415** |
| **Heavy Sprint** | $120 ($40/mo w/ overage) | $90 (1 mo Max) + $20 | $96 *(1 yr perpetual)* | $100 | $100 | **~$526** |

### Smart Cost-Saving Tips
1. **Batch your Tripo3D generation into 1–2 focused months** instead of subscribing all year (unused monthly credits don't roll over).
2. **Batch custom combat animations into 1–2 months of Cascadeur Indie ($19/mo)** — or buy the **$96/yr Indie plan** once so you keep a **perpetual fallback license** forever even after canceling.
3. **Reuse & kitbash props:** 5 good rocks rotated/scaled/sunk differently + 3 good trees cover 80% of an entire open-world valley.
