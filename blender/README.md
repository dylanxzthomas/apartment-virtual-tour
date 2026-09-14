# 2861 California · Unit 4

The editable full-apartment scene is `2861-california-unit-4-daylight.blend`. The website download at `public/models/2861-california-unit-4.blend` contains the same editable geometry, materials, textures and lighting. `prepare_blend_download.py` omits duplicate, unused reference-photo image blocks from that download; the photos remain in the website gallery and in the canonical local Blender file.

The supplied complete plan establishes the layout. The 12 photographs establish visible finishes, fixtures, opening details and probable room correspondences. Dimensions, ceiling height, exterior views and several photo assignments are estimated. The reported 1,140 sq ft has not been verified by measurement. See `FULL_UNIT_EVIDENCE.md` and the Blender text block “READ ME — reconstruction evidence”.

## Two viewing modes

**Rendered tour:** 11 fixed, eye-level, equirectangular Cycles viewpoints at 4096 × 2048, up to 192 samples, denoising, AgX display transform, JPEG quality 96. The website projects these finished images onto an inward-facing sphere with no additional tone mapping or lighting. Looking and zooming are continuous; changing positions uses room markers and a fade. This is not a continuously translated camera, a scan, or an animated fly-through. All viewpoints now use the daylight scene and a consistent −0.7 EV exposure. The deck and external surroundings remain inferred.

At a 60° horizontal field of view, only approximately one-sixth of the panorama’s horizontal pixels are in view; zooming cannot reveal additional detail.

**Free walk:** the same full Blender geometry exported as glTF, with separate Cycles diffuse-light atlases for living, rear bedrooms, front rooms and the exterior. HDR reflection captures approximate specular reflection in each zone. Glass uses simple transparency, and procedural surface shading is approximated. This mode supports continuous movement, room jumps, roofless orbit and top views. The closed deck door is a solid obstacle; the deck remains accessible through its room button.

## Why the old preview differs

`renders/lighting-check.png` is an earlier fixed-camera Cycles preview using the original procedural wood and brighter exposure. It is not a screenshot of the current website and does not represent the later material revision. Cycles computes illumination and view-dependent reflections for each rendered pixel. Free walk uses baked diffuse illumination and an approximate reflection environment. The rendered tour preserves the Cycles appearance at its fixed camera locations, subject to image resolution and compression.

## Reproduction

Run Blender with Metal GPU access on this Mac. The scripts report errors correctly with `--python-exit-code 1`.

For a geometry rebuild from the original kitchen generator, run `build_apartment.py` and then `polish_scene.py` before step 1. The current full scene can be opened directly without rebuilding.

1. `extend_full_unit.py` loads the refined kitchen, replaces its partial architectural shell, and builds every room, fixtures and reference cameras. It saves the editable full scene and composition checks.
2. `refine_daylight.py` saves the daylight scene and three preview images. `check_daylight.py` checks geometric sky visibility through all 10 windows.
3. `render_tour.py` creates the 11 display-ready panoramas, graph manifest and three HDR reflection captures. Optional arguments after `--` select viewpoint IDs.
4. `bake_full_unit.py` creates four independent UV atlases, bakes 512-sample direct and indirect diffuse lighting excluding albedo, and exports the full GLB. Fixed fractional UV gutters and six-pixel extended padding keep neighboring lighting patches separate.
5. `denoise_full_unit.py` denoises each raw atlas and downsamples to 2048 × 2048.
6. `validate_full_unit.py` checks floor support and camera clearance. `node scripts/validate-navigation.mjs` checks room-link reachability, floor positions, solid obstacles and continuous interior routes. `node scripts/validate-full-assets.mjs` checks final delivered geometry, textures and files.

The earlier kitchen-only files and scripts remain for reproducibility. They are not the source for the full-apartment tour.

## Daylight revision

Open `2861-california-unit-4-daylight.blend` for the latest editable source. `refine_daylight.py` preserves the interior reconstruction, retains adjacent siding, opens the rear outlook and adds illustrative distant foliage. It uses Blender 5.2's single-scattering Nishita sky, 50° sun elevation, 135° scene azimuth, 1.5° solar disc, 0.5 solar intensity and 1.5 world strength. These settings are an art-directed soft daylight scenario, not a geolocated sun-path calculation. Eight diffuse bounces provide indirect illumination. No artificial window fill lights remain. Clear window glass refracts viewed rays and uses 96% transparent shadow rays to approximate clear architectural transmission without caustic noise. Shower glass keeps its original refractive shader. Four diffuse atlases also carry exterior illumination to Free walk, avoiding dark facade materials lit only by interior reflection captures.

`render_tour.py` and `bake_full_unit.py` read the daylight source. Run `refine_daylight.py` after the full-unit reconstruction to reproduce it. All web panoramas, reflection captures and baked atlases must be regenerated together when lighting changes.

The daylight outputs live in `public/daylight-tour/` and `public/models/daylight/`. The prior `full` and `tour` outputs are retained locally as a comparison, not loaded by the final daylight website.

Earlier published kitchen-only web assets are retained under `blender/previous-web-assets/` and excluded from the current website bundle.

The web GLB is served as losslessly compressed `apartment.glb.gz`; the viewer decompresses it with the browser’s native DecompressionStream before loading. The geometry download can be unzipped normally. No geometry or texture quality is removed by compression.
