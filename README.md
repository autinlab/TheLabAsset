# TheTunnelAsset

3D assets for The Tunnel: Gaussian splats and meshes of David Goodsell, Art, and the Scripps
building in the 1920s, made from single photos and from a short phone video.

```
splat/        3D Gaussian Splatting .ply files (SHARP, one photo each)
mesh/         textured / vertex-colored meshes (.glb, .usdz)
sprites/      cellPAINT 2D sprites (PNG) and sprites/index.json (see Sprites)
thumbs/       small JPG thumbnails, one per asset
assets.json   machine-readable index of every asset (query this from apps)
tools/        build_manifest.py (regenerates assets.json) + the scripts that made the assets
```

## Assets

| id | kind | subject | file | size |
|---|---|---|---|---|
| `goodsell_portrait_splat` | splat | David Goodsell | [splat/goodsell_portrait.ply](splat/goodsell_portrait.ply) | 66 MB |
| `scripps_1924_splat` | splat | Scripps 1924 | [splat/scripps_1924_photo.ply](splat/scripps_1924_photo.ply) (raw SHARP output) | 66 MB |
| `scripps_1924_no_sky_splat` | splat | Scripps 1924 | [splat/scripps_1924_no_sky.ply](splat/scripps_1924_no_sky.ply) (sky removed) | 35 MB |
| `scripps_1924_sky_backdrop_splat` | splat | Scripps 1924 | [splat/scripps_1924_sky_backdrop.ply](splat/scripps_1924_sky_backdrop.ply) (sky as far backdrop) | 48 MB |
| `scripps_1924_supersplat` | splat | Scripps 1924 | [splat/scripps_1924_supersplat.ply](splat/scripps_1924_supersplat.ply) (edited in SuperSplat, CC BY 4.0) | 32 MB |
| `art_photo_splat` | splat | Art | [splat/art_photo_IMG_9389.ply](splat/art_photo_IMG_9389.ply) | 66 MB |
| `goodsell_portrait_mesh` | mesh | David Goodsell | [mesh/goodsell_portrait_mesh.glb](mesh/goodsell_portrait_mesh.glb) | 8 MB |
| `goodsell_portrait_mesh_bright` | mesh | David Goodsell | [mesh/goodsell_portrait_mesh_bright.glb](mesh/goodsell_portrait_mesh_bright.glb) | 8 MB |
| `goodsell_portrait_splatlook` | mesh | David Goodsell | [mesh/goodsell_portrait_splatlook.glb](mesh/goodsell_portrait_splatlook.glb) | 56 MB |
| `scripps_1924_splatlook` | mesh | Scripps 1924 | [mesh/scripps_1924_splatlook.glb](mesh/scripps_1924_splatlook.glb) (1.1M tris) | 50 MB |
| `scripps_1924_splatlook_quest` | mesh | Scripps 1924 | [mesh/scripps_1924_splatlook_quest.glb](mesh/scripps_1924_splatlook_quest.glb) (290k tris, for Quest) | 13 MB |
| `art_photo_mesh` | mesh | Art | [mesh/art_photo_IMG_9389_mesh.glb](mesh/art_photo_IMG_9389_mesh.glb) | 23 MB |
| `art_video_fullbody_glb` | mesh | Art | [mesh/art_video_IMG_9390_fullbody.glb](mesh/art_video_IMG_9390_fullbody.glb) | 11 MB |
| `art_video_fullbody_usdz` | mesh | Art | [mesh/art_video_IMG_9390_fullbody.usdz](mesh/art_video_IMG_9390_fullbody.usdz) | 22 MB |

<p>
<img src="thumbs/scripps_1924_splatlook.jpg" width="960" alt="Scripps 1924 splat-look meshes">
</p>
<p>
<img src="thumbs/art_video_IMG_9390_fullbody.jpg" width="480" alt="Art full-body mesh, four views">
<img src="thumbs/art_photo_IMG_9389_mesh.jpg" width="480" alt="Art photo mesh, three views">
</p>

## Sprites

`sprites/cellpaint/` holds cellPAINT 2D's flat molecule sprites (about 400 PNGs, 123 MB), with `sprites/index.json`:
URL, size, scale (pixels per Å), kind, PDB id and the recipes and ingredient names that use each. See
[sprites/README.md](sprites/README.md) (scale convention, loading, citations). Licence: to be decided. Regenerate the
index with `python tools/build_sprites_index.py`.

## How they were made

- **Splats**: [SHARP](https://github.com/apple/ml-sharp) (Apple), one photo in, one 3DGS `.ply` out
  (about 1.18M Gaussians, 2 layers of 768x768). SHARP reconstructs only what the camera saw, so
  the back of every scene is empty. Look at them from roughly the front.
- **Scripps 1924**: SHARP on a 1920s photograph of the Scripps building. Cleaned versions
  remove the sky and floaters, or push the sky out to a distant backdrop. `scripps_1924_supersplat`
  is the version edited and published on SuperSplat.
- **Splat-look meshes** (`*_splatlook*`): one small textured quad per Gaussian, so a plain mesh
  renderer (Quest, three.js, Unity without a splat plugin) gets a splat-like look.
- **2.5D meshes** (`goodsell_portrait_mesh*`, `art_photo_mesh`): the front layer of a SHARP splat
  triangulated as a grid, with triangles across depth jumps removed. A relief, not a closed object.
- **Full-body mesh** (`art_video_fullbody_*`): Apple Object Capture (RealityKit
  `PhotogrammetrySession`, medium detail) on 134 sharp frames from a 17 s orbit video.
  It is a full 360 degree model, but the subject moved during the capture, so there is a faint ghost second head
  and an extra sheet of surface on one side. Its scale is arbitrary (about 1.35 m tall), so rescale it to his real
  height before use. It is a candidate for auto-rigging (Mixamo / AccuRIG, then Unity Humanoid).

## Coordinate conventions

| kind | convention | up | notes |
|---|---|---|---|
| splat `.ply` | OpenCV: x right, **y down**, z forward | -Y | camera at origin looking +Z; rotate 180 deg about X for y-up viewers (SuperSplat, Unity) |
| mesh `.glb` / `.usdz` | glTF: x right, **y up** | +Y | opens upright in Blender, Unity, three.js, Quick Look |

Splat `.ply` files use the standard 3DGS layout (`x y z f_dc_0..2 opacity scale_0..2 rot_0..3`,
degree-0 SH, sRGB colors), so they load in SuperSplat, gsplat.js, Spark, three.js splat loaders, and
[UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting) (import step needed in Unity).

## Using `assets.json` from an app

Every asset has a direct, streamable URL:

```
https://raw.githubusercontent.com/autinlab/TheTunnelAsset/main/<path>
```

`assets.json` lists every asset with its `id`, `kind` (`splat` or `mesh`), `subject`, `tags`, `format`,
`mime`, `url`, `bytes`, `sha256` (for caching), `thumbnail`, `coordinates`, and per-format stats
(`gaussians` for splats; `vertices`, `faces` for GLB). Files under 20 MB also have a `cdn_url` on
jsDelivr, which is faster and has CORS caching.

```js
const BASE = "https://raw.githubusercontent.com/autinlab/TheTunnelAsset/main/";
const index = await (await fetch(BASE + "assets.json")).json();

// all splats of the Scripps 1924 building
const splats = index.assets.filter(a => a.kind === "splat" && a.subject === "scripps-1924");

// one asset by id, streamed
const art = index.assets.find(a => a.id === "art_video_fullbody_glb");
const res = await fetch(art.url);            // raw.githubusercontent.com sends CORS: *
const reader = res.body.getReader();         // stream it, or just: await res.arrayBuffer()
```

```csharp
// Unity
var req = UnityWebRequest.Get("https://raw.githubusercontent.com/autinlab/TheTunnelAsset/main/assets.json");
yield return req.SendWebRequest();
var json = req.downloadHandler.text;  // parse with JsonUtility / Newtonsoft, then GET asset.url
```

```bash
# command line: list the ids and URLs of all meshes
curl -s https://raw.githubusercontent.com/autinlab/TheTunnelAsset/main/assets.json \
  | jq -r '.assets[] | select(.kind=="mesh") | "\(.id)\t\(.url)"'
```

Things to know about `raw.githubusercontent.com`:
- It sends `Access-Control-Allow-Origin: *`, so browsers can fetch directly.
- It supports HTTP range requests, but it doesn't guarantee bandwidth and is rate-limited for heavy traffic. For
  production, mirror the files to a CDN or object storage and keep the same `path`s.
- GitHub rejects files over 100 MB. Keep new splats under that, or compress them first (`.spz` / `.sog`).

## Credits and licenses

- `splat/scripps_1924_supersplat.ply`: "Scripps 1924" by LMGL
  ([superspl.at/scene/2e27822f](https://superspl.at/scene/2e27822f)), licensed
  [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). You must credit the author when you reuse it.
  Assets with a license have a `license` field in `assets.json`.
- Splats were made with [SHARP](https://github.com/apple/ml-sharp). See its license for model terms.

## Making new assets (the exact scripts used for the assets above)

Use these scripts as they are. They hold the settings that produced the current assets.
Python scripts need `numpy plyfile trimesh` (+ `scipy pillow` for frames); the
[ml-sharp](https://github.com/apple/ml-sharp) conda env has most of them.

**Photo -> splat -> mesh**

```bash
# 1. splat (Apple SHARP, runs on mps / cuda / cpu; checkpoint downloads on first run)
sharp predict -i photos/ -o out/ --device mps            # -> out/<name>.ply (OpenCV coords)
# 2. 2.5D relief mesh from the front layer, vertex colors, y-up   -> out/<id>_mesh.ply + .glb
python tools/splat_to_mesh.py out/<name>.ply out/<id>_mesh
# 3. splat-look mesh: one quad per Gaussian (optionally decimated for Quest)
python tools/splat2glb.py out/<name>.ply mesh/<id>_splatlook.glb 1.6
python tools/splat2glb.py out/<name>.ply mesh/<id>_splatlook_quest.glb 1.6 100000 "credit"
```

| script | what it does |
|---|---|
| `splat_to_mesh.py` | triangulates layer 0 of the 2x768x768 SHARP grid; drops triangles across depth jumps (z ratio >= 1.04) or with opacity <= 0.1; flips to y-up |
| `splat2glb.py` | args: `in.ply out.glb [sigma] [target_splats] [copyright]`; quads span +-sigma along the 2 largest Gaussian axes; drops opacity < 0.2; unlit linear vertex colors |
| `clean_splat_sky.py` | **example only**: the sky/floater cleanup used for Scripps 1924 (needs a sky mask; thresholds tuned for that photo) |

**Orbit video -> full 360 degree model** (macOS on Apple silicon, Apple Object Capture)

```bash
python tools/select_frames.py in.mov work/frames 10 0.2      # 10 fps, drop blurriest 20%
swift tools/object_capture.swift work/frames work/model.usdz medium   # preview|reduced|medium|full|raw
swift tools/usdz_to_obj.swift work/model.usdz work/obj/model.obj      # ModelIO, with textures
python tools/obj_to_glb.py work/obj/model.obj mesh/<id>_fullbody.glb 1.80   # real height in m, feet at y=0
cp work/model.usdz mesh/<id>_fullbody.usdz
```

`object_capture.swift` uses sequential sample ordering (video frames), high feature sensitivity
and object masking (keeps the subject, drops the room). On Windows or Linux, run the same frames
through RealityScan, Meshroom or COLMAP instead.

Capture tips. Most bad results come from the subject moving.
- The subject stands perfectly still in an A-pose (arms 30-45 degrees out).
- Film two slow loops of 20-40 s: one at chest height, one higher, looking down.
- Use even light with no backlight. Keep the whole body in frame the whole time.
- Shiny, black and very thin parts (glasses, loose hair) reconstruct poorly.
- For rigging: clean up in Blender, decimate to about 50k tris, auto-rig in Mixamo or AccuRIG,
  then use Unity Humanoid.

## Adding an asset

1. Put the file in `splat/` or `mesh/` and a JPG thumbnail in `thumbs/`.
2. Add an entry to `ASSETS` in `tools/build_manifest.py`.
3. Run `python tools/build_manifest.py` (needs `numpy plyfile trimesh`), then commit `assets.json`
   with the files.
