#!/usr/bin/env python3

# Quick script to stitch TE23D-style tiles into a full scene image.
# Tiles named like: 004_1_2_10.png (scene_col_row_sub)
# Just groups tiles, builds each block, then pastes blocks into the mosaic.

import os
import re
import argparse
from collections import defaultdict
from PIL import Image

# default tile/block settings
DEFAULT_TILE_SIZE = 256
DEFAULT_GRID_SIZE = 4
DEFAULT_SUB_BASE = 1
BG_RGBA = (0, 0, 0, 0)   # transparent for gaps

# filename pattern (scene_col_row_sub.ext)
namePattern = re.compile(
    r"^(\d+)_([0-9]+)_([0-9]+)_([0-9]+)\.(png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)

def parseName(fileName):
    """pull scene/col/row/sub from name. return None if not matching."""
    m = namePattern.match(fileName)
    if not m:
        return None
    # ignore extension group
    sceneId, colId, rowId, subId = map(int, m.groups()[:4])
    return sceneId, colId, rowId, subId

def subToRowCol(subIndex, gridSize, subBaseIndex):
    """map sub-index to (row,col) inside block (so sub=1..16 goes to 4x4 layout)."""
    idx = subIndex - subBaseIndex
    # clip if filenames aren't clean
    if idx < 0: idx = 0
    maxIdx = gridSize * gridSize - 1
    if idx > maxIdx: idx = maxIdx
    return idx // gridSize, idx % gridSize

def loadTile(tilePath, tileSize):
    """read tile image and make sure it matches expected size."""
    img = Image.open(tilePath).convert("RGBA")
    if img.size != (tileSize, tileSize):
        img = img.resize((tileSize, tileSize), Image.NEAREST)
    return img

def buildBlocks(tilesDir, sceneId, gridSize, tileSize, subBaseIndex):
    """
    Collect all tiles for this scene and assemble each (col,row) block.
    One block = gridSize x gridSize tiles.
    """
    # track all tile paths by block position
    blockFiles = defaultdict(dict)

    for fileName in os.listdir(tilesDir):
        parsed = parseName(fileName)
        if not parsed:
            continue

        scene, colId, rowId, subId = parsed
        if scene != sceneId:
            continue

        blockFiles[(colId, rowId)][subId] = os.path.join(tilesDir, fileName)

    blockPxSize = gridSize * tileSize
    sceneBlocks = {}

    # build the actual block images
    for (colId, rowId), subDict in blockFiles.items():
        blockImg = Image.new("RGBA", (blockPxSize, blockPxSize), BG_RGBA)

        for subIndex, tilePath in subDict.items():
            r, c = subToRowCol(subIndex, gridSize, subBaseIndex)
            x = c * tileSize
            y = r * tileSize
            tileImg = loadTile(tilePath, tileSize)
            blockImg.alpha_composite(tileImg, (x, y))

        sceneBlocks[(colId, rowId)] = blockImg

    return sceneBlocks

def makeDenseMap(values):
    """compact raw indexes into 0..N-1 (so big gaps don't stretch the mosaic)."""
    uniq = sorted(set(values))
    return {v: i for i, v in enumerate(uniq)}, uniq

def stitchScene(sceneBlocks, strideX, strideY, dense=True):
    """
    Paste all (col,row) blocks into final mosaic.
    dense=True keeps layout close together even if col/row numbers skip.
    """
    if not sceneBlocks:
        raise ValueError("no blocks found to stitch")

    colIds = [c for (c, _) in sceneBlocks.keys()]
    rowIds = [r for (_, r) in sceneBlocks.keys()]

    if dense:
        colMap, _ = makeDenseMap(colIds)
        rowMap, _ = makeDenseMap(rowIds)
        blockPos = {(c, r): (colMap[c] * strideX, rowMap[r] * strideY)
                    for (c, r) in sceneBlocks}
    else:
        blockPos = {(c, r): (c * strideX, r * strideY)
                    for (c, r) in sceneBlocks}

    # get block size from one sample (all same)
    sampleBlock = next(iter(sceneBlocks.values()))
    bw, bh = sampleBlock.size

    # canvas size = max offset + block size
    maxX = max(x for (x, _) in blockPos.values())
    maxY = max(y for (_, y) in blockPos.values())
    canvasW = maxX + bw
    canvasH = maxY + bh

    mosaic = Image.new("RGBA", (canvasW, canvasH), BG_RGBA)

    # paste them in
    for key, img in sceneBlocks.items():
        x, y = blockPos[key]
        mosaic.alpha_composite(img, (x, y))

    return mosaic

def main():
    # args (kept same as original)
    parser = argparse.ArgumentParser()
    parser.add_argument("tiles_dir")
    parser.add_argument("--scene", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--tile", type=int, default=DEFAULT_TILE_SIZE)
    parser.add_argument("--grid", type=int, default=DEFAULT_GRID_SIZE)
    parser.add_argument("--sub-base", type=int, default=DEFAULT_SUB_BASE)
    parser.add_argument("--dense", action="store_true")
    parser.add_argument("--no-dense", dest="dense", action="store_false")
    parser.set_defaults(dense=True)
    parser.add_argument("--stride-x", type=int)
    parser.add_argument("--stride-y", type=int)
    args = parser.parse_args()

    tileSize = args.tile
    gridSize = args.grid
    subBaseIndex = args.sub_base
    tilesDir = args.tiles_dir
    sceneId = args.scene

    # block stride (can override if needed)
    blockPx = gridSize * tileSize
    strideX = args.stride_x if args.stride_x is not None else blockPx
    strideY = args.stride_y if args.stride_y is not None else blockPx

    # build blocks for the scene
    sceneBlocks = buildBlocks(tilesDir, sceneId, gridSize, tileSize, subBaseIndex)

    if not sceneBlocks:
        print(f"no tiles found for scene {sceneId:03d}")
        return

    # stitch into one big image
    mosaic = stitchScene(sceneBlocks, strideX, strideY, dense=args.dense)

    # save output
    outDir = os.path.dirname(args.out)
    if outDir:
        os.makedirs(outDir, exist_ok=True)
    mosaic.save(args.out)

    print(f"[scene {sceneId:03d}] saved to {args.out}, size={mosaic.size}")

if __name__ == "__main__":
    main()
