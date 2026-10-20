# Final v17 first-half CPU audit

Result: **PASS**. No runtime, finite-value, line-pair, deterministic-build, draw-key or score-boundary failures were found.

## Final geometry counts

| Collection | Layers | Line vertices | Triangles |
|---|---:|---:|---:|
| FIRST_HALF | 32 | 193,710 | 0 |
| ORGANIC | 10 | 52,296 | 0 |
| ORBITAL | 7 | 49,072 | 0 |

- Director: 2,264 sampled times and 6,850 draw calls; all collection/layer keys exist and all matrices/gains/reveals are finite.
- Added exit_sorter, exit_canopy, exit_mycelium and orbital_sled are all constructed and reached by the director.
- All new collection meshes are nonempty, deterministic, GL_LINES-only and contain valid endpoint pairs.
- Fourteen cue intervals do not overlap; all end at or before 73.87 s.
- Direct no-GPU calls confirm no first-half draws at or after 73.87 s, and no new draws during the original principal-eye scene 31.83–38.19 s.

## Final bag and payload layout

The final organic assembly has **three mushrooms in one left-hand tall open bag**. The two right mushrooms and secondary sack have been removed. The bag stands on organic_mount; exit_sorter, exit_canopy and exit_mycelium attach the cargo to the moving exit bay. The orbital payload now uses an explicit orbital_sled and a centred embedded gpu_core.

This supersedes the earlier 28-layer / five-mushroom audit.

## Scope

CPU construction and stub choreography only. No GL context, GPU, rendering or Git operation was used. Source SHA-256 snapshots and per-layer bounds/counts are saved in the JSON. The stub host checks finite transforms and correct keys; actual camera visibility, word clearance and style remain the responsibility of the root previews and encoded-frame QA. No production source was changed.
