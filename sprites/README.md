# sprites/

2D sprites of [cellPAINT 2](https://ccsb.scripps.edu/cellpaint): flat, illustrated molecules (proteins, membrane
segments, fibers, lipids, nucleic acids, virus parts) drawn in the style of David Goodsell. meso\* loads them by URL to
draw cellPAINT recipes and scenes. This folder is a copy of cellPAINT's own sprite images, with an index.

```
sprites/
  index.json        machine-readable index (schema thelab-sprites/1): query this from apps
  cellpaint/        the PNGs, original names kept (cellPAINT's Assets/Resources/Recipie/, in the same sub-folders)
    textures/       membrane segments and lipid look, a few protein textures, the ribosome and actin frames
```

**LICENSE: TO BE DECIDED.** No licence applies yet. cellPAINT 2D's own repository is GPL-3.0; the licence of these
images in this repository is pending a decision by Ludovic Autin. There is deliberately no LICENSE file here. Until
then, do not redistribute the sprites outside this lab's projects.

## How they were made

The sprites are cellPAINT 2D's (Autin lab, Scripps Research; source
[corredD/cellPAINT2D](https://github.com/corredD/cellPAINT2D)): each is a transparent PNG of a molecule or part,
illustrated from its PDB structure(s) with the Goodsell watercolor-and-outline look. They are copied unmodified by
`tools/build_sprites_index.py import <cellPAINT2D checkout>` (`Assets/Resources/Recipie/`, plus the membrane and a few
protein textures of `Assets/cellPAINT/Textures/NewAssets/`). The same command reads the recipes
(`Assets/Resources/Recipes/*.json`) to record which ingredient of which recipe uses each image. Not copied: UI images,
cursors, splash screens, third-party packs, and 27 portrait photographs of people (listed in `index.json` `excluded`).
Some files are used by no recipe (older variants, `*_w` white-background versions): their `recipes` list is empty.

Regenerate the index (no checkout needed) with `python tools/build_sprites_index.py`. It never edits `assets.json`.

## Scale convention

From cellPAINT's C# (cellPAINT2D `Assets/cellPAINT/Scripts/PrefabProperties.cs`, `SetupFromNode`, "1 angstrom in the
image is scale2d pixel"):

- A recipe gives each ingredient's `sprite.scale2d`: **image pixels per Å**. The scale belongs to the ingredient in a
  recipe, not to the file (blood-plasma recipes use 2.85, HIV 3.5, others 2 to 4): the index gives `scale2d` (the most
  common value for the file, `null` if no recipe uses it), `scale2d_values` (all) and, per use, `usage[]`.
- A sprite is `width / scale2d` Å wide: `Albumin_C.png` at 2.85 px/Å.
- `offsety` (Å): a membrane protein's image middle sits that far up the membrane normal (negative: down), so the copy's
  place is on the membrane. `lengthy` (Å): a fiber's body length. Both are in Å, not pixels.
- Unity side, for reference: every sprite has `spritePixelsToUnits` 100 and a pivot of (0.5, 0.5) (all the `.meta`
  files), 1 world unit is 1 nm = 10 Å (`Manager.unit_scale` 1), so a sprite is made `100 / (10 x scale2d)` times its
  natural size (`PrefabProperties.cs` `local_scale`, about line 874). `index.json` `scale` repeats this.
- Resolving: `lookup.by_image` maps a recipe's `sprite.image` (a path under `cellpaint/`, e.g. `Albumin_C.png`) to a
  sprite id; `lookup.by_ingredient` maps a cellPAINT ingredient name to its sprite ids. cellPAINT also accepts an image
  name without `.png`: add it.

`kind` is one of `protein`, `protein-membrane` (used on a membrane's surface), `fiber`, `membrane-segment`,
`membrane-look`, `lipid`, `nucleic-acid`, `viral`, `ribosome`, `other`, guessed from names and use. `pdb` lists the PDB
ids from the recipes (or the file name). `contributor` names a person other than the lab where a file says so.

## Loading

Every sprite has a direct URL (`url`, percent-encoded: some names hold spaces or `+`; `id` is the URL-safe name):

```js
const index = await (await fetch('https://raw.githubusercontent.com/autinlab/TheLabAsset/main/sprites/index.json')).json();
const s = index.sprites.find(x => x.id === index.lookup.by_image['Albumin_C.png']);
const img = new Image();
img.crossOrigin = 'anonymous';   // required for a WebGL texture (raw.githubusercontent.com sends CORS: *)
img.src = s.url;
```

`raw.githubusercontent.com` is rate-limited: mirror to a CDN for production and keep the paths.

## Citations

- Gardner A, Autin L, Fuentes D, Maritan M, Barad BA, Medina M, Olson AJ, Grotjahn DA, Goodsell DS.
  **CellPAINT: Turnkey Illustration of Molecular Cell Biology.** *Frontiers in Bioinformatics* 1:660936 (2021).
  doi:[10.3389/fbinf.2021.660936](https://doi.org/10.3389/fbinf.2021.660936)
- Jimenez J, Autin L, Ibanez de Caceres I, Goodsell DS. **Integrative Modeling and Visualization of Exosomes.**
  *Journal of Biocommunication* 43(2) (2019). doi:[10.5210/jbc.v43i2.10331](https://doi.org/10.5210/jbc.v43i2.10331)
  (the exosome recipes `exosome*.json`)
- Earlier cellPAINT: Gardner A, Autin L, Barbaro B, Olson AJ, Goodsell DS. **CellPAINT: Interactive Illustration of
  Dynamic Mesoscale Cellular Environments.** *IEEE Computer Graphics and Applications* 38(6) (2018).
  doi:[10.1109/MCG.2018.2877076](https://doi.org/10.1109/MCG.2018.2877076)

The cellPAINT 2 tutorial credits Adam Gardner and Ludovic Autin, with funding from NIH R01-GM120604.
