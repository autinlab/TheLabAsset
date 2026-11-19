"""cellPAINT 2D sprites: import them from a cellPAINT2D checkout, and regenerate sprites/index.json.

  python tools/build_sprites_index.py import <cellPAINT2D checkout>   # copy the PNGs + write tools/sprites_usage.json
  python tools/build_sprites_index.py                                 # rebuild sprites/index.json from the files

`import` reads the checkout read-only: it copies the sprite PNGs (Assets/Resources/Recipie, and the protein and
membrane textures of Assets/cellPAINT/Textures/NewAssets) into sprites/cellpaint/, and records, from the recipes
(Assets/Resources/Recipes/*.json), which ingredient of which recipe uses each image, with its `scale2d`, `offsety`,
`lengthy` and PDB id. That snapshot (tools/sprites_usage.json) is what the plain run reads, so the index is
regenerated, never hand-edited, and the checkout is only needed to refresh it. Pure standard library.
assets.json (build_manifest.py) is not touched.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import struct
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "sprites"
DEST = SPRITES / "cellpaint"
USAGE = ROOT / "tools" / "sprites_usage.json"
REPO = "autinlab/TheLabAsset"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
SCHEMA = "thelab-sprites/1"
SOURCE_REPO = "https://github.com/corredD/cellPAINT2D"

# Unity: a sprite pixel is 1/100 unit (spritePixelsToUnits 100 in every .meta), pivot (0.5, 0.5), and
# 1 unit = 1 nm = 10 A (Manager.unit_scale = 1). A recipe's `sprite.scale2d` is how many image pixels one A is
# (PrefabProperties.cs SetupFromNode: "1 angstrom in the image is scale2d pixel").
SCALE = {
    "unit": "px_per_angstrom",
    "how": "the recipe's sprite.scale2d (PrefabProperties.SetupFromNode); per-ingredient, not per-file: see usage[]",
    "unity_pixels_per_unit": 100,
    "unity_unit_in_angstrom": 10,
    "offsety": "angstrom: the image's middle sits that far up the membrane normal (surface ingredients)",
    "lengthy": "angstrom: the length of a fiber's body (0 or absent: none)",
}
PIVOT = [0.5, 0.5]

# Sprites copied: Recipie/ (all but the people), and these textures (path in the checkout -> folder under cellpaint/).
TEXTURES = {
    "membrane": [f"MembraneCoarse_View{i}.png" for i in range(1, 5)] + ["Lipid_Lipids.png", "Lipid_Gradient.png", "Lipid_Background.png"],
    "proteins": ["RNA Polymerase.png", "HU.png", "Pyruvate Kinase.png", "PhosphFructoKinase.png", "Ribosome.png", "plv_Polio.png"],
}
TEXTURE_DIRS = {"ribosome_dodec": "Ribosome_Dodec", "actin_frames": "Actin"}  # NewAssets sub-folders

# Photographs of colleagues (the cellvis2 recipe, "Machinery of the community") and two more portraits: not copied,
# the consent of the people shown is not known (listed in index.json `excluded`). The autinlab people are in (Ludo,
# 2026-11-19): ludo, arthur_olson, david_goodsell.
PORTRAITS = {
    "Alexrose", "AndersYnnerman", "Beata-Mierzwa", "bridget-carragher", "danielle_grotjahn",
    "DavidSehnal", "drew_berry", "ElizabethVilla", "graham_johnson", "IvanViola-fotor", "j-wasa",
    "John-Glass", "Markus-Covert", "MatthewSwulius", "PeterMindek", "rommie-amaro", "Roseanna_Zia", "SaiLi",
    "stefano", "TimDavison", "TomBartol", "vera", "vishalSivasankar", "zan",
}
# Contributors named by a file (a person other than the lab), by file stem.
CONTRIBUTORS = {
    "ionizable_David": "David Goodsell",
    "ionizable_Adam_inner": "Adam Gardner",
    "ludo": "Ludovic Autin", "arthur_olson": "Arthur Olson", "david_goodsell": "David Goodsell",
    "Alexrose": "Alex Rose", "vishalSivasankar": "Vishal Sivasankar",
}
# The cats recipe's drawings: left out for now (Ludo, 2026-11-19).
DEFERRED = {"cat1", "cat2", "cat3", "cat4", "cat5", "cat6", "mouse1", "arrow", "molecule", "question"} | {f"catmb{i}" for i in range(1, 9)} | {"fiber1", "fiber2", "fiber3", "mousemb1"}
THIRD_PARTY_HINT = {"Roseanna_Zia"}  # portraits of people outside the lab


def png_size(p: Path) -> tuple[int, int]:
    d = p.read_bytes()[:24]
    return struct.unpack(">II", d[16:24])


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def slug(rel: str) -> str:
    """A URL-safe id from a path under cellpaint/ (no extension): lower case, [a-z0-9_.-] only."""
    s = re.sub(r"\.png$", "", rel, flags=re.I)
    s = s.replace("/", ".").replace("+", "_plus_")
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")


def walk_recipe(o, recipe, out, path=()):
    if isinstance(o, dict):
        sp = o.get("sprite")
        if isinstance(sp, dict) and sp.get("image"):
            num = lambda v: float(v) if v not in (None, "") else None  # noqa: E731
            section = next((k for k in ("surface", "interior") if k in path), "cytoplasme" if "cytoplasme" in path else "")
            comp = path[1] if len(path) > 1 and path[0] == "compartments" else ""
            out.append({
                "image": sp["image"], "recipe": recipe, "ingredient": o.get("name"), "label": o.get("label") or None,
                "pdb": (o.get("source") or {}).get("pdb") or None, "type": o.get("Type"), "section": section,
                "compartment": comp, "scale2d": num(sp.get("scale2d")), "offsety": num(sp.get("offsety")),
                "lengthy": num(sp.get("lengthy")),
            })
        for k, v in o.items():
            walk_recipe(v, recipe, out, path + (k,))
    elif isinstance(o, list):
        for v in o:
            walk_recipe(v, recipe, out, path)


def do_import(checkout: Path) -> None:
    res = checkout / "Assets/Resources/Recipie"
    tex = checkout / "Assets/cellPAINT/Textures/NewAssets"
    copied, skipped = [], []
    DEST.mkdir(parents=True, exist_ok=True)

    def put(src: Path, rel: str, origin: str):
        dst = DEST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append({"file": rel, "origin": origin})

    for p in sorted(res.rglob("*.png")):
        rel = p.relative_to(res).as_posix()
        if p.stem in PORTRAITS:
            skipped.append({"file": rel, "reason": "portrait of a person"})
            continue
        if p.stem in DEFERRED:
            skipped.append({"file": rel, "reason": "cats recipe, left out for now"})
            continue
        put(p, rel, "Assets/Resources/Recipie/" + rel)
    # textures: skip a file the Recipie folder already holds byte for byte
    held = {sha256(p) for p in DEST.rglob("*.png")}
    for folder, names in TEXTURES.items():
        for n in names:
            p = tex / n
            if p.exists() and sha256(p) not in held:
                put(p, f"textures/{folder}/{n}", "Assets/cellPAINT/Textures/NewAssets/" + n)
    for folder, sub in TEXTURE_DIRS.items():
        for p in sorted((tex / sub).glob("*.png")):
            put(p, f"textures/{folder}/{p.name}", f"Assets/cellPAINT/Textures/NewAssets/{sub}/{p.name}")

    usage: list[dict] = []
    for f in sorted((checkout / "Assets/Resources/Recipes").glob("*.json")):
        try:
            walk_recipe(json.loads(f.read_text()), f.name, usage)
        except Exception as e:  # a recipe that does not parse is left out
            print("recipe skipped", f.name, e)
    commit = ""
    try:
        import subprocess
        commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        pass
    USAGE.write_text(json.dumps({"source": SOURCE_REPO, "commit": commit, "copied": copied, "excluded": skipped, "usage": usage}, indent=1) + "\n")
    print(f"copied {len(copied)}, excluded {len(skipped)}, usage rows {len(usage)}")


def kind_of(rel: str, rows: list[dict]) -> str:
    stem = rel.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    low = stem.lower()
    if rel.startswith("textures/membrane/"):
        return "membrane-segment" if "MembraneCoarse" in rel else "membrane-look"
    if re.fullmatch(r"(cat)?mb\d+|mousemb\d+|pmembrane|cell_membrane|hiv_membrane", low):
        return "membrane-segment"
    if "membrane" in low:
        return "membrane-segment"
    if re.fullmatch(r"fiber\d|actin(_\d+)?", low) or rel.startswith(("Actin/", "textures/actin_frames/")) or any(r["type"] == "Grow" for r in rows):
        return "fiber"
    if re.match(r"(lipid|cholesterol|ionizable)", low):
        return "lipid"
    if low in ("rna", "rna2", "messenger_rna", "transfer_rna", "mrna_c", "mrna_c_crop", "mrna_w", "mirna_c") or low.startswith("dna") or low == "trna":
        return "nucleic-acid"
    if re.search(r"capsid|nucleocapsid|envelope|penvelope|rnp-|spike|vaccine_spike", low):
        return "viral"
    if low in ("error", "question", "arrow", "molecule", "grapes", "grapes_old") or low.startswith(("cat", "mouse")):
        return "other"
    if rel.startswith("textures/ribosome_dodec/") or low == "ribosome":
        return "ribosome"
    if any(r["section"] == "surface" for r in rows):
        return "protein-membrane"
    return "protein"


def do_index() -> None:
    meta = json.loads(USAGE.read_text())
    by_img: dict[str, list[dict]] = {}
    for u in meta["usage"]:
        by_img.setdefault(u["image"].replace("\\", "/"), []).append(u)
    by_base_lower = {k.lower(): k for k in by_img}
    items = []
    for p in sorted(DEST.rglob("*.png")):
        rel = p.relative_to(DEST).as_posix()
        stem = rel.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        rows = by_img.get(rel) or by_img.get(rel.rsplit("/", 1)[-1]) or by_img.get(by_base_lower.get(rel.lower(), ""), [])
        w, h = png_size(p)
        scales = sorted({r["scale2d"] for r in rows if r["scale2d"]})
        pdbs = sorted({r["pdb"] for r in rows if r["pdb"]})
        if not pdbs and re.fullmatch(r"[0-9][a-z0-9]{3}(_\d+)?", stem.lower()):
            pdbs = [stem.split("_")[0].lower()]
        file = f"sprites/cellpaint/{rel}"
        item = {
            "id": slug(rel), "file": file, "url": RAW + quote(file), "width": w, "height": h,
            "bytes": p.stat().st_size, "sha256": sha256(p),
            "scale2d": scales[0] if len(scales) == 1 else (max(scales, key=lambda s: sum(r["scale2d"] == s for r in rows)) if scales else None),
            "scale2d_values": scales,
            "pivot": PIVOT, "kind": kind_of(rel, rows),
            "pdb": pdbs, "ingredients": sorted({r["ingredient"] for r in rows if r["ingredient"]}),
            "recipes": sorted({r["recipe"].removesuffix(".json") for r in rows}),
            "usage": [{k: r[k] for k in ("recipe", "ingredient", "label", "section", "compartment", "scale2d", "offsety", "lengthy") if r[k] not in (None, "")} for r in rows],
            "source": "cellPAINT2D " + next((c["origin"] for c in meta["copied"] if c["file"] == rel), ""),
        }
        if stem in CONTRIBUTORS:
            item["contributor"] = CONTRIBUTORS[stem]
        items.append(item)
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate sprite ids"
    # lookups meso* uses: a recipe's `sprite.image` (with or without .png, any case) and an ingredient name -> id
    by_image = {}
    for i in items:
        by_image[i["file"].removeprefix("sprites/cellpaint/")] = i["id"]
    by_ingredient: dict[str, list[str]] = {}
    for i in items:
        for n in i["ingredients"]:
            by_ingredient.setdefault(n, [])
            if i["id"] not in by_ingredient[n]:
                by_ingredient[n].append(i["id"])
    out = {
        "schema": SCHEMA, "repo": f"https://github.com/{REPO}", "base_url": RAW, "updated": date.today().isoformat(),
        "count": len(items), "total_bytes": sum(i["bytes"] for i in items),
        "source": {"repo": meta["source"], "commit": meta["commit"],
                   "note": "cellPAINT 2D (Autin lab, Scripps Research); sprites by Adam Gardner, inspired by David Goodsell. Licensed CC BY 4.0 (sprites/LICENSE)."}, "license": "CC-BY-4.0",
        "scale": SCALE,
        "lookup": {"by_image": by_image, "by_ingredient": by_ingredient},
        "excluded": meta["excluded"],
        "sprites": items,
    }
    (SPRITES / "index.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote sprites/index.json: {len(items)} sprites, {out['total_bytes'] / 1e6:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "import":
        do_import(Path(sys.argv[2]).expanduser())
    do_index()
