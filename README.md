# Apartment Virtual Tour

**A 360° apartment walkthrough built with Blender, Three.js, and GPT Astra-6.**

Starting with 12 interior photos and a floor plan, this project recreates a four-bedroom apartment as a room-by-room virtual tour. Explore 11 viewpoints, look around in every direction, and compare the result with the original photos.

Built by [Dylan Szeto](https://x.com/dylan_szeto) with GPT-Astra 6. Featured apartment: **2861 California Street, Unit 4**.

**[Open the live tour](https://2861-california-unit-4.vercel.app/)** · **[Download the Blender model](https://2861-california-unit-4.vercel.app/models/2861-california-unit-4.blend)**

![Blender daylight rendering of the reconstructed kitchen](public/preview.png)

## Explore the apartment

- Drag to look around, scroll to zoom, and click a marker to move between viewpoints.
- Choose any room from the map. On mobile, tap **Rooms**.
- Open **Original photos** to compare the recreation with its inputs.
- Find the code and editable apartment under **About**.

## Run the website locally

Use Node.js 22.13 or newer in the Node 22 series.

```sh
git clone https://github.com/dylanxzthomas/apartment-virtual-tour.git
cd apartment-virtual-tour
npm ci
npm run dev
```

Open the local URL printed in the terminal. The tour images are included, so Blender, API keys, and a database are not needed to run the website.

To build and preview the production website:

```sh
npm run build
npm run preview
```

To check the included assets and navigation:

```sh
npm run validate
```

## Open and render in Blender

You can work on the apartment directly without running the website or rebuilding the scene.

1. Install [Blender](https://www.blender.org/download/). The included scene was saved with **Blender 5.2.1**; use that version or a compatible newer release.
2. Download the model using the link above, or open `blender/2861-california-unit-4-daylight.blend` from this repository with **File → Open**. Geometry, materials, lighting, and the scene's used textures are included.
3. Explore in the 3D Viewport. Use **View → Navigation → Walk Navigation** for a first-person view; move with **W/A/S/D** and look with the mouse. Left-click confirms the view; Esc cancels. See Blender's [walk navigation guide](https://docs.blender.org/manual/en/latest/editors/3dview/navigate/walk_fly.html).
4. For a rendered image, keep **Cycles** selected in Render Properties. Choose **CPU** as the render device, or configure your GPU in **Preferences → System → Cycles Render Devices**, then select **GPU Compute** in Render Properties. Apple Silicon uses Metal; other supported devices use their corresponding backend. See [Blender's GPU setup guide](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html).
5. Choose **Render → Render Image** to render the active camera. Save the result from the render window's **Image → Save As** menu. Save edits to a new `.blend` file with **File → Save As**.

### Regenerate the web tour

The included `blender/render_tour.py` script opens the daylight scene and renders the website's panoramas. It is configured for **Metal on macOS**. From the repository root, render just the kitchen first:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --python-exit-code 1 \
  --python blender/render_tour.py -- kitchen
```

The result replaces `public/daylight-tour/kitchen.jpg`. Omit `-- kitchen` to render all 11 viewpoints. This also updates the tour manifest and selected reflection captures. Rendering takes substantially longer than starting the website.

On Windows or Linux, use your Blender executable and change the script's Metal device setup to your supported GPU backend or CPU before running it. If you edit a different `.blend` file, update the script's input path or save your changes to the daylight source it loads. After rendering, run `npm run build` to include the new images in the website build.

## How it works

Blender Cycles renders the daylight, shadows, materials, and reflections into 360° images. Three.js displays those images in an interactive viewer; React handles room navigation, the photo gallery, and the interface. Moving to another room loads its panorama and fades it into view.

The public site uses the virtual tour only. An earlier continuous 3D viewer and its lighting assets remain in the repository for people interested in exploring that approach.

## Project structure

- `app/`: interface and styles
- `lib/tour-scene.ts`: the 360° viewer and room markers
- `public/daylight-tour/`: rendered panoramas and viewpoint manifest
- `public/models/`: downloadable Blender model and earlier web-model assets
- `public/references/`: original photos and floor plans
- `blender/`: editable source and modeling/rendering scripts
- `scripts/`: asset and navigation checks

See the [Blender workflow](blender/README.md) for the modeling and lighting pipeline.
